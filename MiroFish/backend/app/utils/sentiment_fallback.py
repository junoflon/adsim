"""
LLM 감정 분석 실패 시 사용하는 로컬 폴백 분석기.
한국어 긍정·부정 키워드 및 패턴으로 sentiment/score/reactions를 추출한다.

완전한 대체는 아니지만 429나 타임아웃으로 LLM 분석이 실패해도
"분석 실패" 대신 의미 있는 신호를 남기는 게 목적.
"""

import re
from typing import Dict, List, Any


# 한국어 긍정·부정 키워드 (가중치 포함)
POSITIVE_TERMS = {
    # 강한 긍정
    "완전 좋": 3.0, "진짜 좋": 2.5, "너무 좋": 2.5, "정말 좋": 2.0, "아주 좋": 2.0,
    "딱 좋": 2.0, "꼭 사": 2.5, "사고 싶": 2.5, "구매 의향": 2.0, "만족": 1.5,
    "최고": 2.0, "훌륭": 2.0, "대박": 2.0, "완벽": 2.0, "이거지": 2.0,
    "추천하고 싶": 2.0, "친구한테": 1.5, "입소문": 1.5, "흥미": 1.2,
    # 중간 긍정
    "좋아": 1.0, "괜찮": 1.0, "끌린": 1.5, "신기": 1.2, "이색": 1.0,
    "매력": 1.5, "편리": 1.2, "유용": 1.2, "깔끔": 1.0, "감각": 1.0,
    "예쁘": 1.0, "귀여": 1.0, "세련": 1.2, "고급": 1.0, "프리미엄": 1.0,
    "혜자": 1.5, "가성비 좋": 1.8, "합리": 1.2, "납득": 1.0,
    "믿을 만": 1.2, "신뢰": 1.2, "공감": 1.2, "도움": 1.0,
    # 약한 긍정
    "나쁘지 않": 0.6, "무난": 0.5, "그럭저럭": 0.3,
}

NEGATIVE_TERMS = {
    # 강한 부정
    "절대 안": -3.0, "전혀 안": -2.5, "싫": -2.0, "별로": -1.8, "안 사": -2.5,
    "안 살": -2.5, "구매 안": -2.5, "구매하지 않": -2.5, "필요 없": -2.0,
    "쓸모 없": -2.0, "의미 없": -1.8, "실망": -2.0, "짜증": -2.0, "불쾌": -2.5,
    "거부감": -2.5, "기분 나쁘": -2.5, "거슬": -1.8, "어이없": -2.0,
    "사기": -2.5, "과장": -1.8, "의심": -1.5, "불신": -2.0, "믿을 수 없": -2.0,
    # 중간 부정
    "비싸": -1.5, "부담": -1.5, "아까": -1.2, "낭비": -1.5, "가성비 안": -1.5,
    "애매": -1.0, "어색": -1.0, "부자연": -1.2, "억지": -1.5, "진부": -1.2,
    "식상": -1.2, "흔해": -0.8, "흔한": -0.8, "뻔한": -1.0, "별 감흥": -1.2,
    "관심 없": -1.5, "흥미 없": -1.5, "와닿지 않": -1.5, "이해 안": -1.2,
    "신뢰 안": -1.8, "약해": -1.0, "부족": -1.0, "아쉬": -1.0, "걱정": -1.0,
    "우려": -1.2, "불안": -1.5, "꺼림칙": -1.5, "찜찜": -1.5,
    # 약한 부정
    "모르겠": -0.3, "글쎄": -0.5, "잘 모르": -0.3, "음…": -0.3,
}


# 점수 언급 패턴: "5점", "8/10", "7 점"
SCORE_PATTERNS = [
    re.compile(r"(\d+)\s*점"),
    re.compile(r"(\d+)\s*/\s*10"),
]


def _assistant_text(conversation_log: List[Dict]) -> str:
    """어시스턴트(에이전트) 응답만 이어붙인 텍스트"""
    parts = []
    for msg in conversation_log or []:
        if msg.get("role") == "assistant":
            content = msg.get("content") or ""
            if content and content != "(응답 실패)":
                parts.append(content)
    return "\n".join(parts)


def _detect_numeric_score(text: str) -> float:
    """텍스트에서 1~10점 언급이 있으면 -1~1로 정규화해서 반환, 없으면 None"""
    for pat in SCORE_PATTERNS:
        m = pat.search(text)
        if m:
            try:
                n = int(m.group(1))
                if 1 <= n <= 10:
                    # 1~10 → -1~1
                    return (n - 5.5) / 4.5
            except Exception:
                continue
    return None


def analyze_sentiment_local(conversation_log: List[Dict]) -> Dict[str, Any]:
    """
    로컬 감정 분석. LLM 없이 키워드 기반으로 sentiment/score/reactions 산출.

    Returns:
        {
            "sentiment": "positive"|"negative"|"neutral",
            "sentiment_score": float in [-1, 1],
            "key_reactions": [str, ...]
        }
    """
    text = _assistant_text(conversation_log)
    if not text.strip():
        return {
            "sentiment": "neutral",
            "sentiment_score": 0.0,
            "key_reactions": ["응답 없음"],
        }

    # 키워드 점수 합산
    score = 0.0
    hits_positive = []
    hits_negative = []
    for term, w in POSITIVE_TERMS.items():
        count = text.count(term)
        if count:
            score += w * count
            hits_positive.append((term, w, count))
    for term, w in NEGATIVE_TERMS.items():
        count = text.count(term)
        if count:
            score += w * count
            hits_negative.append((term, w, count))

    # 정규화: 길이 기반으로 tanh 스케일
    # text 길이 대비 가중합 스케일 — 매우 길어도 [-1, 1]로 수렴
    import math
    normalized = math.tanh(score / 6.0)

    # 명시적 점수 언급이 있으면 그걸 가중 평균
    explicit = _detect_numeric_score(text)
    if explicit is not None:
        normalized = 0.4 * normalized + 0.6 * explicit

    normalized = max(-1.0, min(1.0, normalized))

    # 감정 분류
    if normalized >= 0.3:
        sentiment = "positive"
    elif normalized <= -0.3:
        sentiment = "negative"
    else:
        sentiment = "neutral"

    # 핵심 반응 뽑기 (가중치 큰 순서)
    combined = hits_positive + hits_negative
    combined.sort(key=lambda x: abs(x[1] * x[2]), reverse=True)
    reactions = []
    seen = set()
    for term, _w, _c in combined[:10]:
        # 문장 단위로 해당 키워드가 포함된 짧은 구절을 뽑음
        for sent in re.split(r"[.!?\n]", text):
            s = sent.strip()
            if term in s and 5 <= len(s) <= 70 and s not in seen:
                reactions.append(s)
                seen.add(s)
                break
        if len(reactions) >= 3:
            break

    if not reactions:
        # 긍/부정 키워드 없었으면 상위 문장 한두 개
        sents = [s.strip() for s in re.split(r"[.!?\n]", text) if 10 <= len(s.strip()) <= 70]
        reactions = sents[:2] if sents else ["로컬 분석: 중립 반응"]

    return {
        "sentiment": sentiment,
        "sentiment_score": round(normalized, 2),
        "key_reactions": reactions[:4],
    }

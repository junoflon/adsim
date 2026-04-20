"""
페르소나 관리자
기본 페르소나 설정으로부터 다양한 개별 에이전트를 생성
"""

import random
from typing import Dict, Any, List

# 한국 일반적인 성 (상위 20개)
KOREAN_SURNAMES = [
    "김", "이", "박", "최", "정", "강", "조", "윤", "장", "임",
    "한", "오", "서", "신", "권", "황", "안", "송", "전", "홍"
]

# 연령대/성별별 흔한 이름
NAMES_FEMALE_2030 = ["지연", "서연", "민지", "수빈", "예진", "지민", "혜원", "소영", "유진", "나연"]
NAMES_FEMALE_4050 = ["현정", "미영", "은주", "선희", "정희", "경숙", "영미", "수진", "은영", "진숙"]
NAMES_MALE_2030 = ["민수", "준호", "성민", "지훈", "현우", "동현", "준석", "승우", "태윤", "우진"]
NAMES_MALE_4050 = ["재호", "영수", "성호", "동우", "종민", "경태", "상훈", "진수", "승현", "정호"]

# 성격 특성 풀
PERSONALITY_POOLS = {
    "careful": ["신중함", "꼼꼼함", "분석적", "조심스러움"],
    "trendy": ["트렌드에 민감함", "SNS 활발", "감성적", "호기심 많음"],
    "frugal": ["가성비 추구", "절약 지향", "실용적", "가격 비교 즐김"],
    "premium": ["품질 우선", "브랜드 중시", "디테일 중시", "프리미엄 선호"],
    "social": ["주변 평판 중시", "입소문 잘 퍼뜨림", "추천 잘함", "외향적"],
    "skeptical": ["의심 많음", "검증 필수", "리뷰 꼼꼼히 확인", "쉽게 믿지 않음"]
}

# 직업 풀 (연령대별)
OCCUPATIONS_BY_AGE = {
    "20s": ["대학생", "신입사원", "프리랜서 디자이너", "편의점 알바", "대학원생", "바리스타", "콜센터 상담원", "유튜버 지망생", "영업사원", "간호사"],
    "30s": ["회사원 대리", "마케터", "스타트업 개발자", "자영업자 (카페 운영)", "웨딩플래너", "요가 강사", "중학교 교사", "물류 관리", "플로리스트", "영상 편집자", "변호사 어쏘"],
    "40s": ["팀장", "부장", "편의점 점주", "주부 (자녀 2)", "학원 강사", "IT 중소기업 임원", "부동산 중개인", "화물차 기사", "간호부장", "공인회계사"],
    "50s": ["부장", "임원", "자영업자 (식당 운영)", "주부", "공무원 (행정직)", "사업가", "운수업", "은퇴 준비 중", "치과의사"]
}

# 소득 수준
INCOME_LEVELS = ["하", "중하", "중", "중상", "상"]

# 라이프 상황 / 맥락 (에이전트 개성 강화)
LIFE_CONTEXTS = [
    "최근 이직 준비 중", "혼자 자취 5년 차", "결혼 2년 차, 아이 계획 중", "초등학생 자녀 육아 중",
    "연애 1년 차", "연애 공백기", "반려견과 동거", "최근 부모님과 독립", "대학 졸업 직전",
    "이직한 지 3개월", "재택근무 위주", "출퇴근 2시간", "프리랜서로 수입 불안정", "첫 내 집 마련 고민",
    "최근 건강 이슈로 운동 시작", "다이어트 시도 중", "금연/금주 시도 중", "부업 준비 중",
    "최근 큰 지출이 있어 아끼는 중", "보너스 받아 여유 있음", "최근 친구가 추천한 제품을 많이 써봄",
    "SNS 보다가 충동구매 경험 다수", "리뷰 꼼꼼히 읽고 구매하는 편", "경조사 많은 시즌"
]

# 구매 결정 스타일 (에이전트마다 다르게)
DECISION_STYLES = [
    "리뷰·가격비교 철저히 한 뒤 구매",
    "지인·인플루언서 추천 의존도 높음",
    "브랜드 익숙하지 않으면 안 삼",
    "할인·이벤트 중심으로 구매",
    "패키지·컨셉이 예쁘면 지갑 열림",
    "성분·기능 스펙 꼼꼼히 확인",
    "기분 내키면 즉시 구매 후 후회도 함",
    "중고·당근에서 먼저 찾아보는 편"
]

# 어투 스타일 힌트
SPEAKING_STYLES = [
    "직설적이고 간결하게 말함",
    "완곡하게 돌려서 말함",
    "감정 표현이 풍부함",
    "논리적 근거를 먼저 댐",
    "비유를 자주 씀",
    "짧게 답하는 편",
    "세부 디테일에 집착",
    "솔직하지만 공격적이지 않게"
]


def _get_age_bucket(age: int) -> str:
    if age < 30:
        return "20s"
    elif age < 40:
        return "30s"
    elif age < 50:
        return "40s"
    else:
        return "50s"


def _pick_name(age: int, gender: str) -> str:
    bucket = _get_age_bucket(age)
    if gender == "female":
        pool = NAMES_FEMALE_2030 if bucket in ("20s", "30s") else NAMES_FEMALE_4050
    else:
        pool = NAMES_MALE_2030 if bucket in ("20s", "30s") else NAMES_MALE_4050
    return random.choice(KOREAN_SURNAMES) + random.choice(pool)


def _pick_personality(preset_interests: List[str]) -> List[str]:
    """페르소나 프리셋 관심사에 따라 성격 특성 선택"""
    # 기본 2~3개 랜덤 + 프리셋 힌트
    pools_to_use = []

    # 관심사에 따라 성격 편향
    interest_text = " ".join(preset_interests).lower()
    if any(k in interest_text for k in ["건강", "다이어트", "운동"]):
        pools_to_use.append("careful")
    if any(k in interest_text for k in ["sns", "트렌드", "감성소비", "인스타"]):
        pools_to_use.append("trendy")
    if any(k in interest_text for k in ["가성비", "편의점", "경제"]):
        pools_to_use.append("frugal")
    if any(k in interest_text for k in ["품질", "브랜드", "프리미엄"]):
        pools_to_use.append("premium")

    # 기본 풀 몇 개 추가
    all_pools = list(PERSONALITY_POOLS.keys())
    random.shuffle(all_pools)
    pools_to_use.extend(all_pools[:2])

    # 중복 제거
    pools_to_use = list(set(pools_to_use))[:3]

    # 각 풀에서 1개씩 선택
    traits = []
    for p in pools_to_use:
        traits.append(random.choice(PERSONALITY_POOLS[p]))

    return traits


def _parse_age_range(age_range: str) -> tuple[int, int]:
    """'25-35' 같은 문자열 파싱"""
    try:
        parts = age_range.replace(" ", "").split("-")
        return int(parts[0]), int(parts[1])
    except Exception:
        return 20, 60


def _pick_gender(gender_str: str) -> str:
    """'여성 70%, 남성 30%' 같은 문자열에서 확률적으로 성별 추출"""
    if not gender_str:
        return random.choice(["female", "male"])
    s = gender_str.lower()
    female_weight = 50
    if "여성" in s or "female" in s:
        # "여성 70%" 같은 패턴 찾기
        import re
        m = re.search(r"여성\s*(\d+)%", gender_str)
        if m:
            female_weight = int(m.group(1))
    return "female" if random.random() * 100 < female_weight else "male"


def generate_agents(persona_config: Dict[str, Any], count: int) -> List[Dict[str, Any]]:
    """
    페르소나 설정에서 N명의 다양한 개별 에이전트 생성

    Args:
        persona_config: {
            "name": "2030 건강 관심 여성",
            "age_range": "25-35",
            "gender": "여성 70%, 남성 30%",
            "interests": ["건강", "다이어트"],
            "consumption_habits": "편의점 음료 주 3회 이상"
        }
        count: 생성할 에이전트 수

    Returns:
        [{agent_id, name, age, gender, occupation, interests, personality_traits, ...}, ...]
    """
    age_min, age_max = _parse_age_range(persona_config.get("age_range", "20-60"))
    base_interests = persona_config.get("interests", [])
    consumption = persona_config.get("consumption_habits", "")

    agents = []
    for i in range(count):
        age = random.randint(age_min, age_max)
        gender = _pick_gender(persona_config.get("gender", ""))
        gender_kr = "여성" if gender == "female" else "남성"
        name = _pick_name(age, gender)
        bucket = _get_age_bucket(age)
        occupation = random.choice(OCCUPATIONS_BY_AGE.get(bucket, ["직장인"]))
        personality = _pick_personality(base_interests)

        # 관심사에 약간의 편차 주기 (기본 + 1~2개 추가)
        extra_interests = random.sample(
            ["맛집", "여행", "영화", "독서", "게임", "요리", "쇼핑", "반려동물"],
            k=random.randint(1, 2)
        )
        interests = list(set(base_interests + extra_interests))

        # 소득 수준 (연령대에 따른 편향)
        if bucket == "20s":
            income = random.choice(["하", "중하", "중", "중"])
        elif bucket == "30s":
            income = random.choice(["중하", "중", "중", "중상"])
        else:
            income = random.choice(["중", "중상", "중상", "상"])

        life_ctx = random.choice(LIFE_CONTEXTS)
        decision_style = random.choice(DECISION_STYLES)
        speaking = random.choice(SPEAKING_STYLES)

        agents.append({
            "agent_id": i + 1,
            "name": name,
            "age": age,
            "gender": gender_kr,
            "occupation": occupation,
            "income_level": income,
            "interests": interests,
            "personality_traits": personality,
            "shopping_habits": consumption or f"{bucket} 일반 소비자",
            "life_context": life_ctx,
            "decision_style": decision_style,
            "speaking_style": speaking,
        })

    return agents

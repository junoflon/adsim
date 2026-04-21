"""
AdSim API -- 광고/USP 시뮬레이션 엔드포인트
"""

import os
import threading
from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename

from ..config import Config
from ..database.adsim_db import AdSimDB
from ..services.ad_simulation_service import run_simulation
from ..services.ad_comparison_service import run_comparison

adsim_bp = Blueprint('adsim', __name__, url_prefix='/api/adsim')

ALLOWED_EXTENSIONS = {'pdf', 'txt', 'md', 'docx', 'hwp', 'hwpx', 'xlsx', 'csv'}
MAX_CONTENT_CHARS = 20000


def _ok(data, status=200):
    return jsonify({"success": True, "data": data}), status


def _err(message, status=400):
    return jsonify({"success": False, "error": message}), status


# ── Projects ──

@adsim_bp.route('/projects', methods=['POST'])
def create_project():
    body = request.get_json()
    if not body or not body.get('name') or not body.get('type'):
        return _err("name과 type은 필수입니다")
    if body['type'] not in ('ad_reaction', 'usp_test', 'product_hypothesis', 'brand_hypothesis'):
        return _err("type은 ad_reaction, usp_test, product_hypothesis, brand_hypothesis 중 하나여야 합니다")
    project = AdSimDB.create_project(
        name=body['name'],
        project_type=body['type'],
        description=body.get('description', '')
    )
    return _ok(project, 201)


@adsim_bp.route('/projects', methods=['GET'])
def list_projects():
    return _ok(AdSimDB.list_projects())


@adsim_bp.route('/projects/<project_id>', methods=['GET'])
def get_project(project_id):
    project = AdSimDB.get_project(project_id)
    if not project:
        return _err("프로젝트를 찾을 수 없습니다", 404)
    return _ok(project)


@adsim_bp.route('/projects/<project_id>', methods=['DELETE'])
def delete_project(project_id):
    if not AdSimDB.delete_project(project_id):
        return _err("프로젝트를 찾을 수 없습니다", 404)
    return _ok({"deleted": project_id})


# ── Seed Materials ──

@adsim_bp.route('/projects/<project_id>/seeds', methods=['POST'])
def create_seed(project_id):
    if not AdSimDB.get_project(project_id):
        return _err("프로젝트를 찾을 수 없습니다", 404)

    content = ""
    file_path = ""
    file_size = 0
    reference_url = ""

    if request.content_type and 'multipart/form-data' in request.content_type:
        seed_type = request.form.get('type', 'ad_script')
        content = request.form.get('content', '')
        reference_url = (request.form.get('reference_url') or '').strip()
        file = request.files.get('file')
        if file and file.filename:
            filename = secure_filename(file.filename)
            ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
            if ext not in ALLOWED_EXTENSIONS:
                return _err(f"허용되지 않는 파일 형식입니다. 허용: {sorted(ALLOWED_EXTENSIONS)}")
            upload_dir = os.path.join(Config.UPLOAD_FOLDER, 'adsim', project_id)
            os.makedirs(upload_dir, exist_ok=True)
            file_path = os.path.join(upload_dir, filename)
            file.save(file_path)
            file_size = os.path.getsize(file_path)
            # 파일에서 텍스트 추출
            from ..utils.file_extractor import extract_text
            extracted = extract_text(file_path, max_chars=MAX_CONTENT_CHARS)
            if extracted:
                # 유저 직접 입력 + 파일 텍스트를 함께 합쳐 저장
                content = ((content + "\n\n") if content else "") + f"[첨부 파일: {filename}]\n{extracted}"
    else:
        body = request.get_json()
        if not body:
            return _err("요청 본문이 비어있습니다")
        seed_type = body.get('type', 'ad_script')
        content = body.get('content', '')
        reference_url = (body.get('reference_url') or '').strip()

    # 참조 URL(노션/구글독스 등)이 있으면 내용에 병합
    if reference_url:
        content = ((content + "\n\n") if content else "") + f"[참조 링크]\n{reference_url}\n(위 페이지 내용도 함께 고려해 주세요.)"

    if not content and not file_path:
        return _err("content, file, reference_url 중 하나는 필수입니다")
    if seed_type not in ('ad_script', 'usp_text', 'competitor_info', 'product_concept', 'brand_concept'):
        return _err("type은 ad_script, usp_text, competitor_info, product_concept, brand_concept 중 하나여야 합니다")
    if len(content) > MAX_CONTENT_CHARS:
        content = content[:MAX_CONTENT_CHARS]

    seed = AdSimDB.create_seed(
        project_id=project_id,
        seed_type=seed_type,
        content=content,
        file_path=file_path,
        file_size=file_size
    )
    return _ok(seed, 201)


@adsim_bp.route('/projects/<project_id>/seeds', methods=['GET'])
def list_seeds(project_id):
    if not AdSimDB.get_project(project_id):
        return _err("프로젝트를 찾을 수 없습니다", 404)
    return _ok(AdSimDB.list_seeds(project_id))


@adsim_bp.route('/projects/<project_id>/seeds/<seed_id>', methods=['DELETE'])
def delete_seed(project_id, seed_id):
    if not AdSimDB.delete_seed(seed_id):
        return _err("시드 자료를 찾을 수 없습니다", 404)
    return _ok({"deleted": seed_id})


# ── Persona Configs ──

PRESET_PERSONAS = [
    {"name": "2030 건강 관심 여성", "age_range": "25-35", "gender": "여성 70%, 남성 30%", "interests": ["건강", "다이어트", "운동"], "consumption_habits": "편의점 음료 주 3회 이상 구매"},
    {"name": "3040 직장인 남성", "age_range": "30-45", "gender": "남성 70%, 여성 30%", "interests": ["경력", "효율성", "재테크"], "consumption_habits": "출퇴근 중 커피/음료 구매"},
    {"name": "2030 트렌드세터", "age_range": "20-30", "gender": "여성 60%, 남성 40%", "interests": ["SNS", "신제품", "패션"], "consumption_habits": "인스타 광고 보고 구매 경험 다수"},
    {"name": "4050 가족 중심", "age_range": "40-55", "gender": "여성 50%, 남성 50%", "interests": ["가족", "건강", "교육"], "consumption_habits": "대형마트 장보기 주 1회"},
    {"name": "2030 학생", "age_range": "18-25", "gender": "여성 50%, 남성 50%", "interests": ["가성비", "편의점", "유튜브"], "consumption_habits": "편의점 행사 상품 위주 구매"},
    {"name": "3040 프리미엄 소비자", "age_range": "30-45", "gender": "여성 50%, 남성 50%", "interests": ["품질", "브랜드", "건강기능"], "consumption_habits": "프리미엄 제품 선호, 가격 덜 민감"},
    {"name": "전 연령 일반", "age_range": "20-55", "gender": "여성 50%, 남성 50%", "interests": ["일상", "가성비", "편리함"], "consumption_habits": "다양한 채널에서 구매"},
    {"name": "시니어 보수층", "age_range": "50-65", "gender": "여성 50%, 남성 50%", "interests": ["건강", "전통", "신뢰"], "consumption_habits": "검증된 브랜드만 구매"},
    {"name": "2030 MZ 감성", "age_range": "20-35", "gender": "여성 60%, 남성 40%", "interests": ["감성소비", "인스타그래머블", "경험"], "consumption_habits": "감성적 패키징/스토리에 반응"},
    {"name": "3040 워킹맘", "age_range": "30-45", "gender": "여성 90%, 남성 10%", "interests": ["시간절약", "간편함", "아이건강"], "consumption_habits": "온라인 장보기, 간편식 다수 구매"},
]


@adsim_bp.route('/personas/presets', methods=['GET'])
def get_preset_personas():
    return _ok(PRESET_PERSONAS)


@adsim_bp.route('/personas/auto-generate', methods=['POST'])
def auto_generate_persona():
    body = request.get_json() or {}
    description = (body.get('description') or '').strip()
    if not description:
        return _err("description을 입력하세요")
    if len(description) > 400:
        return _err("description은 400자 이내로 입력하세요")

    # 고정 조건 (사용자가 이미 설정한 값)
    try:
        age_min = int(body.get('age_min', 25))
        age_max = int(body.get('age_max', 40))
        female_ratio = int(body.get('female_ratio', 50))
    except (TypeError, ValueError):
        return _err("age_min, age_max, female_ratio는 정수여야 합니다")
    age_min = max(10, min(90, age_min))
    age_max = max(age_min + 1, min(95, age_max))
    female_ratio = max(0, min(100, female_ratio))

    # 동일 프로젝트 내 기존 페르소나와 중복 회피
    project_id = body.get('project_id')
    existing = []
    if project_id:
        try:
            existing = AdSimDB.list_personas(project_id)
        except Exception:
            existing = []

    try:
        from ..utils.llm_client import LLMClient
        from ..prompts.persona_generator_prompt import create_persona_generation_prompt
        llm = LLMClient()
        result = llm.chat_json(
            messages=[{"role": "user", "content": create_persona_generation_prompt(
                description=description,
                age_min=age_min,
                age_max=age_max,
                female_ratio=female_ratio,
                existing_personas=existing,
            )}],
            temperature=0.7,
            max_tokens=800,
        )
        return _ok({
            'name': result.get('name', description[:30]),
            'age_min': age_min,
            'age_max': age_max,
            'female_ratio': female_ratio,
            'interests': result.get('interests', []),
            'consumption_habits': result.get('consumption_habits', ''),
            'personality_tags': result.get('personality_tags', []),
        })
    except Exception as e:
        return _err(f"페르소나 자동 생성 실패: {e}", 500)


@adsim_bp.route('/projects/<project_id>/personas', methods=['POST'])
def create_persona(project_id):
    if not AdSimDB.get_project(project_id):
        return _err("프로젝트를 찾을 수 없습니다", 404)
    body = request.get_json()
    if not body or not body.get('name') or not body.get('age_range'):
        return _err("name과 age_range는 필수입니다")
    agent_count = body.get('agent_count', 30)
    if not (3 <= agent_count <= 100):
        return _err("agent_count는 3~100 사이여야 합니다")
    persona = AdSimDB.create_persona(
        project_id=project_id,
        name=body['name'],
        age_range=body['age_range'],
        gender=body.get('gender', ''),
        interests=body.get('interests', []),
        consumption_habits=body.get('consumption_habits', ''),
        agent_count=agent_count,
        is_preset=body.get('is_preset', False)
    )
    return _ok(persona, 201)


@adsim_bp.route('/projects/<project_id>/personas', methods=['GET'])
def list_personas(project_id):
    if not AdSimDB.get_project(project_id):
        return _err("프로젝트를 찾을 수 없습니다", 404)
    return _ok(AdSimDB.list_personas(project_id))


@adsim_bp.route('/projects/<project_id>/personas/<persona_id>', methods=['DELETE'])
def delete_persona(project_id, persona_id):
    if not AdSimDB.delete_persona(persona_id):
        return _err("페르소나를 찾을 수 없습니다", 404)
    return _ok({"deleted": persona_id})


# ── Simulations ──

@adsim_bp.route('/projects/<project_id>/simulations', methods=['POST'])
def create_simulation(project_id):
    if not AdSimDB.get_project(project_id):
        return _err("프로젝트를 찾을 수 없습니다", 404)
    body = request.get_json()
    if not body or not body.get('seed_id') or not body.get('persona_id'):
        return _err("seed_id와 persona_id는 필수입니다")
    if not AdSimDB.get_seed(body['seed_id']):
        return _err("시드 자료를 찾을 수 없습니다", 404)
    total_rounds = body.get('total_rounds', 30)
    if not (5 <= total_rounds <= 50):
        return _err("total_rounds는 5~50 사이여야 합니다")

    platform = body.get('platform') or 'unspecified'
    ALLOWED_PLATFORMS = {
        'meta_feed', 'meta_reels', 'google_search', 'youtube_preroll', 'youtube_inline',
        'naver_feed', 'tiktok', 'tv_cf', 'kakao', 'web_article', 'offline', 'unspecified'
    }
    if platform not in ALLOWED_PLATFORMS:
        return _err(f"platform은 {sorted(ALLOWED_PLATFORMS)} 중 하나여야 합니다")

    simulation = AdSimDB.create_simulation(
        project_id=project_id,
        persona_config_id=body['persona_id'],
        seed_id=body['seed_id'],
        total_rounds=total_rounds
    )

    # 시뮬레이션 실행에 필요한 데이터 수집
    seed = AdSimDB.get_seed(body['seed_id'])
    personas = AdSimDB.list_personas(project_id)
    persona = next((p for p in personas if p['persona_id'] == body['persona_id']), None)
    if not persona:
        return _err("페르소나를 찾을 수 없습니다", 404)

    agent_count = body.get('custom_agent_count') or persona['agent_count']

    # 비동기로 시뮬레이션 실행
    thread = threading.Thread(
        target=run_simulation,
        kwargs={
            'simulation_id': simulation['simulation_id'],
            'seed_content': seed['content'] or '',
            'persona_config': persona,
            'total_rounds': total_rounds,
            'agent_count': agent_count,
            'seed_type': seed.get('type', 'ad_script'),
            'platform': platform,
        },
        daemon=True
    )
    thread.start()

    return _ok(simulation, 202)


@adsim_bp.route('/simulations/<simulation_id>', methods=['GET'])
def get_simulation(simulation_id):
    sim = AdSimDB.get_simulation(simulation_id)
    if not sim:
        return _err("시뮬레이션을 찾을 수 없습니다", 404)
    return _ok(sim)


@adsim_bp.route('/simulations/<simulation_id>/progress', methods=['GET'])
def get_simulation_progress(simulation_id):
    sim = AdSimDB.get_simulation(simulation_id)
    if not sim:
        return _err("시뮬레이션을 찾을 수 없습니다", 404)
    progress = 0
    if sim['total_rounds'] > 0:
        progress = round(sim['current_round'] / sim['total_rounds'] * 100)
    return _ok({
        "simulation_id": simulation_id,
        "status": sim['status'],
        "current_round": sim['current_round'],
        "total_rounds": sim['total_rounds'],
        "progress_percent": progress
    })


@adsim_bp.route('/simulations/<simulation_id>/cancel', methods=['PATCH'])
def cancel_simulation(simulation_id):
    sim = AdSimDB.get_simulation(simulation_id)
    if not sim:
        return _err("시뮬레이션을 찾을 수 없습니다", 404)
    if sim['status'] not in ('pending', 'running'):
        return _err("취소할 수 없는 상태입니다")
    AdSimDB.update_simulation_status(simulation_id, "failed")
    return _ok({"simulation_id": simulation_id, "status": "failed"})


# ── Results ──

@adsim_bp.route('/simulations/<simulation_id>/report', methods=['GET'])
def get_report(simulation_id):
    report = AdSimDB.get_report(simulation_id)
    if not report:
        return _err("보고서가 아직 생성되지 않았습니다", 404)
    return _ok(report)


@adsim_bp.route('/simulations/<simulation_id>/responses', methods=['GET'])
def list_responses(simulation_id):
    responses = AdSimDB.list_responses(simulation_id)
    return _ok({
        "total_agents": len(responses),
        "responses": [{
            "response_id": r["response_id"],
            "agent_id": r["agent_id"],
            "agent_name": r["agent_name"],
            "sentiment": r["sentiment"],
            "sentiment_score": r["sentiment_score"],
            "key_reactions": r["key_reactions"]
        } for r in responses]
    })


@adsim_bp.route('/simulations/<simulation_id>/responses/<response_id>', methods=['GET'])
def get_response_detail(simulation_id, response_id):
    resp = AdSimDB.get_response(response_id)
    if not resp:
        return _err("에이전트 반응을 찾을 수 없습니다", 404)
    return _ok(resp)


@adsim_bp.route('/simulations/<simulation_id>/rounds', methods=['GET'])
def list_rounds(simulation_id):
    return _ok(AdSimDB.list_rounds(simulation_id))


@adsim_bp.route('/simulations/<simulation_id>/responses.csv', methods=['GET'])
def export_responses_csv(simulation_id):
    """에이전트별 응답을 CSV로 내보내기"""
    import csv
    import io
    from flask import Response as FlaskResponse

    responses = AdSimDB.list_responses(simulation_id)
    if not responses:
        return _err("응답이 없습니다", 404)

    output = io.StringIO()
    # UTF-8 BOM: 엑셀에서 한글 깨짐 방지
    output.write('\ufeff')
    writer = csv.writer(output)
    writer.writerow([
        'agent_id', 'agent_name', 'sentiment', 'sentiment_score',
        'key_reactions', 'age', 'gender', 'occupation', 'life_context',
        'decision_style', 'speaking_style', 'interests', 'income_level'
    ])
    for r in responses:
        p = r.get('agent_persona', {}) or {}
        writer.writerow([
            r.get('agent_id', ''),
            r.get('agent_name', ''),
            r.get('sentiment', ''),
            r.get('sentiment_score', ''),
            ' · '.join(r.get('key_reactions', []) or []),
            p.get('age', ''),
            p.get('gender', ''),
            p.get('occupation', ''),
            p.get('life_context', ''),
            p.get('decision_style', ''),
            p.get('speaking_style', ''),
            ', '.join(p.get('interests', []) or []),
            p.get('income_level', ''),
        ])
    csv_data = output.getvalue()
    filename = f"adsim_{simulation_id}_responses.csv"
    return FlaskResponse(
        csv_data,
        mimetype='text/csv; charset=utf-8',
        headers={'Content-Disposition': f'attachment; filename="{filename}"'}
    )


# ── A/B Comparisons ──

@adsim_bp.route('/projects/<project_id>/comparisons', methods=['POST'])
def create_comparison(project_id):
    if not AdSimDB.get_project(project_id):
        return _err("프로젝트를 찾을 수 없습니다", 404)
    body = request.get_json()
    if not body:
        return _err("요청 본문이 비어있습니다")
    required = ['name', 'persona_id', 'seed_a_id', 'seed_b_id']
    missing = [k for k in required if not body.get(k)]
    if missing:
        return _err(f"필수 필드 누락: {', '.join(missing)}")
    if body['seed_a_id'] == body['seed_b_id']:
        return _err("seed_a_id와 seed_b_id는 서로 달라야 합니다")

    seed_a = AdSimDB.get_seed(body['seed_a_id'])
    seed_b = AdSimDB.get_seed(body['seed_b_id'])
    if not seed_a or not seed_b:
        return _err("시드 자료를 찾을 수 없습니다", 404)

    personas = AdSimDB.list_personas(project_id)
    persona = next((p for p in personas if p['persona_id'] == body['persona_id']), None)
    if not persona:
        return _err("페르소나를 찾을 수 없습니다", 404)

    total_rounds = body.get('total_rounds', 4)
    if not (1 <= total_rounds <= 10):
        return _err("total_rounds는 1~10 사이여야 합니다")
    agent_count = body.get('custom_agent_count') or persona['agent_count']

    comparison = AdSimDB.create_comparison(
        project_id=project_id,
        name=body['name'],
        persona_config_id=body['persona_id'],
        seed_a_id=body['seed_a_id'],
        seed_b_id=body['seed_b_id'],
    )

    thread = threading.Thread(
        target=run_comparison,
        kwargs={
            'comparison_id': comparison['comparison_id'],
            'project_id': project_id,
            'persona_config': persona,
            'seed_a': seed_a,
            'seed_b': seed_b,
            'total_rounds': total_rounds,
            'agent_count': agent_count,
        },
        daemon=True,
    )
    thread.start()

    return _ok(comparison, 202)


@adsim_bp.route('/projects/<project_id>/comparisons', methods=['GET'])
def list_comparisons(project_id):
    if not AdSimDB.get_project(project_id):
        return _err("프로젝트를 찾을 수 없습니다", 404)
    return _ok(AdSimDB.list_comparisons(project_id))


@adsim_bp.route('/comparisons/<comparison_id>', methods=['GET'])
def get_comparison(comparison_id):
    comparison = AdSimDB.get_comparison(comparison_id)
    if not comparison:
        return _err("비교를 찾을 수 없습니다", 404)
    return _ok(comparison)


@adsim_bp.route('/comparisons/<comparison_id>', methods=['DELETE'])
def delete_comparison(comparison_id):
    if not AdSimDB.delete_comparison(comparison_id):
        return _err("비교를 찾을 수 없습니다", 404)
    return _ok({"deleted": comparison_id})

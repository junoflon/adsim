<template>
  <div class="adsim-compare">
    <header class="topbar">
      <div class="topbar-left">
        <div class="logo" @click="$router.push('/adsim')">
          <span class="logo-mark">◆</span>
          <span class="logo-text">AdSim</span>
        </div>
        <span class="breadcrumb-sep">/</span>
        <span class="breadcrumb-link" @click="$router.push(`/adsim/project/${projectId}`)">{{ project?.name || '프로젝트' }}</span>
        <span class="breadcrumb-sep">/</span>
        <span class="breadcrumb-current">A/B 비교</span>
      </div>
    </header>

    <div class="content" v-if="project">
      <div class="page-header">
        <h1>A/B 비교 시뮬레이션</h1>
        <p class="sub">같은 타겟에 두 광고안을 동시 테스트하고 어느 쪽이 더 효과적인지 비교합니다.</p>
      </div>

      <!-- Setup -->
      <section v-if="!activeComparisonId" class="panel">
        <!-- Seeds A/B -->
        <div class="grid-2">
          <div class="ab-card">
            <div class="ab-header"><span class="ab-tag a">A</span> 광고안</div>
            <textarea v-model="seedAContent" placeholder="A 광고안 내용을 붙여넣으세요..." rows="10" maxlength="5000"></textarea>
            <span class="len">{{ seedAContent.length }} / 5,000</span>
          </div>
          <div class="ab-card">
            <div class="ab-header"><span class="ab-tag b">B</span> 광고안</div>
            <textarea v-model="seedBContent" placeholder="B 광고안 내용을 붙여넣으세요..." rows="10" maxlength="5000"></textarea>
            <span class="len">{{ seedBContent.length }} / 5,000</span>
          </div>
        </div>

        <!-- Persona -->
        <div class="section-title">타겟 페르소나</div>
        <div class="persona-grid">
          <div v-for="(p, i) in presets" :key="i"
               :class="['persona-card', { selected: selectedPreset === i }]"
               @click="selectedPreset = i" tabindex="0" role="radio">
            <div class="persona-check" v-if="selectedPreset === i">✓</div>
            <div class="persona-name">{{ p.name }}</div>
            <div class="persona-age">{{ p.age_range }}</div>
            <div class="persona-tags">
              <span v-for="(t, ti) in p.interests?.slice(0, 3)" :key="ti" class="ptag">{{ t }}</span>
            </div>
          </div>
        </div>

        <!-- Settings -->
        <div class="settings-row">
          <div class="field">
            <label>에이전트 수</label>
            <input type="range" v-model.number="agentCount" min="10" max="60" step="5" />
            <span class="val">{{ agentCount }}명 × 2안</span>
          </div>
          <div class="field">
            <label>비교 이름</label>
            <input type="text" v-model="compareName" placeholder="예: 신제품 음료 A vs B" maxlength="60" class="text-input" />
          </div>
        </div>

        <button class="run-btn" :disabled="!canRun || starting" @click="handleRun">
          <span v-if="starting" class="spinner-sm"></span>
          <span v-else>A/B 비교 시작 →</span>
        </button>
        <p class="cost-hint">※ 시뮬레이션 2개를 동시 실행합니다. LLM 비용이 단일 실행의 2배입니다.</p>
      </section>

      <!-- Progress / Result -->
      <section v-else class="panel">
        <div v-if="!comparison" class="center-state">
          <div class="spinner-lg"></div><p>비교 불러오는 중...</p>
        </div>

        <div v-else-if="comparison.status === 'pending' || comparison.status === 'running'" class="running">
          <div class="orbit"><div class="orbit-dot" v-for="n in 3" :key="n" :style="{ animationDelay: n * 0.4 + 's' }"></div></div>
          <h2>A/B 비교 진행 중</h2>
          <p class="run-desc">두 광고안의 시뮬레이션이 병렬로 실행되고 있습니다.</p>
          <div class="sub-sims">
            <div class="sub-sim">
              <span class="ab-tag a">A</span>
              <span>{{ subStatus(comparison.simulation_a_id) }}</span>
            </div>
            <div class="sub-sim">
              <span class="ab-tag b">B</span>
              <span>{{ subStatus(comparison.simulation_b_id) }}</span>
            </div>
          </div>
        </div>

        <div v-else-if="comparison.status === 'failed'" class="center-state">
          <div class="fail-icon">✕</div>
          <h2>비교 실패</h2>
          <p>실행 중 오류가 발생했습니다.</p>
          <button class="btn-ghost" @click="reset">다시 시도</button>
        </div>

        <div v-else-if="comparison.status === 'completed' && comparison.comparison_result" class="result">
          <div class="winner-box" :class="'w-' + comparison.comparison_result.winner">
            <div class="winner-label">승자</div>
            <div class="winner-value">
              <span v-if="comparison.comparison_result.winner === 'tie'">🤝 무승부</span>
              <span v-else>{{ comparison.comparison_result.winner }}안 승리</span>
            </div>
            <p class="winner-reason">{{ comparison.comparison_result.winner_reason }}</p>
          </div>

          <div class="sent-compare">
            <div class="sent-col">
              <div class="col-head"><span class="ab-tag a">A</span></div>
              <div class="bar-row"><span>긍정</span><div class="bar"><div class="fill pos" :style="{ width: (comparison.comparison_result.sentiment_a?.positive || 0) + '%' }"></div></div><span>{{ comparison.comparison_result.sentiment_a?.positive || 0 }}%</span></div>
              <div class="bar-row"><span>중립</span><div class="bar"><div class="fill neu" :style="{ width: (comparison.comparison_result.sentiment_a?.neutral || 0) + '%' }"></div></div><span>{{ comparison.comparison_result.sentiment_a?.neutral || 0 }}%</span></div>
              <div class="bar-row"><span>부정</span><div class="bar"><div class="fill neg" :style="{ width: (comparison.comparison_result.sentiment_a?.negative || 0) + '%' }"></div></div><span>{{ comparison.comparison_result.sentiment_a?.negative || 0 }}%</span></div>
            </div>
            <div class="sent-col">
              <div class="col-head"><span class="ab-tag b">B</span></div>
              <div class="bar-row"><span>긍정</span><div class="bar"><div class="fill pos" :style="{ width: (comparison.comparison_result.sentiment_b?.positive || 0) + '%' }"></div></div><span>{{ comparison.comparison_result.sentiment_b?.positive || 0 }}%</span></div>
              <div class="bar-row"><span>중립</span><div class="bar"><div class="fill neu" :style="{ width: (comparison.comparison_result.sentiment_b?.neutral || 0) + '%' }"></div></div><span>{{ comparison.comparison_result.sentiment_b?.neutral || 0 }}%</span></div>
              <div class="bar-row"><span>부정</span><div class="bar"><div class="fill neg" :style="{ width: (comparison.comparison_result.sentiment_b?.negative || 0) + '%' }"></div></div><span>{{ comparison.comparison_result.sentiment_b?.negative || 0 }}%</span></div>
            </div>
          </div>

          <div class="grid-2">
            <div class="swot">
              <h4><span class="ab-tag a">A</span> 강점</h4>
              <ul><li v-for="(x, i) in comparison.comparison_result.a_strengths" :key="i">{{ x }}</li></ul>
              <h4>약점</h4>
              <ul><li v-for="(x, i) in comparison.comparison_result.a_weaknesses" :key="i">{{ x }}</li></ul>
            </div>
            <div class="swot">
              <h4><span class="ab-tag b">B</span> 강점</h4>
              <ul><li v-for="(x, i) in comparison.comparison_result.b_strengths" :key="i">{{ x }}</li></ul>
              <h4>약점</h4>
              <ul><li v-for="(x, i) in comparison.comparison_result.b_weaknesses" :key="i">{{ x }}</li></ul>
            </div>
          </div>

          <div class="diff-box">
            <h3>핵심 차이점</h3>
            <ul><li v-for="(x, i) in comparison.comparison_result.key_differences" :key="i">{{ x }}</li></ul>
          </div>

          <div class="rec-box">
            <h3>추천사항</h3>
            <p>{{ comparison.comparison_result.recommendation }}</p>
          </div>

          <div class="result-nav">
            <button class="btn-ghost" @click="reset">새 비교 시작</button>
            <div class="sub-links">
              <a v-if="comparison.simulation_a_id" :href="`/adsim/simulation/${comparison.simulation_a_id}`" target="_blank">A 상세 →</a>
              <a v-if="comparison.simulation_b_id" :href="`/adsim/simulation/${comparison.simulation_b_id}`" target="_blank">B 상세 →</a>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import {
  getProject, getPresetPersonas, createSeed, createPersona,
  createComparison, getComparison, getSimulation,
} from '../api/adsim.js'

const route = useRoute()
const projectId = route.params.projectId

const project = ref(null)
const presets = ref([])
const seedAContent = ref('')
const seedBContent = ref('')
const selectedPreset = ref(null)
const agentCount = ref(20)
const compareName = ref('')
const starting = ref(false)
const activeComparisonId = ref(null)
const comparison = ref(null)
const subSimStatus = ref({})
let poll = null

const canRun = computed(() =>
  seedAContent.value.trim() && seedBContent.value.trim() && selectedPreset.value !== null && compareName.value.trim()
)

const subStatus = (simId) => {
  if (!simId) return '대기 중...'
  const s = subSimStatus.value[simId]
  if (!s) return '시작 중...'
  if (s.status === 'completed') return '✓ 완료'
  if (s.status === 'failed') return '✗ 실패'
  return `진행 중 (${s.current_round}/${s.total_rounds})`
}

const handleRun = async () => {
  if (!canRun.value || starting.value) return
  starting.value = true
  try {
    const preset = presets.value[selectedPreset.value]
    const personaRes = await createPersona(projectId, { ...preset, agent_count: agentCount.value, is_preset: true })
    const [seedARes, seedBRes] = await Promise.all([
      createSeed(projectId, { type: project.value.type === 'ad_reaction' ? 'ad_script' : 'usp_text', content: seedAContent.value }),
      createSeed(projectId, { type: project.value.type === 'ad_reaction' ? 'ad_script' : 'usp_text', content: seedBContent.value }),
    ])
    const res = await createComparison(projectId, {
      name: compareName.value,
      persona_id: personaRes.data.data.persona_id,
      seed_a_id: seedARes.data.data.seed_id,
      seed_b_id: seedBRes.data.data.seed_id,
      total_rounds: 4,
      custom_agent_count: agentCount.value,
    })
    activeComparisonId.value = res.data.data.comparison_id
    startPolling()
  } catch (e) {
    alert('시작 실패: ' + (e.response?.data?.error || e.message))
  } finally { starting.value = false }
}

const loadComparison = async () => {
  if (!activeComparisonId.value) return
  try {
    const r = await getComparison(activeComparisonId.value)
    comparison.value = r.data.data
    // poll sub simulations too
    const ids = [comparison.value.simulation_a_id, comparison.value.simulation_b_id].filter(Boolean)
    if (ids.length) {
      const results = await Promise.all(ids.map(id => getSimulation(id).then(x => x.data.data).catch(() => null)))
      const map = {}
      results.filter(Boolean).forEach(s => { map[s.simulation_id] = s })
      subSimStatus.value = map
    }
    if (['completed', 'failed'].includes(comparison.value.status)) {
      stopPolling()
    }
  } catch (e) { console.error(e) }
}

const startPolling = () => {
  loadComparison()
  poll = setInterval(loadComparison, 3000)
}
const stopPolling = () => { if (poll) { clearInterval(poll); poll = null } }

const reset = () => {
  stopPolling()
  activeComparisonId.value = null
  comparison.value = null
  seedAContent.value = ''
  seedBContent.value = ''
  compareName.value = ''
  selectedPreset.value = null
}

onMounted(async () => {
  const [p, pr] = await Promise.all([getProject(projectId), getPresetPersonas()])
  project.value = p.data.data
  presets.value = pr.data.data
})
onUnmounted(stopPolling)
</script>

<style scoped>
* { box-sizing: border-box; }
.adsim-compare { min-height: 100vh; background: #0c0f14; color: #e8eaf0; font-family: 'IBM Plex Sans', 'Noto Sans KR', system-ui, sans-serif; -webkit-font-smoothing: antialiased; }

.topbar { height: 56px; display: flex; align-items: center; padding: 0 32px; border-bottom: 1px solid #1e2636; background: rgba(12,15,20,0.85); backdrop-filter: blur(12px); position: sticky; top: 0; z-index: 50; }
.topbar-left { display: flex; align-items: center; gap: 10px; }
.logo { display: flex; align-items: center; gap: 8px; cursor: pointer; }
.logo-mark { color: #d4a053; }
.logo-text { font-family: 'IBM Plex Mono', monospace; font-weight: 600; font-size: 0.95rem; }
.breadcrumb-sep { color: #5a6378; }
.breadcrumb-link { font-size: 0.85rem; color: #8b93a6; cursor: pointer; }
.breadcrumb-link:hover { color: #d4a053; }
.breadcrumb-current { font-size: 0.85rem; color: #8b93a6; }

.content { max-width: 960px; margin: 0 auto; padding: 32px 24px 80px; }
.page-header { margin-bottom: 32px; }
.page-header h1 { font-size: 1.6rem; margin: 0 0 8px; }
.sub { color: #8b93a6; margin: 0; font-size: 0.9rem; }

.panel { animation: fadeIn 0.3s; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } }

.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 28px; }
.ab-card { background: #181d27; border: 1px solid #1e2636; border-radius: 8px; padding: 16px; position: relative; }
.ab-header { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; font-weight: 600; font-size: 0.95rem; }
.ab-tag { width: 24px; height: 24px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-family: 'IBM Plex Mono', monospace; font-size: 0.75rem; font-weight: 700; color: #0c0f14; }
.ab-tag.a { background: #5ea8d4; }
.ab-tag.b { background: #a87ed4; }
.ab-card textarea { width: 100%; background: #0c0f14; border: 1px solid #2a3244; color: #e8eaf0; padding: 12px; font-family: 'IBM Plex Mono', monospace; font-size: 0.83rem; line-height: 1.6; border-radius: 6px; resize: vertical; min-height: 180px; outline: none; }
.ab-card textarea:focus { border-color: #d4a053; }
.len { font-family: 'IBM Plex Mono', monospace; font-size: 0.68rem; color: #5a6378; margin-top: 6px; display: block; text-align: right; }

.section-title { font-size: 0.95rem; font-weight: 600; margin: 24px 0 12px; }
.persona-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(190px, 1fr)); gap: 10px; margin-bottom: 24px; }
.persona-card { background: #181d27; border: 1px solid #1e2636; border-radius: 8px; padding: 14px; cursor: pointer; transition: all 0.2s; position: relative; outline: none; }
.persona-card:hover { border-color: #5a6378; }
.persona-card.selected { border-color: #d4a053; background: rgba(212,160,83,0.08); }
.persona-check { position: absolute; top: 8px; right: 8px; width: 20px; height: 20px; background: #d4a053; color: #0c0f14; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.65rem; font-weight: 700; }
.persona-name { font-weight: 600; font-size: 0.85rem; margin-bottom: 4px; }
.persona-age { font-family: 'IBM Plex Mono', monospace; font-size: 0.7rem; color: #5a6378; margin-bottom: 6px; }
.persona-tags { display: flex; flex-wrap: wrap; gap: 4px; }
.ptag { font-size: 0.65rem; padding: 2px 7px; background: #232a38; border-radius: 99px; color: #8b93a6; }

.settings-row { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 24px; }
.field { background: #181d27; border: 1px solid #1e2636; border-radius: 8px; padding: 14px 16px; }
.field label { display: block; font-size: 0.78rem; color: #8b93a6; margin-bottom: 10px; font-family: 'IBM Plex Mono', monospace; text-transform: uppercase; letter-spacing: 0.5px; }
.field input[type="range"] { width: 100%; appearance: none; height: 4px; background: #2a3244; border-radius: 2px; outline: none; }
.field input[type="range"]::-webkit-slider-thumb { appearance: none; width: 16px; height: 16px; border-radius: 50%; background: #d4a053; cursor: pointer; border: 2px solid #0c0f14; }
.val { display: block; margin-top: 6px; font-family: 'IBM Plex Mono', monospace; font-size: 0.82rem; color: #d4a053; font-weight: 600; }
.text-input { width: 100%; background: #0c0f14; border: 1px solid #2a3244; color: #e8eaf0; padding: 10px 12px; border-radius: 6px; font-size: 0.9rem; outline: none; font-family: inherit; }
.text-input:focus { border-color: #d4a053; }

.run-btn { width: 100%; background: #d4a053; color: #0c0f14; border: none; padding: 16px; border-radius: 8px; font-weight: 700; font-size: 1rem; cursor: pointer; transition: all 0.25s; }
.run-btn:hover:not(:disabled) { background: #e0b060; box-shadow: 0 6px 24px rgba(212,160,83,0.3); }
.run-btn:disabled { opacity: 0.35; cursor: not-allowed; }
.spinner-sm { display: inline-block; width: 14px; height: 14px; border: 2px solid rgba(0,0,0,0.2); border-top-color: #0c0f14; border-radius: 50%; animation: spin 0.6s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.cost-hint { text-align: center; font-size: 0.78rem; color: #5a6378; margin-top: 12px; }

/* Running / Result */
.center-state { text-align: center; padding: 80px 0; color: #8b93a6; }
.spinner-lg { width: 28px; height: 28px; border: 3px solid #2a3244; border-top-color: #d4a053; border-radius: 50%; animation: spin 0.8s linear infinite; margin: 0 auto 16px; }
.running { text-align: center; padding: 60px 0; }
.running h2 { font-size: 1.4rem; margin: 0 0 8px; }
.run-desc { color: #8b93a6; margin-bottom: 32px; }
.orbit { width: 64px; height: 64px; position: relative; margin: 0 auto 24px; }
.orbit-dot { width: 10px; height: 10px; background: #d4a053; border-radius: 50%; position: absolute; top: 50%; left: 50%; animation: orbit-spin 1.8s linear infinite; }
@keyframes orbit-spin { to { transform: rotate(360deg) translateX(24px); } }
.sub-sims { display: flex; justify-content: center; gap: 24px; font-family: 'IBM Plex Mono', monospace; font-size: 0.88rem; color: #8b93a6; }
.sub-sim { display: flex; align-items: center; gap: 10px; }

.fail-icon { font-size: 2.5rem; color: #ef4444; margin-bottom: 16px; }

.result { display: flex; flex-direction: column; gap: 20px; }
.winner-box { background: #181d27; border: 1px solid #1e2636; border-radius: 10px; padding: 28px; text-align: center; }
.winner-box.w-A { border-left: 4px solid #5ea8d4; }
.winner-box.w-B { border-left: 4px solid #a87ed4; }
.winner-box.w-tie { border-left: 4px solid #8b93a6; }
.winner-label { font-family: 'IBM Plex Mono', monospace; font-size: 0.72rem; color: #5a6378; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; }
.winner-value { font-size: 1.8rem; font-weight: 700; margin-bottom: 12px; color: #d4a053; }
.winner-reason { color: #8b93a6; line-height: 1.7; max-width: 600px; margin: 0 auto; }

.sent-compare { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.sent-col { background: #181d27; border: 1px solid #1e2636; border-radius: 8px; padding: 18px; }
.col-head { margin-bottom: 14px; }
.bar-row { display: grid; grid-template-columns: 40px 1fr 44px; gap: 10px; align-items: center; font-size: 0.82rem; margin-bottom: 8px; }
.bar { height: 7px; background: #232a38; border-radius: 4px; overflow: hidden; }
.fill { height: 100%; transition: width 0.6s; }
.fill.pos { background: #4ade80; }
.fill.neu { background: #94a3b8; }
.fill.neg { background: #ef4444; }

.swot { background: #181d27; border: 1px solid #1e2636; border-radius: 8px; padding: 20px; }
.swot h4 { font-size: 0.88rem; margin: 0 0 8px; display: flex; align-items: center; gap: 8px; }
.swot h4:not(:first-child) { margin-top: 16px; }
.swot ul { list-style: none; padding: 0; margin: 0; }
.swot li { font-size: 0.85rem; color: #8b93a6; line-height: 1.6; padding-left: 14px; position: relative; margin-bottom: 6px; }
.swot li::before { content: '•'; position: absolute; left: 0; color: #d4a053; }

.diff-box, .rec-box { background: #181d27; border: 1px solid #1e2636; border-radius: 8px; padding: 22px; }
.diff-box h3, .rec-box h3 { font-size: 1rem; margin: 0 0 12px; }
.diff-box ul { list-style: none; padding: 0; margin: 0; }
.diff-box li { font-size: 0.88rem; color: #8b93a6; line-height: 1.7; padding-left: 18px; position: relative; }
.diff-box li::before { content: '→'; position: absolute; left: 0; color: #d4a053; }
.rec-box { border-left: 3px solid #4ade80; }
.rec-box p { margin: 0; color: #8b93a6; line-height: 1.75; font-size: 0.9rem; }

.result-nav { display: flex; justify-content: space-between; align-items: center; margin-top: 16px; padding-top: 20px; border-top: 1px solid #1e2636; }
.btn-ghost { background: none; border: 1px solid #2a3244; color: #8b93a6; padding: 10px 20px; border-radius: 6px; cursor: pointer; font-size: 0.85rem; }
.btn-ghost:hover { border-color: #d4a053; color: #d4a053; }
.sub-links { display: flex; gap: 16px; }
.sub-links a { color: #d4a053; text-decoration: none; font-size: 0.85rem; }
.sub-links a:hover { text-decoration: underline; }

@media (max-width: 768px) {
  .grid-2, .sent-compare, .settings-row { grid-template-columns: 1fr; }
  .persona-grid { grid-template-columns: 1fr 1fr; }
}
</style>

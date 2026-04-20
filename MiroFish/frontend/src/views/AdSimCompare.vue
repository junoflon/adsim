<template>
  <div class="page">
    <header class="topbar">
      <div class="bar-left">
        <span class="brand" @click="$router.push('/adsim')">AdSim</span>
        <span class="bar-sep">/</span>
        <span class="bar-link" @click="$router.push(`/adsim/project/${projectId}`)">{{ project?.name || '프로젝트' }}</span>
        <span class="bar-sep">/</span>
        <span class="bar-crumb">A/B 비교</span>
      </div>
    </header>
    <div class="rule-line"></div>

    <main class="wrap" v-if="project">
      <!-- Setup -->
      <section v-if="!activeComparisonId">
        <div class="page-head">
          <span class="eyebrow">A/B Comparison</span>
          <h1>두 광고안 중,<br/><span class="italic">어느 쪽이 더 효과적일까요?</span></h1>
          <p class="lede">
            같은 타겟 집단에 두 광고안을 동시에 테스트하고, AI가 승자와 그 이유를 분석합니다.
          </p>
        </div>

        <!-- AB inputs -->
        <div class="ab-grid">
          <div class="ab-card a">
            <div class="ab-head">
              <span class="ab-tag">A</span>
              <span class="ab-label">광고안 A</span>
            </div>
            <textarea v-model="seedAContent"
                      placeholder="A 광고안 내용을 붙여넣으세요…"
                      rows="10" maxlength="5000"></textarea>
            <span class="len">{{ seedAContent.length }} / 5,000</span>
          </div>
          <div class="ab-divider">
            <span class="vs">vs</span>
          </div>
          <div class="ab-card b">
            <div class="ab-head">
              <span class="ab-tag">B</span>
              <span class="ab-label">광고안 B</span>
            </div>
            <textarea v-model="seedBContent"
                      placeholder="B 광고안 내용을 붙여넣으세요…"
                      rows="10" maxlength="5000"></textarea>
            <span class="len">{{ seedBContent.length }} / 5,000</span>
          </div>
        </div>

        <!-- Persona -->
        <div class="section-label">
          <span class="sl-n">01</span>
          <span class="sl-text">타겟 페르소나 선택</span>
        </div>
        <div class="persona-grid">
          <button v-for="(p, i) in presets" :key="i"
                  :class="['p-card', { on: selectedPreset === i }]"
                  @click="selectedPreset = i"
                  type="button">
            <span class="p-n">{{ String(i + 1).padStart(2, '0') }}</span>
            <h3 class="p-name">{{ p.name }}</h3>
            <span class="p-age">{{ p.age_range }}세</span>
            <div class="p-tags">
              <span v-for="(t, ti) in p.interests?.slice(0, 3)" :key="ti">{{ t }}</span>
            </div>
          </button>
        </div>

        <!-- Settings -->
        <div class="section-label">
          <span class="sl-n">02</span>
          <span class="sl-text">실행 설정</span>
        </div>
        <div class="settings-row">
          <div class="setting">
            <label>비교 이름</label>
            <input type="text" v-model="compareName" placeholder="예: 신제품 음료 A vs B" maxlength="60" />
          </div>
          <div class="setting">
            <label>에이전트 수 (각 안당)</label>
            <div class="range-wrap">
              <input type="range" v-model.number="agentCount" min="10" max="60" step="5" />
              <span class="range-val">{{ agentCount }}명</span>
            </div>
          </div>
        </div>

        <button class="go-btn" :disabled="!canRun || starting" @click="handleRun">
          <span v-if="starting" class="spin"></span>
          <template v-else>
            <span>A/B 비교 시작</span>
            <span class="arrow">→</span>
          </template>
        </button>
        <p class="cost-hint">※ 시뮬레이션 2개를 동시 실행합니다. LLM 비용이 단일 실행의 2배입니다.</p>
      </section>

      <!-- Progress / Result -->
      <section v-else>
        <div v-if="!comparison" class="state-center">
          <span class="dot-pulse"></span>
          <p>불러오는 중…</p>
        </div>

        <div v-else-if="comparison.status === 'pending' || comparison.status === 'running'" class="running">
          <span class="eyebrow">Running</span>
          <h1>A/B 비교 진행 중</h1>
          <p class="lede">두 광고안이 동시에 테스트되고 있습니다.</p>
          <div class="ab-status">
            <div class="as-col">
              <span class="ab-tag big a">A</span>
              <div>
                <div class="as-label">광고안 A</div>
                <div class="as-val">{{ subStatus(comparison.simulation_a_id) }}</div>
              </div>
            </div>
            <div class="as-col">
              <span class="ab-tag big b">B</span>
              <div>
                <div class="as-label">광고안 B</div>
                <div class="as-val">{{ subStatus(comparison.simulation_b_id) }}</div>
              </div>
            </div>
          </div>
        </div>

        <div v-else-if="comparison.status === 'failed'" class="state-center">
          <span class="eyebrow err">Failed</span>
          <h1>비교 실패</h1>
          <p>실행 중 오류가 발생했습니다.</p>
          <button class="next-btn" @click="reset">다시 시도하기</button>
        </div>

        <div v-else-if="comparison.status === 'completed' && comparison.comparison_result" class="result">
          <header class="result-head">
            <span class="eyebrow">Verdict</span>
          </header>

          <!-- Winner -->
          <div class="winner" :class="'w-' + comparison.comparison_result.winner">
            <span class="w-label">승자</span>
            <h2 class="w-title">
              <template v-if="comparison.comparison_result.winner === 'tie'">
                <span class="italic">무승부</span>
              </template>
              <template v-else>
                <span class="w-letter">{{ comparison.comparison_result.winner }}</span>
                안이 더 설득력 있었어요
              </template>
            </h2>
            <p class="w-reason">{{ comparison.comparison_result.winner_reason }}</p>
          </div>

          <!-- Sentiment compare -->
          <div class="sent-compare">
            <div class="sc-col">
              <div class="sc-head"><span class="ab-tag a">A</span><span>광고안 A</span></div>
              <div class="sbar"><span>긍정</span><div class="st"><div class="sf pos" :style="{ width: (comparison.comparison_result.sentiment_a?.positive || 0) + '%' }"></div></div><span class="pct">{{ comparison.comparison_result.sentiment_a?.positive || 0 }}%</span></div>
              <div class="sbar"><span>중립</span><div class="st"><div class="sf neu" :style="{ width: (comparison.comparison_result.sentiment_a?.neutral || 0) + '%' }"></div></div><span class="pct">{{ comparison.comparison_result.sentiment_a?.neutral || 0 }}%</span></div>
              <div class="sbar"><span>부정</span><div class="st"><div class="sf neg" :style="{ width: (comparison.comparison_result.sentiment_a?.negative || 0) + '%' }"></div></div><span class="pct">{{ comparison.comparison_result.sentiment_a?.negative || 0 }}%</span></div>
            </div>
            <div class="sc-col">
              <div class="sc-head"><span class="ab-tag b">B</span><span>광고안 B</span></div>
              <div class="sbar"><span>긍정</span><div class="st"><div class="sf pos" :style="{ width: (comparison.comparison_result.sentiment_b?.positive || 0) + '%' }"></div></div><span class="pct">{{ comparison.comparison_result.sentiment_b?.positive || 0 }}%</span></div>
              <div class="sbar"><span>중립</span><div class="st"><div class="sf neu" :style="{ width: (comparison.comparison_result.sentiment_b?.neutral || 0) + '%' }"></div></div><span class="pct">{{ comparison.comparison_result.sentiment_b?.neutral || 0 }}%</span></div>
              <div class="sbar"><span>부정</span><div class="st"><div class="sf neg" :style="{ width: (comparison.comparison_result.sentiment_b?.negative || 0) + '%' }"></div></div><span class="pct">{{ comparison.comparison_result.sentiment_b?.negative || 0 }}%</span></div>
            </div>
          </div>

          <!-- SWOT -->
          <div class="swot-grid">
            <div class="swot-card a">
              <div class="swot-head"><span class="ab-tag a">A</span><span>광고안 A</span></div>
              <div class="swot-sec">
                <h4><span class="plus">+</span>강점</h4>
                <ul><li v-for="(x, i) in comparison.comparison_result.a_strengths" :key="i">{{ x }}</li></ul>
              </div>
              <div class="swot-sec">
                <h4><span class="minus">−</span>약점</h4>
                <ul><li v-for="(x, i) in comparison.comparison_result.a_weaknesses" :key="i">{{ x }}</li></ul>
              </div>
            </div>
            <div class="swot-card b">
              <div class="swot-head"><span class="ab-tag b">B</span><span>광고안 B</span></div>
              <div class="swot-sec">
                <h4><span class="plus">+</span>강점</h4>
                <ul><li v-for="(x, i) in comparison.comparison_result.b_strengths" :key="i">{{ x }}</li></ul>
              </div>
              <div class="swot-sec">
                <h4><span class="minus">−</span>약점</h4>
                <ul><li v-for="(x, i) in comparison.comparison_result.b_weaknesses" :key="i">{{ x }}</li></ul>
              </div>
            </div>
          </div>

          <!-- Differences -->
          <div class="card diff-card">
            <h3 class="card-title">핵심 차이점</h3>
            <ol class="num-list">
              <li v-for="(x, i) in comparison.comparison_result.key_differences" :key="i">
                <span class="num">{{ String(i + 1).padStart(2, '0') }}</span>
                <span>{{ x }}</span>
              </li>
            </ol>
          </div>

          <!-- Rec -->
          <div class="card rec-card">
            <h3 class="card-title">추천사항</h3>
            <p class="rec-text">{{ comparison.comparison_result.recommendation }}</p>
          </div>

          <div class="result-nav">
            <button class="ghost-btn" @click="reset">새 비교 시작</button>
            <div class="detail-links">
              <a v-if="comparison.simulation_a_id" :href="`/adsim/simulation/${comparison.simulation_a_id}`" target="_blank">A 상세 →</a>
              <a v-if="comparison.simulation_b_id" :href="`/adsim/simulation/${comparison.simulation_b_id}`" target="_blank">B 상세 →</a>
            </div>
          </div>
        </div>
      </section>
    </main>
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
  if (!simId) return '대기 중…'
  const s = subSimStatus.value[simId]
  if (!s) return '시작 중…'
  if (s.status === 'completed') return '✓ 완료'
  if (s.status === 'failed') return '✗ 실패'
  return `진행 중 · ${s.current_round}/${s.total_rounds}`
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
    comparison.value = (await getComparison(activeComparisonId.value)).data.data
    const ids = [comparison.value.simulation_a_id, comparison.value.simulation_b_id].filter(Boolean)
    if (ids.length) {
      const results = await Promise.all(ids.map(id => getSimulation(id).then(x => x.data.data).catch(() => null)))
      const map = {}
      results.filter(Boolean).forEach(s => { map[s.simulation_id] = s })
      subSimStatus.value = map
    }
    if (['completed', 'failed'].includes(comparison.value.status)) stopPolling()
  } catch (e) { console.error(e) }
}

const startPolling = () => { loadComparison(); poll = setInterval(loadComparison, 3000) }
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
.page {
  min-height: 100vh;
  max-width: 1160px;
  margin: 0 auto;
  padding: 0 40px;
}
.topbar { display: flex; padding: 22px 0 18px; }
.bar-left { display: flex; align-items: center; gap: 12px; min-width: 0; }
.brand { font-family: var(--font-display); font-weight: 500; font-size: 20px; cursor: pointer; letter-spacing: -0.01em; font-variation-settings: 'opsz' 40; }
.bar-sep { color: var(--ink-faint); font-family: var(--font-display); }
.bar-link { font-family: var(--font-body); font-size: 14px; color: var(--ink-muted); cursor: pointer; }
.bar-link:hover { color: var(--accent); }
.bar-crumb { font-family: var(--font-display); font-style: italic; font-size: 17px; color: var(--ink-soft); font-variation-settings: 'opsz' 24, 'SOFT' 80; }
.rule-line { height: 1px; background: var(--ink); }

.wrap { max-width: 980px; margin: 0 auto; padding: 56px 0 100px; }

.eyebrow {
  font-family: var(--font-mono);
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.22em;
  color: var(--accent);
  display: block;
  margin-bottom: 14px;
}
.eyebrow.err { color: var(--negative); }

.page-head { margin-bottom: 56px; }
.page-head h1 {
  font-family: var(--font-display);
  font-weight: 400;
  font-size: 56px;
  letter-spacing: -0.025em;
  line-height: 1.06;
  margin: 0 0 18px;
  font-variation-settings: 'opsz' 144, 'SOFT' 30;
}
.italic { font-style: italic; color: var(--accent); font-variation-settings: 'opsz' 144, 'SOFT' 100; }
.lede { font-size: 17px; line-height: 1.6; color: var(--ink-soft); margin: 0; max-width: 600px; }

/* AB inputs */
.ab-grid {
  display: grid;
  grid-template-columns: 1fr 48px 1fr;
  gap: 0;
  align-items: stretch;
  margin-bottom: 56px;
}
.ab-card {
  background: var(--paper-card);
  border: 1px solid var(--rule);
  border-radius: var(--radius-lg);
  padding: 20px 22px;
  display: flex;
  flex-direction: column;
  transition: border-color 0.2s;
}
.ab-card.a { border-top: 3px solid var(--type-a); }
.ab-card.b { border-top: 3px solid var(--type-b); }
.ab-card:focus-within { border-color: var(--ink); }
.ab-head { display: flex; align-items: center; gap: 12px; margin-bottom: 14px; }
.ab-tag {
  width: 32px; height: 32px;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-display);
  font-weight: 600;
  font-size: 16px;
  color: #fff;
  background: var(--ink);
  font-variation-settings: 'opsz' 24;
}
.ab-card.a .ab-tag, .ab-tag.a { background: var(--type-a); }
.ab-card.b .ab-tag, .ab-tag.b { background: var(--type-b); }
.ab-tag.big { width: 48px; height: 48px; font-size: 22px; }
.ab-label { font-weight: 500; font-size: 15px; color: var(--ink); }
.ab-card textarea {
  width: 100%;
  flex: 1;
  background: transparent;
  border: none;
  color: var(--ink);
  padding: 0;
  font-family: var(--font-body);
  font-size: 14px;
  line-height: 1.65;
  resize: vertical;
  min-height: 200px;
  outline: none;
}
.ab-card textarea::placeholder {
  color: var(--ink-faint);
  font-family: var(--font-display);
  font-style: italic;
  font-variation-settings: 'opsz' 14;
}
.len { font-family: var(--font-mono); font-size: 11px; color: var(--ink-muted); text-align: right; margin-top: 10px; letter-spacing: 0.02em; }
.ab-divider { display: flex; align-items: center; justify-content: center; }
.vs {
  font-family: var(--font-display);
  font-style: italic;
  font-weight: 500;
  font-size: 22px;
  color: var(--accent);
  font-variation-settings: 'opsz' 24, 'SOFT' 100;
}

/* Section labels */
.section-label {
  display: flex;
  align-items: center;
  gap: 14px;
  margin: 0 0 20px;
  padding-top: 24px;
  border-top: 1px solid var(--rule);
}
.sl-n {
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--accent);
  letter-spacing: 0.1em;
}
.sl-text {
  font-family: var(--font-display);
  font-style: italic;
  font-weight: 500;
  font-size: 20px;
  letter-spacing: -0.01em;
  color: var(--ink);
  font-variation-settings: 'opsz' 24, 'SOFT' 80;
}

/* Persona */
.persona-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 10px; margin-bottom: 40px; }
.p-card {
  background: var(--paper-card);
  border: 1px solid var(--rule);
  border-radius: var(--radius-lg);
  padding: 18px 18px;
  cursor: pointer;
  text-align: left;
  font-family: var(--font-body);
  color: var(--ink);
  transition: all 0.2s;
}
.p-card:hover { border-color: var(--ink-muted); transform: translateY(-1px); }
.p-card.on { border-color: var(--ink); background: var(--ink); color: var(--paper-raised); box-shadow: 0 12px 28px -16px rgba(26,24,21,0.5); }
.p-n { font-family: var(--font-mono); font-size: 10px; color: var(--ink-faint); display: block; margin-bottom: 8px; letter-spacing: 0.1em; }
.p-card.on .p-n { color: var(--accent); }
.p-name { font-family: var(--font-display); font-weight: 500; font-size: 15px; margin: 0 0 4px; letter-spacing: -0.01em; font-variation-settings: 'opsz' 24; }
.p-age { font-family: var(--font-mono); font-size: 11px; color: var(--ink-muted); display: block; margin-bottom: 10px; }
.p-card.on .p-age { color: var(--paper-sunk); }
.p-tags { display: flex; flex-wrap: wrap; gap: 4px; }
.p-tags span { font-size: 10px; padding: 2px 7px; background: var(--paper-sunk); border-radius: 99px; color: var(--ink-soft); }
.p-card.on .p-tags span { background: rgba(245,241,232,0.15); color: var(--paper-raised); }

/* Settings */
.settings-row { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 40px; }
.setting {
  background: var(--paper-card);
  border: 1px solid var(--rule);
  border-radius: var(--radius-lg);
  padding: 20px 22px;
}
.setting label {
  font-family: var(--font-mono);
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.14em;
  color: var(--ink-muted);
  display: block;
  margin-bottom: 12px;
}
.setting input[type="text"] {
  width: 100%;
  background: transparent;
  border: none;
  color: var(--ink);
  font-family: var(--font-display);
  font-weight: 500;
  font-size: 22px;
  letter-spacing: -0.01em;
  outline: none;
  padding: 4px 0;
  border-bottom: 1px solid var(--rule);
  transition: border-color 0.2s;
  font-variation-settings: 'opsz' 40;
}
.setting input[type="text"]:focus { border-color: var(--ink); }
.setting input[type="text"]::placeholder { color: var(--ink-faint); font-style: italic; font-variation-settings: 'opsz' 24, 'SOFT' 80; }

.range-wrap { display: flex; align-items: center; gap: 14px; }
.range-wrap input[type="range"] { flex: 1; appearance: none; height: 3px; background: var(--rule); border-radius: 2px; outline: none; }
.range-wrap input[type="range"]::-webkit-slider-thumb { appearance: none; width: 18px; height: 18px; border-radius: 50%; background: var(--ink); cursor: pointer; border: 3px solid var(--paper-card); box-shadow: 0 0 0 1px var(--ink); }
.range-val {
  font-family: var(--font-display);
  font-weight: 500;
  font-size: 22px;
  color: var(--accent);
  min-width: 70px;
  text-align: right;
  font-variation-settings: 'opsz' 40;
}

/* Go button */
.go-btn {
  width: 100%;
  background: var(--ink);
  color: var(--paper-raised);
  border: none;
  padding: 24px 32px;
  border-radius: var(--radius-lg);
  cursor: pointer;
  font-family: var(--font-body);
  font-weight: 500;
  font-size: 17px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 14px;
  transition: background 0.25s;
}
.go-btn:hover:not(:disabled) { background: var(--accent); }
.go-btn:disabled { opacity: 0.35; cursor: not-allowed; }
.go-btn .arrow { font-family: var(--font-display); font-size: 22px; transition: transform 0.2s; }
.go-btn:hover:not(:disabled) .arrow { transform: translateX(6px); }
.cost-hint { text-align: center; font-size: 13px; color: var(--ink-muted); margin: 14px 0 0; }

/* Running state */
.state-center { text-align: center; padding: 80px 0; }
.state-center h1 { font-family: var(--font-display); font-weight: 400; font-size: 40px; margin: 0 0 12px; letter-spacing: -0.02em; font-variation-settings: 'opsz' 144; }
.state-center p { color: var(--ink-muted); margin: 0 0 24px; }
.dot-pulse { width: 10px; height: 10px; border-radius: 50%; background: var(--accent); display: inline-block; margin-bottom: 14px; animation: pulse 1.2s infinite; }
@keyframes pulse { 0%,100% { opacity: 0.4; } 50% { opacity: 1; } }

.running { text-align: center; padding: 60px 0; max-width: 640px; margin: 0 auto; }
.running h1 { font-family: var(--font-display); font-weight: 400; font-size: 44px; margin: 0 0 14px; letter-spacing: -0.02em; font-variation-settings: 'opsz' 144; }
.ab-status { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 40px; }
.as-col {
  background: var(--paper-card);
  border: 1px solid var(--rule);
  border-radius: var(--radius-lg);
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  text-align: left;
}
.as-label { font-family: var(--font-mono); font-size: 11px; color: var(--ink-muted); text-transform: uppercase; letter-spacing: 0.12em; margin-bottom: 4px; }
.as-val { font-family: var(--font-display); font-style: italic; font-size: 18px; font-variation-settings: 'opsz' 24, 'SOFT' 80; }

.next-btn { background: var(--ink); color: var(--paper-raised); border: none; padding: 14px 26px; border-radius: var(--radius); cursor: pointer; font-family: var(--font-body); font-weight: 500; font-size: 14px; transition: background 0.2s; }
.next-btn:hover { background: var(--accent); }

/* Result */
.result-head { margin-bottom: 32px; }

.winner {
  padding: 56px 48px;
  border-radius: var(--radius-lg);
  text-align: center;
  margin-bottom: 24px;
  border: 1px solid var(--rule);
  background: var(--paper-card);
}
.winner.w-A { border-top: 4px solid var(--type-a); }
.winner.w-B { border-top: 4px solid var(--type-b); }
.winner.w-tie { border-top: 4px solid var(--neutral); }
.w-label { font-family: var(--font-mono); font-size: 11px; color: var(--accent); text-transform: uppercase; letter-spacing: 0.22em; display: block; margin-bottom: 14px; }
.w-title {
  font-family: var(--font-display);
  font-weight: 400;
  font-size: 44px;
  letter-spacing: -0.025em;
  line-height: 1.1;
  margin: 0 0 20px;
  color: var(--ink);
  font-variation-settings: 'opsz' 144, 'SOFT' 30;
}
.w-letter { color: var(--accent); font-style: italic; font-weight: 600; font-variation-settings: 'opsz' 144, 'SOFT' 100; }
.w-reason { font-size: 16px; line-height: 1.65; color: var(--ink-soft); max-width: 560px; margin: 0 auto; }

/* Sentiment compare */
.sent-compare { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 24px; }
.sc-col { background: var(--paper-card); border: 1px solid var(--rule); border-radius: var(--radius-lg); padding: 24px; }
.sc-head { display: flex; align-items: center; gap: 10px; margin-bottom: 18px; font-weight: 500; font-size: 14px; }
.sbar { display: grid; grid-template-columns: 44px 1fr 40px; gap: 12px; align-items: center; font-size: 13px; margin-bottom: 10px; color: var(--ink-soft); }
.sbar .st { height: 6px; background: var(--paper-sunk); border-radius: 3px; overflow: hidden; }
.sbar .sf { height: 100%; transition: width 0.6s; }
.sbar .sf.pos { background: var(--positive); }
.sbar .sf.neu { background: var(--neutral); }
.sbar .sf.neg { background: var(--negative); }
.sbar .pct { font-family: var(--font-mono); font-size: 12px; font-weight: 600; text-align: right; color: var(--ink); }

/* SWOT */
.swot-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 24px; }
.swot-card {
  background: var(--paper-card);
  border: 1px solid var(--rule);
  border-radius: var(--radius-lg);
  padding: 26px;
}
.swot-card.a { border-top: 3px solid var(--type-a); }
.swot-card.b { border-top: 3px solid var(--type-b); }
.swot-head { display: flex; align-items: center; gap: 10px; margin-bottom: 22px; font-weight: 500; font-size: 14px; }
.swot-sec { margin-bottom: 20px; }
.swot-sec:last-child { margin-bottom: 0; }
.swot-sec h4 {
  font-family: var(--font-mono);
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.14em;
  color: var(--ink-muted);
  margin: 0 0 10px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.plus, .minus { font-family: var(--font-display); font-size: 18px; line-height: 1; }
.plus { color: var(--positive); }
.minus { color: var(--negative); }
.swot-sec ul { list-style: none; padding: 0; margin: 0; }
.swot-sec li {
  font-size: 14px;
  line-height: 1.6;
  color: var(--ink-soft);
  padding: 6px 0 6px 14px;
  position: relative;
}
.swot-sec li::before {
  content: '';
  width: 4px; height: 4px;
  background: var(--ink-faint);
  border-radius: 50%;
  position: absolute;
  left: 0; top: 14px;
}

/* Diff + Rec cards */
.card { background: var(--paper-card); border: 1px solid var(--rule); border-radius: var(--radius-lg); padding: 28px; margin-bottom: 14px; }
.card-title {
  font-family: var(--font-display);
  font-style: italic;
  font-weight: 400;
  font-size: 22px;
  letter-spacing: -0.01em;
  margin: 0 0 20px;
  color: var(--ink);
  font-variation-settings: 'opsz' 24, 'SOFT' 80;
}
.num-list { list-style: none; padding: 0; margin: 0; }
.num-list li { display: flex; gap: 14px; margin-bottom: 14px; font-size: 14px; line-height: 1.6; color: var(--ink-soft); }
.num-list .num { font-family: var(--font-mono); font-size: 11px; color: var(--accent); letter-spacing: 0.05em; flex-shrink: 0; margin-top: 4px; }
.rec-card { border-left: 3px solid var(--positive); }
.rec-text { margin: 0; font-size: 15px; line-height: 1.75; color: var(--ink-soft); }

/* Result nav */
.result-nav { display: flex; justify-content: space-between; align-items: center; margin-top: 32px; padding-top: 24px; border-top: 1px solid var(--rule); }
.ghost-btn { background: none; border: 1px solid var(--rule); color: var(--ink-soft); padding: 10px 20px; border-radius: var(--radius); cursor: pointer; font-family: var(--font-body); font-size: 14px; transition: all 0.2s; }
.ghost-btn:hover { border-color: var(--ink); color: var(--ink); }
.detail-links { display: flex; gap: 20px; }
.detail-links a { color: var(--accent); text-decoration: none; font-size: 14px; font-weight: 500; }
.detail-links a:hover { text-decoration: underline; text-underline-offset: 3px; }

.spin { width: 14px; height: 14px; border: 2px solid rgba(255,255,255,0.25); border-top-color: currentColor; border-radius: 50%; display: inline-block; animation: spin 0.7s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 820px) {
  .page { padding: 0 20px; }
  .wrap { padding: 36px 0 60px; }
  .ab-grid { grid-template-columns: 1fr; gap: 14px; }
  .ab-divider { padding: 12px 0; }
  .settings-row, .sent-compare, .swot-grid, .ab-status { grid-template-columns: 1fr; }
  .persona-grid { grid-template-columns: 1fr 1fr; }
  .page-head h1, .winner .w-title { font-size: 36px; }
  .winner { padding: 32px 24px; }
  .setting input[type="text"], .range-val { font-size: 18px; }
}
</style>

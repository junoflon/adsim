<template>
  <div class="adsim-result">
    <header class="topbar">
      <div class="topbar-left">
        <div class="logo" @click="$router.push('/adsim')">
          <span class="logo-mark">◆</span>
          <span class="logo-text">AdSim</span>
        </div>
        <span class="breadcrumb-sep">/</span>
        <span class="breadcrumb-current">시뮬레이션 결과</span>
      </div>
    </header>

    <div class="content">
      <!-- Loading / Running -->
      <div v-if="!sim" class="center-state">
        <div class="spinner-lg"></div>
        <p>데이터를 불러오는 중...</p>
      </div>

      <div v-else-if="sim.status === 'pending' || sim.status === 'running'" class="running-state">
        <div class="run-visual">
          <div class="orbit">
            <div class="orbit-dot" v-for="n in 3" :key="n" :style="{ animationDelay: n * 0.4 + 's' }"></div>
          </div>
        </div>
        <h1>시뮬레이션 진행 중</h1>
        <p class="run-desc">{{ sim.status === 'pending' ? '시작 대기 중...' : `${agentLabel} 가상 소비자가 반응하고 있습니다` }}</p>

        <div class="progress-wrap">
          <div class="progress-track">
            <div class="progress-fill" :style="{ width: progress + '%' }"></div>
          </div>
          <div class="progress-labels">
            <span>{{ sim.current_round }} / {{ sim.total_rounds }} 라운드</span>
            <span class="progress-pct">{{ progress }}%</span>
          </div>
        </div>
        <button class="btn-cancel" @click="handleCancel">시뮬레이션 취소</button>
      </div>

      <!-- Failed -->
      <div v-else-if="sim.status === 'failed'" class="center-state">
        <div class="fail-icon">✕</div>
        <h2>시뮬레이션 실패</h2>
        <p>실행 중 오류가 발생했습니다. 설정을 확인하고 다시 시도하세요.</p>
        <button class="btn-back-home" @click="$router.push('/adsim')">프로젝트 목록으로</button>
      </div>

      <!-- Completed -->
      <div v-else-if="sim.status === 'completed'" class="results">
        <div class="result-header">
          <h1>분석 결과</h1>
          <span class="result-meta">{{ formatDate(sim.completed_at) }} 완료</span>
        </div>

        <!-- Report -->
        <div v-if="report" class="report-grid">
          <!-- Sentiment Overview -->
          <div class="report-card sentiment-card">
            <h3 class="card-title">전체 반응</h3>
            <div class="sentiment-bars">
              <div class="sbar">
                <div class="sbar-label">긍정</div>
                <div class="sbar-track"><div class="sbar-fill positive" :style="{ width: report.overall_sentiment.positive + '%' }"></div></div>
                <div class="sbar-pct">{{ report.overall_sentiment.positive }}%</div>
              </div>
              <div class="sbar">
                <div class="sbar-label">중립</div>
                <div class="sbar-track"><div class="sbar-fill neutral" :style="{ width: report.overall_sentiment.neutral + '%' }"></div></div>
                <div class="sbar-pct">{{ report.overall_sentiment.neutral }}%</div>
              </div>
              <div class="sbar">
                <div class="sbar-label">부정</div>
                <div class="sbar-track"><div class="sbar-fill negative" :style="{ width: report.overall_sentiment.negative + '%' }"></div></div>
                <div class="sbar-pct">{{ report.overall_sentiment.negative }}%</div>
              </div>
            </div>
          </div>

          <!-- Insights -->
          <div class="report-card">
            <h3 class="card-title">핵심 인사이트</h3>
            <ul class="insight-list">
              <li v-for="(item, i) in report.key_insights" :key="i">
                <span class="insight-marker">{{ i + 1 }}</span>
                <span>{{ item }}</span>
              </li>
            </ul>
          </div>

          <!-- Concerns -->
          <div class="report-card warn-card">
            <h3 class="card-title">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 9v4M12 17h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/></svg>
              우려사항
            </h3>
            <ul class="insight-list">
              <li v-for="(item, i) in report.concerns" :key="i">{{ item }}</li>
            </ul>
          </div>

          <!-- Recommendations -->
          <div class="report-card success-card">
            <h3 class="card-title">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 11-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
              추천사항
            </h3>
            <ul class="insight-list">
              <li v-for="(item, i) in report.recommendations" :key="i">{{ item }}</li>
            </ul>
          </div>
        </div>

        <!-- Full Report Text -->
        <details v-if="report?.full_report_text" class="full-report">
          <summary>상세 보고서 전문 보기</summary>
          <div class="report-text">{{ report.full_report_text }}</div>
        </details>

        <!-- Agent Responses -->
        <section v-if="responses.length > 0" class="agents-section">
          <h2>에이전트 반응 <span class="agent-count">{{ responses.length }}명</span></h2>
          <div class="agent-table">
            <div class="agent-row header-row">
              <span class="col-name">에이전트</span>
              <span class="col-sent">감정</span>
              <span class="col-score">점수</span>
              <span class="col-react">핵심 반응</span>
            </div>
            <div v-for="r in responses" :key="r.response_id" class="agent-row data-row"
                 @click="$router.push(`/adsim/simulation/${simulationId}/agent/${r.response_id}`)"
                 tabindex="0" role="button">
              <span class="col-name">{{ r.agent_name }}</span>
              <span :class="['col-sent', 'badge-' + r.sentiment]">{{ sentLabel(r.sentiment) }}</span>
              <span class="col-score">
                <span class="score-bar" :style="{ width: ((r.sentiment_score + 1) / 2 * 100) + '%', background: scoreColor(r.sentiment_score) }"></span>
                {{ r.sentiment_score?.toFixed(1) }}
              </span>
              <span class="col-react">{{ r.key_reactions?.join(' · ') }}</span>
            </div>
          </div>
        </section>

        <div v-if="!report && responses.length === 0" class="center-state" style="padding:40px 0">
          <p>LLM 연동 후 시뮬레이션을 실행하면 여기에 결과가 표시됩니다.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getSimulation, getReport, listResponses, cancelSimulation } from '../api/adsim.js'

const route = useRoute()
const router = useRouter()
const simulationId = route.params.simulationId

const sim = ref(null)
const report = ref(null)
const responses = ref([])
let poll = null

const progress = computed(() => {
  if (!sim.value || !sim.value.total_rounds) return 0
  return Math.round(sim.value.current_round / sim.value.total_rounds * 100)
})
const agentLabel = computed(() => sim.value?.total_rounds ? '' : '')

const load = async () => {
  try {
    const r = await getSimulation(simulationId)
    sim.value = r.data.data
    if (sim.value.status === 'completed') {
      if (poll) { clearInterval(poll); poll = null }
      try {
        const [rpt, resp] = await Promise.all([getReport(simulationId), listResponses(simulationId)])
        report.value = rpt.data.data
        responses.value = resp.data.data.responses || []
      } catch (_) {}
    } else if (sim.value.status === 'failed') {
      if (poll) { clearInterval(poll); poll = null }
    }
  } catch (e) { console.error(e) }
}

const handleCancel = async () => {
  if (!confirm('시뮬레이션을 취소하시겠습니까?')) return
  await cancelSimulation(simulationId)
  await load()
}

const sentLabel = (s) => ({ positive: '긍정', negative: '부정', neutral: '중립' }[s] || s)
const scoreColor = (s) => s > 0.3 ? '#4ade80' : s < -0.3 ? '#ef4444' : '#94a3b8'
const formatDate = (d) => d ? new Intl.DateTimeFormat('ko-KR', { month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' }).format(new Date(d)) : ''

onMounted(() => { load(); poll = setInterval(load, 2500) })
onUnmounted(() => { if (poll) clearInterval(poll) })
</script>

<style scoped>
:root {
  --bg: #0c0f14; --bg-raised: #141821; --bg-card: #181d27; --bg-hover: #1e2433;
  --surface: #232a38; --border: #2a3244; --border-light: #1e2636;
  --text: #e8eaf0; --text-secondary: #8b93a6; --text-muted: #5a6378;
  --accent: #d4a053; --accent-dim: rgba(212,160,83,0.15);
  --positive: #4ade80; --negative: #ef4444; --neutral-c: #94a3b8;
  --radius: 8px;
  --font: 'IBM Plex Sans', 'Noto Sans KR', system-ui, sans-serif;
  --mono: 'IBM Plex Mono', 'JetBrains Mono', monospace;
}
* { box-sizing: border-box; }
.adsim-result { min-height: 100vh; background: var(--bg); color: var(--text); font-family: var(--font); -webkit-font-smoothing: antialiased; }
.topbar { height: 56px; display: flex; align-items: center; padding: 0 32px; border-bottom: 1px solid var(--border-light); background: rgba(12,15,20,0.85); backdrop-filter: blur(12px); position: sticky; top: 0; z-index: 50; }
.topbar-left { display: flex; align-items: center; gap: 10px; }
.logo { display: flex; align-items: center; gap: 8px; cursor: pointer; }
.logo-mark { color: var(--accent); }
.logo-text { font-family: var(--mono); font-weight: 600; font-size: 0.95rem; }
.breadcrumb-sep { color: var(--text-muted); }
.breadcrumb-current { font-size: 0.85rem; color: var(--text-secondary); }
.content { max-width: 960px; margin: 0 auto; padding: 40px 24px 80px; }

.center-state { text-align: center; padding: 80px 0; color: var(--text-secondary); }
.spinner-lg { width: 28px; height: 28px; border: 3px solid var(--border); border-top-color: var(--accent); border-radius: 50%; animation: spin 0.8s linear infinite; margin: 0 auto 16px; }
@keyframes spin { to { transform: rotate(360deg); } }

/* Running */
.running-state { text-align: center; padding: 60px 0; }
.running-state h1 { font-size: 1.6rem; margin: 0 0 8px; }
.run-desc { color: var(--text-secondary); margin-bottom: 36px; }
.orbit { width: 64px; height: 64px; position: relative; margin: 0 auto 24px; }
.orbit-dot { width: 10px; height: 10px; background: var(--accent); border-radius: 50%; position: absolute; top: 50%; left: 50%; animation: orbit-spin 1.8s linear infinite; }
@keyframes orbit-spin { to { transform: rotate(360deg) translateX(24px); } }
.progress-wrap { max-width: 400px; margin: 0 auto 24px; }
.progress-track { height: 6px; background: var(--surface); border-radius: 3px; overflow: hidden; }
.progress-fill { height: 100%; background: linear-gradient(90deg, var(--accent), #e0b060); border-radius: 3px; transition: width 0.5s; }
.progress-labels { display: flex; justify-content: space-between; margin-top: 8px; font-family: var(--mono); font-size: 0.78rem; color: var(--text-muted); }
.progress-pct { color: var(--accent); font-weight: 600; }
.btn-cancel { background: none; border: 1px solid var(--border); color: var(--text-muted); padding: 8px 20px; border-radius: 6px; cursor: pointer; font-size: 0.85rem; }
.btn-cancel:hover { border-color: var(--negative); color: var(--negative); }

.fail-icon { font-size: 2.5rem; color: var(--negative); margin-bottom: 16px; }
.btn-back-home { background: var(--surface); color: var(--text); border: 1px solid var(--border); padding: 10px 24px; border-radius: 6px; cursor: pointer; margin-top: 16px; }

/* Results */
.result-header { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 28px; }
.result-header h1 { font-size: 1.6rem; margin: 0; }
.result-meta { font-family: var(--mono); font-size: 0.78rem; color: var(--text-muted); }

.report-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 28px; }
.report-card { background: var(--bg-card); border: 1px solid var(--border-light); border-radius: var(--radius); padding: 22px; }
.sentiment-card { grid-column: span 2; }
.warn-card { border-left: 3px solid #f59e0b; }
.success-card { border-left: 3px solid var(--positive); }
.card-title { font-size: 0.88rem; font-weight: 600; margin: 0 0 16px; display: flex; align-items: center; gap: 8px; }
.card-title svg { color: var(--text-muted); }

.sentiment-bars { display: flex; flex-direction: column; gap: 10px; }
.sbar { display: grid; grid-template-columns: 48px 1fr 48px; gap: 10px; align-items: center; }
.sbar-label { font-size: 0.8rem; color: var(--text-secondary); }
.sbar-track { height: 8px; background: var(--surface); border-radius: 4px; overflow: hidden; }
.sbar-fill { height: 100%; border-radius: 4px; transition: width 0.6s ease; }
.sbar-fill.positive { background: var(--positive); }
.sbar-fill.neutral { background: var(--neutral-c); }
.sbar-fill.negative { background: var(--negative); }
.sbar-pct { font-family: var(--mono); font-size: 0.8rem; text-align: right; font-weight: 600; }

.insight-list { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 10px; }
.insight-list li { font-size: 0.88rem; line-height: 1.55; color: var(--text-secondary); display: flex; align-items: flex-start; gap: 8px; }
.insight-marker { font-family: var(--mono); font-size: 0.7rem; color: var(--accent); background: var(--accent-dim); width: 20px; height: 20px; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0; margin-top: 2px; }

.full-report { margin-bottom: 32px; }
.full-report summary { cursor: pointer; font-size: 0.88rem; color: var(--accent); padding: 12px 0; }
.report-text { background: var(--bg-card); border: 1px solid var(--border-light); border-radius: var(--radius); padding: 24px; font-size: 0.88rem; line-height: 1.8; color: var(--text-secondary); white-space: pre-wrap; max-height: 500px; overflow-y: auto; }

/* Agents */
.agents-section { margin-top: 36px; }
.agents-section h2 { font-size: 1.2rem; margin: 0 0 16px; display: flex; align-items: center; gap: 10px; }
.agent-count { font-family: var(--mono); font-size: 0.75rem; color: var(--text-muted); background: var(--surface); padding: 2px 10px; border-radius: 99px; }
.agent-table { border: 1px solid var(--border-light); border-radius: var(--radius); overflow: hidden; }
.agent-row { display: grid; grid-template-columns: 180px 64px 100px 1fr; padding: 10px 18px; align-items: center; font-size: 0.84rem; }
.header-row { background: var(--bg-card); font-weight: 600; font-size: 0.78rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.3px; font-family: var(--mono); }
.data-row { border-top: 1px solid var(--border-light); cursor: pointer; transition: background 0.15s; }
.data-row:hover { background: var(--bg-hover); }
.badge-positive { color: var(--positive); }
.badge-negative { color: var(--negative); }
.badge-neutral { color: var(--neutral-c); }
.col-score { display: flex; align-items: center; gap: 8px; font-family: var(--mono); font-size: 0.8rem; }
.score-bar { height: 4px; border-radius: 2px; min-width: 4px; }
.col-react { color: var(--text-muted); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

@media (max-width: 768px) {
  .report-grid { grid-template-columns: 1fr; }
  .sentiment-card { grid-column: span 1; }
  .agent-row { grid-template-columns: 1fr 60px 60px; }
  .col-react { display: none; }
}
</style>

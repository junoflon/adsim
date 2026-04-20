<template>
  <div class="page">
    <header class="topbar">
      <div class="bar-left">
        <span class="brand" @click="$router.push('/adsim')">AdSim</span>
        <span class="bar-sep">/</span>
        <span class="bar-crumb">시뮬레이션 결과</span>
      </div>
    </header>
    <div class="rule-line"></div>

    <main class="wrap">
      <div v-if="notFound" class="state-center">
        <span class="panel-eyebrow err">Not Found</span>
        <h1>시뮬레이션을 찾을 수 없어요</h1>
        <p>배포나 재시작으로 이 세션이 소실되었을 수 있습니다.<br/>프로젝트 목록에서 새로 시작해주세요.</p>
        <button class="next-btn" @click="$router.push('/adsim')">프로젝트 목록으로</button>
      </div>

      <div v-else-if="!sim" class="state-center">
        <span class="dot-pulse"></span>
        <p>불러오는 중…</p>
      </div>

      <!-- Running -->
      <div v-else-if="sim.status === 'pending' || sim.status === 'running'" class="running">
        <span class="panel-eyebrow">Simulating</span>
        <h1>에이전트들이 반응하고 있어요.</h1>
        <p class="running-lede">
          가상 소비자들이 라운드별로 광고를 곱씹고 감정을 정리합니다.
        </p>

        <div class="progress-wrap">
          <div class="progress-track">
            <div class="progress-fill" :style="{ width: progress + '%' }"></div>
          </div>
          <div class="progress-meta">
            <span>{{ sim.current_round }} / {{ sim.total_rounds }} 라운드</span>
            <span class="progress-pct">{{ progress }}%</span>
          </div>
        </div>

        <button class="cancel-btn" @click="handleCancel">시뮬레이션 취소</button>
      </div>

      <!-- Failed -->
      <div v-else-if="sim.status === 'failed'" class="state-center">
        <span class="panel-eyebrow err">Failed</span>
        <h1>실행 중 문제가 발생했어요.</h1>
        <p>설정을 확인하고 다시 시도해주세요.</p>
        <button class="next-btn" @click="$router.push('/adsim')">프로젝트 목록으로</button>
      </div>

      <!-- Completed -->
      <div v-else-if="sim.status === 'completed'" class="result">
        <header class="result-head">
          <span class="panel-eyebrow">Report</span>
          <h1>분석 결과</h1>
          <time>{{ formatDate(sim.completed_at) }} 완료</time>
        </header>

        <!-- Script diagnosis -->
        <section class="card script-card" v-if="report?.script_analysis">
          <div class="script-head">
            <span class="script-eyebrow">Script Diagnosis</span>
            <h2>대본 진단</h2>
            <p class="script-sub">에이전트 반응과 별개로, 대본 자체의 구성을 분석합니다.</p>
          </div>

          <div class="script-top">
            <div class="script-field">
              <span class="sf-label">핵심 메시지</span>
              <p>{{ report.script_analysis.core_message }}</p>
            </div>
            <div class="script-field">
              <span class="sf-label">훅 강도</span>
              <p>{{ report.script_analysis.hook_strength }}</p>
            </div>
            <div class="script-field" v-if="report.script_analysis.tone">
              <span class="sf-label">톤 키워드</span>
              <div class="tone-chips">
                <span v-for="(t, i) in toneArr" :key="i">{{ t }}</span>
              </div>
            </div>
          </div>

          <div class="script-sw">
            <div>
              <h4>강점</h4>
              <ul><li v-for="(x, i) in report.script_analysis.strengths" :key="i">{{ x }}</li></ul>
            </div>
            <div>
              <h4>약점</h4>
              <ul><li v-for="(x, i) in report.script_analysis.weaknesses" :key="i">{{ x }}</li></ul>
            </div>
          </div>

          <div class="script-field" v-if="report.script_analysis.platform_fit">
            <span class="sf-label">매체 적합성</span>
            <p>{{ report.script_analysis.platform_fit }}</p>
          </div>

          <div class="script-field" v-if="report.script_analysis.risks?.length">
            <span class="sf-label warn">⚠ 주의할 리스크</span>
            <ul class="risk-list">
              <li v-for="(r, i) in report.script_analysis.risks" :key="i">{{ r }}</li>
            </ul>
          </div>
        </section>

        <!-- Sentiment -->
        <section class="card sent-card" v-if="report">
          <h2 class="card-title">전체 반응</h2>
          <div class="sent-bars">
            <div class="sbar">
              <div class="sbar-label"><span class="sbar-dot pos"></span>긍정</div>
              <div class="sbar-track"><div class="sbar-fill pos" :style="{ width: report.overall_sentiment.positive + '%' }"></div></div>
              <div class="sbar-pct">{{ report.overall_sentiment.positive }}%</div>
            </div>
            <div class="sbar">
              <div class="sbar-label"><span class="sbar-dot neu"></span>중립</div>
              <div class="sbar-track"><div class="sbar-fill neu" :style="{ width: report.overall_sentiment.neutral + '%' }"></div></div>
              <div class="sbar-pct">{{ report.overall_sentiment.neutral }}%</div>
            </div>
            <div class="sbar">
              <div class="sbar-label"><span class="sbar-dot neg"></span>부정</div>
              <div class="sbar-track"><div class="sbar-fill neg" :style="{ width: report.overall_sentiment.negative + '%' }"></div></div>
              <div class="sbar-pct">{{ report.overall_sentiment.negative }}%</div>
            </div>
          </div>
        </section>

        <!-- Insights / Concerns / Recs -->
        <div class="grid-3" v-if="report">
          <section class="card">
            <h2 class="card-title">핵심 인사이트</h2>
            <ol class="num-list">
              <li v-for="(x, i) in report.key_insights" :key="i">
                <span class="num">{{ String(i + 1).padStart(2, '0') }}</span>
                <span>{{ x }}</span>
              </li>
            </ol>
          </section>
          <section class="card warn">
            <h2 class="card-title">우려사항</h2>
            <ul class="dot-list">
              <li v-for="(x, i) in report.concerns" :key="i">{{ x }}</li>
            </ul>
          </section>
          <section class="card rec">
            <h2 class="card-title">추천사항</h2>
            <ul class="dot-list">
              <li v-for="(x, i) in report.recommendations" :key="i">{{ x }}</li>
            </ul>
          </section>
        </div>

        <details v-if="report?.full_report_text" class="full-report">
          <summary>상세 보고서 전문</summary>
          <div class="report-body">{{ report.full_report_text }}</div>
        </details>

        <!-- Agent responses -->
        <section v-if="responses.length" class="agents-sec">
          <div class="sec-head">
            <h2>에이전트 반응</h2>
            <span>{{ responses.length }}명</span>
          </div>
          <ol class="agent-list">
            <li v-for="(r, i) in responses" :key="r.response_id"
                @click="$router.push(`/adsim/simulation/${simulationId}/agent/${r.response_id}`)"
                tabindex="0" role="button">
              <span class="ag-n">{{ String(i + 1).padStart(2, '0') }}</span>
              <span class="ag-name">{{ r.agent_name }}</span>
              <span :class="['ag-sent', r.sentiment]">{{ sentLabel(r.sentiment) }}</span>
              <span class="ag-score">
                <span class="score-bar" :style="{ width: ((r.sentiment_score + 1) / 2 * 100) + '%', background: scoreColor(r.sentiment_score) }"></span>
                {{ r.sentiment_score?.toFixed(2) }}
              </span>
              <span class="ag-react">{{ r.key_reactions?.join(' · ') }}</span>
              <span class="ag-arrow">→</span>
            </li>
          </ol>
        </section>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { getSimulation, getReport, listResponses, cancelSimulation } from '../api/adsim.js'

const route = useRoute()
const simulationId = route.params.simulationId

const sim = ref(null)
const report = ref(null)
const responses = ref([])
let poll = null

const progress = computed(() => {
  if (!sim.value || !sim.value.total_rounds) return 0
  return Math.round(sim.value.current_round / sim.value.total_rounds * 100)
})

const notFound = ref(false)
const load = async () => {
  try {
    sim.value = (await getSimulation(simulationId)).data.data
    notFound.value = false
    if (sim.value.status === 'completed') {
      if (poll) { clearInterval(poll); poll = null }
      // 독립 fetch: 한쪽이 실패해도 다른 쪽은 살아남도록
      getReport(simulationId).then(r => { report.value = r.data.data }).catch(e => console.error('report load fail', e))
      listResponses(simulationId).then(r => { responses.value = r.data.data.responses || [] }).catch(e => console.error('responses load fail', e))
    } else if (sim.value.status === 'failed' && poll) { clearInterval(poll); poll = null }
  } catch (e) {
    if (e.response?.status === 404) {
      notFound.value = true
      if (poll) { clearInterval(poll); poll = null }
    } else {
      console.error(e)
    }
  }
}

const handleCancel = async () => {
  if (!confirm('시뮬레이션을 취소하시겠습니까?')) return
  await cancelSimulation(simulationId)
  await load()
}

const sentLabel = (s) => ({ positive: '긍정', negative: '부정', neutral: '중립' }[s] || s)
const toneArr = computed(() => {
  const t = report.value?.script_analysis?.tone
  if (!t) return []
  if (Array.isArray(t)) return t
  return String(t).split(/[,·、]/).map(x => x.trim()).filter(Boolean)
})
const scoreColor = (s) => s > 0.3 ? 'var(--positive)' : s < -0.3 ? 'var(--negative)' : 'var(--neutral)'
const formatDate = (d) => d ? new Intl.DateTimeFormat('ko-KR', { month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' }).format(new Date(d)) : ''

onMounted(() => { load(); poll = setInterval(load, 2500) })
onUnmounted(() => { if (poll) clearInterval(poll) })
</script>

<style scoped>
.page {
  min-height: 100vh;
  max-width: 1160px;
  margin: 0 auto;
  padding: 0 40px;
}
.topbar { display: flex; padding: 22px 0 18px; }
.bar-left { display: flex; align-items: center; gap: 14px; }
.brand {
  font-family: var(--font-display);
  font-weight: 500;
  font-size: 20px;
  cursor: pointer;
  letter-spacing: -0.01em;
  font-variation-settings: 'opsz' 40;
}
.bar-sep { color: var(--ink-faint); font-family: var(--font-display); font-size: 18px; }
.bar-crumb { font-family: var(--font-display); font-style: italic; font-size: 17px; color: var(--ink-soft); font-variation-settings: 'opsz' 24, 'SOFT' 80; }
.rule-line { height: 1px; background: var(--ink); }

.wrap {
  max-width: 920px;
  margin: 0 auto;
  padding: 56px 0 100px;
}

.panel-eyebrow {
  font-family: var(--font-mono);
  font-size: 11px;
  letter-spacing: 0.2em;
  color: var(--accent);
  text-transform: uppercase;
  display: block;
  margin-bottom: 14px;
}
.panel-eyebrow.err { color: var(--negative); }

/* States */
.state-center { text-align: center; padding: 80px 0; }
.state-center h1 { font-family: var(--font-display); font-weight: 400; font-size: 36px; margin: 0 0 12px; letter-spacing: -0.02em; font-variation-settings: 'opsz' 144; }
.state-center p { color: var(--ink-muted); margin: 0 0 24px; }
.dot-pulse { width: 10px; height: 10px; border-radius: 50%; background: var(--accent); display: inline-block; margin-bottom: 12px; animation: pulse 1.2s infinite; }
@keyframes pulse { 0%, 100% { opacity: 0.4; } 50% { opacity: 1; } }

/* Running */
.running { padding: 60px 0; max-width: 640px; margin: 0 auto; text-align: center; }
.running h1 {
  font-family: var(--font-display);
  font-weight: 400;
  font-size: 48px;
  letter-spacing: -0.025em;
  line-height: 1.08;
  margin: 0 0 16px;
  font-variation-settings: 'opsz' 144, 'SOFT' 30;
}
.running-lede { font-size: 16px; color: var(--ink-soft); line-height: 1.6; margin: 0 0 48px; }
.progress-wrap { max-width: 440px; margin: 0 auto 30px; }
.progress-track { height: 4px; background: var(--rule); border-radius: 2px; overflow: hidden; }
.progress-fill { height: 100%; background: var(--accent); border-radius: 2px; transition: width 0.5s; }
.progress-meta { display: flex; justify-content: space-between; margin-top: 12px; font-family: var(--font-mono); font-size: 12px; color: var(--ink-muted); letter-spacing: 0.04em; }
.progress-pct { color: var(--accent); font-weight: 600; }
.cancel-btn { background: none; border: 1px solid var(--rule); color: var(--ink-muted); padding: 10px 20px; border-radius: 99px; cursor: pointer; font-size: 13px; font-family: var(--font-body); transition: all 0.2s; }
.cancel-btn:hover { border-color: var(--negative); color: var(--negative); }

.next-btn { background: var(--ink); color: var(--paper-raised); border: none; padding: 14px 26px; border-radius: var(--radius); cursor: pointer; font-family: var(--font-body); font-weight: 500; font-size: 14px; transition: background 0.2s; }
.next-btn:hover { background: var(--accent); }

/* Result */
.result-head { margin-bottom: 40px; }
.result-head h1 {
  font-family: var(--font-display);
  font-weight: 400;
  font-size: 56px;
  margin: 0 0 10px;
  letter-spacing: -0.025em;
  line-height: 1;
  font-variation-settings: 'opsz' 144, 'SOFT' 30;
}
.result-head time { font-family: var(--font-mono); font-size: 12px; color: var(--ink-muted); letter-spacing: 0.05em; }

.card {
  background: var(--paper-card);
  border: 1px solid var(--rule);
  border-radius: var(--radius-lg);
  padding: 28px;
}
.card-title {
  font-family: var(--font-display);
  font-style: italic;
  font-weight: 400;
  font-size: 20px;
  margin: 0 0 22px;
  letter-spacing: -0.01em;
  color: var(--ink);
  font-variation-settings: 'opsz' 24, 'SOFT' 80;
}

/* Script diagnosis card */
.script-card { border-left: 3px solid var(--ink); margin-bottom: 14px; padding: 32px; }
.script-head { margin-bottom: 24px; }
.script-eyebrow {
  font-family: var(--font-mono);
  font-size: 10px;
  letter-spacing: 0.22em;
  color: var(--ink-muted);
  text-transform: uppercase;
  display: block;
  margin-bottom: 8px;
}
.script-head h2 {
  font-family: var(--font-display);
  font-weight: 600;
  font-size: 26px;
  margin: 0 0 6px;
  letter-spacing: -0.02em;
}
.script-sub { font-size: 13px; color: var(--ink-muted); margin: 0; line-height: 1.5; }

.script-top { display: grid; grid-template-columns: 1fr; gap: 18px; margin-bottom: 24px; padding-bottom: 24px; border-bottom: 1px solid var(--rule); }
.script-field { }
.sf-label {
  font-family: var(--font-mono);
  font-size: 10px;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--ink-muted);
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
}
.sf-label.warn { color: var(--ink); font-weight: 700; }
.script-field p { font-size: 15px; line-height: 1.7; color: var(--ink); margin: 0; }

.tone-chips { display: flex; flex-wrap: wrap; gap: 6px; }
.tone-chips span { font-size: 12px; padding: 4px 10px; background: var(--ink); color: var(--paper); border-radius: 99px; font-weight: 500; }

.script-sw { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-bottom: 24px; }
.script-sw h4 {
  font-family: var(--font-mono);
  font-size: 11px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--ink-muted);
  margin: 0 0 10px;
  font-weight: 600;
}
.script-sw ul { list-style: none; padding: 0; margin: 0; }
.script-sw li { font-size: 14px; line-height: 1.65; color: var(--ink); padding: 4px 0 4px 14px; position: relative; }
.script-sw li::before { content: ''; width: 5px; height: 5px; background: var(--ink); border-radius: 50%; position: absolute; left: 0; top: 12px; }
.script-sw > div:last-child li::before { background: var(--paper); border: 1.5px solid var(--ink); }

.risk-list { list-style: none; padding: 0; margin: 0; }
.risk-list li {
  font-size: 14px;
  line-height: 1.65;
  color: var(--ink);
  padding: 10px 14px;
  background: var(--paper-sunk);
  border: 1px solid var(--rule);
  border-radius: var(--radius);
  margin-bottom: 8px;
}

.sent-card { margin-bottom: 14px; }
.sent-bars { display: flex; flex-direction: column; gap: 14px; }
.sbar { display: grid; grid-template-columns: 80px 1fr 48px; gap: 14px; align-items: center; }
.sbar-label { font-size: 14px; color: var(--ink-soft); display: flex; align-items: center; gap: 8px; }
.sbar-dot { width: 8px; height: 8px; border-radius: 50%; }
.sbar-dot.pos { background: var(--positive); }
.sbar-dot.neu { background: var(--neutral); }
.sbar-dot.neg { background: var(--negative); }
.sbar-track { height: 8px; background: var(--paper-sunk); border-radius: 4px; overflow: hidden; }
.sbar-fill { height: 100%; border-radius: 4px; transition: width 0.8s ease; }
.sbar-fill.pos { background: var(--positive); }
.sbar-fill.neu { background: var(--neutral); }
.sbar-fill.neg { background: var(--negative); }
.sbar-pct { font-family: var(--font-mono); font-size: 13px; font-weight: 600; text-align: right; color: var(--ink); }

.grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; margin-bottom: 32px; margin-top: 14px; }
.card.warn { border-top: 3px solid var(--negative); }
.card.rec { border-top: 3px solid var(--positive); }

.num-list, .dot-list { list-style: none; padding: 0; margin: 0; }
.num-list li { display: flex; gap: 14px; margin-bottom: 14px; line-height: 1.55; font-size: 14px; color: var(--ink-soft); }
.num-list .num {
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--accent);
  letter-spacing: 0.05em;
  flex-shrink: 0;
  margin-top: 3px;
}
.dot-list li {
  font-size: 14px;
  line-height: 1.55;
  color: var(--ink-soft);
  padding-left: 18px;
  position: relative;
  margin-bottom: 12px;
}
.dot-list li::before {
  content: '';
  width: 5px; height: 5px;
  background: var(--accent);
  border-radius: 50%;
  position: absolute;
  left: 0; top: 8px;
}

.full-report { margin-bottom: 40px; background: var(--paper-card); border: 1px solid var(--rule); border-radius: var(--radius-lg); padding: 8px 24px; }
.full-report summary { cursor: pointer; padding: 14px 0; font-family: var(--font-display); font-style: italic; font-size: 16px; color: var(--accent); font-variation-settings: 'opsz' 24; list-style: none; }
.full-report summary::before { content: '▸ '; }
.full-report[open] summary::before { content: '▾ '; }
.report-body {
  white-space: pre-wrap;
  line-height: 1.8;
  font-size: 14px;
  color: var(--ink-soft);
  padding: 8px 0 20px;
  max-height: 500px;
  overflow-y: auto;
}

.agents-sec { margin-top: 48px; }
.sec-head { display: flex; align-items: baseline; justify-content: space-between; margin-bottom: 20px; }
.sec-head h2 {
  font-family: var(--font-display);
  font-weight: 500;
  font-size: 28px;
  margin: 0;
  letter-spacing: -0.015em;
  font-variation-settings: 'opsz' 40;
}
.sec-head span { font-family: var(--font-mono); font-size: 12px; color: var(--ink-muted); }

.agent-list { list-style: none; padding: 0; margin: 0; border-top: 1px solid var(--rule); }
.agent-list li {
  display: grid;
  grid-template-columns: 36px 120px 56px 120px 1fr 20px;
  gap: 14px;
  align-items: center;
  padding: 14px 0;
  border-bottom: 1px solid var(--rule);
  cursor: pointer;
  font-size: 13px;
  transition: background 0.15s, padding 0.2s;
  outline: none;
}
.agent-list li:hover, .agent-list li:focus-visible {
  background: var(--paper-raised);
  padding-left: 14px;
  padding-right: 14px;
  margin: 0 -14px;
}
.ag-n { font-family: var(--font-mono); color: var(--ink-faint); font-size: 11px; letter-spacing: 0.05em; }
.ag-name { font-weight: 500; color: var(--ink); }
.ag-sent {
  font-size: 11px;
  font-family: var(--font-mono);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  padding: 3px 8px;
  border-radius: 99px;
  text-align: center;
}
.ag-sent.positive { background: var(--positive-bg); color: var(--positive); }
.ag-sent.negative { background: var(--negative-bg); color: var(--negative); }
.ag-sent.neutral  { background: var(--neutral-bg);  color: var(--neutral); }
.ag-score { display: flex; align-items: center; gap: 8px; font-family: var(--font-mono); font-size: 12px; color: var(--ink-soft); }
.score-bar { height: 4px; border-radius: 2px; min-width: 4px; max-width: 80px; }
.ag-react { color: var(--ink-muted); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-size: 12px; }
.ag-arrow { color: var(--ink-faint); font-family: var(--font-display); }
.agent-list li:hover .ag-arrow { color: var(--accent); }

@media (max-width: 820px) {
  .page { padding: 0 20px; }
  .wrap { padding: 36px 0 60px; }
  .grid-3 { grid-template-columns: 1fr; }
  .agent-list li { grid-template-columns: 30px 1fr 56px 20px; font-size: 13px; }
  .ag-score, .ag-react { display: none; }
  .result-head h1 { font-size: 36px; }
}
</style>

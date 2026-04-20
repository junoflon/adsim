<template>
  <div class="page">
    <header class="topbar">
      <div class="bar-left">
        <span class="brand" @click="$router.push('/adsim')">AdSim</span>
        <span class="bar-sep">/</span>
        <span class="bar-crumb">{{ project?.name || '...' }}</span>
      </div>
      <div class="bar-right">
        <button class="compare-link" @click="$router.push(`/adsim/project/${projectId}/compare`)" v-if="project">
          A/B 비교 <span class="arrow">→</span>
        </button>
      </div>
    </header>

    <div class="rule-line"></div>

    <main v-if="project" class="wrap">
      <!-- Progress meter -->
      <nav class="progress-nav">
        <div v-for="(s, i) in steps" :key="i" class="step-item"
             :class="{ on: currentStep === i, done: currentStep > i }"
             @click="currentStep = i">
          <span class="step-n">{{ String(i + 1).padStart(2, '0') }}</span>
          <span class="step-label">{{ s.label }}</span>
          <span class="step-rule" v-if="i < steps.length - 1"></span>
        </div>
      </nav>

      <!-- Step 1 — Seed -->
      <section v-show="currentStep === 0" class="panel">
        <div class="panel-head">
          <span class="panel-eyebrow">Step 01</span>
          <h1>무엇을 테스트할까요?</h1>
          <p class="panel-lede">{{ ledeText }}</p>
        </div>

        <div class="editor">
          <textarea v-model="seedContent"
                    :placeholder="placeholderText"
                    rows="10"
                    maxlength="5000"></textarea>
          <div class="editor-foot">
            <span class="char-n" :class="{ warn: seedContent.length > 4500 }">
              {{ seedContent.length.toLocaleString() }} / 5,000
            </span>
            <button class="add-btn" :disabled="!seedContent.trim() || uploading" @click="handleUploadSeed">
              <span v-if="uploading" class="spin"></span>
              <span v-else>{{ seeds.length > 0 ? '+ 추가 업로드' : '업로드하기' }}</span>
            </button>
          </div>
        </div>

        <TransitionGroup name="list" tag="ul" class="seed-list" v-if="seeds.length">
          <li v-for="(s, i) in seeds" :key="s.seed_id">
            <span class="seed-n">{{ String(i + 1).padStart(2, '0') }}</span>
            <p>{{ s.content?.slice(0, 80) }}{{ s.content?.length > 80 ? '…' : '' }}</p>
            <button class="seed-del" @click="handleDeleteSeed(s.seed_id)" aria-label="삭제">✕</button>
          </li>
        </TransitionGroup>

        <div class="panel-nav">
          <span></span>
          <button class="next-btn" :disabled="seeds.length === 0" @click="currentStep = 1">
            페르소나 설정하기 →
          </button>
        </div>
      </section>

      <!-- Step 2 — Persona -->
      <section v-show="currentStep === 1" class="panel">
        <div class="panel-head">
          <span class="panel-eyebrow">Step 02</span>
          <h1>누구에게 보여줄까요?</h1>
          <p class="panel-lede">AI 에이전트가 이 집단의 특성으로 광고를 평가합니다.</p>
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
            <p class="p-habit">{{ p.consumption_habits }}</p>
            <span class="p-check" v-if="selectedPreset === i">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg>
            </span>
          </button>
        </div>

        <div class="slider-card">
          <div class="slider-head">
            <div>
              <label>에이전트 수</label>
              <p class="slider-sub">많을수록 정확도 ↑, 비용 ↑</p>
            </div>
            <span class="slider-val">{{ agentCount }}<span class="slider-unit">명</span></span>
          </div>
          <input type="range" v-model.number="agentCount" min="10" max="100" step="5" />
          <div class="slider-marks">
            <span>10</span><span>30</span><span>50</span><span>70</span><span>100</span>
          </div>
          <p class="slider-hint">
            <span v-if="agentCount <= 20">빠른 테스트 · 예산 절약</span>
            <span v-else-if="agentCount <= 50">균형 잡힌 선택 · 권장</span>
            <span v-else>정밀 분석 · 비용 증가</span>
          </p>
        </div>

        <div class="panel-nav">
          <button class="back-btn" @click="currentStep = 0">← 이전</button>
          <button class="next-btn" :disabled="selectedPreset === null" @click="currentStep = 2">
            실행 설정 →
          </button>
        </div>
      </section>

      <!-- Step 3 — Run -->
      <section v-show="currentStep === 2" class="panel">
        <div class="panel-head">
          <span class="panel-eyebrow">Step 03</span>
          <h1>준비되었어요.</h1>
          <p class="panel-lede">설정을 확인하고 시뮬레이션을 시작하세요.</p>
        </div>

        <dl class="summary">
          <div>
            <dt>시드 자료</dt>
            <dd>{{ seeds.length }}개 업로드됨</dd>
          </div>
          <div>
            <dt>타겟 페르소나</dt>
            <dd>{{ selectedPreset !== null ? presets[selectedPreset]?.name : '미선택' }}</dd>
          </div>
          <div>
            <dt>에이전트</dt>
            <dd>{{ agentCount }}명</dd>
          </div>
          <div>
            <dt>라운드</dt>
            <dd class="round-control">
              <button @click="totalRounds = Math.max(5, totalRounds - 5)" aria-label="줄이기">−</button>
              <span>{{ totalRounds }}</span>
              <button @click="totalRounds = Math.min(50, totalRounds + 5)" aria-label="늘리기">+</button>
            </dd>
          </div>
        </dl>

        <button class="go-btn" :disabled="!canRun || running" @click="handleRun">
          <span v-if="running" class="spin"></span>
          <template v-else>
            <span class="go-label">시뮬레이션 시작</span>
            <span class="go-arrow">→</span>
          </template>
        </button>

        <p class="run-hint">몇 분 정도 걸립니다. 완료되면 자동으로 결과 화면으로 이동해요.</p>

        <div class="panel-nav">
          <button class="back-btn" @click="currentStep = 1">← 이전</button>
          <span></span>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getProject, listSeeds, createSeed, deleteSeed, getPresetPersonas, createPersona, startSimulation } from '../api/adsim.js'

const route = useRoute()
const router = useRouter()
const projectId = route.params.projectId

const project = ref(null)
const seeds = ref([])
const presets = ref([])
const seedContent = ref('')
const selectedPreset = ref(null)
const agentCount = ref(30)
const totalRounds = ref(30)
const currentStep = ref(0)
const uploading = ref(false)
const running = ref(false)
const steps = [
  { label: '시드 자료' },
  { label: '페르소나' },
  { label: '실행' },
]

const canRun = computed(() => seeds.value.length > 0 && selectedPreset.value !== null)

const ledeText = computed(() => {
  const t = project.value?.type
  if (t === 'product_hypothesis') return '제품 컨셉을 입력하세요. 타겟에게 실제로 필요한 제품인지 검증합니다.'
  if (t === 'usp_test') return 'USP(제품 차별점)를 입력하세요. 여러 개를 비교하려면 따로 업로드하세요.'
  return '광고 대본을 붙여넣으세요. 텍스트가 구체적일수록 현실적인 반응이 나옵니다.'
})
const placeholderText = computed(() => {
  const t = project.value?.type
  if (t === 'product_hypothesis') return '예: 3분 만에 집에서 만드는 저당 디저트 밀키트. 냉동 보관 7일, 칼로리 150kcal 이하, 1팩 4,900원…'
  if (t === 'usp_test') return '예: 제로칼로리인데도 진짜 과일 맛이 나는 유일한 음료'
  return '예: [나레이션] 지금까지 이런 맛은 없었다. 제로칼로리인데 진짜 맛있는 …'
})
const seedTypeFor = (t) => {
  if (t === 'product_hypothesis') return 'product_concept'
  if (t === 'usp_test') return 'usp_text'
  return 'ad_script'
}

onMounted(async () => {
  try {
    const [pRes, sRes, prRes] = await Promise.all([
      getProject(projectId), listSeeds(projectId), getPresetPersonas()
    ])
    project.value = pRes.data.data
    seeds.value = sRes.data.data
    presets.value = prRes.data.data
  } catch (e) { console.error(e) }
})

const handleUploadSeed = async () => {
  if (!seedContent.value.trim() || uploading.value) return
  uploading.value = true
  try {
    const seedType = seedTypeFor(project.value.type)
    await createSeed(projectId, { type: seedType, content: seedContent.value })
    seedContent.value = ''
    seeds.value = (await listSeeds(projectId)).data.data
  } catch (e) {
    alert('업로드 실패: ' + (e.response?.data?.error || e.message))
  } finally { uploading.value = false }
}

const handleDeleteSeed = async (id) => {
  await deleteSeed(projectId, id)
  seeds.value = (await listSeeds(projectId)).data.data
}

const handleRun = async () => {
  if (!canRun.value || running.value) return
  running.value = true
  try {
    const preset = presets.value[selectedPreset.value]
    const personaRes = await createPersona(projectId, { ...preset, agent_count: agentCount.value, is_preset: true })
    const simRes = await startSimulation(projectId, {
      seed_id: seeds.value[0].seed_id,
      persona_id: personaRes.data.data.persona_id,
      total_rounds: totalRounds.value
    })
    router.push(`/adsim/simulation/${simRes.data.data.simulation_id}`)
  } catch (e) {
    alert('시작 실패: ' + (e.response?.data?.error || e.message))
  } finally { running.value = false }
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  max-width: 1160px;
  margin: 0 auto;
  padding: 0 40px;
}

/* ─ Topbar ─ */
.topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 22px 0 18px;
}
.bar-left { display: flex; align-items: center; gap: 14px; min-width: 0; }
.brand {
  font-family: var(--font-display);
  font-weight: 500;
  font-size: 20px;
  letter-spacing: -0.01em;
  cursor: pointer;
  font-variation-settings: 'opsz' 40;
}
.bar-sep { color: var(--ink-faint); font-size: 18px; font-family: var(--font-display); }
.bar-crumb {
  font-family: var(--font-display);
  font-style: italic;
  font-size: 17px;
  color: var(--ink-soft);
  font-variation-settings: 'opsz' 24, 'SOFT' 80;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.compare-link {
  background: none;
  border: 1px solid var(--rule);
  color: var(--ink);
  padding: 8px 16px;
  border-radius: 99px;
  cursor: pointer;
  font-family: var(--font-body);
  font-size: 13px;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
}
.compare-link:hover { border-color: var(--accent); color: var(--accent); }
.compare-link .arrow { font-family: var(--font-display); }
.rule-line { height: 1px; background: var(--ink); }

.wrap {
  max-width: 780px;
  margin: 0 auto;
  padding: 56px 0 100px;
}

/* ─ Progress nav ─ */
.progress-nav {
  display: flex;
  align-items: center;
  margin-bottom: 72px;
}
.step-item {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  transition: color 0.2s;
}
.step-n {
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--ink-faint);
  letter-spacing: 0.1em;
  transition: color 0.2s;
}
.step-label {
  font-size: 14px;
  color: var(--ink-muted);
  transition: color 0.2s;
}
.step-rule {
  width: 60px;
  height: 1px;
  background: var(--rule);
  margin: 0 20px;
}
.step-item.on .step-n { color: var(--accent); }
.step-item.on .step-label {
  color: var(--ink);
  font-weight: 500;
  font-family: var(--font-display);
  font-style: italic;
  font-size: 17px;
  font-variation-settings: 'opsz' 24;
}
.step-item.done .step-n { color: var(--ink); }
.step-item.done .step-label { color: var(--ink-soft); }

/* ─ Panel ─ */
.panel {
  animation: fade 0.35s;
}
@keyframes fade {
  from { opacity: 0; transform: translateY(6px); }
  to   { opacity: 1; transform: translateY(0); }
}
.panel-head { margin-bottom: 40px; }
.panel-eyebrow {
  font-family: var(--font-mono);
  font-size: 11px;
  letter-spacing: 0.2em;
  color: var(--accent);
  text-transform: uppercase;
  display: block;
  margin-bottom: 14px;
}
.panel h1 {
  font-family: var(--font-display);
  font-weight: 400;
  font-size: 48px;
  letter-spacing: -0.025em;
  line-height: 1.05;
  margin: 0 0 14px;
  color: var(--ink);
  font-variation-settings: 'opsz' 144, 'SOFT' 30;
}
.panel-lede {
  font-size: 16px;
  line-height: 1.6;
  color: var(--ink-soft);
  margin: 0;
  max-width: 560px;
}

/* ─ Editor ─ */
.editor {
  background: var(--paper-card);
  border: 1px solid var(--rule);
  border-radius: var(--radius-lg);
  overflow: hidden;
  transition: border-color 0.2s, box-shadow 0.2s;
  margin-bottom: 22px;
}
.editor:focus-within {
  border-color: var(--ink);
  box-shadow: 0 0 0 3px var(--accent-dim);
}
.editor textarea {
  width: 100%;
  background: transparent;
  border: none;
  color: var(--ink);
  padding: 24px;
  font-family: var(--font-body);
  font-size: 15px;
  line-height: 1.65;
  resize: vertical;
  min-height: 220px;
  outline: none;
}
.editor textarea::placeholder {
  color: var(--ink-faint);
  font-family: var(--font-display);
  font-style: italic;
  font-variation-settings: 'opsz' 14;
}
.editor-foot {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 20px;
  border-top: 1px solid var(--rule);
  background: var(--paper-raised);
}
.char-n {
  font-family: var(--font-mono);
  font-size: 12px;
  color: var(--ink-muted);
  letter-spacing: 0.02em;
}
.char-n.warn { color: var(--negative); }
.add-btn {
  background: var(--ink);
  color: var(--paper-raised);
  border: none;
  padding: 9px 18px;
  border-radius: var(--radius);
  font-family: var(--font-body);
  font-weight: 500;
  font-size: 13px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: background 0.2s;
}
.add-btn:hover:not(:disabled) { background: var(--accent); }
.add-btn:disabled { opacity: 0.35; cursor: not-allowed; }

/* ─ Seed list ─ */
.seed-list {
  list-style: none;
  padding: 0;
  margin: 0 0 32px;
}
.seed-list li {
  display: grid;
  grid-template-columns: 40px 1fr 32px;
  gap: 16px;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid var(--rule);
  background: var(--paper-raised);
  border-radius: var(--radius);
  margin-bottom: 6px;
}
.seed-n {
  font-family: var(--font-mono);
  font-size: 12px;
  color: var(--ink-faint);
  letter-spacing: 0.05em;
}
.seed-list p {
  margin: 0;
  font-size: 14px;
  color: var(--ink-soft);
  line-height: 1.5;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
}
.seed-del {
  background: none;
  border: none;
  color: var(--ink-faint);
  cursor: pointer;
  font-size: 16px;
  width: 28px; height: 28px;
  border-radius: 50%;
  transition: all 0.2s;
}
.seed-del:hover { background: var(--paper-sunk); color: var(--accent); }
.list-enter-active, .list-leave-active { transition: all 0.3s; }
.list-enter-from { opacity: 0; transform: translateX(-8px); }
.list-leave-to { opacity: 0; transform: translateX(8px); }

/* ─ Persona grid ─ */
.persona-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 12px;
  margin-bottom: 40px;
}
.p-card {
  background: var(--paper-card);
  border: 1px solid var(--rule);
  border-radius: var(--radius-lg);
  padding: 22px 20px;
  text-align: left;
  cursor: pointer;
  font-family: var(--font-body);
  color: var(--ink);
  position: relative;
  transition: all 0.2s;
  min-height: 180px;
}
.p-card:hover { border-color: var(--ink-muted); transform: translateY(-2px); box-shadow: 0 8px 20px -12px rgba(26,24,21,0.15); }
.p-card.on {
  border-color: var(--ink);
  background: var(--ink);
  color: var(--paper-raised);
  box-shadow: 0 12px 28px -16px rgba(26,24,21,0.5);
}
.p-n {
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--ink-faint);
  letter-spacing: 0.1em;
  display: block;
  margin-bottom: 10px;
}
.p-card.on .p-n { color: var(--accent); }
.p-name {
  font-family: var(--font-display);
  font-weight: 500;
  font-size: 17px;
  margin: 0 0 4px;
  letter-spacing: -0.01em;
  font-variation-settings: 'opsz' 24;
}
.p-age {
  font-family: var(--font-mono);
  font-size: 12px;
  color: var(--ink-muted);
  display: block;
  margin-bottom: 12px;
}
.p-card.on .p-age { color: var(--paper-sunk); }
.p-tags { display: flex; flex-wrap: wrap; gap: 4px; margin-bottom: 10px; }
.p-tags span {
  font-size: 11px;
  padding: 3px 8px;
  background: var(--paper-sunk);
  border-radius: 99px;
  color: var(--ink-soft);
}
.p-card.on .p-tags span { background: rgba(245, 241, 232, 0.15); color: var(--paper-raised); }
.p-habit {
  font-size: 12px;
  color: var(--ink-muted);
  line-height: 1.45;
  margin: 0;
}
.p-card.on .p-habit { color: var(--paper-sunk); }
.p-check {
  position: absolute;
  top: 18px;
  right: 18px;
  width: 26px; height: 26px;
  background: var(--accent);
  color: #fff;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
}

/* ─ Slider card ─ */
.slider-card {
  background: var(--paper-card);
  border: 1px solid var(--rule);
  border-radius: var(--radius-lg);
  padding: 28px;
  margin-bottom: 40px;
}
.slider-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 18px;
}
.slider-head label {
  font-weight: 500;
  font-size: 15px;
  display: block;
  margin-bottom: 4px;
}
.slider-sub { font-size: 12px; color: var(--ink-muted); margin: 0; }
.slider-val {
  font-family: var(--font-display);
  font-weight: 400;
  font-size: 44px;
  color: var(--accent);
  line-height: 1;
  font-variation-settings: 'opsz' 144;
}
.slider-unit { font-size: 16px; color: var(--ink-muted); margin-left: 4px; }
.slider-card input[type="range"] {
  width: 100%;
  appearance: none;
  height: 3px;
  background: var(--rule);
  outline: none;
  border-radius: 2px;
}
.slider-card input[type="range"]::-webkit-slider-thumb {
  appearance: none;
  width: 22px; height: 22px;
  border-radius: 50%;
  background: var(--ink);
  cursor: pointer;
  border: 3px solid var(--paper-card);
  box-shadow: 0 0 0 1px var(--ink);
  transition: transform 0.2s;
}
.slider-card input[type="range"]::-webkit-slider-thumb:hover {
  transform: scale(1.15);
  background: var(--accent);
  box-shadow: 0 0 0 1px var(--accent);
}
.slider-marks {
  display: flex;
  justify-content: space-between;
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--ink-faint);
  margin-top: 10px;
  letter-spacing: 0.05em;
}
.slider-hint {
  text-align: center;
  font-family: var(--font-display);
  font-style: italic;
  font-size: 15px;
  color: var(--ink-soft);
  margin: 20px 0 0;
  font-variation-settings: 'opsz' 24;
}

/* ─ Summary list (Step 3) ─ */
.summary {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1px;
  background: var(--rule);
  border: 1px solid var(--rule);
  border-radius: var(--radius-lg);
  overflow: hidden;
  margin-bottom: 32px;
}
.summary div {
  background: var(--paper-card);
  padding: 22px 24px;
}
.summary dt {
  font-family: var(--font-mono);
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.14em;
  color: var(--ink-muted);
  margin-bottom: 8px;
}
.summary dd {
  margin: 0;
  font-family: var(--font-display);
  font-weight: 500;
  font-size: 22px;
  color: var(--ink);
  font-variation-settings: 'opsz' 40;
  letter-spacing: -0.01em;
}
.round-control {
  display: flex;
  align-items: center;
  gap: 18px;
}
.round-control button {
  width: 32px; height: 32px;
  border-radius: 50%;
  border: 1px solid var(--rule);
  background: var(--paper-raised);
  color: var(--ink);
  cursor: pointer;
  font-size: 18px;
  line-height: 1;
  transition: all 0.2s;
}
.round-control button:hover { border-color: var(--accent); color: var(--accent); }
.round-control span { min-width: 28px; text-align: center; }

/* ─ Go button ─ */
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
  transition: background 0.25s, transform 0.1s;
  margin-bottom: 14px;
}
.go-btn:hover:not(:disabled) { background: var(--accent); }
.go-btn:active:not(:disabled) { transform: translateY(1px); }
.go-btn:disabled { opacity: 0.4; cursor: not-allowed; }
.go-label { font-weight: 500; letter-spacing: -0.005em; }
.go-arrow {
  font-family: var(--font-display);
  font-size: 24px;
  transition: transform 0.25s;
}
.go-btn:hover:not(:disabled) .go-arrow { transform: translateX(6px); }
.run-hint {
  text-align: center;
  font-size: 13px;
  color: var(--ink-muted);
  margin: 0 0 40px;
}

/* ─ Panel nav (back/next) ─ */
.panel-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 48px;
  padding-top: 24px;
  border-top: 1px solid var(--rule);
}
.back-btn {
  background: none;
  border: none;
  color: var(--ink-muted);
  cursor: pointer;
  font-family: var(--font-body);
  font-size: 14px;
  padding: 8px 0;
  transition: color 0.2s;
}
.back-btn:hover { color: var(--ink); }
.next-btn {
  background: var(--ink);
  color: var(--paper-raised);
  border: none;
  padding: 14px 24px;
  border-radius: var(--radius);
  cursor: pointer;
  font-family: var(--font-body);
  font-weight: 500;
  font-size: 14px;
  transition: background 0.2s;
}
.next-btn:hover:not(:disabled) { background: var(--accent); }
.next-btn:disabled { opacity: 0.35; cursor: not-allowed; }

.spin {
  width: 14px; height: 14px;
  border: 2px solid rgba(255,255,255,0.25);
  border-top-color: currentColor;
  border-radius: 50%;
  display: inline-block;
  animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 820px) {
  .page { padding: 0 20px; }
  .wrap { padding: 36px 0 60px; }
  .panel h1 { font-size: 34px; }
  .progress-nav { flex-wrap: wrap; gap: 12px; margin-bottom: 40px; }
  .step-rule { display: none; }
  .persona-grid { grid-template-columns: 1fr 1fr; }
  .summary { grid-template-columns: 1fr; }
}
</style>

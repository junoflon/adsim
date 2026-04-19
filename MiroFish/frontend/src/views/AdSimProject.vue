<template>
  <div class="adsim-project">
    <header class="topbar">
      <div class="topbar-left">
        <div class="logo" @click="$router.push('/adsim')">
          <span class="logo-mark">◆</span>
          <span class="logo-text">AdSim</span>
        </div>
        <span class="breadcrumb-sep">/</span>
        <span class="breadcrumb-current">{{ project?.name || '...' }}</span>
      </div>
      <div class="topbar-right">
        <button class="ab-entry" @click="$router.push(`/adsim/project/${projectId}/compare`)" v-if="project">
          <span class="ab-icon">⚖️</span>
          A/B 비교
        </button>
      </div>
    </header>

    <div class="content" v-if="project">
      <!-- Stepper -->
      <div class="stepper">
        <div v-for="(s, i) in steps" :key="i" :class="['step', { active: currentStep === i, done: currentStep > i }]"
             @click="currentStep = i">
          <span class="step-num">{{ i + 1 }}</span>
          <span class="step-label">{{ s }}</span>
        </div>
      </div>

      <!-- Step 1: Seed -->
      <section v-show="currentStep === 0" class="panel">
        <div class="panel-header">
          <h2>시드 자료 업로드</h2>
          <p class="panel-desc">{{ project.type === 'ad_reaction' ? '광고 대본을 입력하세요. 텍스트가 구체적일수록 더 현실적인 반응을 얻습니다.' : 'USP(제품 차별점)를 입력하세요. 여러 개를 비교하려면 각각 따로 업로드하세요.' }}</p>
        </div>

        <div class="textarea-wrap">
          <textarea v-model="seedContent"
                    :placeholder="project.type === 'ad_reaction' ? '광고 대본을 붙여넣으세요...\n\n예: [나레이션] 지금까지 이런 맛은 없었다. 제로칼로리인데 진짜 맛있는...' : 'USP를 입력하세요...\n\n예: 제로칼로리인데도 진짜 과일 맛이 나는 유일한 음료'"
                    rows="8"
                    maxlength="5000"></textarea>
          <div class="textarea-footer">
            <span class="char-count" :class="{ warn: seedContent.length > 4500 }">{{ seedContent.length }} / 5,000</span>
            <button class="btn-accent" :disabled="!seedContent.trim() || uploading" @click="handleUploadSeed">
              <span v-if="uploading" class="spinner-sm"></span>
              <span v-else>{{ seeds.length > 0 ? '+ 추가' : '업로드' }}</span>
            </button>
          </div>
        </div>

        <TransitionGroup name="list" tag="div" class="seed-list">
          <div v-for="s in seeds" :key="s.seed_id" class="seed-chip">
            <span class="chip-dot" :class="s.type"></span>
            <span class="chip-text">{{ s.content?.slice(0, 60) }}{{ s.content?.length > 60 ? '...' : '' }}</span>
            <button class="chip-remove" @click="handleDeleteSeed(s.seed_id)" aria-label="삭제">×</button>
          </div>
        </TransitionGroup>

        <div class="panel-nav">
          <div></div>
          <button class="btn-next" :disabled="seeds.length === 0" @click="currentStep = 1">
            다음: 페르소나 설정 →
          </button>
        </div>
      </section>

      <!-- Step 2: Persona -->
      <section v-show="currentStep === 1" class="panel">
        <div class="panel-header">
          <h2>타겟 페르소나</h2>
          <p class="panel-desc">가상 소비자 집단을 선택하세요. 이 사람들이 당신의 광고에 반응합니다.</p>
        </div>

        <div class="persona-grid">
          <div v-for="(p, i) in presets" :key="i"
               :class="['persona-card', { selected: selectedPreset === i }]"
               @click="selectedPreset = i" tabindex="0" role="radio"
               :aria-checked="selectedPreset === i">
            <div class="persona-check" v-if="selectedPreset === i">✓</div>
            <div class="persona-name">{{ p.name }}</div>
            <div class="persona-age">{{ p.age_range }}</div>
            <div class="persona-tags">
              <span v-for="(t, ti) in p.interests?.slice(0, 3)" :key="ti" class="ptag">{{ t }}</span>
            </div>
            <div class="persona-habits">{{ p.consumption_habits }}</div>
          </div>
        </div>

        <div class="slider-section">
          <div class="slider-header">
            <label>에이전트 수</label>
            <span class="slider-value">{{ agentCount }}명</span>
          </div>
          <input type="range" v-model.number="agentCount" min="10" max="100" step="5" class="range-slider" />
          <div class="slider-marks">
            <span>10</span><span>30</span><span>50</span><span>70</span><span>100</span>
          </div>
          <div class="slider-hint">
            <span v-if="agentCount <= 20">⚡ 빠른 테스트 — 비용 절약</span>
            <span v-else-if="agentCount <= 50">✦ 균형 잡힌 선택</span>
            <span v-else>🔬 정밀 분석 — 비용 증가</span>
          </div>
        </div>

        <div class="panel-nav">
          <button class="btn-back" @click="currentStep = 0">← 이전</button>
          <button class="btn-next" :disabled="selectedPreset === null" @click="currentStep = 2">
            다음: 실행 설정 →
          </button>
        </div>
      </section>

      <!-- Step 3: Run -->
      <section v-show="currentStep === 2" class="panel">
        <div class="panel-header">
          <h2>시뮬레이션 실행</h2>
          <p class="panel-desc">설정을 확인하고 시뮬레이션을 시작하세요.</p>
        </div>

        <div class="summary-grid">
          <div class="summary-item">
            <span class="summary-label">시드 자료</span>
            <span class="summary-value">{{ seeds.length }}개 업로드됨</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">타겟 페르소나</span>
            <span class="summary-value">{{ selectedPreset !== null ? presets[selectedPreset]?.name : '미선택' }}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">에이전트 수</span>
            <span class="summary-value">{{ agentCount }}명</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">라운드 수</span>
            <div class="round-input-wrap">
              <button class="round-btn" @click="totalRounds = Math.max(5, totalRounds - 5)">−</button>
              <span class="round-value">{{ totalRounds }}</span>
              <button class="round-btn" @click="totalRounds = Math.min(50, totalRounds + 5)">+</button>
            </div>
          </div>
        </div>

        <button class="run-btn" :disabled="!canRun || running" @click="handleRun">
          <span v-if="running" class="spinner-sm"></span>
          <template v-else>
            <span>시뮬레이션 시작</span>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
          </template>
        </button>

        <div class="panel-nav">
          <button class="btn-back" @click="currentStep = 1">← 이전</button>
          <div></div>
        </div>
      </section>
    </div>
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
const steps = ['시드 자료', '페르소나', '실행']

const canRun = computed(() => seeds.value.length > 0 && selectedPreset.value !== null)

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
    const seedType = project.value.type === 'ad_reaction' ? 'ad_script' : 'usp_text'
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
:root {
  --bg: #0c0f14; --bg-raised: #141821; --bg-card: #181d27; --bg-hover: #1e2433;
  --surface: #232a38; --border: #2a3244; --border-light: #1e2636;
  --text: #e8eaf0; --text-secondary: #8b93a6; --text-muted: #5a6378;
  --accent: #d4a053; --accent-dim: rgba(212,160,83,0.15); --accent-glow: rgba(212,160,83,0.3);
  --radius: 8px;
  --font: 'IBM Plex Sans', 'Noto Sans KR', system-ui, sans-serif;
  --mono: 'IBM Plex Mono', 'JetBrains Mono', monospace;
}
* { box-sizing: border-box; }
.adsim-project { min-height: 100vh; background: var(--bg); color: var(--text); font-family: var(--font); -webkit-font-smoothing: antialiased; }

.topbar { height: 56px; display: flex; align-items: center; justify-content: space-between; padding: 0 32px; border-bottom: 1px solid var(--border-light); background: rgba(12,15,20,0.85); backdrop-filter: blur(12px); position: sticky; top: 0; z-index: 50; }
.ab-entry { background: transparent; border: 1px solid var(--border); color: var(--text-secondary); padding: 7px 14px; border-radius: 6px; cursor: pointer; font-size: 0.82rem; display: flex; align-items: center; gap: 6px; font-family: inherit; transition: all 0.2s; }
.ab-entry:hover { border-color: var(--accent); color: var(--accent); }
.ab-icon { font-size: 0.9rem; }
.topbar-left { display: flex; align-items: center; gap: 10px; }
.logo { display: flex; align-items: center; gap: 8px; cursor: pointer; }
.logo-mark { color: var(--accent); }
.logo-text { font-family: var(--mono); font-weight: 600; font-size: 0.95rem; }
.breadcrumb-sep { color: var(--text-muted); }
.breadcrumb-current { font-size: 0.85rem; color: var(--text-secondary); }

.content { max-width: 780px; margin: 0 auto; padding: 32px 24px 80px; }

/* Stepper */
.stepper { display: flex; gap: 4px; margin-bottom: 36px; background: var(--bg-raised); border-radius: 10px; padding: 4px; border: 1px solid var(--border-light); }
.step { flex: 1; display: flex; align-items: center; gap: 8px; padding: 10px 16px; border-radius: 8px; cursor: pointer; font-size: 0.85rem; color: var(--text-muted); transition: all 0.2s; }
.step:hover { color: var(--text-secondary); }
.step.active { background: var(--surface); color: var(--text); }
.step.done { color: var(--accent); }
.step-num { font-family: var(--mono); font-weight: 600; font-size: 0.75rem; width: 22px; height: 22px; border-radius: 50%; display: flex; align-items: center; justify-content: center; border: 1px solid var(--border); }
.step.active .step-num { background: var(--accent); color: var(--bg); border-color: var(--accent); }
.step.done .step-num { background: var(--accent-dim); border-color: var(--accent); }

/* Panel */
.panel { animation: fadeIn 0.3s ease; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } }
.panel-header { margin-bottom: 24px; }
.panel-header h2 { font-size: 1.3rem; font-weight: 600; margin: 0 0 8px; }
.panel-desc { font-size: 0.9rem; color: var(--text-secondary); line-height: 1.6; margin: 0; }

/* Textarea */
.textarea-wrap { background: var(--bg-card); border: 1px solid var(--border-light); border-radius: var(--radius); overflow: hidden; margin-bottom: 16px; }
.textarea-wrap textarea { width: 100%; background: transparent; border: none; color: var(--text); padding: 16px; font-family: var(--mono); font-size: 0.85rem; line-height: 1.7; resize: vertical; min-height: 160px; outline: none; }
.textarea-wrap textarea::placeholder { color: var(--text-muted); }
.textarea-footer { display: flex; justify-content: space-between; align-items: center; padding: 10px 16px; border-top: 1px solid var(--border-light); }
.char-count { font-family: var(--mono); font-size: 0.7rem; color: var(--text-muted); }
.char-count.warn { color: #e05252; }
.btn-accent { background: var(--accent); color: var(--bg); border: none; padding: 8px 18px; border-radius: 6px; font-weight: 600; cursor: pointer; font-size: 0.82rem; display: flex; align-items: center; gap: 6px; transition: all 0.2s; }
.btn-accent:disabled { opacity: 0.4; cursor: not-allowed; }
.btn-accent:hover:not(:disabled) { background: #e0b060; }
.spinner-sm { width: 14px; height: 14px; border: 2px solid rgba(0,0,0,0.2); border-top-color: var(--bg); border-radius: 50%; animation: spin 0.6s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

/* Seeds */
.seed-list { display: flex; flex-direction: column; gap: 6px; margin-bottom: 24px; }
.seed-chip { display: flex; align-items: center; gap: 10px; padding: 10px 14px; background: var(--bg-card); border: 1px solid var(--border-light); border-radius: 6px; font-size: 0.83rem; }
.chip-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--accent); flex-shrink: 0; }
.chip-text { flex: 1; color: var(--text-secondary); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.chip-remove { background: none; border: none; color: var(--text-muted); cursor: pointer; font-size: 1.1rem; padding: 0 4px; }
.chip-remove:hover { color: #e05252; }
.list-enter-active, .list-leave-active { transition: all 0.3s ease; }
.list-enter-from { opacity: 0; transform: translateX(-10px); }
.list-leave-to { opacity: 0; transform: translateX(10px); }

/* Personas */
.persona-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(210px, 1fr)); gap: 10px; margin-bottom: 28px; }
.persona-card { background: var(--bg-card); border: 1px solid var(--border-light); border-radius: var(--radius); padding: 16px; cursor: pointer; transition: all 0.2s; position: relative; outline: none; }
.persona-card:hover { border-color: var(--text-muted); }
.persona-card.selected { border-color: var(--accent); background: var(--accent-dim); }
.persona-check { position: absolute; top: 10px; right: 10px; width: 22px; height: 22px; background: var(--accent); color: var(--bg); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.7rem; font-weight: 700; }
.persona-name { font-weight: 600; font-size: 0.9rem; margin-bottom: 4px; }
.persona-age { font-family: var(--mono); font-size: 0.72rem; color: var(--text-muted); margin-bottom: 8px; }
.persona-tags { display: flex; flex-wrap: wrap; gap: 4px; margin-bottom: 8px; }
.ptag { font-size: 0.68rem; padding: 2px 8px; background: var(--surface); border-radius: 99px; color: var(--text-secondary); }
.persona-habits { font-size: 0.75rem; color: var(--text-muted); line-height: 1.4; }

/* Slider */
.slider-section { background: var(--bg-card); border: 1px solid var(--border-light); border-radius: var(--radius); padding: 20px; margin-bottom: 24px; }
.slider-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.slider-header label { font-size: 0.9rem; font-weight: 500; }
.slider-value { font-family: var(--mono); font-weight: 600; color: var(--accent); font-size: 1.1rem; }
.range-slider { width: 100%; appearance: none; height: 4px; background: var(--border); border-radius: 2px; outline: none; }
.range-slider::-webkit-slider-thumb { appearance: none; width: 18px; height: 18px; border-radius: 50%; background: var(--accent); cursor: pointer; border: 3px solid var(--bg); box-shadow: 0 0 0 1px var(--accent); }
.slider-marks { display: flex; justify-content: space-between; font-family: var(--mono); font-size: 0.65rem; color: var(--text-muted); margin-top: 6px; }
.slider-hint { text-align: center; font-size: 0.78rem; color: var(--text-secondary); margin-top: 12px; }

/* Summary */
.summary-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 28px; }
.summary-item { background: var(--bg-card); border: 1px solid var(--border-light); border-radius: var(--radius); padding: 16px; }
.summary-label { display: block; font-size: 0.75rem; color: var(--text-muted); margin-bottom: 6px; font-family: var(--mono); text-transform: uppercase; letter-spacing: 0.5px; }
.summary-value { font-weight: 600; font-size: 0.95rem; }
.round-input-wrap { display: flex; align-items: center; gap: 12px; margin-top: 4px; }
.round-btn { width: 30px; height: 30px; border-radius: 6px; border: 1px solid var(--border); background: var(--surface); color: var(--text); cursor: pointer; font-size: 1.1rem; display: flex; align-items: center; justify-content: center; }
.round-btn:hover { border-color: var(--accent); color: var(--accent); }
.round-value { font-family: var(--mono); font-weight: 600; font-size: 1.2rem; min-width: 32px; text-align: center; }

.run-btn { width: 100%; background: var(--accent); color: var(--bg); border: none; padding: 16px; border-radius: var(--radius); font-weight: 700; font-size: 1rem; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 10px; transition: all 0.25s; font-family: var(--font); }
.run-btn:hover:not(:disabled) { background: #e0b060; box-shadow: 0 6px 24px var(--accent-glow); }
.run-btn:disabled { opacity: 0.35; cursor: not-allowed; }

/* Nav */
.panel-nav { display: flex; justify-content: space-between; margin-top: 32px; padding-top: 20px; border-top: 1px solid var(--border-light); }
.btn-back { background: none; border: none; color: var(--text-muted); cursor: pointer; font-size: 0.85rem; padding: 8px 0; }
.btn-back:hover { color: var(--text); }
.btn-next { background: var(--surface); color: var(--text); border: 1px solid var(--border); padding: 10px 20px; border-radius: 6px; cursor: pointer; font-size: 0.85rem; transition: all 0.2s; }
.btn-next:hover:not(:disabled) { border-color: var(--accent); color: var(--accent); }
.btn-next:disabled { opacity: 0.3; cursor: not-allowed; }

@media (max-width: 768px) {
  .content { padding: 20px 16px 60px; }
  .persona-grid { grid-template-columns: 1fr 1fr; }
  .summary-grid { grid-template-columns: 1fr; }
  .stepper { flex-direction: column; }
}
</style>

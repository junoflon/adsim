<template>
  <div class="page">
    <!-- Masthead -->
    <header class="masthead">
      <div class="mast-left">
        <span class="mast-mono">AdSim — Vol.1</span>
      </div>
      <div class="mast-center">
        <span class="brand" @click="$router.push('/')">AdSim</span>
      </div>
      <div class="mast-right">
        <span class="mast-mono">{{ today }}</span>
      </div>
    </header>

    <div class="rule-line"></div>

    <!-- Hero: editorial cover -->
    <section class="hero">
      <div class="hero-eyebrow">
        <span class="eyebrow-line"></span>
        <span class="eyebrow-text">광고 전에, 반응을 먼저 보다</span>
      </div>
      <h1 class="hero-title">
        <span class="hero-italic">가상 소비자</span>에게<br/>
        광고를 먼저 <span class="hero-underline">보여주세요</span>.
      </h1>
      <p class="hero-lede">
        수십 명의 AI 에이전트가 당신의 광고 대본과 USP에 반응합니다.
        단순한 점수가 아니라, <em>"왜 좋은지"</em>와 <em>"왜 싫은지"</em>를 대화로 돌려드립니다.
      </p>
      <div class="hero-actions">
        <button class="btn-primary" @click="openCreate">
          새 프로젝트 시작하기
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M13 6l6 6-6 6"/></svg>
        </button>
        <button class="btn-link" @click="scrollToList">
          {{ projects.length ? `진행 중인 프로젝트 ${projects.length}개 보기` : '사용 가이드' }}
        </button>
      </div>
    </section>

    <!-- Feature band -->
    <section class="features">
      <div class="feature">
        <div class="feat-num">01</div>
        <h3>광고 대본 입력</h3>
        <p>텍스트 붙여넣기 또는 PDF 업로드. 최대 5,000자.</p>
      </div>
      <div class="feature">
        <div class="feat-num">02</div>
        <h3>페르소나 선택</h3>
        <p>10가지 프리셋 타겟 또는 직접 설정한 집단.</p>
      </div>
      <div class="feature">
        <div class="feat-num">03</div>
        <h3>분석 보고서</h3>
        <p>감정 분포, 인사이트, 우려사항, 개선 추천.</p>
      </div>
    </section>

    <div class="rule-line"></div>

    <!-- Projects -->
    <section class="projects" ref="projectsEl">
      <div class="sec-head">
        <h2 class="sec-title">프로젝트</h2>
        <span class="sec-count" v-if="projects.length">{{ projects.length }}</span>
      </div>

      <div v-if="loading" class="state">
        <span class="dot-pulse"></span>
        <span>불러오는 중</span>
      </div>

      <div v-else-if="projects.length === 0" class="empty">
        <p class="empty-title">아직 만든 프로젝트가 없어요</p>
        <p class="empty-hint">위 버튼으로 첫 테스트를 시작해보세요.</p>
      </div>

      <ol v-else class="project-list">
        <li v-for="(p, i) in projects" :key="p.project_id" class="project-row"
            @click="$router.push(`/adsim/project/${p.project_id}`)"
            tabindex="0" role="button"
            @keydown.enter="$router.push(`/adsim/project/${p.project_id}`)">
          <span class="row-idx">{{ String(i + 1).padStart(2, '0') }}</span>
          <div class="row-main">
            <div class="row-top">
              <span class="row-type" :class="p.type">{{ p.type === 'ad_reaction' ? '광고 반응' : 'USP 테스트' }}</span>
              <time>{{ formatDate(p.created_at) }}</time>
            </div>
              <h3 class="row-name">{{ p.name }}</h3>
              <p class="row-desc">{{ p.description || '설명 없음' }}</p>
          </div>
          <button class="row-del" @click.stop="handleDelete(p.project_id)" aria-label="삭제">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M18 6L6 18M6 6l12 12"/></svg>
          </button>
          <span class="row-arrow">→</span>
        </li>
      </ol>
    </section>

    <footer class="page-foot">
      <span>AdSim · MiroFish Engine</span>
      <span class="foot-mono">광고를 먼저 보고, 반응을 먼저 읽다</span>
    </footer>

    <!-- Create Modal -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showCreateModal" class="overlay" @click.self="showCreateModal = false">
          <div class="sheet" role="dialog" aria-modal="true">
            <div class="sheet-head">
              <span class="sheet-eyebrow">NEW PROJECT</span>
              <button class="sheet-close" @click="showCreateModal = false" aria-label="닫기">✕</button>
            </div>

            <h2 class="sheet-title">무엇을 테스트하시겠어요?</h2>

            <div class="field">
              <label>프로젝트 이름</label>
              <input v-model="form.name" placeholder="예: 신제품 음료 TV광고 테스트"
                     ref="nameInput" maxlength="60" @keydown.enter="handleCreate" />
            </div>

            <div class="field">
              <label>테스트 종류</label>
              <div class="pick">
                <button :class="['pick-btn', { on: form.type === 'ad_reaction' }]"
                        @click="form.type = 'ad_reaction'">
                  <span class="pick-title">광고 반응</span>
                  <span class="pick-sub">대본/영상 반응 예측</span>
                </button>
                <button :class="['pick-btn', { on: form.type === 'usp_test' }]"
                        @click="form.type = 'usp_test'">
                  <span class="pick-title">USP 테스트</span>
                  <span class="pick-sub">차별점 수용도 테스트</span>
                </button>
              </div>
            </div>

            <div class="field">
              <label>메모 <span class="opt">선택</span></label>
              <textarea v-model="form.description" placeholder="이 테스트의 목적이나 맥락" rows="3"></textarea>
            </div>

            <div class="sheet-foot">
              <button class="btn-ghost" @click="showCreateModal = false">취소</button>
              <button class="btn-primary sm" :disabled="!form.name.trim() || creating" @click="handleCreate">
                <span v-if="creating" class="spin"></span>
                <span v-else>만들기</span>
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { listProjects, createProject, deleteProject } from '../api/adsim.js'

const projects = ref([])
const loading = ref(true)
const creating = ref(false)
const showCreateModal = ref(false)
const nameInput = ref(null)
const projectsEl = ref(null)
const form = ref({ name: '', type: 'ad_reaction', description: '' })

const today = new Intl.DateTimeFormat('ko-KR', { year: 'numeric', month: 'long', day: 'numeric' }).format(new Date())

const loadProjects = async () => {
  loading.value = true
  try { projects.value = (await listProjects()).data.data } catch (e) { console.error(e) }
  finally { loading.value = false }
}

const openCreate = async () => {
  showCreateModal.value = true
  await nextTick()
  nameInput.value?.focus()
}

const handleCreate = async () => {
  if (!form.value.name.trim() || creating.value) return
  creating.value = true
  try {
    await createProject(form.value)
    showCreateModal.value = false
    form.value = { name: '', type: 'ad_reaction', description: '' }
    await loadProjects()
  } catch (e) {
    alert('생성 실패: ' + (e.response?.data?.error || e.message))
  } finally { creating.value = false }
}

const handleDelete = async (id) => {
  if (!confirm('이 프로젝트와 모든 데이터가 삭제됩니다.\n계속하시겠습니까?')) return
  try { await deleteProject(id); await loadProjects() } catch (e) { alert('삭제 실패') }
}

const scrollToList = () => projectsEl.value?.scrollIntoView({ behavior: 'smooth' })

const formatDate = (d) => d ? new Intl.DateTimeFormat('ko-KR', { month: 'short', day: 'numeric' }).format(new Date(d)) : ''

onMounted(loadProjects)
</script>

<style scoped>
.page {
  min-height: 100vh;
  max-width: 1160px;
  margin: 0 auto;
  padding: 0 40px 0;
}

/* ─ Masthead ─ */
.masthead {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  padding: 22px 0 18px;
}
.mast-mono {
  font-family: var(--font-mono);
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.14em;
  color: var(--ink-muted);
}
.mast-right { text-align: right; }
.brand {
  font-family: var(--font-display);
  font-weight: 500;
  font-size: 22px;
  letter-spacing: -0.01em;
  cursor: pointer;
  font-variation-settings: 'opsz' 40, 'SOFT' 50;
}
.rule-line {
  height: 1px;
  background: var(--ink);
  opacity: 0.85;
}

/* ─ Hero ─ */
.hero {
  padding: 80px 0 60px;
  max-width: 860px;
}
.hero-eyebrow {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 28px;
}
.eyebrow-line {
  width: 36px;
  height: 1px;
  background: var(--accent);
}
.eyebrow-text {
  font-family: var(--font-mono);
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.22em;
  color: var(--accent);
}
.hero-title {
  font-family: var(--font-display);
  font-weight: 400;
  font-size: clamp(40px, 6vw, 76px);
  line-height: 1.02;
  letter-spacing: -0.025em;
  margin: 0 0 28px;
  color: var(--ink);
  font-variation-settings: 'opsz' 144, 'SOFT' 30;
}
.hero-italic {
  font-style: italic;
  color: var(--accent);
  font-variation-settings: 'opsz' 144, 'SOFT' 100;
}
.hero-underline {
  background-image: linear-gradient(var(--accent), var(--accent));
  background-size: 100% 4px;
  background-repeat: no-repeat;
  background-position: 0 96%;
  padding: 0 2px;
}
.hero-lede {
  font-size: 19px;
  line-height: 1.65;
  color: var(--ink-soft);
  max-width: 620px;
  margin: 0 0 40px;
}
.hero-lede em {
  font-family: var(--font-display);
  font-style: italic;
  font-weight: 500;
  color: var(--ink);
}

.hero-actions {
  display: flex;
  align-items: center;
  gap: 22px;
}

/* ─ Buttons ─ */
.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  background: var(--ink);
  color: var(--paper-raised);
  border: none;
  padding: 18px 28px;
  font-family: var(--font-body);
  font-weight: 500;
  font-size: 15px;
  letter-spacing: -0.005em;
  cursor: pointer;
  border-radius: var(--radius);
  transition: background 0.2s, transform 0.1s;
}
.btn-primary:hover { background: var(--accent); }
.btn-primary:active { transform: translateY(1px); }
.btn-primary.sm { padding: 12px 22px; font-size: 14px; }
.btn-primary:disabled { opacity: 0.4; cursor: not-allowed; }
.btn-primary svg { transition: transform 0.2s; }
.btn-primary:hover svg { transform: translateX(3px); }

.btn-link {
  background: none;
  border: none;
  color: var(--ink-soft);
  cursor: pointer;
  font-family: var(--font-body);
  font-size: 14px;
  padding: 18px 0;
  text-decoration: underline;
  text-decoration-thickness: 1px;
  text-underline-offset: 4px;
  text-decoration-color: var(--ink-faint);
  transition: color 0.2s, text-decoration-color 0.2s;
}
.btn-link:hover {
  color: var(--accent);
  text-decoration-color: var(--accent);
}

.btn-ghost {
  background: none;
  border: 1px solid var(--rule);
  color: var(--ink-soft);
  padding: 12px 22px;
  border-radius: var(--radius);
  cursor: pointer;
  font-family: var(--font-body);
  font-size: 14px;
  transition: border-color 0.2s, color 0.2s;
}
.btn-ghost:hover { border-color: var(--ink); color: var(--ink); }

/* ─ Features ─ */
.features {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0;
  padding: 56px 0;
  border-top: 1px solid var(--rule);
}
.feature {
  padding: 32px 32px 32px 0;
  border-right: 1px solid var(--rule);
}
.feature:last-child { border-right: none; padding-right: 0; }
.feature:not(:first-child) { padding-left: 32px; }
.feat-num {
  font-family: var(--font-mono);
  font-size: 12px;
  color: var(--accent);
  margin-bottom: 16px;
  letter-spacing: 0.1em;
}
.feature h3 {
  font-family: var(--font-display);
  font-weight: 500;
  font-size: 22px;
  margin: 0 0 10px;
  letter-spacing: -0.01em;
  font-variation-settings: 'opsz' 40;
}
.feature p {
  font-size: 14px;
  line-height: 1.6;
  color: var(--ink-muted);
  margin: 0;
}

/* ─ Projects section ─ */
.projects { padding: 56px 0 80px; }
.sec-head {
  display: flex;
  align-items: baseline;
  gap: 16px;
  margin-bottom: 32px;
}
.sec-title {
  font-family: var(--font-display);
  font-weight: 400;
  font-size: 44px;
  letter-spacing: -0.02em;
  margin: 0;
  font-variation-settings: 'opsz' 144, 'SOFT' 30;
}
.sec-count {
  font-family: var(--font-mono);
  font-size: 13px;
  color: var(--ink-muted);
}

.state {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 60px 0;
  color: var(--ink-muted);
  font-size: 14px;
}
.dot-pulse {
  width: 8px; height: 8px;
  border-radius: 50%;
  background: var(--accent);
  animation: pulse 1.2s infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 0.4; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.3); }
}

.empty {
  text-align: center;
  padding: 80px 0;
}
.empty-title {
  font-family: var(--font-display);
  font-style: italic;
  font-size: 22px;
  color: var(--ink-soft);
  margin: 0 0 8px;
  font-variation-settings: 'opsz' 40;
}
.empty-hint {
  font-size: 14px;
  color: var(--ink-muted);
  margin: 0;
}

.project-list {
  list-style: none;
  padding: 0;
  margin: 0;
  border-top: 1px solid var(--rule);
}
.project-row {
  display: grid;
  grid-template-columns: 56px 1fr 40px 32px;
  gap: 20px;
  align-items: center;
  padding: 26px 0;
  border-bottom: 1px solid var(--rule);
  cursor: pointer;
  transition: background 0.2s, padding 0.2s;
  outline: none;
  position: relative;
}
.project-row:hover, .project-row:focus-visible {
  background: var(--paper-raised);
  padding-left: 16px;
  padding-right: 16px;
  margin: 0 -16px;
}
.row-idx {
  font-family: var(--font-mono);
  font-size: 13px;
  color: var(--ink-faint);
  letter-spacing: 0.05em;
}
.row-main { min-width: 0; }
.row-top {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 6px;
}
.row-type {
  font-family: var(--font-mono);
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.14em;
  padding: 3px 9px;
  border-radius: 99px;
  border: 1px solid var(--rule);
  color: var(--ink-soft);
}
.row-type.ad_reaction { border-color: var(--type-a); color: var(--type-a); }
.row-type.usp_test    { border-color: var(--type-b); color: var(--type-b); }
.row-top time {
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--ink-muted);
  letter-spacing: 0.05em;
}
.row-name {
  font-family: var(--font-display);
  font-weight: 500;
  font-size: 24px;
  margin: 0 0 4px;
  letter-spacing: -0.015em;
  color: var(--ink);
  font-variation-settings: 'opsz' 40;
}
.row-desc {
  font-size: 14px;
  color: var(--ink-muted);
  margin: 0;
  line-height: 1.5;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
}
.row-del {
  opacity: 0;
  background: none;
  border: 1px solid var(--rule);
  color: var(--ink-muted);
  border-radius: 50%;
  width: 32px; height: 32px;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
}
.project-row:hover .row-del, .project-row:focus-within .row-del { opacity: 1; }
.row-del:hover { border-color: var(--accent); color: var(--accent); }
.row-arrow {
  font-family: var(--font-display);
  color: var(--ink-faint);
  font-size: 22px;
  transition: transform 0.2s, color 0.2s;
}
.project-row:hover .row-arrow { color: var(--accent); transform: translateX(4px); }

/* ─ Footer ─ */
.page-foot {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 40px 0;
  border-top: 1px solid var(--rule);
  font-size: 13px;
  color: var(--ink-muted);
}
.foot-mono {
  font-family: var(--font-display);
  font-style: italic;
  font-size: 14px;
  font-variation-settings: 'opsz' 14;
}

/* ─ Modal ─ */
.overlay {
  position: fixed;
  inset: 0;
  background: rgba(26, 24, 21, 0.32);
  backdrop-filter: blur(6px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
  padding: 24px;
}
.sheet {
  background: var(--paper-raised);
  border: 1px solid var(--rule);
  border-radius: var(--radius-lg);
  width: 520px;
  max-width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  padding: 32px 34px;
  box-shadow: 0 32px 80px -20px rgba(26, 24, 21, 0.25);
}
.sheet-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 18px;
}
.sheet-eyebrow {
  font-family: var(--font-mono);
  font-size: 11px;
  letter-spacing: 0.2em;
  color: var(--accent);
}
.sheet-close {
  background: none;
  border: none;
  color: var(--ink-muted);
  cursor: pointer;
  font-size: 18px;
  padding: 6px 10px;
  border-radius: 50%;
  transition: all 0.2s;
}
.sheet-close:hover { background: var(--paper-sunk); color: var(--ink); }
.sheet-title {
  font-family: var(--font-display);
  font-weight: 400;
  font-size: 32px;
  letter-spacing: -0.02em;
  margin: 0 0 28px;
  color: var(--ink);
  line-height: 1.1;
  font-variation-settings: 'opsz' 144, 'SOFT' 50;
}

.field { margin-bottom: 22px; }
.field label {
  display: block;
  font-family: var(--font-body);
  font-weight: 500;
  font-size: 13px;
  color: var(--ink-soft);
  margin-bottom: 10px;
  letter-spacing: 0.01em;
}
.field .opt { font-weight: 400; color: var(--ink-faint); margin-left: 4px; }
.field input, .field textarea {
  width: 100%;
  background: var(--paper-card);
  border: 1px solid var(--rule);
  color: var(--ink);
  padding: 12px 14px;
  font-family: var(--font-body);
  font-size: 15px;
  border-radius: var(--radius);
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.field input::placeholder, .field textarea::placeholder { color: var(--ink-faint); }
.field input:focus, .field textarea:focus {
  border-color: var(--ink);
  box-shadow: 0 0 0 3px var(--accent-dim);
}
.field textarea { resize: vertical; min-height: 80px; line-height: 1.5; }

.pick { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.pick-btn {
  background: var(--paper-card);
  border: 1px solid var(--rule);
  border-radius: var(--radius);
  padding: 16px 14px;
  cursor: pointer;
  text-align: left;
  font-family: var(--font-body);
  color: var(--ink);
  transition: all 0.2s;
}
.pick-btn:hover { border-color: var(--ink-muted); }
.pick-btn.on {
  border-color: var(--ink);
  background: var(--ink);
  color: var(--paper-raised);
  box-shadow: 0 0 0 3px var(--accent-dim);
}
.pick-title { display: block; font-weight: 600; font-size: 14px; margin-bottom: 4px; }
.pick-sub { display: block; font-size: 12px; color: var(--ink-muted); }
.pick-btn.on .pick-sub { color: var(--paper-sunk); }

.sheet-foot {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 28px;
  padding-top: 22px;
  border-top: 1px solid var(--rule);
}

.spin {
  width: 14px; height: 14px;
  border: 2px solid rgba(255,255,255,0.25);
  border-top-color: currentColor;
  border-radius: 50%;
  display: inline-block;
  animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.modal-enter-active, .modal-leave-active { transition: opacity 0.25s, transform 0.25s; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
.modal-enter-from .sheet, .modal-leave-to .sheet { transform: translateY(12px) scale(0.98); }

/* ─ Responsive ─ */
@media (max-width: 820px) {
  .page { padding: 0 20px; }
  .features { grid-template-columns: 1fr; }
  .feature { border-right: none; border-bottom: 1px solid var(--rule); padding: 24px 0; }
  .feature:not(:first-child) { padding-left: 0; }
  .feature:last-child { border-bottom: none; }
  .hero { padding: 48px 0 40px; }
  .hero-actions { flex-direction: column; align-items: flex-start; gap: 6px; }
  .project-row { grid-template-columns: 40px 1fr 24px; }
  .row-del { display: none; }
  .sec-title { font-size: 32px; }
}
</style>

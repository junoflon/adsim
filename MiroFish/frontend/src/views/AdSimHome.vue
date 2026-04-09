<template>
  <div class="adsim-home">
    <!-- Top Bar -->
    <header class="topbar">
      <div class="topbar-left">
        <div class="logo" @click="$router.push('/')" tabindex="0" role="button" aria-label="MiroFish 홈">
          <span class="logo-mark">◆</span>
          <span class="logo-text">AdSim</span>
        </div>
        <span class="logo-divider"></span>
        <span class="logo-sub">광고 시뮬레이션 엔진</span>
      </div>
      <div class="topbar-right">
        <span class="status-pill"><span class="pulse"></span>시스템 정상</span>
      </div>
    </header>

    <!-- Hero -->
    <section class="hero">
      <div class="hero-inner">
        <div class="hero-label">MiroFish 기반 마케팅 인텔리전스</div>
        <h1 class="hero-title">
          광고를 집행하기 전에,<br/>
          <span class="accent">가상 소비자의 반응</span>을 먼저 확인하세요.
        </h1>
        <p class="hero-desc">
          수십 명의 AI 에이전트가 당신의 광고에 진짜 소비자처럼 반응합니다.
          점수만 주는 게 아니라, <em>왜</em> 좋은지 <em>왜</em> 싫은지 대화로 확인하세요.
        </p>
        <button class="cta-btn" @click="showCreateModal = true">
          <span>새 프로젝트 시작</span>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
        </button>
      </div>
      <div class="hero-deco">
        <div class="deco-grid">
          <div v-for="n in 16" :key="n" class="deco-cell" :style="{ animationDelay: n * 0.08 + 's' }"></div>
        </div>
      </div>
    </section>

    <!-- Project List -->
    <section class="projects-section">
      <div class="section-header">
        <h2>프로젝트</h2>
        <span class="count-badge" v-if="projects.length">{{ projects.length }}개</span>
      </div>

      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <span>프로젝트를 불러오는 중...</span>
      </div>

      <div v-else-if="projects.length === 0" class="empty-state">
        <div class="empty-icon">◇</div>
        <p>아직 프로젝트가 없습니다</p>
        <p class="empty-hint">위 버튼으로 첫 프로젝트를 만들어보세요</p>
      </div>

      <div v-else class="project-list">
        <article v-for="p in projects" :key="p.project_id" class="project-card"
                 @click="$router.push(`/adsim/project/${p.project_id}`)"
                 tabindex="0" role="button"
                 @keydown.enter="$router.push(`/adsim/project/${p.project_id}`)">
          <div class="card-top">
            <span class="card-type-dot" :class="p.type"></span>
            <span class="card-type-label">{{ p.type === 'ad_reaction' ? '광고 반응' : 'USP 테스트' }}</span>
            <button class="card-delete" @click.stop="handleDelete(p.project_id)" aria-label="프로젝트 삭제">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6L6 18M6 6l12 12"/></svg>
            </button>
          </div>
          <h3 class="card-name">{{ p.name }}</h3>
          <p class="card-desc">{{ p.description || '설명이 없습니다' }}</p>
          <div class="card-footer">
            <time class="card-date">{{ formatDate(p.created_at) }}</time>
            <span class="card-arrow">→</span>
          </div>
        </article>
      </div>
    </section>

    <!-- Create Modal -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showCreateModal" class="modal-overlay" @click.self="showCreateModal = false" @keydown.escape="showCreateModal = false">
          <div class="modal" role="dialog" aria-modal="true" aria-labelledby="modal-title">
            <div class="modal-header">
              <h2 id="modal-title">새 프로젝트</h2>
              <button class="modal-close" @click="showCreateModal = false" aria-label="닫기">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6L6 18M6 6l12 12"/></svg>
              </button>
            </div>

            <div class="modal-body">
              <div class="field">
                <label for="proj-name">프로젝트 이름 <span class="required">*</span></label>
                <input id="proj-name" v-model="form.name" placeholder="예: 신규 음료 TV광고 테스트"
                       ref="nameInput" maxlength="60" @keydown.enter="handleCreate" />
                <span class="char-count">{{ form.name.length }}/60</span>
              </div>

              <div class="field">
                <label>시뮬레이션 유형 <span class="required">*</span></label>
                <div class="type-selector">
                  <button :class="['type-option', { active: form.type === 'ad_reaction' }]"
                          @click="form.type = 'ad_reaction'">
                    <span class="type-icon">📺</span>
                    <span class="type-label">광고 반응 테스트</span>
                    <span class="type-help">광고 대본/영상에 대한 소비자 반응 예측</span>
                  </button>
                  <button :class="['type-option', { active: form.type === 'usp_test' }]"
                          @click="form.type = 'usp_test'">
                    <span class="type-icon">🎯</span>
                    <span class="type-label">USP 시장 반응</span>
                    <span class="type-help">제품 차별점(USP)에 대한 시장 수용도 테스트</span>
                  </button>
                </div>
              </div>

              <div class="field">
                <label for="proj-desc">설명 <span class="optional">(선택)</span></label>
                <textarea id="proj-desc" v-model="form.description" placeholder="프로젝트에 대한 간단한 메모" rows="3"></textarea>
              </div>
            </div>

            <div class="modal-footer">
              <button class="btn-ghost" @click="showCreateModal = false">취소</button>
              <button class="btn-primary" :disabled="!form.name.trim() || creating" @click="handleCreate">
                <span v-if="creating" class="spinner-sm"></span>
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
const form = ref({ name: '', type: 'ad_reaction', description: '' })

const loadProjects = async () => {
  loading.value = true
  try {
    const res = await listProjects()
    projects.value = res.data.data
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
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
  } finally {
    creating.value = false
  }
}

const handleDelete = async (id) => {
  if (!confirm('이 프로젝트와 모든 데이터가 삭제됩니다. 계속하시겠습니까?')) return
  try {
    await deleteProject(id)
    await loadProjects()
  } catch (e) {
    alert('삭제 실패')
  }
}

const formatDate = (d) => {
  if (!d) return ''
  const date = new Date(d)
  return new Intl.DateTimeFormat('ko-KR', { year: 'numeric', month: 'long', day: 'numeric' }).format(date)
}

// Auto-focus name input when modal opens
const openModal = () => {
  showCreateModal.value = true
  nextTick(() => nameInput.value?.focus())
}

onMounted(loadProjects)
</script>

<style scoped>
/* ── Design Tokens ── */
:root {
  --bg: #0c0f14;
  --bg-raised: #141821;
  --bg-card: #181d27;
  --bg-hover: #1e2433;
  --surface: #232a38;
  --border: #2a3244;
  --border-light: #1e2636;
  --text: #e8eaf0;
  --text-secondary: #8b93a6;
  --text-muted: #5a6378;
  --accent: #d4a053;
  --accent-dim: rgba(212, 160, 83, 0.15);
  --accent-glow: rgba(212, 160, 83, 0.3);
  --danger: #e05252;
  --type-ad: #5ea8d4;
  --type-usp: #a87ed4;
  --radius: 8px;
  --font: 'IBM Plex Sans', 'Noto Sans KR', system-ui, sans-serif;
  --mono: 'IBM Plex Mono', 'JetBrains Mono', monospace;
}

* { box-sizing: border-box; }
.adsim-home {
  min-height: 100vh;
  background: var(--bg);
  color: var(--text);
  font-family: var(--font);
  -webkit-font-smoothing: antialiased;
}

/* ── Topbar ── */
.topbar {
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 32px;
  border-bottom: 1px solid var(--border-light);
  background: rgba(12, 15, 20, 0.85);
  backdrop-filter: blur(12px);
  position: sticky;
  top: 0;
  z-index: 50;
}
.topbar-left { display: flex; align-items: center; gap: 12px; }
.logo { display: flex; align-items: center; gap: 8px; cursor: pointer; transition: opacity 0.2s; }
.logo:hover { opacity: 0.8; }
.logo-mark { color: var(--accent); font-size: 1rem; }
.logo-text { font-family: var(--mono); font-weight: 600; font-size: 0.95rem; letter-spacing: 0.5px; }
.logo-divider { width: 1px; height: 18px; background: var(--border); }
.logo-sub { font-size: 0.78rem; color: var(--text-muted); }
.status-pill { font-size: 0.72rem; color: var(--text-secondary); display: flex; align-items: center; gap: 6px; font-family: var(--mono); }
.pulse { width: 6px; height: 6px; border-radius: 50%; background: #4ade80; animation: pulse-glow 2s infinite; }
@keyframes pulse-glow { 0%, 100% { box-shadow: 0 0 0 0 rgba(74,222,128,0.4); } 50% { box-shadow: 0 0 0 4px rgba(74,222,128,0); } }

/* ── Hero ── */
.hero {
  padding: 72px 32px 56px;
  display: flex;
  align-items: center;
  gap: 40px;
  max-width: 1200px;
  margin: 0 auto;
  position: relative;
}
.hero-inner { flex: 1; }
.hero-label {
  font-family: var(--mono);
  font-size: 0.72rem;
  color: var(--accent);
  text-transform: uppercase;
  letter-spacing: 2px;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.hero-label::before { content: ''; width: 20px; height: 1px; background: var(--accent); }
.hero-title {
  font-size: 2.4rem;
  font-weight: 600;
  line-height: 1.35;
  margin: 0 0 20px;
  letter-spacing: -0.5px;
}
.accent { color: var(--accent); }
.hero-desc {
  font-size: 1rem;
  line-height: 1.75;
  color: var(--text-secondary);
  max-width: 540px;
  margin-bottom: 32px;
}
.hero-desc em { color: var(--text); font-style: normal; font-weight: 500; }
.cta-btn {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  background: var(--accent);
  color: var(--bg);
  border: none;
  padding: 14px 28px;
  font-family: var(--font);
  font-weight: 600;
  font-size: 0.95rem;
  border-radius: var(--radius);
  cursor: pointer;
  transition: all 0.25s;
}
.cta-btn:hover { background: #e0b060; transform: translateY(-1px); box-shadow: 0 6px 20px var(--accent-glow); }
.cta-btn:active { transform: translateY(0); }

.hero-deco { flex-shrink: 0; }
.deco-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 6px; }
.deco-cell {
  width: 28px; height: 28px;
  border: 1px solid var(--border);
  border-radius: 4px;
  animation: cell-fade 3s infinite ease-in-out;
}
@keyframes cell-fade { 0%, 100% { opacity: 0.15; } 50% { opacity: 0.4; border-color: var(--accent-dim); } }

/* ── Projects ── */
.projects-section { max-width: 1200px; margin: 0 auto; padding: 0 32px 80px; }
.section-header { display: flex; align-items: center; gap: 12px; margin-bottom: 24px; border-top: 1px solid var(--border-light); padding-top: 32px; }
.section-header h2 { font-size: 1.2rem; font-weight: 600; margin: 0; }
.count-badge { font-family: var(--mono); font-size: 0.72rem; color: var(--text-muted); background: var(--surface); padding: 3px 10px; border-radius: 99px; }

.loading-state { display: flex; align-items: center; gap: 12px; padding: 48px 0; color: var(--text-secondary); justify-content: center; }
.spinner { width: 18px; height: 18px; border: 2px solid var(--border); border-top-color: var(--accent); border-radius: 50%; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

.empty-state { text-align: center; padding: 64px 0; color: var(--text-muted); }
.empty-icon { font-size: 2rem; margin-bottom: 12px; opacity: 0.4; }
.empty-hint { font-size: 0.85rem; margin-top: 4px; }

.project-list { display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 16px; }
.project-card {
  background: var(--bg-card);
  border: 1px solid var(--border-light);
  border-radius: var(--radius);
  padding: 24px;
  cursor: pointer;
  transition: all 0.25s;
  position: relative;
  outline: none;
}
.project-card:hover, .project-card:focus-visible { border-color: var(--accent-dim); background: var(--bg-hover); transform: translateY(-2px); box-shadow: 0 8px 24px rgba(0,0,0,0.3); }
.card-top { display: flex; align-items: center; gap: 8px; margin-bottom: 14px; }
.card-type-dot { width: 8px; height: 8px; border-radius: 50%; }
.card-type-dot.ad_reaction { background: var(--type-ad); }
.card-type-dot.usp_test { background: var(--type-usp); }
.card-type-label { font-family: var(--mono); font-size: 0.7rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; }
.card-delete { position: absolute; top: 16px; right: 16px; background: none; border: none; color: var(--text-muted); cursor: pointer; padding: 4px; border-radius: 4px; opacity: 0; transition: all 0.2s; }
.project-card:hover .card-delete { opacity: 1; }
.card-delete:hover { color: var(--danger); background: rgba(224,82,82,0.1); }
.card-name { font-size: 1.1rem; font-weight: 600; margin-bottom: 6px; }
.card-desc { font-size: 0.85rem; color: var(--text-secondary); line-height: 1.5; margin-bottom: 16px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.card-footer { display: flex; justify-content: space-between; align-items: center; }
.card-date { font-family: var(--mono); font-size: 0.72rem; color: var(--text-muted); }
.card-arrow { color: var(--accent); font-size: 1.1rem; opacity: 0; transition: all 0.25s; }
.project-card:hover .card-arrow { opacity: 1; transform: translateX(4px); }

/* ── Modal ── */
.modal-overlay {
  position: fixed; inset: 0;
  background: rgba(0,0,0,0.7);
  backdrop-filter: blur(8px);
  display: flex; align-items: center; justify-content: center;
  z-index: 200;
  padding: 20px;
}
.modal {
  background: #ffffff;
  color: #1a1a2e;
  border: none;
  border-radius: 14px;
  width: 520px;
  max-width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 24px 64px rgba(0,0,0,0.4);
}
.modal-header { display: flex; justify-content: space-between; align-items: center; padding: 28px 28px 0; }
.modal-header h2 { font-size: 1.25rem; font-weight: 700; margin: 0; color: #1a1a2e; }
.modal-close { background: none; border: none; color: #999; cursor: pointer; padding: 4px; border-radius: 4px; }
.modal-close:hover { color: #333; background: #f0f0f0; }
.modal-body { padding: 24px 28px; }
.modal-footer { display: flex; justify-content: flex-end; gap: 10px; padding: 16px 28px 24px; border-top: 1px solid #eee; }

.field { margin-bottom: 20px; position: relative; }
.field label { display: block; font-size: 0.85rem; font-weight: 600; margin-bottom: 8px; color: #444; }
.required { color: #e05252; }
.optional { color: #aaa; font-weight: 400; font-size: 0.8rem; }
.field input, .field textarea {
  width: 100%;
  background: #f8f8fa;
  border: 1.5px solid #ddd;
  color: #1a1a2e;
  padding: 12px 14px;
  font-family: var(--font);
  font-size: 0.9rem;
  border-radius: 8px;
  outline: none;
  transition: border-color 0.2s;
}
.field input::placeholder, .field textarea::placeholder { color: #aaa; }
.field input:focus, .field textarea:focus { border-color: #d4a053; box-shadow: 0 0 0 3px rgba(212,160,83,0.15); }
.field textarea { resize: vertical; min-height: 72px; }
.char-count { position: absolute; right: 10px; bottom: 10px; font-family: var(--mono); font-size: 0.65rem; color: #bbb; }

.type-selector { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.type-option {
  background: #f8f8fa;
  border: 2px solid #e0e0e0;
  border-radius: 10px;
  padding: 16px;
  cursor: pointer;
  text-align: left;
  transition: all 0.2s;
  color: #1a1a2e;
  font-family: var(--font);
}
.type-option:hover { border-color: #bbb; background: #f0f0f5; }
.type-option.active { border-color: #d4a053; background: rgba(212,160,83,0.08); box-shadow: 0 0 0 3px rgba(212,160,83,0.12); }
.type-icon { font-size: 1.4rem; display: block; margin-bottom: 8px; }
.type-label { display: block; font-weight: 600; font-size: 0.88rem; margin-bottom: 4px; color: #1a1a2e; }
.type-help { display: block; font-size: 0.75rem; color: #888; line-height: 1.4; }

.btn-ghost { background: none; border: 1px solid #ddd; color: #666; padding: 10px 20px; border-radius: 8px; cursor: pointer; font-family: var(--font); font-size: 0.88rem; transition: all 0.2s; }
.btn-ghost:hover { border-color: #999; color: #333; }
.btn-primary { background: #1a1a2e; color: #fff; border: none; padding: 10px 24px; border-radius: 8px; font-weight: 600; cursor: pointer; font-family: var(--font); font-size: 0.88rem; transition: all 0.2s; display: flex; align-items: center; gap: 8px; }
.btn-primary:hover:not(:disabled) { background: #d4a053; }
.btn-primary:disabled { opacity: 0.3; cursor: not-allowed; }
.spinner-sm { width: 14px; height: 14px; border: 2px solid rgba(0,0,0,0.2); border-top-color: var(--bg); border-radius: 50%; animation: spin 0.6s linear infinite; }

/* ── Transitions ── */
.modal-enter-active { transition: all 0.25s ease; }
.modal-leave-active { transition: all 0.2s ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
.modal-enter-from .modal, .modal-leave-to .modal { transform: scale(0.95) translateY(10px); }

@media (max-width: 768px) {
  .hero { flex-direction: column; padding: 48px 20px 40px; }
  .hero-title { font-size: 1.7rem; }
  .hero-deco { display: none; }
  .project-list { grid-template-columns: 1fr; }
  .topbar { padding: 0 16px; }
  .projects-section { padding: 0 16px 60px; }
  .type-selector { grid-template-columns: 1fr; }
}
</style>

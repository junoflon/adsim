<template>
  <div class="agent-chat">
    <header class="topbar">
      <div class="topbar-left">
        <div class="logo" @click="$router.push('/adsim')">
          <span class="logo-mark">◆</span>
          <span class="logo-text">AdSim</span>
        </div>
        <span class="breadcrumb-sep">/</span>
        <span class="breadcrumb-link" @click="$router.back()">결과</span>
        <span class="breadcrumb-sep">/</span>
        <span class="breadcrumb-current">{{ agent?.agent_name || '...' }}</span>
      </div>
    </header>

    <div class="content" v-if="!agent">
      <div class="center-state">
        <div class="spinner-lg"></div>
        <p>에이전트 데이터를 불러오는 중...</p>
      </div>
    </div>

    <div class="content" v-else>
      <!-- Agent Profile -->
      <div class="profile-header">
        <div class="avatar" :class="agent.sentiment">
          {{ agent.agent_name?.charAt(0) }}
        </div>
        <div class="profile-info">
          <h1>{{ agent.agent_name }}</h1>
          <div class="profile-meta">
            <span :class="['sentiment-pill', agent.sentiment]">
              {{ sentLabel(agent.sentiment) }}
            </span>
            <span class="score-pill">점수 {{ agent.sentiment_score?.toFixed(1) }}</span>
          </div>
        </div>
      </div>

      <!-- Persona -->
      <div class="info-card">
        <div class="info-label">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
          페르소나
        </div>
        <div class="info-body">
          <template v-if="typeof agent.agent_persona === 'object'">
            <div class="persona-detail" v-for="(val, key) in agent.agent_persona" :key="key">
              <span class="pd-key">{{ key }}</span>
              <span class="pd-val">{{ Array.isArray(val) ? val.join(', ') : val }}</span>
            </div>
          </template>
          <p v-else>{{ agent.agent_persona }}</p>
        </div>
      </div>

      <!-- Key Reactions -->
      <div class="info-card" v-if="agent.key_reactions?.length">
        <div class="info-label">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>
          핵심 반응
        </div>
        <div class="reaction-tags">
          <span v-for="(r, i) in agent.key_reactions" :key="i" class="rtag">{{ r }}</span>
        </div>
      </div>

      <!-- Conversation Log -->
      <div class="chat-section">
        <h2>
          대화 로그
          <span class="chat-count" v-if="agent.conversation_log?.length">{{ agent.conversation_log.length }}개 메시지</span>
        </h2>

        <div v-if="!agent.conversation_log?.length" class="empty-chat">
          <p>대화 로그가 없습니다</p>
          <p class="empty-hint">LLM 연동 후 시뮬레이션을 실행하면 대화가 기록됩니다</p>
        </div>

        <div v-else class="chat-timeline">
          <div v-for="(msg, i) in agent.conversation_log" :key="i" :class="['msg', msg.role]">
            <div class="msg-avatar">
              <span v-if="msg.role === 'user'">Q</span>
              <span v-else>{{ agent.agent_name?.charAt(0) }}</span>
            </div>
            <div class="msg-body">
              <div class="msg-meta">
                <span class="msg-sender">{{ msg.role === 'user' ? '질문' : agent.agent_name }}</span>
                <span v-if="msg.round" class="msg-round">라운드 {{ msg.round }}</span>
              </div>
              <div class="msg-text">{{ msg.content }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getResponseDetail } from '../api/adsim.js'

const route = useRoute()
const agent = ref(null)
const sentLabel = (s) => ({ positive: '긍정', negative: '부정', neutral: '중립' }[s] || s)

onMounted(async () => {
  try {
    const res = await getResponseDetail(route.params.simulationId, route.params.agentId)
    agent.value = res.data.data
  } catch (e) { console.error(e) }
})
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
.agent-chat { min-height: 100vh; background: var(--bg); color: var(--text); font-family: var(--font); -webkit-font-smoothing: antialiased; }
.topbar { height: 56px; display: flex; align-items: center; padding: 0 32px; border-bottom: 1px solid var(--border-light); background: rgba(12,15,20,0.85); backdrop-filter: blur(12px); position: sticky; top: 0; z-index: 50; }
.topbar-left { display: flex; align-items: center; gap: 10px; }
.logo { display: flex; align-items: center; gap: 8px; cursor: pointer; }
.logo-mark { color: var(--accent); }
.logo-text { font-family: var(--mono); font-weight: 600; font-size: 0.95rem; }
.breadcrumb-sep { color: var(--text-muted); }
.breadcrumb-link { font-size: 0.85rem; color: var(--text-secondary); cursor: pointer; }
.breadcrumb-link:hover { color: var(--text); }
.breadcrumb-current { font-size: 0.85rem; color: var(--text-secondary); }
.content { max-width: 760px; margin: 0 auto; padding: 36px 24px 80px; }

.center-state { text-align: center; padding: 80px 0; color: var(--text-secondary); }
.spinner-lg { width: 28px; height: 28px; border: 3px solid var(--border); border-top-color: var(--accent); border-radius: 50%; animation: spin 0.8s linear infinite; margin: 0 auto 16px; }
@keyframes spin { to { transform: rotate(360deg); } }

/* Profile Header */
.profile-header { display: flex; align-items: center; gap: 18px; margin-bottom: 28px; }
.avatar { width: 56px; height: 56px; border-radius: 14px; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 1.3rem; }
.avatar.positive { background: rgba(74,222,128,0.15); color: var(--positive); }
.avatar.negative { background: rgba(239,68,68,0.15); color: var(--negative); }
.avatar.neutral { background: rgba(148,163,184,0.15); color: var(--neutral-c); }
.profile-info h1 { font-size: 1.4rem; font-weight: 600; margin: 0 0 6px; }
.profile-meta { display: flex; gap: 8px; }
.sentiment-pill { font-family: var(--mono); font-size: 0.72rem; padding: 3px 10px; border-radius: 99px; font-weight: 600; }
.sentiment-pill.positive { background: rgba(74,222,128,0.15); color: var(--positive); }
.sentiment-pill.negative { background: rgba(239,68,68,0.15); color: var(--negative); }
.sentiment-pill.neutral { background: rgba(148,163,184,0.15); color: var(--neutral-c); }
.score-pill { font-family: var(--mono); font-size: 0.72rem; padding: 3px 10px; border-radius: 99px; background: var(--surface); color: var(--text-secondary); }

/* Info Cards */
.info-card { background: var(--bg-card); border: 1px solid var(--border-light); border-radius: var(--radius); padding: 18px 20px; margin-bottom: 14px; }
.info-label { display: flex; align-items: center; gap: 8px; font-size: 0.78rem; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; font-family: var(--mono); margin-bottom: 12px; }
.info-label svg { color: var(--text-muted); }
.info-body p { font-size: 0.88rem; color: var(--text-secondary); line-height: 1.6; margin: 0; white-space: pre-wrap; }
.persona-detail { display: flex; gap: 12px; padding: 6px 0; border-bottom: 1px solid var(--border-light); font-size: 0.85rem; }
.persona-detail:last-child { border: none; }
.pd-key { font-family: var(--mono); font-size: 0.75rem; color: var(--text-muted); min-width: 100px; flex-shrink: 0; }
.pd-val { color: var(--text-secondary); }

.reaction-tags { display: flex; flex-wrap: wrap; gap: 6px; }
.rtag { font-size: 0.8rem; padding: 5px 12px; background: var(--accent-dim); border: 1px solid rgba(212,160,83,0.2); border-radius: 99px; color: var(--accent); }

/* Chat */
.chat-section { margin-top: 28px; }
.chat-section h2 { font-size: 1.1rem; font-weight: 600; margin: 0 0 20px; display: flex; align-items: center; gap: 10px; }
.chat-count { font-family: var(--mono); font-size: 0.72rem; color: var(--text-muted); background: var(--surface); padding: 2px 10px; border-radius: 99px; font-weight: 400; }

.empty-chat { text-align: center; padding: 48px; background: var(--bg-card); border: 1px solid var(--border-light); border-radius: var(--radius); color: var(--text-muted); }
.empty-hint { font-size: 0.82rem; margin-top: 4px; }

.chat-timeline { display: flex; flex-direction: column; gap: 2px; }
.msg { display: flex; gap: 12px; padding: 16px; border-radius: var(--radius); transition: background 0.15s; }
.msg:hover { background: var(--bg-card); }
.msg-avatar { width: 32px; height: 32px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-family: var(--mono); font-weight: 600; font-size: 0.75rem; flex-shrink: 0; }
.msg.user .msg-avatar { background: var(--surface); color: var(--text-muted); }
.msg.assistant .msg-avatar { background: var(--accent-dim); color: var(--accent); }
.msg-body { flex: 1; min-width: 0; }
.msg-meta { display: flex; align-items: center; gap: 10px; margin-bottom: 6px; }
.msg-sender { font-size: 0.8rem; font-weight: 600; }
.msg-round { font-family: var(--mono); font-size: 0.65rem; color: var(--text-muted); background: var(--surface); padding: 1px 8px; border-radius: 99px; }
.msg-text { font-size: 0.9rem; line-height: 1.7; color: var(--text-secondary); }
.msg.user .msg-text { color: var(--text-muted); font-style: italic; }

@media (max-width: 768px) {
  .content { padding: 24px 16px 60px; }
  .profile-header { flex-direction: column; align-items: flex-start; }
}
</style>

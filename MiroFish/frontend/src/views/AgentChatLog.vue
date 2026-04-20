<template>
  <div class="page">
    <header class="topbar">
      <div class="bar-left">
        <span class="brand" @click="$router.push('/adsim')">AdSim</span>
        <span class="bar-sep">/</span>
        <span class="bar-link" @click="goBack">결과</span>
        <span class="bar-sep">/</span>
        <span class="bar-crumb">{{ agent?.agent_name || '…' }}</span>
      </div>
      <div class="bar-right">
        <button class="close-btn" @click="goBack" aria-label="닫기">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6L6 18M6 6l12 12"/></svg>
          <span>닫기</span>
        </button>
      </div>
    </header>
    <div class="rule-line"></div>

    <main class="wrap" v-if="!agent">
      <div class="state-center">
        <span class="dot-pulse"></span>
        <p>에이전트 데이터를 불러오는 중…</p>
      </div>
    </main>

    <main class="wrap" v-else>
      <!-- Profile -->
      <header class="profile">
        <div class="p-avatar" :class="agent.sentiment">{{ agent.agent_name?.charAt(0) }}</div>
        <div class="p-info">
          <span class="p-eyebrow">Agent Transcript</span>
          <h1>{{ agent.agent_name }}</h1>
          <div class="p-meta">
            <span :class="['pill', agent.sentiment]">{{ sentLabel(agent.sentiment) }}</span>
            <span class="score">감정 점수 {{ agent.sentiment_score?.toFixed(2) }}</span>
          </div>
        </div>
      </header>

      <!-- Persona -->
      <section class="card">
        <h2 class="card-title">페르소나</h2>
        <dl class="persona-grid" v-if="typeof agent.agent_persona === 'object'">
          <template v-for="(val, key) in prettyPersona" :key="key">
            <dt>{{ personaKeyLabel(key) }}</dt>
            <dd>{{ Array.isArray(val) ? val.join(' · ') : val }}</dd>
          </template>
        </dl>
        <p v-else>{{ agent.agent_persona }}</p>
      </section>

      <!-- Key Reactions -->
      <section class="card" v-if="agent.key_reactions?.length">
        <h2 class="card-title">핵심 반응</h2>
        <div class="reaction-tags">
          <span v-for="(r, i) in agent.key_reactions" :key="i">{{ r }}</span>
        </div>
      </section>

      <!-- Conversation -->
      <section class="chat-section">
        <div class="sec-head">
          <h2>대화 로그</h2>
          <span v-if="agent.conversation_log?.length">{{ agent.conversation_log.length }}개 메시지</span>
        </div>

        <div v-if="!agent.conversation_log?.length" class="empty-chat">
          <p>대화 로그가 없습니다.</p>
        </div>

        <ol v-else class="chat-list">
          <li v-for="(msg, i) in agent.conversation_log" :key="i" :class="['msg', msg.role]">
            <div class="msg-rail">
              <span class="msg-role">{{ msg.role === 'user' ? 'Q' : 'A' }}</span>
              <span v-if="msg.round" class="msg-round">R{{ msg.round }}</span>
            </div>
            <div class="msg-body">
              <div class="msg-who">{{ msg.role === 'user' ? '시뮬레이터 질문' : agent.agent_name }}</div>
              <div class="msg-text">{{ msg.content }}</div>
            </div>
          </li>
        </ol>
      </section>

      <div class="bottom-nav">
        <button class="back-big" @click="goBack">← 결과로 돌아가기</button>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getResponseDetail } from '../api/adsim.js'

const route = useRoute()
const router = useRouter()
const agent = ref(null)

const sentLabel = (s) => ({ positive: '긍정', negative: '부정', neutral: '중립' }[s] || s)

const KEY_LABELS = {
  name: '이름',
  age: '나이',
  gender: '성별',
  occupation: '직업',
  income_level: '소득 수준',
  interests: '관심사',
  personality_traits: '성격',
  shopping_habits: '소비 습관',
  life_context: '생활 맥락',
  decision_style: '결정 스타일',
  speaking_style: '말투',
  agent_id: '에이전트 ID',
}
const KEY_ORDER = [
  'name', 'age', 'gender', 'occupation', 'income_level',
  'interests', 'personality_traits', 'life_context',
  'decision_style', 'speaking_style', 'shopping_habits',
]
const personaKeyLabel = (k) => KEY_LABELS[k] || k
const prettyPersona = computed(() => {
  const p = agent.value?.agent_persona || {}
  const ordered = {}
  for (const k of KEY_ORDER) if (k in p) ordered[k] = p[k]
  for (const k in p) if (!(k in ordered) && k !== 'agent_id') ordered[k] = p[k]
  return ordered
})

const goBack = () => {
  if (window.history.length > 1) router.back()
  else router.push(`/adsim/simulation/${route.params.simulationId}`)
}

onMounted(async () => {
  try {
    agent.value = (await getResponseDetail(route.params.simulationId, route.params.agentId)).data.data
  } catch (e) { console.error(e) }
})
</script>

<style scoped>
.page {
  min-height: 100vh;
  max-width: 1160px;
  margin: 0 auto;
  padding: 0 40px;
}
.topbar { display: flex; justify-content: space-between; align-items: center; padding: 22px 0 18px; }
.bar-left { display: flex; align-items: center; gap: 12px; min-width: 0; }
.brand { font-family: var(--font-display); font-weight: 600; font-size: 20px; cursor: pointer; letter-spacing: -0.01em; }
.bar-sep { color: var(--ink-faint); }
.bar-link { font-size: 14px; color: var(--ink-muted); cursor: pointer; }
.bar-link:hover { color: var(--ink); }
.bar-crumb { font-size: 14px; color: var(--ink-soft); font-weight: 500; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.rule-line { height: 1px; background: var(--ink); }

.close-btn {
  background: none;
  border: 1px solid var(--rule);
  color: var(--ink);
  padding: 8px 14px 8px 12px;
  border-radius: 99px;
  cursor: pointer;
  font-family: var(--font-body);
  font-size: 13px;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s;
}
.close-btn:hover { background: var(--ink); color: var(--paper); border-color: var(--ink); }

.wrap { max-width: 820px; margin: 0 auto; padding: 40px 0 80px; }

.state-center { text-align: center; padding: 80px 0; color: var(--ink-muted); }
.dot-pulse { width: 10px; height: 10px; border-radius: 50%; background: var(--ink); display: inline-block; margin-bottom: 14px; animation: pulse 1.2s infinite; }
@keyframes pulse { 0%,100% { opacity: 0.4; } 50% { opacity: 1; } }

.profile { display: flex; align-items: center; gap: 22px; margin-bottom: 36px; }
.p-avatar {
  width: 72px; height: 72px;
  border-radius: 50%;
  background: var(--paper-sunk);
  color: var(--ink);
  display: flex; align-items: center; justify-content: center;
  font-family: var(--font-display);
  font-weight: 600;
  font-size: 28px;
  border: 1px solid var(--rule);
}
.p-avatar.positive { background: var(--ink); color: var(--paper); border-color: var(--ink); }
.p-avatar.negative { background: var(--paper); color: var(--ink); border: 2px solid var(--ink); }
.p-avatar.neutral { background: var(--paper-sunk); }

.p-info { min-width: 0; }
.p-eyebrow {
  font-family: var(--font-mono);
  font-size: 10px;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--ink-muted);
  display: block;
  margin-bottom: 6px;
}
.p-info h1 {
  font-family: var(--font-display);
  font-weight: 600;
  font-size: 32px;
  letter-spacing: -0.02em;
  margin: 0 0 10px;
}
.p-meta { display: flex; gap: 10px; align-items: center; }
.pill {
  font-family: var(--font-mono);
  font-size: 11px;
  padding: 4px 10px;
  border-radius: 99px;
  border: 1px solid;
  letter-spacing: 0.08em;
}
.pill.positive { background: var(--ink); color: var(--paper); border-color: var(--ink); }
.pill.negative { background: var(--paper); color: var(--ink); border-color: var(--ink); }
.pill.neutral  { background: var(--paper-sunk); color: var(--ink-muted); border-color: var(--rule); }
.score {
  font-family: var(--font-mono);
  font-size: 12px;
  color: var(--ink-muted);
}

.card {
  background: var(--paper-card);
  border: 1px solid var(--rule);
  border-radius: var(--radius-lg);
  padding: 26px;
  margin-bottom: 14px;
}
.card-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--ink-muted);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  margin: 0 0 18px;
  font-family: var(--font-mono);
}

.persona-grid {
  display: grid;
  grid-template-columns: 140px 1fr;
  gap: 10px 20px;
  margin: 0;
}
.persona-grid dt {
  font-size: 12px;
  color: var(--ink-muted);
  font-weight: 500;
  padding: 4px 0;
}
.persona-grid dd {
  margin: 0;
  font-size: 14px;
  color: var(--ink);
  line-height: 1.5;
  padding: 4px 0;
  border-bottom: 1px solid var(--rule-soft);
}
.persona-grid dt:last-of-type + dd,
.persona-grid dd:last-of-type { border-bottom: none; }

.reaction-tags { display: flex; flex-wrap: wrap; gap: 6px; }
.reaction-tags span {
  font-size: 13px;
  padding: 6px 14px;
  background: var(--paper-sunk);
  border: 1px solid var(--rule);
  border-radius: 99px;
  color: var(--ink);
}

.chat-section { margin-top: 36px; }
.sec-head { display: flex; align-items: baseline; justify-content: space-between; margin-bottom: 20px; }
.sec-head h2 {
  font-family: var(--font-display);
  font-weight: 600;
  font-size: 22px;
  margin: 0;
  letter-spacing: -0.01em;
}
.sec-head span { font-family: var(--font-mono); font-size: 12px; color: var(--ink-muted); }

.empty-chat { text-align: center; padding: 48px; background: var(--paper-raised); border: 1px solid var(--rule); border-radius: var(--radius-lg); color: var(--ink-muted); }

.chat-list { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 0; }
.msg {
  display: grid;
  grid-template-columns: 64px 1fr;
  gap: 16px;
  padding: 22px 0;
  border-bottom: 1px solid var(--rule);
}
.msg:last-child { border-bottom: none; }
.msg-rail { display: flex; flex-direction: column; align-items: flex-start; gap: 6px; }
.msg-role {
  width: 32px; height: 32px;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-family: var(--font-mono);
  font-weight: 700;
  font-size: 13px;
  border: 1px solid var(--ink);
}
.msg.user .msg-role { background: var(--paper); color: var(--ink); }
.msg.assistant .msg-role { background: var(--ink); color: var(--paper); }
.msg-round {
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--ink-faint);
  letter-spacing: 0.08em;
}
.msg-who {
  font-size: 12px;
  font-weight: 600;
  color: var(--ink-muted);
  margin-bottom: 6px;
  letter-spacing: 0.02em;
}
.msg.assistant .msg-who { color: var(--ink); }
.msg-text {
  font-size: 15px;
  line-height: 1.75;
  color: var(--ink);
  white-space: pre-wrap;
  word-wrap: break-word;
}
.msg.user .msg-text { color: var(--ink-muted); font-size: 14px; }

.bottom-nav {
  margin-top: 48px;
  padding-top: 24px;
  border-top: 1px solid var(--rule);
  display: flex;
  justify-content: center;
}
.back-big {
  background: var(--ink);
  color: var(--paper);
  border: none;
  padding: 14px 26px;
  border-radius: var(--radius);
  cursor: pointer;
  font-family: var(--font-body);
  font-weight: 500;
  font-size: 14px;
  transition: background 0.2s;
}
.back-big:hover { background: var(--ink-soft); }

@media (max-width: 720px) {
  .page { padding: 0 20px; }
  .wrap { padding: 28px 0 60px; }
  .persona-grid { grid-template-columns: 100px 1fr; }
  .p-info h1 { font-size: 24px; }
  .profile { flex-direction: column; align-items: flex-start; gap: 14px; }
}
</style>

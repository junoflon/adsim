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
                    rows="8"
                    maxlength="20000"></textarea>
          <div class="editor-foot">
            <span class="char-n" :class="{ warn: seedContent.length > 18000 }">
              {{ seedContent.length.toLocaleString() }} / 20,000
            </span>
            <button class="add-btn" :disabled="!canUpload || uploading" @click="handleUploadSeed">
              <span v-if="uploading" class="spin"></span>
              <span v-else>{{ seeds.length > 0 ? '+ 추가 업로드' : '업로드하기' }}</span>
            </button>
          </div>
        </div>

        <!-- 첨부 파일 & 참조 링크 (제품/브랜드 가설만) -->
        <div class="attach-block" v-if="supportsAttachments">
          <div class="attach-row">
            <label class="attach-file">
              <input type="file" accept=".pdf,.hwp,.hwpx,.docx,.txt,.md" @change="onFilePick" />
              <span class="attach-btn">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M17 8l-5-5-5 5M12 3v12"/></svg>
                {{ attachedFile ? attachedFile.name : '파일 첨부 (PDF · HWP · DOCX)' }}
              </span>
              <button v-if="attachedFile" type="button" class="attach-clear" @click.prevent="clearFile">✕</button>
            </label>
          </div>
          <div class="attach-row" v-if="project.type === 'brand_hypothesis'">
            <label class="attach-url">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 13a5 5 0 007.54.54l3-3a5 5 0 00-7.07-7.07l-1.72 1.72M14 11a5 5 0 00-7.54-.54l-3 3a5 5 0 007.07 7.07l1.72-1.72"/></svg>
              <input type="url" v-model="referenceUrl"
                     placeholder="노션 · 구글 독스 · Figma 등 참조 링크 (선택)" />
            </label>
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
          <p class="panel-lede">프리셋을 골라 시작하고, 필요하면 세부 조건을 직접 다듬으세요.</p>
        </div>

        <div class="tabs">
          <button :class="['tab', { on: personaMode === 'preset' }]" @click="personaMode = 'preset'">프리셋 선택</button>
          <button :class="['tab', { on: personaMode === 'custom' }]" @click="personaMode = 'custom'">직접 설정</button>
        </div>

        <!-- Preset mode -->
        <div v-if="personaMode === 'preset'">
          <div class="persona-grid">
            <button v-for="(p, i) in presets" :key="i"
                    :class="['p-card', { on: selectedPreset === i }]"
                    @click="pickPreset(i)"
                    type="button">
              <span class="p-n">{{ String(i + 1).padStart(2, '0') }}</span>
              <h3 class="p-name">{{ p.name }}</h3>
              <span class="p-age">{{ p.age_range }}세 · {{ p.gender }}</span>
              <div class="p-tags">
                <span v-for="(t, ti) in p.interests?.slice(0, 3)" :key="ti">{{ t }}</span>
              </div>
              <p class="p-habit">{{ p.consumption_habits }}</p>
              <span class="p-check" v-if="selectedPreset === i">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg>
              </span>
            </button>
          </div>
          <p class="tab-hint" v-if="selectedPreset !== null">
            프리셋을 선택했어요. 세부 조정이 필요하면 <button class="link-btn" @click="switchToCustom">직접 설정으로 전환</button>
          </p>
        </div>

        <!-- Custom mode -->
        <div v-else class="custom-panel">
          <!-- AI auto-fill -->
          <div class="ai-gen">
            <label class="ai-label">
              <span class="ai-tag">AI</span>
              한 줄로 타겟을 묘사하면 나머지 필드를 자동으로 채워드려요.
            </label>
            <p class="ai-hint">※ 연령대·성별 비율은 아래 설정을 그대로 사용합니다. 같은 프로젝트 내 기존 페르소나와 겹치지 않게 작성됩니다.</p>
            <div class="ai-row">
              <input type="text" v-model="aiDescription"
                     placeholder="예: 편의점에서 음료 자주 사는 2030 직장인"
                     maxlength="200"
                     @keydown.enter.prevent="handleAutoGenerate" />
              <button type="button" class="ai-btn" :disabled="!aiDescription.trim() || aiGenerating" @click="handleAutoGenerate">
                <span v-if="aiGenerating" class="spin"></span>
                <span v-else>자동 작성</span>
              </button>
            </div>
          </div>

          <div class="cfield">
            <label>페르소나 이름</label>
            <input type="text" v-model="customPersona.name" placeholder="예: 3040 퇴근 후 편의점 애용층" maxlength="40" />
          </div>

          <div class="cgrid">
            <div class="cfield">
              <label>연령대</label>
              <div class="range-pair">
                <input type="number" v-model.number="customPersona.ageMin" min="15" max="80" />
                <span>~</span>
                <input type="number" v-model.number="customPersona.ageMax" min="15" max="80" />
                <span class="suffix">세</span>
              </div>
            </div>
            <div class="cfield">
              <label>성별 구성</label>
              <div class="gender-split">
                <div class="split-track">
                  <div class="split-fill f" :style="{ width: customPersona.femaleRatio + '%' }"></div>
                </div>
                <div class="split-nums">
                  <span>여 {{ customPersona.femaleRatio }}%</span>
                  <input type="range" v-model.number="customPersona.femaleRatio" min="0" max="100" step="10" />
                  <span>남 {{ 100 - customPersona.femaleRatio }}%</span>
                </div>
              </div>
            </div>
          </div>

          <div class="cfield">
            <label>관심사 · 라이프스타일</label>
            <div class="chips">
              <button v-for="interest in allInterests" :key="interest" type="button"
                      :class="['chip', { on: customPersona.interests.includes(interest) }]"
                      @click="toggleInterest(interest)">{{ interest }}</button>
            </div>
            <div class="chip-input">
              <input type="text" v-model="newInterest" placeholder="직접 추가 (엔터)" @keydown.enter.prevent="addCustomInterest" />
            </div>
          </div>

          <div class="cfield">
            <label>소비 습관 · 맥락</label>
            <textarea v-model="customPersona.consumption_habits" rows="3"
                      placeholder="예: 편의점 음료를 주 3회 이상 구매. 새로운 맛이나 건강 기능성 제품에 관심이 많고, 가격은 2,000~3,500원을 적정선으로 봄."></textarea>
            <p class="field-hint">구체적일수록 에이전트가 해당 상황을 반영합니다.</p>
          </div>

          <div class="cfield">
            <label>성격 강조 (선택)</label>
            <div class="chips">
              <button v-for="pt in personalityPresets" :key="pt" type="button"
                      :class="['chip', { on: customPersona.personalityTags.includes(pt) }]"
                      @click="togglePersonality(pt)">{{ pt }}</button>
            </div>
          </div>
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
          <button class="next-btn" :disabled="!personaReady" @click="currentStep = 2">
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
            <dd>{{ activePersonaSummary }}</dd>
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

        <!-- Platform selection — 광고 가설에서만 -->
        <div class="platform-card" v-if="supportsPlatform">
          <label class="platform-label">이 광고가 노출될 매체</label>
          <p class="platform-sub">같은 대본도 매체에 따라 반응이 달라집니다. 노출 맥락을 선택하세요.</p>
          <div class="platform-grid">
            <button v-for="p in platforms" :key="p.key" type="button"
                    :class="['plat', { on: selectedPlatform === p.key }]"
                    @click="selectedPlatform = p.key">
              <span class="plat-name">{{ p.name }}</span>
              <span class="plat-sub">{{ p.sub }}</span>
            </button>
          </div>
        </div>

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
import { getProject, listSeeds, createSeed, deleteSeed, getPresetPersonas, createPersona, startSimulation, autoGeneratePersona } from '../api/adsim.js'

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
const selectedPlatform = ref('unspecified')
const platforms = [
  { key: 'meta_feed', name: 'Meta 피드', sub: 'Instagram / Facebook 피드 광고' },
  { key: 'meta_reels', name: 'Meta 릴스', sub: 'Instagram / Facebook 릴스' },
  { key: 'youtube_preroll', name: 'YouTube 프리롤', sub: '영상 재생 전 5초 건너뛰기 광고' },
  { key: 'youtube_inline', name: 'YouTube 중간', sub: '영상 중간 미드롤 광고' },
  { key: 'google_search', name: 'Google 검색', sub: '검색 결과 상단 검색 광고' },
  { key: 'naver_feed', name: '네이버', sub: '네이버 메인 / 쇼핑 / 검색 디스플레이' },
  { key: 'tiktok', name: 'TikTok', sub: 'For You 피드 인피드 광고' },
  { key: 'kakao', name: '카카오톡', sub: '친구탭 / 쇼핑 상단 노출' },
  { key: 'tv_cf', name: 'TV CF', sub: '지상파/케이블 15~30초 CF' },
  { key: 'web_article', name: '기사/블로그', sub: '뉴스/블로그 본문 중간 네이티브' },
  { key: 'offline', name: '오프라인', sub: '옥외/매장 POP/전단지' },
  { key: 'unspecified', name: '매체 미지정', sub: '일반적인 노출 상황' },
]
const currentStep = ref(0)
const uploading = ref(false)
const running = ref(false)
const steps = [
  { label: '시드 자료' },
  { label: '페르소나' },
  { label: '실행' },
]

const personaMode = ref('preset') // 'preset' | 'custom'
const newInterest = ref('')
const aiDescription = ref('')
const aiGenerating = ref(false)
const customPersona = ref({
  name: '',
  ageMin: 25,
  ageMax: 40,
  femaleRatio: 50,
  interests: [],
  consumption_habits: '',
  personalityTags: [],
})
const allInterests = [
  '건강', '다이어트', '운동', '뷰티', '패션', '육아', '커피', '편의점',
  '맛집', '여행', 'SNS', '게임', '독서', '재테크', '자기계발', '반려동물',
  '친환경', '명품', '가성비', '신제품',
]
const personalityPresets = [
  '신중함', '트렌드 민감', '가성비 추구', '프리미엄 선호',
  '의심 많음', '입소문 전파', '충동구매 성향', '브랜드 충성',
]

const canRun = computed(() => {
  if (seeds.value.length === 0) return false
  if (personaMode.value === 'preset') return selectedPreset.value !== null
  return !!customPersona.value.name.trim() && customPersona.value.interests.length > 0
})

const pickPreset = (i) => { selectedPreset.value = i }
const switchToCustom = () => {
  if (selectedPreset.value !== null) {
    const p = presets.value[selectedPreset.value]
    const [mn, mx] = (p.age_range || '25-40').split('-').map(x => parseInt(x) || 30)
    const fMatch = /여성\s*(\d+)/.exec(p.gender || '')
    customPersona.value = {
      name: p.name,
      ageMin: mn, ageMax: mx,
      femaleRatio: fMatch ? parseInt(fMatch[1]) : 50,
      interests: [...(p.interests || [])],
      consumption_habits: p.consumption_habits || '',
      personalityTags: [],
    }
  }
  personaMode.value = 'custom'
}
const toggleInterest = (x) => {
  const arr = customPersona.value.interests
  const idx = arr.indexOf(x)
  if (idx >= 0) arr.splice(idx, 1); else arr.push(x)
}
const togglePersonality = (x) => {
  const arr = customPersona.value.personalityTags
  const idx = arr.indexOf(x)
  if (idx >= 0) arr.splice(idx, 1); else arr.push(x)
}
const addCustomInterest = () => {
  const v = newInterest.value.trim()
  if (v && !customPersona.value.interests.includes(v)) customPersona.value.interests.push(v)
  newInterest.value = ''
}
const handleAutoGenerate = async () => {
  const desc = aiDescription.value.trim()
  if (!desc || aiGenerating.value) return
  aiGenerating.value = true
  try {
    const res = await autoGeneratePersona({
      description: desc,
      age_min: customPersona.value.ageMin,
      age_max: customPersona.value.ageMax,
      female_ratio: customPersona.value.femaleRatio,
      project_id: projectId,
    })
    const g = res.data.data
    // 연령/성별은 사용자 값 유지, 나머지만 덮어쓰기
    customPersona.value.name = g.name || customPersona.value.name
    customPersona.value.interests = Array.isArray(g.interests) ? g.interests : customPersona.value.interests
    customPersona.value.consumption_habits = g.consumption_habits || customPersona.value.consumption_habits
    customPersona.value.personalityTags = Array.isArray(g.personality_tags) ? g.personality_tags : customPersona.value.personalityTags
  } catch (e) {
    alert('자동 작성 실패: ' + (e.response?.data?.error || e.message))
  } finally { aiGenerating.value = false }
}
const personaReady = computed(() => {
  if (personaMode.value === 'preset') return selectedPreset.value !== null
  return !!customPersona.value.name.trim() && customPersona.value.interests.length > 0
})
const activePersonaSummary = computed(() => {
  if (personaMode.value === 'preset') return selectedPreset.value !== null ? presets.value[selectedPreset.value]?.name : '미선택'
  if (!customPersona.value.name) return '미선택'
  const c = customPersona.value
  return `${c.name} (${c.ageMin}-${c.ageMax}세 · 여 ${c.femaleRatio}% / 남 ${100 - c.femaleRatio}%)`
})

const ledeText = computed(() => {
  const t = project.value?.type
  if (t === 'brand_hypothesis') return '브랜드 기획서·스토리·비주얼 자료를 올려주세요. 문서를 정성스럽게 읽고 타겟 공감도를 평가합니다.'
  if (t === 'product_hypothesis') return '제품 컨셉·기획서·스펙 문서를 올려주세요. 타겟에게 실제로 필요한 제품인지 검증합니다.'
  if (t === 'usp_test') return 'USP(제품 차별점)를 입력하세요. 여러 개를 비교하려면 따로 업로드하세요.'
  return '광고 대본을 붙여넣으세요. 텍스트가 구체적일수록 현실적인 반응이 나옵니다.'
})
const placeholderText = computed(() => {
  const t = project.value?.type
  if (t === 'brand_hypothesis') return '브랜드 핵심 메시지·스토리·톤앤매너를 간단히 설명하거나, 기획서 파일을 첨부해도 돼요.\n예: "느리지만 진심을 다하는 로컬 카페 브랜드. 원두는 ○○농장 직거래…"'
  if (t === 'product_hypothesis') return '제품 컨셉을 설명하거나 기획서를 첨부하세요.\n예: 3분 만에 집에서 만드는 저당 디저트 밀키트. 냉동 보관 7일, 칼로리 150kcal 이하, 1팩 4,900원…'
  if (t === 'usp_test') return '예: 제로칼로리인데도 진짜 과일 맛이 나는 유일한 음료'
  return '예: [나레이션] 지금까지 이런 맛은 없었다. 제로칼로리인데 진짜 맛있는 …'
})
const seedTypeFor = (t) => {
  if (t === 'brand_hypothesis') return 'brand_concept'
  if (t === 'product_hypothesis') return 'product_concept'
  if (t === 'usp_test') return 'usp_text'
  return 'ad_script'
}
const supportsAttachments = computed(() => {
  const t = project.value?.type
  return t === 'product_hypothesis' || t === 'brand_hypothesis'
})
const supportsPlatform = computed(() => project.value?.type === 'ad_reaction')
const attachedFile = ref(null)
const referenceUrl = ref('')
const onFilePick = (e) => {
  const f = e.target.files?.[0]
  attachedFile.value = f || null
}
const clearFile = () => { attachedFile.value = null }
const canUpload = computed(() => seedContent.value.trim() || attachedFile.value || referenceUrl.value.trim())

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
  if (!canUpload.value || uploading.value) return
  uploading.value = true
  try {
    const seedType = seedTypeFor(project.value.type)
    if (attachedFile.value || referenceUrl.value.trim()) {
      const fd = new FormData()
      fd.append('type', seedType)
      if (seedContent.value.trim()) fd.append('content', seedContent.value)
      if (attachedFile.value) fd.append('file', attachedFile.value)
      if (referenceUrl.value.trim()) fd.append('reference_url', referenceUrl.value.trim())
      await createSeed(projectId, fd)
    } else {
      await createSeed(projectId, { type: seedType, content: seedContent.value })
    }
    seedContent.value = ''
    attachedFile.value = null
    referenceUrl.value = ''
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
    let personaPayload
    if (personaMode.value === 'preset') {
      const preset = presets.value[selectedPreset.value]
      personaPayload = { ...preset, agent_count: agentCount.value, is_preset: true }
    } else {
      const c = customPersona.value
      const habits = c.consumption_habits + (c.personalityTags.length ? ` · 성격 성향: ${c.personalityTags.join(', ')}` : '')
      personaPayload = {
        name: c.name,
        age_range: `${c.ageMin}-${c.ageMax}`,
        gender: `여성 ${c.femaleRatio}%, 남성 ${100 - c.femaleRatio}%`,
        interests: c.interests,
        consumption_habits: habits.trim(),
        agent_count: agentCount.value,
        is_preset: false,
      }
    }
    const personaRes = await createPersona(projectId, personaPayload)
    const simPayload = {
      seed_id: seeds.value[0].seed_id,
      persona_id: personaRes.data.data.persona_id,
      total_rounds: totalRounds.value,
    }
    if (supportsPlatform.value) simPayload.platform = selectedPlatform.value
    const simRes = await startSimulation(projectId, simPayload)
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

/* ─ Attachments block ─ */
.attach-block {
  margin-bottom: 22px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.attach-row { display: flex; }
.attach-file {
  flex: 1;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  position: relative;
}
.attach-file input[type="file"] {
  position: absolute;
  opacity: 0;
  pointer-events: none;
  width: 0.1px;
  height: 0.1px;
}
.attach-btn {
  flex: 1;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 13px 16px;
  border: 1.5px dashed var(--rule);
  border-radius: var(--radius);
  color: var(--ink-muted);
  font-size: 13px;
  font-weight: 500;
  transition: all 0.2s;
  background: var(--paper-raised);
}
.attach-file:hover .attach-btn {
  border-color: var(--ink);
  color: var(--ink);
  background: var(--paper-card);
}
.attach-btn svg { flex-shrink: 0; }
.attach-clear {
  background: none;
  border: 1px solid var(--rule);
  color: var(--ink-muted);
  border-radius: 50%;
  width: 26px; height: 26px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  transition: all 0.15s;
  flex-shrink: 0;
}
.attach-clear:hover { border-color: var(--ink); color: var(--ink); }

.attach-url {
  flex: 1;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 11px 14px;
  border: 1px solid var(--rule);
  border-radius: var(--radius);
  background: var(--paper-raised);
  transition: all 0.2s;
}
.attach-url:focus-within { border-color: var(--ink); background: var(--paper-card); }
.attach-url svg { color: var(--ink-muted); flex-shrink: 0; }
.attach-url input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  font-family: var(--font-body);
  font-size: 13px;
  color: var(--ink);
}
.attach-url input::placeholder { color: var(--ink-faint); }

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

/* ─ Tabs ─ */
.tabs {
  display: flex;
  gap: 0;
  margin-bottom: 22px;
  border-bottom: 1px solid var(--rule);
}
.tab {
  background: none;
  border: none;
  padding: 12px 18px;
  font-family: var(--font-body);
  font-size: 14px;
  font-weight: 500;
  color: var(--ink-muted);
  cursor: pointer;
  border-bottom: 2px solid transparent;
  margin-bottom: -1px;
  transition: color 0.2s, border-color 0.2s;
}
.tab:hover { color: var(--ink); }
.tab.on {
  color: var(--ink);
  border-bottom-color: var(--ink);
}

.tab-hint {
  margin: 16px 0 0;
  font-size: 13px;
  color: var(--ink-muted);
}
.link-btn {
  background: none;
  border: none;
  padding: 0;
  color: var(--ink);
  font-family: inherit;
  font-size: inherit;
  cursor: pointer;
  text-decoration: underline;
  text-underline-offset: 3px;
}
.link-btn:hover { color: var(--accent); }

/* ─ AI auto-generate block ─ */
.ai-gen {
  background: var(--ink);
  color: var(--paper);
  border-radius: var(--radius-lg);
  padding: 22px 24px;
  margin-bottom: 28px;
}
.ai-label {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 6px;
  color: var(--paper);
}
.ai-tag {
  font-family: var(--font-mono);
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.15em;
  padding: 2px 8px;
  border: 1px solid var(--paper);
  border-radius: 99px;
}
.ai-hint {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
  margin: 0 0 14px;
  line-height: 1.5;
}
.ai-row {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 10px;
}
.ai-row input {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: var(--paper);
  padding: 11px 14px;
  font-family: var(--font-body);
  font-size: 14px;
  border-radius: var(--radius);
  outline: none;
  transition: all 0.2s;
}
.ai-row input::placeholder { color: rgba(255, 255, 255, 0.4); }
.ai-row input:focus {
  background: rgba(255, 255, 255, 0.15);
  border-color: var(--paper);
}
.ai-btn {
  background: var(--paper);
  color: var(--ink);
  border: none;
  padding: 11px 20px;
  border-radius: var(--radius);
  font-family: var(--font-body);
  font-weight: 600;
  font-size: 13px;
  cursor: pointer;
  transition: background 0.2s;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}
.ai-btn:hover:not(:disabled) { background: var(--paper-sunk); }
.ai-btn:disabled { opacity: 0.4; cursor: not-allowed; }
.ai-btn .spin {
  border-color: rgba(10, 10, 10, 0.2);
  border-top-color: var(--ink);
}

/* ─ Custom persona panel ─ */
.custom-panel {
  background: var(--paper-card);
  border: 1px solid var(--rule);
  border-radius: var(--radius-lg);
  padding: 28px;
  margin-bottom: 40px;
}
.cgrid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}
.cfield { margin-bottom: 20px; }
.cfield:last-child { margin-bottom: 0; }
.cfield label {
  display: block;
  font-family: var(--font-mono);
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.14em;
  color: var(--ink-muted);
  margin-bottom: 10px;
  font-weight: 500;
}
.cfield input[type="text"], .cfield input[type="number"], .cfield textarea {
  background: var(--paper-raised);
  border: 1px solid var(--rule);
  color: var(--ink);
  padding: 10px 14px;
  font-family: var(--font-body);
  font-size: 14px;
  border-radius: var(--radius);
  outline: none;
  transition: border-color 0.2s;
  width: 100%;
}
.cfield input:focus, .cfield textarea:focus {
  border-color: var(--ink);
  background: var(--paper-card);
}
.cfield input::placeholder, .cfield textarea::placeholder { color: var(--ink-faint); }
.cfield textarea { min-height: 72px; line-height: 1.6; resize: vertical; }
.field-hint { font-size: 12px; color: var(--ink-muted); margin: 8px 0 0; }

.range-pair {
  display: flex;
  align-items: center;
  gap: 10px;
}
.range-pair input[type="number"] { width: 80px; text-align: center; }
.range-pair span { color: var(--ink-muted); font-size: 14px; }
.range-pair .suffix { font-size: 13px; color: var(--ink-faint); margin-left: 2px; }

.gender-split { margin-top: 4px; }
.split-track {
  height: 6px;
  background: var(--paper-sunk);
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 10px;
  border: 1px solid var(--rule);
}
.split-fill { height: 100%; background: var(--ink); transition: width 0.3s; }
.split-nums { display: grid; grid-template-columns: 70px 1fr 70px; gap: 10px; align-items: center; font-size: 12px; color: var(--ink-soft); font-family: var(--font-mono); }
.split-nums input[type="range"] { appearance: none; height: 2px; background: var(--rule); border-radius: 1px; outline: none; }
.split-nums input[type="range"]::-webkit-slider-thumb { appearance: none; width: 16px; height: 16px; border-radius: 50%; background: var(--ink); border: 2px solid var(--paper-card); box-shadow: 0 0 0 1px var(--ink); cursor: pointer; }

.chips { display: flex; flex-wrap: wrap; gap: 6px; }
.chip {
  background: var(--paper-raised);
  border: 1px solid var(--rule);
  color: var(--ink-soft);
  padding: 7px 13px;
  border-radius: 99px;
  font-family: var(--font-body);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.15s;
}
.chip:hover { border-color: var(--ink-muted); color: var(--ink); }
.chip.on {
  background: var(--ink);
  border-color: var(--ink);
  color: var(--paper);
}
.chip-input { margin-top: 10px; }
.chip-input input {
  width: 100%;
  background: transparent;
  border: none;
  border-bottom: 1px dashed var(--rule);
  padding: 6px 2px;
  font-family: var(--font-body);
  font-size: 13px;
  color: var(--ink);
  outline: none;
}
.chip-input input:focus { border-bottom-color: var(--ink); }

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

/* ─ Platform picker ─ */
.platform-card {
  background: var(--paper-card);
  border: 1px solid var(--rule);
  border-radius: var(--radius-lg);
  padding: 24px 26px;
  margin-bottom: 22px;
}
.platform-label {
  display: block;
  font-weight: 600;
  font-size: 15px;
  color: var(--ink);
  margin-bottom: 6px;
}
.platform-sub {
  font-size: 13px;
  color: var(--ink-muted);
  margin: 0 0 18px;
  line-height: 1.5;
}
.platform-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 8px;
}
.plat {
  background: var(--paper-raised);
  border: 1px solid var(--rule);
  border-radius: var(--radius);
  padding: 12px 14px;
  cursor: pointer;
  text-align: left;
  font-family: var(--font-body);
  color: var(--ink);
  transition: all 0.15s;
}
.plat:hover { border-color: var(--ink-muted); }
.plat.on {
  background: var(--ink);
  border-color: var(--ink);
  color: var(--paper);
}
.plat-name {
  display: block;
  font-weight: 600;
  font-size: 13px;
  margin-bottom: 2px;
}
.plat-sub {
  display: block;
  font-size: 11px;
  color: var(--ink-muted);
  line-height: 1.4;
}
.plat.on .plat-sub { color: rgba(255,255,255,0.6); }

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

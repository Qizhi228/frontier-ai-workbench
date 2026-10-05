<script setup>
import { computed, onMounted, ref } from 'vue'

const apiBase = import.meta.env.VITE_API_BASE || '/api'
const goal = ref('')
const scheduleTime = ref('09:00')
const tasks = ref([])
const selectedTask = ref(null)
const report = ref(null)
const running = ref(false)
const error = ref('')

const selectedSources = computed(() => report.value?.sources || [])

async function request(path, options = {}) {
  const response = await fetch(`${apiBase}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!response.ok) throw new Error(await response.text())
  return response.json()
}

async function loadTasks() {
  tasks.value = await request('/tasks')
  if (tasks.value.length && !selectedTask.value) selectTask(tasks.value[0])
}

async function createAndRun() {
  if (!goal.value.trim() || running.value) return
  running.value = true
  error.value = ''
  try {
    const task = await request('/tasks', { method: 'POST', body: JSON.stringify({ goal: goal.value, schedule_time: scheduleTime.value }) })
    selectedTask.value = task
    await runTask(task.id)
    goal.value = ''
  } catch (err) {
    error.value = err.message
  } finally {
    running.value = false
  }
}

async function runTask(taskId) {
  running.value = true
  error.value = ''
  try {
    const result = await request(`/tasks/${taskId}/run`, { method: 'POST' })
    report.value = { markdown: result.report, sources: [] }
    await loadTasks()
    selectedTask.value = tasks.value.find((item) => item.id === taskId) || selectedTask.value
    const saved = await request(`/tasks/${taskId}/report`)
    report.value = saved
  } catch (err) {
    error.value = err.message
  } finally {
    running.value = false
  }
}

async function selectTask(task) {
  selectedTask.value = task
  report.value = null
  if (task.status === 'completed') {
    try { report.value = await request(`/tasks/${task.id}/report`) } catch (err) { error.value = err.message }
  }
}

onMounted(loadTasks)
</script>

<template>
  <main class="app-shell">
    <header class="topbar">
      <div class="brand"><span class="brand-mark">✦</span><div><strong>Frontier AI Workbench</strong><small>前沿 AI 技术研究工作台</small></div></div>
      <div class="top-status"><span class="pulse"></span> Mock mode <span class="divider">/</span> Single-user workspace</div>
    </header>

    <section class="hero">
      <div><p class="kicker">RESEARCH · CITE · REMEMBER</p><h1>把前沿技术变成<br /><em>下一步可以执行的判断。</em></h1><p class="hero-copy">输入一个主题，工作台会收集来源、提取变化、生成简报，并保存到你的个人知识库。</p></div>
      <div class="hero-stat"><span>01</span><strong>Reliable sources</strong><p>官方博客、文档、GitHub 与技术论文优先。</p></div>
    </section>

    <section class="workspace-grid">
      <aside class="panel task-panel">
        <div class="panel-title"><span>任务</span><span class="count">{{ tasks.length }}</span></div>
        <div class="new-task">
          <textarea v-model="goal" placeholder="研究一个主题，例如：AI Agent 工具调用趋势"></textarea>
          <div class="task-options"><label>每日 <input v-model="scheduleTime" type="time" /></label><button :disabled="running || !goal.trim()" @click="createAndRun">{{ running ? '执行中...' : '立即研究' }}</button></div>
        </div>
        <div class="task-list">
          <button v-for="task in tasks" :key="task.id" class="task-item" :class="{ active: selectedTask?.id === task.id }" @click="selectTask(task)">
            <span class="task-dot" :class="task.status"></span><span class="task-text">{{ task.goal }}</span><span class="task-status">{{ task.status }}</span>
          </button>
          <p v-if="!tasks.length" class="empty">还没有研究任务。先输入一个主题。</p>
        </div>
      </aside>

      <section class="panel report-panel">
        <div class="panel-title"><span>研究结果</span><span v-if="selectedTask" class="task-chip">{{ selectedTask.status }}</span></div>
        <div v-if="error" class="error-box">{{ error }}</div>
        <div v-if="!report" class="empty-state"><div class="empty-icon">✧</div><h2>等待一个值得研究的问题</h2><p>从左侧提交主题。第一版使用 Mock 来源和模型，不需要 API Key。</p></div>
        <article v-else class="report-content"><div class="report-meta">GENERATED REPORT <span>{{ selectedTask?.goal }}</span></div><pre>{{ report.markdown }}</pre></article>
      </section>

      <aside class="panel source-panel">
        <div class="panel-title"><span>来源与边界</span><span class="source-count">{{ selectedSources.length }} sources</span></div>
        <div v-if="selectedSources.length" class="source-list"><a v-for="source in selectedSources" :key="source.url" :href="source.url" target="_blank" rel="noreferrer" class="source-card"><span class="source-type">SOURCE</span><strong>{{ source.title }}</strong><small>{{ source.published_at }}</small><span class="source-arrow">↗</span></a></div>
        <div v-else class="source-empty"><p>报告来源会显示在这里。</p><p>高风险动作（修改代码、删除、发送、部署）默认需要审批。</p></div>
      </aside>
    </section>

    <footer><span>Frontier AI Workbench · 0.1.0</span><span>Research before execution.</span></footer>
  </main>
</template>

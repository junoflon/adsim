import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Process from '../views/MainView.vue'
import SimulationView from '../views/SimulationView.vue'
import SimulationRunView from '../views/SimulationRunView.vue'
import ReportView from '../views/ReportView.vue'
import InteractionView from '../views/InteractionView.vue'
import AdSimHome from '../views/AdSimHome.vue'
import AdSimProject from '../views/AdSimProject.vue'
import AdSimResult from '../views/AdSimResult.vue'
import AgentChatLog from '../views/AgentChatLog.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/process/:projectId',
    name: 'Process',
    component: Process,
    props: true
  },
  {
    path: '/simulation/:simulationId',
    name: 'Simulation',
    component: SimulationView,
    props: true
  },
  {
    path: '/simulation/:simulationId/start',
    name: 'SimulationRun',
    component: SimulationRunView,
    props: true
  },
  {
    path: '/report/:reportId',
    name: 'Report',
    component: ReportView,
    props: true
  },
  {
    path: '/interaction/:reportId',
    name: 'Interaction',
    component: InteractionView,
    props: true
  },
  {
    path: '/adsim',
    name: 'AdSimHome',
    component: AdSimHome
  },
  {
    path: '/adsim/project/:projectId',
    name: 'AdSimProject',
    component: AdSimProject,
    props: true
  },
  {
    path: '/adsim/simulation/:simulationId',
    name: 'AdSimResult',
    component: AdSimResult,
    props: true
  },
  {
    path: '/adsim/simulation/:simulationId/agent/:agentId',
    name: 'AgentChatLog',
    component: AgentChatLog,
    props: true
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router

import axios from 'axios'

const API_BASE = '/api/adsim'

const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' }
})

// Projects
export const createProject = (data) => api.post('/projects', data)
export const listProjects = () => api.get('/projects')
export const getProject = (id) => api.get(`/projects/${id}`)
export const deleteProject = (id) => api.delete(`/projects/${id}`)

// Seeds
export const createSeed = (projectId, data) => {
  if (data instanceof FormData) {
    return axios.post(`${API_BASE}/projects/${projectId}/seeds`, data, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  }
  return api.post(`/projects/${projectId}/seeds`, data)
}
export const listSeeds = (projectId) => api.get(`/projects/${projectId}/seeds`)
export const deleteSeed = (projectId, seedId) => api.delete(`/projects/${projectId}/seeds/${seedId}`)

// Personas
export const getPresetPersonas = () => api.get('/personas/presets')
export const createPersona = (projectId, data) => api.post(`/projects/${projectId}/personas`, data)
export const listPersonas = (projectId) => api.get(`/projects/${projectId}/personas`)
export const deletePersona = (projectId, personaId) => api.delete(`/projects/${projectId}/personas/${personaId}`)

// Simulations
export const startSimulation = (projectId, data) => api.post(`/projects/${projectId}/simulations`, data)
export const getSimulation = (id) => api.get(`/simulations/${id}`)
export const getSimulationProgress = (id) => api.get(`/simulations/${id}/progress`)
export const cancelSimulation = (id) => api.patch(`/simulations/${id}/cancel`)

// Results
export const getReport = (simId) => api.get(`/simulations/${simId}/report`)
export const listResponses = (simId) => api.get(`/simulations/${simId}/responses`)
export const getResponseDetail = (simId, respId) => api.get(`/simulations/${simId}/responses/${respId}`)
export const listRounds = (simId) => api.get(`/simulations/${simId}/rounds`)

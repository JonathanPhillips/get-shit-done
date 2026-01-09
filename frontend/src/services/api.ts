import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Create axios instance
const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// API service object
export const api = {
  health: {
    check: async () => {
      const { data } = await apiClient.get('/health')
      return data
    },
    detailed: async () => {
      const { data } = await apiClient.get('/health/detailed')
      return data
    },
  },

  tasks: {
    list: async (params?: { status?: string; skip?: number; limit?: number }) => {
      const { data } = await apiClient.get('/api/tasks', { params })
      return data
    },
    get: async (id: number) => {
      const { data } = await apiClient.get(`/api/tasks/${id}`)
      return data
    },
    create: async (task: any) => {
      const { data } = await apiClient.post('/api/tasks', task)
      return data
    },
    update: async (id: number, task: any) => {
      const { data } = await apiClient.patch(`/api/tasks/${id}`, task)
      return data
    },
    delete: async (id: number) => {
      await apiClient.delete(`/api/tasks/${id}`)
    },
    complete: async (id: number) => {
      const { data } = await apiClient.post(`/api/tasks/${id}/complete`)
      return data
    },
    incrementPomodoro: async (id: number) => {
      const { data } = await apiClient.post(`/api/tasks/${id}/increment-pomodoro`)
      return data
    },
  },

  pomodoro: {
    sessions: {
      list: async (params?: { status?: string; task_id?: number; skip?: number; limit?: number }) => {
        const { data } = await apiClient.get('/api/pomodoro/sessions', { params })
        return data
      },
      get: async (id: number) => {
        const { data } = await apiClient.get(`/api/pomodoro/sessions/${id}`)
        return data
      },
      start: async (session: any) => {
        const { data } = await apiClient.post('/api/pomodoro/sessions', session)
        return data
      },
      update: async (id: number, session: any) => {
        const { data } = await apiClient.patch(`/api/pomodoro/sessions/${id}`, session)
        return data
      },
      complete: async (id: number) => {
        const { data } = await apiClient.post(`/api/pomodoro/sessions/${id}/complete`)
        return data
      },
      interrupt: async (id: number) => {
        const { data } = await apiClient.post(`/api/pomodoro/sessions/${id}/interrupt`)
        return data
      },
    },
    getActive: async () => {
      const { data } = await apiClient.get('/api/pomodoro/active')
      return data
    },
    stats: async () => {
      const { data } = await apiClient.get('/api/pomodoro/stats')
      return data
    },
  },
}

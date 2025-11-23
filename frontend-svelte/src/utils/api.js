import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const apiService = {
  async getStatus() {
    const response = await api.get('/api/status')
    return response.data
  },

  async uploadRealImage(file) {
    const formData = new FormData()
    formData.append('file', file)
    const response = await api.post('/api/upload/real', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return response.data
  },

  async uploadFakeImage(file) {
    const formData = new FormData()
    formData.append('file', file)
    const response = await api.post('/api/upload/fake', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return response.data
  },

  async uploadBatch(files, category) {
    const formData = new FormData()
    files.forEach(file => formData.append('files', file))
    formData.append('category', category)
    const response = await api.post('/api/upload/batch', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return response.data
  },

  async listRealImages() {
    const response = await api.get('/api/images/real')
    return response.data
  },

  async listFakeImages() {
    const response = await api.get('/api/images/fake')
    return response.data
  },

  async deleteRealImage(filename) {
    const response = await api.delete(`/api/images/real/${filename}`)
    return response.data
  },

  async deleteFakeImage(filename) {
    const response = await api.delete(`/api/images/fake/${filename}`)
    return response.data
  },

  async trainDetector() {
    const response = await api.post('/api/train')
    return response.data
  },

  async predictImage(file) {
    const formData = new FormData()
    formData.append('file', file)
    const response = await api.post('/api/predict', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return response.data
  },

  async predictBatch(files) {
    const formData = new FormData()
    files.forEach(file => formData.append('files', file))
    const response = await api.post('/api/predict/batch', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return response.data
  },

  async getStats() {
    const response = await api.get('/api/stats')
    return response.data
  },

  async getMemoryStats() {
    const response = await api.get('/api/memory')
    return response.data
  },

  async getHistory() {
    const response = await api.get('/api/history')
    return response.data
  },
}

export { api }


import { request } from '@/utils/request.js'

export class PosterService {
  async getPosters(params = {}) {
    return await request.get('/api/posters', { params })
  }

  async getPosterById(id) {
    return await request.get(`/api/posters/${id}`)
  }

  async uploadPoster(formData) {
    return await request.post('/api/posters/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  }

  async likePoster(id) {
    return await request.post(`/api/posters/${id}/like`)
  }

  async getPosterComments(id) {
    return await request.get(`/api/posters/${id}/comments`)
  }
}

export default new PosterService()

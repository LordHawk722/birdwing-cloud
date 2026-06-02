import { request } from '@/utils/request.js'

export class BirdApiService {
  async getBirdList(params = {}) {
    return await request.get('/api/birds', { params })
  }

  async getBirdById(id) {
    return await request.get(`/api/birds/${id}`)
  }

  async searchBirds(keyword) {
    return await request.get('/api/birds/search', { params: { keyword } })
  }

  async identifyBird(imageFile) {
    const formData = new FormData()
    formData.append('image', imageFile)
    return await request.post('/api/birds/identify', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  }

  async getBirdCategories() {
    return await request.get('/api/birds/categories')
  }
}

export default new BirdApiService()

/**
 * 鸟类API服务 - Web版本
 */
import { request } from '@/utils/request.js'
import { API_CONFIG } from '@/config/api.js'

class BirdService {
  async getPosterList(params = {}) {
    const { page = 1, size = 20, type = 'all' } = params
    const response = await request.get(`${API_CONFIG.BIRD_API}/posters`, { params: { page, size, type } })
    return { code: 200, data: response.data, message: '获取成功' }
  }

  async searchPosters(params) {
    const { keyword, page = 1, size = 20 } = params
    if (!keyword || keyword.trim() === '') throw new Error('搜索关键词不能为空')
    const response = await request.get(`${API_CONFIG.BIRD_API}/posters/search`, { params: { keyword: keyword.trim(), page, size } })
    return { code: 200, data: response.data, message: '搜索成功' }
  }

  async getPosterDetail(posterId) {
    if (!posterId) throw new Error('海报ID不能为空')
    const response = await request.get(`${API_CONFIG.BIRD_API}/posters/${posterId}`)
    return { code: 200, data: response.data, message: '获取成功' }
  }

  async likePoster(posterId) {
    if (!posterId) throw new Error('海报ID不能为空')
    const response = await request.post(`${API_CONFIG.BIRD_API}/posters/${posterId}/like`)
    return { code: 200, data: response.data, message: '点赞成功' }
  }

  async unlikePoster(posterId) {
    if (!posterId) throw new Error('海报ID不能为空')
    const response = await request.post(`${API_CONFIG.BIRD_API}/posters/${posterId}/unlike`)
    return { code: 200, data: response.data, message: '取消点赞成功' }
  }

  async getEncyclopediaList(params = {}) {
    const { page = 1, size = 20, category = 'all' } = params
    const response = await request.get(`${API_CONFIG.BIRD_API}/encyclopedia`, { params: { page, size, category } })
    return { code: 200, data: response.data, message: '获取成功' }
  }

  async searchEncyclopedia(params) {
    const { keyword, page = 1, size = 20 } = params
    if (!keyword || keyword.trim() === '') throw new Error('搜索关键词不能为空')
    const response = await request.get(`${API_CONFIG.BIRD_API}/encyclopedia/search`, { params: { keyword: keyword.trim(), page, size } })
    return { code: 200, data: response.data, message: '搜索成功' }
  }

  async getBirdDetail(birdId) {
    if (!birdId) throw new Error('鸟类ID不能为空')
    const response = await request.get(`${API_CONFIG.BIRD_API}/encyclopedia/${birdId}`)
    return { code: 200, data: response.data, message: '获取成功' }
  }

  async getBirdCategories() {
    const response = await request.get(`${API_CONFIG.BIRD_API}/categories`)
    return { code: 200, data: response.data, message: '获取成功' }
  }

  async getRankingList(params = {}) {
    const { type = 'views', period = 'week', limit = 50 } = params
    const response = await request.get(`${API_CONFIG.BIRD_API}/ranking`, { params: { type, period, limit } })
    return { code: 200, data: response.data, message: '获取成功' }
  }

  async uploadBirdPhoto(params) {
    const { imageFile, description = '', location = '', tags = [] } = params
    if (!imageFile) throw new Error('图片不能为空')
    const formData = new FormData()
    formData.append('image', imageFile)
    formData.append('description', description)
    formData.append('location', location)
    formData.append('tags', JSON.stringify(tags))
    const response = await request.post(`${API_CONFIG.BIRD_API}/upload`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    return { code: 200, data: response.data, message: '上传成功' }
  }

  async getEncyclopedia(params = {}) {
    return await request.get('/api/birds/encyclopedia', { params })
  }

  async searchBirds(keyword) {
    return await request.get('/api/birds/search', { params: { keyword } })
  }

  async likeBird(id) {
    return await request.post(`/api/birds/${id}/like`)
  }
}

export default new BirdService()

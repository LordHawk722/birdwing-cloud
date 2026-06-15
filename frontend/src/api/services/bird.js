/**
 * 鸟类服务 — 与后端 /api/birds/* 路由对应
 */
import { request } from '@/utils/request.js'
import { API_ENDPOINTS } from '@/config/api.js'

export class BirdApiService {
  /** 获取鸟类排行榜 → GET /api/birds/rankings */
  async getRankings(topN = 10) {
    return request.get(API_ENDPOINTS.BIRD.RANKINGS, { params: { top_n: topN } })
  }

  /** 搜索鸟类 → GET /api/birds/search */
  async searchBirds(keyword, page = 1, pageSize = 10) {
    return request.get(API_ENDPOINTS.BIRD.SEARCH, {
      params: { keyword, page, page_size: pageSize }
    })
  }

  /** 获取鸟类详情 → GET /api/birds/{id} */
  async getBirdDetail(id) {
    return request.get(API_ENDPOINTS.BIRD.DETAIL.replace('{id}', id))
  }
}

export default new BirdApiService()

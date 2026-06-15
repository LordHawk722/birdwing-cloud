/**
 * @deprecated 此文件已被拆分至 api/services/bird.js、api/services/post.js 等。
 * 保留此文件作为向后兼容的重导出包装。
 */
import BirdApiService from './services/bird.js'
import PostService from './services/post.js'

class BirdService {
  // 鸟类相关 → api/services/bird.js
  async getRankingList(params = {}) {
    return BirdApiService.getRankings(params.limit || 10)
  }
  async searchBirds(keyword) {
    return BirdApiService.searchBirds(keyword)
  }
  async getBirdDetail(birdId) {
    return BirdApiService.getBirdDetail(birdId)
  }

  // 帖子相关 → api/services/post.js
  async getPosterList(params = {}) {
    return PostService.getPostList(params.page || 1, params.size || 20)
  }
  async getPosterDetail(posterId) {
    return PostService.getPostDetail(posterId)
  }
  async likePoster(posterId) {
    return PostService.toggleLike(posterId)
  }
  async unlikePoster(posterId) {
    return PostService.toggleLike(posterId) // 后端是 toggle 模式，再次调用即取消
  }

  // 暂不支持的方法（后端无对应端点）
  async searchPosters() { throw new Error('searchPosters not supported — use GET /api/posts with client-side filtering') }
  async getEncyclopediaList() { return BirdApiService.searchBirds('', 1, 20) }
  async searchEncyclopedia(params) { return BirdApiService.searchBirds(params.keyword, params.page, params.size) }
  async getBirdCategories() { throw new Error('getBirdCategories not supported — backend has no categories endpoint') }
  async uploadBirdPhoto() { throw new Error('uploadBirdPhoto — use UploadService.uploadImage() instead') }
  async getEncyclopedia() { return BirdApiService.searchBirds('', 1, 20) }
  async likeBird() { throw new Error('likeBird not supported') }
}

export default new BirdService()

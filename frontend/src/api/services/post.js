/**
 * 帖子服务 — 与后端 /api/posts/* 路由对应
 */
import { request } from '@/utils/request.js'
import { API_ENDPOINTS } from '@/config/api.js'

export class PostService {
  /** 帖子列表 → GET /api/posts */
  async getPostList(page = 1, pageSize = 10) {
    return request.get(API_ENDPOINTS.POST.LIST, {
      params: { page, page_size: pageSize }
    })
  }

  /** 帖子详情 → GET /api/posts/{id} */
  async getPostDetail(id) {
    return request.get(API_ENDPOINTS.POST.DETAIL.replace('{id}', id))
  }

  /** 创建帖子 → POST /api/posts （需登录） */
  async createPost(data) {
    return request.post(API_ENDPOINTS.POST.CREATE, data)
  }

  /** 更新帖子 → PUT /api/posts/{id} （需登录 + 本人） */
  async updatePost(id, data) {
    return request.put(API_ENDPOINTS.POST.UPDATE.replace('{id}', id), data)
  }

  /** 删除帖子 → DELETE /api/posts/{id} （需登录 + 本人） */
  async deletePost(id) {
    return request.delete(API_ENDPOINTS.POST.DELETE.replace('{id}', id))
  }

  /** 位置统计 → GET /api/posts/locations */
  async getLocations() {
    return request.get(API_ENDPOINTS.POST.LOCATIONS)
  }

  /** 点赞/取消点赞 → POST /api/posts/{id}/like （需登录，toggle 模式） */
  async toggleLike(id) {
    return request.post(API_ENDPOINTS.POST.LIKE.replace('{id}', id))
  }

  /** 评论列表 → GET /api/posts/{id}/comments */
  async getComments(id, page = 1, pageSize = 20) {
    return request.get(API_ENDPOINTS.POST.COMMENTS.replace('{id}', id), {
      params: { page, page_size: pageSize }
    })
  }

  /** 发表评论 → POST /api/posts/{id}/comments （需登录） */
  async createComment(id, content) {
    return request.post(API_ENDPOINTS.POST.CREATE_COMMENT.replace('{id}', id), { content })
  }
}

export default new PostService()

/**
 * 用户服务 — 与后端 /api/users/* 路由对应
 */
import { request } from '@/utils/request.js'
import { API_ENDPOINTS } from '@/config/api.js'

export class UserService {
  /** 注册 → POST /api/users/register */
  async register(username, password) {
    return request.post(API_ENDPOINTS.USER.REGISTER, { username, password })
  }

  /** 登录 → POST /api/users/login */
  async login(username, password) {
    return request.post(API_ENDPOINTS.USER.LOGIN, { username, password })
  }

  /** 获取当前用户信息 → GET /api/users/me */
  async getCurrentUser() {
    return request.get(API_ENDPOINTS.USER.ME)
  }

  /** 更新个人信息 → PUT /api/users/me */
  async updateProfile(data) {
    return request.put(API_ENDPOINTS.USER.ME, data)
  }

  /** 获取指定用户信息 → GET /api/users/{id} */
  async getUserById(userId) {
    return request.get(API_ENDPOINTS.USER.DETAIL.replace('{id}', userId))
  }
}

export default new UserService()

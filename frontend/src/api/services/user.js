import { request } from '@/utils/request.js'
import { introMock } from '../mocks/editIntroMock.js'

export class UserService {
  async getIntro() {
    // 开发环境使用mock数据
    if (import.meta.env.DEV) {
      return introMock.data.intro
    }
    const response = await request.get('/api/user/intro')
    return response.data?.intro || ''
  }

  async updateIntro(intro) {
    const response = await request.put('/api/user/intro', { intro })
    return response.data
  }

  async getUserProfile() {
    const response = await request.get('/api/user/profile')
    return response.data
  }

  async updateUserProfile(profile) {
    const response = await request.put('/api/user/profile', profile)
    return response.data
  }
}

export default new UserService()

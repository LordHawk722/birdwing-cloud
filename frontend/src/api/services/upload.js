/**
 * 上传服务 — 与后端 /api/upload/* 路由对应
 */
import { uploadFile } from '@/utils/request.js'
import { API_ENDPOINTS } from '@/config/api.js'

export class UploadService {
  /** 上传图片 → POST /api/upload/image */
  async uploadImage(file, onProgress) {
    return uploadFile(API_ENDPOINTS.UPLOAD.IMAGE, file, onProgress)
  }
}

export default new UploadService()

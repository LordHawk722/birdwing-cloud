/**
 * 识别服务 — 与后端 /api/recognition/* 路由对应
 */
import { request } from '@/utils/request.js'
import { API_ENDPOINTS } from '@/config/api.js'

export class RecognitionService {
  /** 分析图片（已有 image_url）→ POST /api/recognition/analyze （需登录） */
  async analyzeImage(imageUrl) {
    return request.post(API_ENDPOINTS.RECOGNITION.ANALYZE, { image_url: imageUrl })
  }

  /** 上传并识别 → POST /api/recognition/analyze-with-image （需登录） */
  async analyzeWithImage(file, onProgress) {
    const formData = new FormData()
    formData.append('file', file)
    return request.post(API_ENDPOINTS.RECOGNITION.ANALYZE_WITH_IMAGE, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 30000,
      onUploadProgress: onProgress
        ? (e) => onProgress(Math.round((e.loaded / e.total) * 100))
        : undefined,
    })
  }

  /** 获取识别记录列表 → GET /api/recognition/records （需登录） */
  async getRecords(page = 1, pageSize = 20) {
    return request.get(API_ENDPOINTS.RECOGNITION.RECORDS, {
      params: { page, page_size: pageSize }
    })
  }

  /** 获取识别记录详情 → GET /api/recognition/records/{id} （需登录） */
  async getRecordDetail(id) {
    return request.get(API_ENDPOINTS.RECOGNITION.RECORD_DETAIL.replace('{id}', id))
  }

  /** 保存识别结果 → POST /api/recognition/records （需登录） */
  async saveRecord(imageUrl, results) {
    return request.post(API_ENDPOINTS.RECOGNITION.RECORDS, {
      image_url: imageUrl,
      result: results,
    })
  }
}

export default new RecognitionService()

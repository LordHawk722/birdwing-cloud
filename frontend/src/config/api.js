/**
 * API配置文件 - Web版本
 * 端点路径与后端 FastAPI 路由一致
 */
const ENV = {
  development: {
    BASE_URL: '',
  },
  production: {
    BASE_URL: '',
  }
}

const CURRENT_ENV = import.meta.env.MODE || 'development'

export const API_CONFIG = {
  ...ENV[CURRENT_ENV],
  TIMEOUT: 10000,
  RETRY_COUNT: 3,
  RETRY_DELAY: 1000,
  UPLOAD: {
    MAX_FILE_SIZE: 10,   // 后端限制 10MB
    ALLOWED_IMAGE_TYPES: ['jpg', 'jpeg', 'png', 'webp', 'gif'],
    UPLOAD_TIMEOUT: 30000
  },
  PAGINATION: {
    DEFAULT_PAGE: 1,
    DEFAULT_SIZE: 20,
    MAX_SIZE: 50          // 后端限制最大 50
  },
  HEADERS: {
    'Content-Type': 'application/json',
    'X-Client-Type': 'web',
    'X-Client-Version': '1.0.0'
  }
}

export const STATUS_CODES = {
  SUCCESS: 200,
  CREATED: 201,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  METHOD_NOT_ALLOWED: 405,
  REQUEST_TIMEOUT: 408,
  PAYLOAD_TOO_LARGE: 413,
  UNPROCESSABLE: 422,
  INTERNAL_SERVER_ERROR: 500
}

export const ERROR_MESSAGES = {
  [STATUS_CODES.BAD_REQUEST]: '请求参数错误',
  [STATUS_CODES.UNAUTHORIZED]: '请先登录',
  [STATUS_CODES.FORBIDDEN]: '没有访问权限',
  [STATUS_CODES.NOT_FOUND]: '请求的资源不存在',
  [STATUS_CODES.REQUEST_TIMEOUT]: '请求超时，请稍后重试',
  [STATUS_CODES.PAYLOAD_TOO_LARGE]: '文件过大',
  [STATUS_CODES.UNPROCESSABLE]: '请求数据校验失败',
  [STATUS_CODES.INTERNAL_SERVER_ERROR]: '服务器内部错误',
  NETWORK_ERROR: '网络连接失败，请检查网络设置',
  TIMEOUT_ERROR: '网络超时，请稍后重试',
  UPLOAD_ERROR: '文件上传失败，请重试',
  INVALID_TOKEN: '登录状态已过期，请重新登录',
  UNKNOWN_ERROR: '未知错误，请联系客服'
}

/**
 * API 端点 — 与后端 app/routers/*.py 保持一致
 */
export const API_ENDPOINTS = {
  USER: {
    REGISTER: '/api/users/register',
    LOGIN: '/api/users/login',
    ME: '/api/users/me',          // GET 获取 / PUT 更新
    DETAIL: '/api/users/{id}',    // GET 获取指定用户
  },
  POST: {
    LIST: '/api/posts',                // GET 列表
    DETAIL: '/api/posts/{id}',         // GET 详情
    CREATE: '/api/posts',              // POST 创建
    UPDATE: '/api/posts/{id}',         // PUT 更新
    DELETE: '/api/posts/{id}',         // DELETE 删除
    LIKE: '/api/posts/{id}/like',      // POST 切换点赞
    COMMENTS: '/api/posts/{id}/comments',       // GET 评论列表
    CREATE_COMMENT: '/api/posts/{id}/comments', // POST 发表评论
  },
  BIRD: {
    RANKINGS: '/api/birds/rankings',   // GET 排行榜
    SEARCH: '/api/birds/search',       // GET 搜索
    DETAIL: '/api/birds/{id}',         // GET 详情
  },
  UPLOAD: {
    IMAGE: '/api/upload/image',        // POST 上传图片
  },
  RECOGNITION: {
    ANALYZE: '/api/recognition/analyze',                     // POST AI分析
    ANALYZE_WITH_IMAGE: '/api/recognition/analyze-with-image', // POST 上传并识别
    RECORDS: '/api/recognition/records',                     // GET 列表 / POST 保存
    RECORD_DETAIL: '/api/recognition/records/{id}',          // GET 详情
  },
}

export const STORAGE_KEYS = {
  TOKEN: 'access_token',
  REFRESH_TOKEN: 'refresh_token',
  USER_INFO: 'user_info',
  SETTINGS: 'app_settings',
  SEARCH_HISTORY: 'search_history',
  FAVORITE_BIRDS: 'favorite_birds',
  UPLOAD_DRAFTS: 'upload_drafts',
  CHAT_HISTORY: 'chat_history'
}

export const EVENT_NAMES = {
  LOGIN_SUCCESS: 'loginSuccess',
  LOGOUT: 'logout',
  TOKEN_EXPIRED: 'tokenExpired',
  NETWORK_ERROR: 'networkError',
  UPLOAD_PROGRESS: 'uploadProgress',
  UPLOAD_SUCCESS: 'uploadSuccess',
  UPLOAD_FAILED: 'uploadFailed',
  BIRD_IDENTIFIED: 'birdIdentified'
}

/**
 * 将端点中的 {id} 占位符替换为实际参数值
 */
export function getApiUrl(endpoint, params = {}) {
  let url = endpoint
  Object.keys(params).forEach(key => {
    url = url.replace(`{${key}}`, params[key])
  })
  return url
}

export function getErrorMessage(statusCode, defaultMessage = ERROR_MESSAGES.UNKNOWN_ERROR) {
  return ERROR_MESSAGES[statusCode] || defaultMessage
}

export default API_CONFIG

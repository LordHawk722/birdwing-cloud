/**
 * API配置文件 - Web版本
 */
const ENV = {
  development: {
    BASE_URL: 'http://localhost:8080',
    BIRD_API: 'http://localhost:8080/api/v1/birds',
    USER_API: 'http://localhost:8080/api/v1/users',
    UPLOAD_API: 'http://localhost:8080/api/v1/upload',
    WEBSOCKET_URL: 'ws://localhost:8080/ws'
  },
  production: {
    BASE_URL: 'https://api.birdwing.cloud',
    BIRD_API: 'https://api.birdwing.cloud/api/v1/birds',
    USER_API: 'https://api.birdwing.cloud/api/v1/users',
    UPLOAD_API: 'https://api.birdwing.cloud/api/v1/upload',
    WEBSOCKET_URL: 'wss://api.birdwing.cloud/ws'
  }
}

const CURRENT_ENV = import.meta.env.MODE || 'development'

export const API_CONFIG = {
  ...ENV[CURRENT_ENV],
  TIMEOUT: 10000,
  RETRY_COUNT: 3,
  RETRY_DELAY: 1000,
  UPLOAD: {
    MAX_FILE_SIZE: 50,
    ALLOWED_IMAGE_TYPES: ['jpg', 'jpeg', 'png', 'webp', 'gif'],
    UPLOAD_TIMEOUT: 30000
  },
  PAGINATION: {
    DEFAULT_PAGE: 1,
    DEFAULT_SIZE: 20,
    MAX_SIZE: 100
  },
  API_VERSION: 'v1',
  HEADERS: {
    'Content-Type': 'application/json',
    'X-Client-Type': 'web',
    'X-Client-Version': '1.0.0'
  }
}

export const STATUS_CODES = {
  SUCCESS: 200,
  CREATED: 201,
  NO_CONTENT: 204,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  METHOD_NOT_ALLOWED: 405,
  REQUEST_TIMEOUT: 408,
  CONFLICT: 409,
  PAYLOAD_TOO_LARGE: 413,
  TOO_MANY_REQUESTS: 429,
  INTERNAL_SERVER_ERROR: 500,
  SERVICE_UNAVAILABLE: 503,
  GATEWAY_TIMEOUT: 504
}

export const ERROR_MESSAGES = {
  [STATUS_CODES.BAD_REQUEST]: '请求参数错误',
  [STATUS_CODES.UNAUTHORIZED]: '请先登录',
  [STATUS_CODES.FORBIDDEN]: '没有访问权限',
  [STATUS_CODES.NOT_FOUND]: '请求的资源不存在',
  [STATUS_CODES.REQUEST_TIMEOUT]: '请求超时，请稍后重试',
  [STATUS_CODES.TOO_MANY_REQUESTS]: '请求过于频繁，请稍后重试',
  [STATUS_CODES.INTERNAL_SERVER_ERROR]: '服务器内部错误',
  [STATUS_CODES.SERVICE_UNAVAILABLE]: '服务暂时不可用',
  NETWORK_ERROR: '网络连接失败，请检查网络设置',
  TIMEOUT_ERROR: '网络超时，请稍后重试',
  UPLOAD_ERROR: '文件上传失败，请重试',
  INVALID_TOKEN: '登录状态已过期，请重新登录',
  UNKNOWN_ERROR: '未知错误，请联系客服'
}

export const API_ENDPOINTS = {
  USER: {
    LOGIN: '/auth/login',
    LOGOUT: '/auth/logout',
    REGISTER: '/auth/register',
    PROFILE: '/users/profile',
    UPDATE_PROFILE: '/users/profile',
    CHANGE_PASSWORD: '/users/password',
    FAVORITES: '/users/favorites',
    UPLOADS: '/users/uploads',
    STATISTICS: '/users/statistics'
  },
  BIRD: {
    LIST: '/birds',
    DETAIL: '/birds/{id}',
    SEARCH: '/birds/search',
    CATEGORIES: '/birds/categories',
    ENCYCLOPEDIA: '/birds/encyclopedia',
    IDENTIFY: '/birds/identify',
    NEARBY: '/birds/nearby',
    STATISTICS: '/birds/statistics',
    LIKE: '/birds/{id}/like',
    UNLIKE: '/birds/{id}/unlike'
  },
  POSTER: {
    LIST: '/posters',
    DETAIL: '/posters/{id}',
    SEARCH: '/posters/search',
    UPLOAD: '/posters/upload',
    UPDATE: '/posters/{id}',
    DELETE: '/posters/{id}',
    LIKE: '/posters/{id}/like',
    COMMENTS: '/posters/{id}/comments'
  },
  RANKING: {
    VIEWS: '/ranking/views',
    LIKES: '/ranking/likes',
    UPLOADS: '/ranking/uploads',
    USERS: '/ranking/users'
  },
  UPLOAD: {
    IMAGE: '/upload/image',
    AUDIO: '/upload/audio',
    VIDEO: '/upload/video',
    AVATAR: '/upload/avatar'
  },
  SYSTEM: {
    CONFIG: '/system/config',
    VERSION: '/system/version',
    ANNOUNCEMENTS: '/system/announcements',
    FEEDBACK: '/system/feedback'
  }
}

export const HTTP_METHODS = { GET: 'GET', POST: 'POST', PUT: 'PUT', DELETE: 'DELETE', PATCH: 'PATCH' }
export const CONTENT_TYPES = { JSON: 'application/json', FORM_DATA: 'multipart/form-data', URL_ENCODED: 'application/x-www-form-urlencoded' }

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
  CHAT_MESSAGE: 'chatMessage',
  BIRD_IDENTIFIED: 'birdIdentified'
}

export function getApiUrl(endpoint, params = {}) {
  let url = API_CONFIG.BASE_URL + endpoint
  Object.keys(params).forEach(key => {
    url = url.replace(`{${key}}`, params[key])
  })
  return url
}

export function getUploadUrl(type = 'image') {
  const uploadEndpoints = {
    image: API_ENDPOINTS.UPLOAD.IMAGE,
    audio: API_ENDPOINTS.UPLOAD.AUDIO,
    video: API_ENDPOINTS.UPLOAD.VIDEO,
    avatar: API_ENDPOINTS.UPLOAD.AVATAR
  }
  return getApiUrl(uploadEndpoints[type] || uploadEndpoints.image)
}

export function isSupportedFileType(filename, type = 'image') {
  const extension = filename.toLowerCase().split('.').pop()
  const typeMap = {
    image: API_CONFIG.UPLOAD.ALLOWED_IMAGE_TYPES
  }
  return typeMap[type]?.includes(extension) || false
}

export function isValidFileSize(fileSize) {
  const maxSize = API_CONFIG.UPLOAD.MAX_FILE_SIZE * 1024 * 1024
  return fileSize <= maxSize
}

export function getErrorMessage(statusCode, defaultMessage = ERROR_MESSAGES.UNKNOWN_ERROR) {
  return ERROR_MESSAGES[statusCode] || defaultMessage
}

export default API_CONFIG

/**
 * 阿里云OSS配置文件 - Web版本
 */

const OSS_CONFIG = {
  region: 'oss-cn-shanghai',
  bucket: 'birdfront-oss',
  endpoint: 'https://birdfront-oss.oss-cn-shanghai.aliyuncs.com',

  imageProcess: {
    quality: 80,
    sizes: {
      thumbnail: '150x150',
      small: '300x300',
      medium: '600x600',
      large: '1200x1200',
      banner: '1920x600'
    },
    format: 'webp',
    fallbackFormat: 'jpg'
  },

  cache: {
    maxAge: 86400 * 30,
    enableBrowserCache: true
  },

  security: {
    enableRefererProtection: true,
    allowedReferers: [
      'http://localhost:3000',
      'http://127.0.0.1:3000'
    ]
  },

  environment: {
    current: import.meta.env.MODE || 'development',
    development: {
      enableImageOptimization: false,
      enableCache: false,
      logLevel: 'debug'
    },
    production: {
      enableImageOptimization: true,
      enableCache: true,
      logLevel: 'error'
    }
  }
}

/**
 * 获取OSS图片URL
 * @param {string} filename - OSS上的文件名/路径
 * @param {string} size - 尺寸类型 (icon|small-icon|avatar|medium|large|banner|post|post-thumb|upload-bg|upload-text)
 * @returns {string} 完整的OSS URL
 */
export function getOSSUrl(filename, size = 'icon') {
  if (!filename) return ''

  const cleanFilename = filename.startsWith('/') ? filename.slice(1) : filename

  // 如果已经是完整 URL，直接返回
  if (cleanFilename.startsWith('http://') || cleanFilename.startsWith('https://')) {
    return cleanFilename
  }

  // 后端上传的文件（uploads/ 开头）不是 OSS 资源，直接返回相对路径
  if (cleanFilename.startsWith('uploads/')) {
    return '/' + cleanFilename
  }

  // 前端本地静态资源（static/ 开头）也直接返回相对路径
  if (cleanFilename.startsWith('static/')) {
    return '/' + cleanFilename
  }

  const baseUrl = OSS_CONFIG.endpoint

  const sizeParams = {
    'icon': '?x-oss-process=image/resize,m_lfit,w_48,h_48/quality,q_90',
    'small-icon': '?x-oss-process=image/resize,m_lfit,w_32,h_32/quality,q_90',
    'tiny-icon': '?x-oss-process=image/resize,m_lfit,w_16,h_16/quality,q_90',
    'avatar': '?x-oss-process=image/resize,m_lfit,w_80,h_80/quality,q_90',
    'small': '?x-oss-process=image/resize,m_lfit,w_150,h_150/quality,q_90',
    'medium': '?x-oss-process=image/resize,m_lfit,w_300,h_300/quality,q_85',
    'large': '?x-oss-process=image/resize,m_lfit,w_600,h_600/quality,q_85',
    'banner': '?x-oss-process=image/resize,m_lfit,w_750,h_400/quality,q_85',
    'post': '?x-oss-process=image/resize,m_lfit,w_400,h_600/quality,q_85',
    'post-thumb': '?x-oss-process=image/resize,m_lfit,w_300,h_450/quality,q_80',
    'upload-bg': '?x-oss-process=image/resize,m_lfit,w_300,h_60/quality,q_85',
    'upload-text': '?x-oss-process=image/resize,m_lfit,w_150,h_30/quality,q_90',
    'marker': '?x-oss-process=image/resize,m_lfit,w_40,h_40/quality,q_90/format,webp',
    'bird-image': '?x-oss-process=image/resize,m_lfit,w_600,h_400/quality,q_85'
  }

  const params = sizeParams[size] || sizeParams['icon']
  return `${baseUrl}/${cleanFilename}${params}`
}

export function getOSSConfig() {
  const currentEnv = OSS_CONFIG.environment.current
  const envConfig = OSS_CONFIG.environment[currentEnv] || OSS_CONFIG.environment.development
  return { ...OSS_CONFIG, ...envConfig }
}

export function validateOSSConfig() {
  const config = getOSSConfig()
  const errors = []
  if (!config.bucket || config.bucket === 'your-bucket-name') {
    errors.push('OSS bucket name is not configured')
  }
  if (!config.endpoint) {
    errors.push('OSS endpoint is not configured')
  }
  if (!config.region) {
    errors.push('OSS region is not configured')
  }
  return { isValid: errors.length === 0, errors, config }
}

export default OSS_CONFIG

/**
 * API响应类型定义
 */

/**
 * @typedef {Object} BaseResponse
 * @property {number} code - 状态码
 * @property {string} message - 消息
 * @property {T} data - 数据
 * @template T
 */

/**
 * @typedef {Object} IntroResponse
 * @property {string} intro - 个人介绍
 */

export const ResponseCode = {
  SUCCESS: 200,
  CREATED: 201,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  INTERNAL_ERROR: 500
}

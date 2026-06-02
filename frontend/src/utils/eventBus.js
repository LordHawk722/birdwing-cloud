/**
 * 简易事件总线 - Web版本
 * 替换 uni.$emit / uni.$on / uni.$off
 */

class EventBus {
  constructor() {
    this.events = new Map()
  }

  /**
   * 监听事件
   * @param {string} event - 事件名
   * @param {Function} callback - 回调函数
   */
  on(event, callback) {
    if (!this.events.has(event)) {
      this.events.set(event, [])
    }
    this.events.get(event).push(callback)
  }

  /**
   * 触发事件
   * @param {string} event - 事件名
   * @param {*} data - 事件数据
   */
  emit(event, data) {
    const callbacks = this.events.get(event)
    if (callbacks) {
      callbacks.forEach(cb => {
        try {
          cb(data)
        } catch (error) {
          console.error(`事件 ${event} 处理失败:`, error)
        }
      })
    }
  }

  /**
   * 移除事件监听
   * @param {string} event - 事件名
   * @param {Function} callback - 回调函数，不传则移除所有
   */
  off(event, callback) {
    if (!callback) {
      this.events.delete(event)
    } else {
      const callbacks = this.events.get(event)
      if (callbacks) {
        const index = callbacks.indexOf(callback)
        if (index > -1) callbacks.splice(index, 1)
      }
    }
  }

  /**
   * 监听一次
   * @param {string} event
   * @param {Function} callback
   */
  once(event, callback) {
    const wrapper = (data) => {
      callback(data)
      this.off(event, wrapper)
    }
    this.on(event, wrapper)
  }
}

const eventBus = new EventBus()
export default eventBus

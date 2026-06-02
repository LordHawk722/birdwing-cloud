/**
 * Toast提示工具 - Web版本
 * 替换 uni.showToast / uni.showLoading / uni.hideLoading
 */

let toastTimer = null
let loadingEl = null

/**
 * 显示Toast消息
 * @param {string} title - 消息内容
 * @param {string} icon - 图标类型 (success|error|none|loading)
 * @param {number} duration - 显示时长(ms)
 */
export function showToast(title, icon = 'none', duration = 2000) {
  // 移除之前的toast
  const existing = document.querySelector('.toast-container')
  if (existing) existing.remove()
  if (toastTimer) clearTimeout(toastTimer)

  const container = document.createElement('div')
  container.className = 'toast-container'

  const message = document.createElement('div')
  message.className = 'toast-message'
  if (icon && icon !== 'none') {
    message.classList.add(`toast-icon-${icon}`)
  }
  message.textContent = title

  container.appendChild(message)
  document.body.appendChild(container)

  toastTimer = setTimeout(() => {
    container.remove()
  }, duration)
}

/**
 * 显示加载中
 * @param {string} title - 加载文字
 */
export function showLoading(title = '加载中...') {
  hideLoading()
  const overlay = document.createElement('div')
  overlay.className = 'loading-overlay-global'
  overlay.innerHTML = `
    <div class="loading-content-global">
      <div class="loading-spinner-global"></div>
      <span class="loading-text-global">${title}</span>
    </div>
  `
  document.body.appendChild(overlay)
  loadingEl = overlay
}

/**
 * 隐藏加载中
 */
export function hideLoading() {
  if (loadingEl) {
    loadingEl.remove()
    loadingEl = null
  }
}

/**
 * 显示确认对话框
 * @param {string} title - 标题
 * @param {string} content - 内容
 * @returns {Promise<boolean>} 用户选择结果
 */
export function showModal(title, content) {
  return new Promise((resolve) => {
    const overlay = document.createElement('div')
    overlay.className = 'modal-overlay'

    overlay.innerHTML = `
      <div class="modal-content">
        <div class="modal-title">${title}</div>
        <div class="modal-body">${content}</div>
        <div class="modal-buttons">
          <button class="modal-btn modal-btn-cancel" id="modal-cancel">取消</button>
          <button class="modal-btn modal-btn-confirm" id="modal-confirm">确定</button>
        </div>
      </div>
    `

    document.body.appendChild(overlay)

    overlay.querySelector('#modal-cancel').onclick = () => {
      overlay.remove()
      resolve(false)
    }
    overlay.querySelector('#modal-confirm').onclick = () => {
      overlay.remove()
      resolve(true)
    }
    overlay.addEventListener('click', (e) => {
      if (e.target === overlay) {
        overlay.remove()
        resolve(false)
      }
    })
  })
}

/**
 * 显示可编辑的对话框
 * @param {string} title - 标题
 * @param {string} defaultContent - 默认内容
 * @returns {Promise<{confirm: boolean, content: string}>}
 */
export function showEditableModal(title, defaultContent = '') {
  return new Promise((resolve) => {
    const overlay = document.createElement('div')
    overlay.className = 'modal-overlay'

    overlay.innerHTML = `
      <div class="modal-content">
        <div class="modal-title">${title}</div>
        <textarea id="modal-textarea" style="width:100%;height:80px;border:1px solid #ddd;border-radius:8px;padding:8px;font-size:14px;resize:none;margin-bottom:16px;">${defaultContent}</textarea>
        <div class="modal-buttons">
          <button class="modal-btn modal-btn-cancel" id="modal-cancel">取消</button>
          <button class="modal-btn modal-btn-confirm" id="modal-confirm">确定</button>
        </div>
      </div>
    `

    document.body.appendChild(overlay)

    overlay.querySelector('#modal-cancel').onclick = () => {
      overlay.remove()
      resolve({ confirm: false, content: '' })
    }
    overlay.querySelector('#modal-confirm').onclick = () => {
      const textarea = overlay.querySelector('#modal-textarea')
      const content = textarea.value
      overlay.remove()
      resolve({ confirm: true, content })
    }
  })
}

/**
 * 显示操作菜单
 * @param {string[]} itemList - 菜单项列表
 * @returns {Promise<number>} 选中的索引，取消返回-1
 */
export function showActionSheet(itemList) {
  return new Promise((resolve) => {
    const overlay = document.createElement('div')
    overlay.className = 'modal-overlay'

    const items = itemList.map((item, index) =>
      `<button class="action-sheet-item" data-index="${index}">${item}</button>`
    ).join('')

    overlay.innerHTML = `
      <div class="action-sheet-content">
        <div class="action-sheet-items">${items}</div>
        <button class="action-sheet-cancel">取消</button>
      </div>
    `

    document.body.appendChild(overlay)

    overlay.querySelectorAll('.action-sheet-item').forEach(btn => {
      btn.onclick = () => {
        const index = parseInt(btn.dataset.index)
        overlay.remove()
        resolve(index)
      }
    })
    overlay.querySelector('.action-sheet-cancel').onclick = () => {
      overlay.remove()
      resolve(-1)
    }
    overlay.addEventListener('click', (e) => {
      if (e.target === overlay) {
        overlay.remove()
        resolve(-1)
      }
    })
  })
}

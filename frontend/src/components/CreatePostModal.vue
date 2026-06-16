<template>
  <div v-if="visible" class="modal-overlay" @click.self="cancel">
    <div class="create-post-modal">
      <div class="modal-header">
        <h3>📝 发布动态</h3>
        <button class="modal-close" @click="cancel">×</button>
      </div>
      <div class="modal-body">
        <div class="form-group">
          <label class="form-label">标题 <span class="required">*</span></label>
          <input v-model="form.title" class="input-field" placeholder="给你的动态起个标题..." maxlength="200" />
        </div>
        <div class="form-group">
          <label class="form-label">内容</label>
          <textarea v-model="form.content" class="input-field input-textarea" placeholder="分享你的观鸟故事..." rows="3" maxlength="2000"></textarea>
        </div>
        <div class="form-group">
          <label class="form-label">位置</label>
          <div class="location-input-wrap">
            <input ref="locationInput" v-model="form.location" class="input-field" placeholder="输入位置名称..." autocomplete="off" maxlength="100" @input="onLocationInput" />
            <div v-if="locationSuggestions.length > 0" class="location-dropdown">
              <div v-for="(s, i) in locationSuggestions" :key="i" class="location-item" @mousedown.prevent="selectLocation(s)">
                <span class="loc-name">{{ s.name }}</span>
                <span class="loc-addr">{{ s.address }}</span>
              </div>
            </div>
          </div>
        </div>
        <div class="form-group">
          <label class="form-label">图片</label>
          <div v-if="form.imagePreview" class="image-preview">
            <img :src="form.imagePreview" alt="预览" />
            <button class="remove-image" @click="removeImage">×</button>
          </div>
          <button v-else class="upload-image-btn" @click="pickImage">📷 添加图片</button>
        </div>
        <div v-if="errorMsg" class="error-banner">{{ errorMsg }}</div>
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary" @click="cancel" :disabled="submitting">取消</button>
        <button class="btn btn-primary" @click="submit" :disabled="submitting || !form.title.trim()">
          {{ submitting ? '发布中...' : '发布' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch, nextTick } from 'vue'
import { chooseImages } from '@/utils/helpers.js'
import { showToast } from '@/utils/toast.js'
import PostService from '@/api/services/post.js'
import UploadService from '@/api/services/upload.js'

const BAIDU_MAP_KEY = import.meta.env.VITE_BAIDU_MAP_API_KEY || ''

const props = defineProps({
  visible: { type: Boolean, default: false },
})

const emit = defineEmits(['update:visible', 'created'])

const submitting = ref(false)
const errorMsg = ref('')
const form = reactive({ title: '', content: '', location: '', imagePreview: '', imageFile: null })
const locationInput = ref(null)
const locationSuggestions = ref([])
const locationConfirmed = ref('')
let acInstance = null

// 每次打开时重置表单
watch(() => props.visible, async (v) => {
  if (v) {
    form.title = ''; form.content = ''; form.location = ''
    form.imagePreview = ''; form.imageFile = null
    errorMsg.value = ''
    locationSuggestions.value = []
    locationConfirmed.value = ''
    await loadBaiduMap()
    await nextTick()
    initAutocomplete()
  }
})

function loadBaiduMap() {
  return new Promise((resolve) => {
    if (window.BMap) { resolve(); return }
    const script = document.createElement('script')
    script.src = `https://api.map.baidu.com/api?v=2.0&ak=${BAIDU_MAP_KEY}&callback=onBaiduMapForModal`
    window.onBaiduMapForModal = () => { resolve() }
    document.head.appendChild(script)
  })
}

function initAutocomplete() {
  if (!window.BMap || !locationInput.value) return
  if (acInstance) { acInstance.dispose(); acInstance = null }
  acInstance = new BMap.Autocomplete({ input: locationInput.value, location: '全国' })
  acInstance.addEventListener('onsearchcomplete', () => {
    const r = acInstance.getResults()
    if (r && r.getNumPois) {
      const list = []
      for (let i = 0; i < r.getNumPois(); i++) {
        const poi = r.getPoi(i)
        list.push({ name: poi.title || '', address: poi.address || '' })
      }
      locationSuggestions.value = list
    } else { locationSuggestions.value = [] }
  })
  acInstance.addEventListener('onconfirm', (e) => {
    const val = e.item.value
    const parts = []
    if (val.province) parts.push(val.province)
    if (val.city) parts.push(val.city)
    if (val.district) parts.push(val.district)
    if (val.business) parts.push(val.business)
    if (val.street) parts.push(val.street)
    const selected = parts.join('') || val.business || e.item.value
    form.location = selected
    locationConfirmed.value = selected
    locationSuggestions.value = []
  })
}

function onLocationInput() { locationConfirmed.value = '' }

function selectLocation(s) {
  form.location = s.name
  locationConfirmed.value = s.name
  locationSuggestions.value = []
}

function cancel() {
  if (submitting.value) return
  emit('update:visible', false)
}

async function pickImage() {
  try {
    const result = await chooseImages({ count: 1 })
    if (result.tempFilePaths?.length) {
      form.imagePreview = result.tempFilePaths[0]
      form.imageFile = result.files[0]
    }
  } catch { /* 取消选择 */ }
}

function removeImage() {
  form.imagePreview = ''
  form.imageFile = null
}

async function submit() {
  if (!form.title.trim()) { errorMsg.value = '请输入标题'; return }
  errorMsg.value = ''
  submitting.value = true
  try {
    let images = []
    if (form.imageFile) {
      const uploadRes = await UploadService.uploadImage(form.imageFile)
      const url = uploadRes.data?.data?.url
      if (url) images = [url]
    }
    await PostService.createPost({
      title: form.title.trim(),
      content: form.content.trim(),
      location: form.location.trim(),
      images,
    })
    emit('update:visible', false)
    emit('created')
    showToast('发布成功', 'success')
  } catch (err) {
    errorMsg.value = err?.message || '发布失败，请稍后重试'
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed; inset: 0; z-index: 1000;
  background: rgba(0,0,0,0.4);
  display: flex; align-items: center; justify-content: center;
  padding: 20px;
}
.create-post-modal {
  width: 100%; max-width: 480px; max-height: 90vh;
  background: var(--color-surface); border-radius: var(--radius-xl);
  box-shadow: var(--shadow-xl);
}
.modal-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 20px 24px 0;
}
.modal-header h3 { font-size: 18px; font-weight: 700; color: var(--color-text); }
.modal-close {
  background: none; border: none; font-size: 22px; color: var(--color-text-muted);
  cursor: pointer; padding: 0; line-height: 1;
}
.modal-body { padding: 16px 24px; }
.modal-footer {
  display: flex; justify-content: flex-end; gap: 10px;
  padding: 0 24px 20px;
}

.form-group { margin-bottom: 16px; }
.form-label { display: block; font-size: 13px; font-weight: 600; color: var(--color-text); margin-bottom: 6px; }
.form-label .required { color: #ef4444; }
.input-field {
  width: 100%; padding: 10px 14px;
  border: 1px solid var(--color-border); border-radius: var(--radius-sm);
  font-size: 14px; color: var(--color-text); background: var(--color-bg);
  outline: none; box-sizing: border-box; transition: border-color var(--transition-fast);
}
.input-field:focus { border-color: var(--color-primary); box-shadow: 0 0 0 3px rgba(5,150,105,0.1); }
.input-textarea { resize: vertical; min-height: 80px; }

.error-banner {
  background: #fef2f2; color: #dc2626; padding: 10px 14px;
  border-radius: var(--radius-sm); font-size: 13px;
  border: 1px solid #fecaca;
}

.image-preview { position: relative; display: inline-block; }
.image-preview img {
  width: 120px; height: 120px; object-fit: cover;
  border-radius: var(--radius-sm); border: 1px solid var(--color-border);
}
.remove-image {
  position: absolute; top: -8px; right: -8px;
  width: 24px; height: 24px; border-radius: 50%;
  background: #333; color: #fff; border: none;
  font-size: 14px; cursor: pointer; display: flex; align-items: center; justify-content: center;
}
.upload-image-btn {
  padding: 12px 20px; background: var(--color-bg); color: var(--color-text-secondary);
  border: 2px dashed var(--color-border); border-radius: var(--radius-sm);
  font-size: 14px; cursor: pointer; transition: all 0.2s;
}
.upload-image-btn:hover { border-color: var(--color-primary); color: var(--color-primary); }

/* 位置下拉 */
.location-input-wrap { position: relative; }
.location-dropdown {
  position: absolute; top: 100%; left: 0; right: 0; z-index: 1100;
  background: var(--color-surface); border: 1px solid var(--color-border);
  border-radius: var(--radius-md); box-shadow: var(--shadow-lg);
  max-height: 200px; overflow-y: auto;
}
.location-item {
  padding: 10px 14px; cursor: pointer;
  border-bottom: 1px solid var(--color-border);
}
.location-item:last-child { border-bottom: none; }
.location-item:hover { background: var(--color-primary-bg); }
.loc-name { font-size: 14px; font-weight: 600; color: var(--color-text); display: block; }
.loc-addr { font-size: 12px; color: var(--color-text-muted); }

@media (max-width: 768px) {
  .create-post-modal { max-height: 100vh; border-radius: 0; }
}
</style>

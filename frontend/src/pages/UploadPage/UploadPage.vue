<template>
  <div class="upload-page">
    <div class="upload-card">
      <div class="upload-header">
        <h2>📸 上传观鸟记录</h2>
        <p>上传照片，AI 帮你识别鸟类，一键发布到社区</p>
      </div>

      <div class="upload-body">
        <!-- 上传区 -->
        <div v-if="!imageUrl" class="upload-zone" @click="handleUpload">
          <div class="upload-icon-wrapper"><span class="upload-icon">📤</span></div>
          <h3>点击上传图片</h3>
          <p>支持 JPG、PNG、WebP、GIF 格式，最大 10MB</p>
        </div>

        <!-- 图片预览 + 识别按钮（上传后始终显示） -->
        <div v-if="imageUrl" class="preview-section">
          <img :src="imageUrl" alt="预览" class="preview-img" />
          <div class="preview-actions">
            <button class="btn btn-secondary" @click="handleReset">重新选择</button>
            <button class="btn btn-primary" @click="handleRecognize" :disabled="recognizing">
              {{ recognizing ? '识别中...' : recognized ? '🔄 重新识别' : '🔍 识别鸟类' }}
            </button>
          </div>
          <div v-if="recognizing" class="analyzing-hint">
            <div class="loading-spinner"></div>
            <span>AI 正在识别鸟类，请稍候...</span>
          </div>
          <div v-if="errorMsg" class="error-banner">
            <span>{{ errorMsg }}</span>
            <button class="btn btn-secondary" @click="errorMsg = ''">关闭</button>
          </div>
        </div>

        <!-- 识别结果（识别成功后显示） -->
        <div v-if="results.length > 0" class="results-box">
          <h3>🔍 识别结果</h3>
          <div v-for="(r, i) in results" :key="i" class="result-item" :class="{ 'result-top': i === 0 }">
            <span class="result-rank">{{ i + 1 }}</span>
            <div class="result-info">
              <span class="result-name">{{ r.name }}</span>
              <div class="result-bar-bg">
                <div class="result-bar-fill" :style="{ width: `${Math.round(r.confidence * 100)}%` }"></div>
              </div>
            </div>
            <span class="result-confidence">{{ Math.round(r.confidence * 100) }}%</span>
            <button class="btn btn-sm" :class="selectedBirdName === r.name ? 'btn-primary' : 'btn-outline'"
              @click="selectBird(r)">
              {{ selectedBirdName === r.name ? '已选' : '选择' }}
            </button>
          </div>
        </div>

        <!-- 发帖表单（始终显示） -->
        <div class="post-form">
          <h3>📝 发布帖子</h3>

          <div class="form-group">
            <label>标题 <span class="required">*</span></label>
            <input v-model="postForm.title" type="text" class="input-field" placeholder="输入帖子标题..." maxlength="200" />
          </div>

          <div class="form-group">
            <label>内容</label>
            <textarea v-model="postForm.content" class="input-field" rows="3" placeholder="分享你的观鸟体验..."></textarea>
          </div>

          <div class="form-group">
            <label>位置 <span class="required">*</span></label>
            <div class="location-input-wrap">
              <input ref="locationInput" v-model="postForm.location" type="text" class="input-field"
                placeholder="输入位置名称..." autocomplete="off" @input="onLocationInput" />
              <div v-if="locationSuggestions.length > 0" class="location-dropdown">
                <div v-for="(s, i) in locationSuggestions" :key="i" class="location-item"
                  :class="{ active: i === suggestionIndex }" @mousedown.prevent="selectLocation(s)">
                  <span class="loc-name">{{ s.name }}</span>
                  <span class="loc-addr">{{ s.address }}</span>
                </div>
              </div>
            </div>
          </div>

          <div class="form-actions">
            <button class="btn btn-primary btn-block" :disabled="submitting || !canSubmit" @click="submitPost">
              {{ submitting ? '发布中...' : '🚀 发布帖子' }}
            </button>
          </div>

          <div v-if="postError" class="error-banner">
            <span>{{ postError }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { showToast, showModal } from '@/utils/toast.js'
import { chooseImages } from '@/utils/helpers.js'
import RecognitionService from '@/api/services/recognition.js'
import PostService from '@/api/services/post.js'
import UploadService from '@/api/services/upload.js'

const router = useRouter()
const BAIDU_MAP_KEY = import.meta.env.VITE_BAIDU_MAP_API_KEY || ''

// ===== 图片 =====
const imageUrl = ref('')       // 本地预览 URL（blob）
const serverImageUrl = ref('') // 服务器返回的图片路径
const imageFile = ref(null)
const errorMsg = ref('')

// ===== 识别 =====
const recognizing = ref(false)
const recognized = ref(false)
const results = ref([])
const selectedBirdName = ref('')

// ===== 发帖 =====
const locationInput = ref(null)
const postForm = ref({ title: '', content: '', location: '' })
const submitting = ref(false)
const postError = ref('')
const locationSuggestions = ref([])
const suggestionIndex = ref(-1)
const locationConfirmed = ref('')
let acInstance = null

const canSubmit = computed(() =>
  postForm.value.title.trim() && postForm.value.location.trim() &&
  postForm.value.location.trim() === locationConfirmed.value
)

onMounted(async () => {
  await loadBaiduMap()
  await nextTick()
  initAutocomplete()
})

// ===== 图片上传 =====
const handleUpload = async () => {
  try {
    const result = await chooseImages({ count: 1 })
    if (result.tempFilePaths.length) {
      imageUrl.value = result.tempFilePaths[0]
      imageFile.value = result.files[0]
      errorMsg.value = ''
      recognized.value = false
      results.value = []
      selectedBirdName.value = ''
    }
  } catch { showToast('选择失败', 'error') }
}

const handleReset = async () => {
  const ok = await showModal('确认', '确定要重新选择图片吗？之前的识别结果将丢失。')
  if (ok) {
    imageUrl.value = ''
    imageFile.value = null
    recognized.value = false
    results.value = []
    selectedBirdName.value = ''
    errorMsg.value = ''
    postForm.value = { title: '', content: '', location: '' }
    locationConfirmed.value = ''
  }
}

// ===== 识别 =====
const handleRecognize = async () => {
  if (!imageFile.value) return showToast('请先选择图片', 'none')
  recognizing.value = true
  errorMsg.value = ''
  try {
    const res = await RecognitionService.analyzeWithImage(imageFile.value)
    const data = res.data?.data
    if (data?.results?.length) {
      results.value = data.results
      serverImageUrl.value = data.image_url || ''
      recognized.value = true
      selectBird(data.results[0])
      showToast('识别完成！', 'success')
    } else {
      errorMsg.value = '未能识别出鸟类，请尝试更清晰的照片'
    }
  } catch (err) {
    const status = err?.statusCode
    if (status === 401) errorMsg.value = '请先登录后再使用识别功能'
    else if (status === 413) errorMsg.value = '文件过大，请选择 10MB 以内的图片'
    else if (status === 400) errorMsg.value = '不支持的文件格式'
    else errorMsg.value = err?.message || '识别失败，请稍后重试'
  } finally { recognizing.value = false }
}

const selectBird = (bird) => {
  selectedBirdName.value = bird.name
  postForm.value.title = `发现了一只${bird.name}！`
  if (!postForm.value.content) {
    postForm.value.content = `今天在户外观察到一只${bird.name}，AI 识别置信度 ${Math.round(bird.confidence * 100)}%，和大家分享~`
  }
}

// ===== 百度地图 =====
function loadBaiduMap() {
  return new Promise((resolve) => {
    if (window.BMap) { resolve(); return }
    const script = document.createElement('script')
    script.src = `https://api.map.baidu.com/api?v=2.0&ak=${BAIDU_MAP_KEY}&callback=onBaiduMapForUpload`
    window.onBaiduMapForUpload = () => { resolve() }
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
    suggestionIndex.value = -1
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
    postForm.value.location = selected
    locationConfirmed.value = selected
    locationSuggestions.value = []
  })
}

function onLocationInput() { locationConfirmed.value = '' }

function selectLocation(s) {
  postForm.value.location = s.name
  locationConfirmed.value = s.name
  locationSuggestions.value = []
}

// ===== 发布 =====
async function submitPost() {
  if (!canSubmit.value) return
  submitting.value = true
  postError.value = ''
  try {
    // 如果有图片但还没上传（未走识别流程），先上传图片
    if (!serverImageUrl.value && imageFile.value) {
      const res = await UploadService.uploadImage(imageFile.value)
      serverImageUrl.value = res.data?.data?.url || ''
    }
    await PostService.createPost({
      title: postForm.value.title.trim(),
      content: postForm.value.content.trim(),
      images: serverImageUrl.value ? [serverImageUrl.value] : [],
      location: postForm.value.location.trim(),
    })
    showToast('发布成功！', 'success')
    setTimeout(() => router.push('/'), 800)
  } catch (err) {
    const status = err?.statusCode
    if (status === 401) postError.value = '请先登录后再发布帖子'
    else postError.value = err?.message || '发布失败，请重试'
  } finally { submitting.value = false }
}
</script>

<style scoped>
.upload-page { max-width: 640px; margin: 40px auto; padding: 0 20px; }

.upload-card {
  background: var(--color-surface); border-radius: var(--radius-xl);
  border: 1px solid var(--color-border); overflow: hidden; box-shadow: var(--shadow-md);
}
.upload-header {
  text-align: center; padding: 40px 24px 24px;
  background: linear-gradient(135deg, var(--color-primary-bg), var(--color-accent-bg));
}
.upload-header h2 { font-size: 24px; color: var(--color-text); margin-bottom: 6px; }
.upload-header p { font-size: 14px; color: var(--color-text-secondary); }
.upload-body { padding: 32px 24px; }

/* 上传区 */
.upload-zone {
  border: 2px dashed var(--color-border); border-radius: var(--radius-lg);
  padding: 60px 40px; text-align: center; cursor: pointer;
  transition: all 0.2s; background: var(--color-bg);
}
.upload-zone:hover { border-color: var(--color-primary-light); background: var(--color-primary-bg); transform: translateY(-2px); }
.upload-icon-wrapper { width: 72px; height: 72px; margin: 0 auto 16px; background: linear-gradient(135deg, var(--color-primary-bg), var(--color-accent-bg)); border-radius: 50%; display: flex; align-items: center; justify-content: center; }
.upload-icon { font-size: 32px; }
.upload-zone h3 { font-size: 16px; color: var(--color-text); margin-bottom: 6px; }
.upload-zone p { font-size: 13px; color: var(--color-text-muted); }

/* 预览 + 识别按钮 */
.preview-section { text-align: center; }
.preview-img { width: 100%; max-height: 400px; object-fit: contain; border-radius: var(--radius-md); background: var(--color-bg); margin-bottom: 20px; }
.preview-actions { display: flex; gap: 12px; justify-content: center; }

/* 识别中 */
.analyzing-hint { display: flex; align-items: center; justify-content: center; gap: 10px; margin-top: 20px; padding: 14px; background: var(--color-primary-bg); border-radius: var(--radius-sm); font-size: 14px; color: var(--color-primary); }
.loading-spinner { width: 20px; height: 20px; border: 2px solid var(--color-border); border-top-color: var(--color-primary); border-radius: 50%; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

/* 结果 + 发帖 */
.result-post-section { display: flex; flex-direction: column; gap: 24px; }
.result-preview-row { display: flex; align-items: center; gap: 12px; }
.result-preview-img { width: 120px; height: 90px; object-fit: cover; border-radius: var(--radius-md); }
.btn-sm { padding: 4px 12px; font-size: 12px; }

.results-box { background: var(--color-bg); border-radius: var(--radius-md); padding: 16px; }
.results-box h3 { font-size: 15px; color: var(--color-text); margin-bottom: 12px; }
.result-item { display: flex; align-items: center; gap: 10px; padding: 8px 10px; border-radius: var(--radius-sm); margin-bottom: 6px; }
.result-item.result-top { background: var(--color-primary-bg); }
.result-rank { width: 24px; height: 24px; border-radius: 50%; background: var(--color-surface); display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 700; color: var(--color-text-muted); flex-shrink: 0; }
.result-top .result-rank { background: var(--color-primary); color: #fff; }
.result-info { flex: 1; min-width: 0; }
.result-name { font-size: 14px; font-weight: 600; color: var(--color-text); display: block; margin-bottom: 4px; }
.result-bar-bg { height: 6px; background: var(--color-border); border-radius: 3px; overflow: hidden; }
.result-bar-fill { height: 100%; background: linear-gradient(90deg, var(--color-primary), var(--color-primary-light)); border-radius: 3px; transition: width 0.6s ease; }
.result-confidence { font-size: 13px; font-weight: 700; color: var(--color-primary); width: 40px; text-align: right; flex-shrink: 0; }
.btn-outline { background: transparent; border: 1px solid var(--color-border); color: var(--color-text-secondary); }
.btn-outline:hover { border-color: var(--color-primary); color: var(--color-primary); }

/* 发帖表单 */
.post-form h3 { font-size: 16px; color: var(--color-text); margin-bottom: 16px; }
.form-group { margin-bottom: 16px; }
.form-group label { display: block; font-size: 14px; font-weight: 600; color: var(--color-text); margin-bottom: 6px; }
.required { color: #ef4444; }
.input-field { width: 100%; padding: 10px 14px; font-size: 14px; border: 1px solid var(--color-border); border-radius: var(--radius-md); background: var(--color-bg); color: var(--color-text); outline: none; box-sizing: border-box; }
.input-field:focus { border-color: var(--color-primary); }
.location-input-wrap { position: relative; }
.location-dropdown { position: absolute; top: 100%; left: 0; right: 0; z-index: 300; background: var(--color-surface); border: 1px solid var(--color-border); border-radius: var(--radius-md); box-shadow: var(--shadow-lg); max-height: 200px; overflow-y: auto; }
.location-item { padding: 10px 14px; cursor: pointer; border-bottom: 1px solid var(--color-border); }
.location-item:last-child { border-bottom: none; }
.location-item:hover, .location-item.active { background: var(--color-primary-bg); }
.loc-name { font-size: 14px; font-weight: 600; color: var(--color-text); display: block; }
.loc-addr { font-size: 12px; color: var(--color-text-muted); }
.form-actions { margin-top: 20px; }
.btn-block { width: 100%; padding: 12px; font-size: 16px; }

.error-banner { background: #fef2f2; color: #dc2626; padding: 12px 16px; border-radius: var(--radius-sm); font-size: 13px; margin-top: 12px; border: 1px solid #fecaca; display: flex; align-items: center; justify-content: space-between; gap: 12px; }

@media (max-width: 768px) {
  .upload-page { margin: 20px auto; }
  .upload-header { padding: 28px 16px 20px; }
  .upload-body { padding: 24px 16px; }
  .upload-zone { padding: 40px 20px; }
}
</style>

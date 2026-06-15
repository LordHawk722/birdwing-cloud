<template>
  <div class="upload-page">
    <!-- 模式切换 -->
    <div class="mode-tabs">
      <button :class="{ active: mode === 'recognize' }" @click="mode = 'recognize'">📸 上传识别</button>
      <button :class="{ active: mode === 'post' }" @click="switchToPost">📝 发布帖子</button>
    </div>

    <!-- ===== 模式一：上传识别（原有功能） ===== -->
    <div v-if="mode === 'recognize'" class="upload-card">
      <div class="upload-header">
        <h2>📸 上传鸟类照片</h2>
        <p>选择一张清晰的照片，让我们帮你识别鸟类品种</p>
      </div>

      <div class="upload-body">
        <div v-if="results.length > 0" class="results-area">
          <img v-if="imageUrl" :src="imageUrl" alt="预览" class="preview-img" />
          <div class="results-list">
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
            </div>
          </div>
          <div class="results-actions">
            <button class="btn btn-secondary" @click="handleReset">重新上传</button>
          </div>
        </div>

        <div v-else-if="imageUrl" class="preview-area">
          <img :src="imageUrl" alt="预览" class="preview-img" />
          <div class="preview-actions">
            <button class="btn btn-secondary" @click="handleReset">重新选择</button>
            <button class="btn btn-primary" @click="handleAnalyze" :disabled="analyzing">
              {{ analyzing ? '分析中...' : '🔍 开始分析' }}
            </button>
          </div>
        </div>

        <div v-else class="upload-zone" @click="handleUpload">
          <div class="upload-icon-wrapper"><span class="upload-icon">📤</span></div>
          <h3>点击上传图片</h3>
          <p>支持 JPG、PNG、WebP、GIF 格式，最大 10MB</p>
        </div>

        <div v-if="analyzing" class="analyzing-hint">
          <div class="loading-spinner"></div>
          <span>正在识别鸟类，请稍候...</span>
        </div>

        <div v-if="errorMsg" class="error-banner">
          <span>{{ errorMsg }}</span>
          <button class="btn btn-secondary" @click="errorMsg='';handleReset()">重试</button>
        </div>
      </div>
    </div>

    <!-- ===== 模式二：发布帖子 ===== -->
    <div v-if="mode === 'post'" class="upload-card">
      <div class="upload-header">
        <h2>📝 发布观鸟帖子</h2>
        <p>分享你的观鸟记录，选择拍摄位置</p>
      </div>

      <div class="upload-body">
        <!-- 标题 -->
        <div class="form-group">
          <label>标题 <span class="required">*</span></label>
          <input
            v-model="postForm.title"
            type="text"
            class="input-field"
            placeholder="输入帖子标题..."
            maxlength="200"
          />
        </div>

        <!-- 内容 -->
        <div class="form-group">
          <label>内容</label>
          <textarea
            v-model="postForm.content"
            class="input-field"
            rows="4"
            placeholder="分享你的观鸟体验..."
          ></textarea>
        </div>

        <!-- 图片 -->
        <div class="form-group">
          <label>图片</label>
          <div v-if="postForm.imageUrl" class="post-preview-img">
            <img :src="postForm.imageUrl" alt="预览" />
            <button class="btn btn-secondary btn-sm" @click="clearPostImage">更换</button>
          </div>
          <div v-else class="upload-zone upload-zone-sm" @click="uploadPostImage">
            <span>📤 点击上传图片</span>
          </div>
        </div>

        <!-- 位置（百度地图自动补全） -->
        <div class="form-group">
          <label>位置 <span class="required">*</span></label>
          <div class="location-input-wrap">
            <input
              ref="locationInput"
              v-model="postForm.location"
              type="text"
              class="input-field"
              placeholder="输入位置名称（从下拉建议中选择）..."
              autocomplete="off"
              @input="onLocationInput"
            />
            <div v-if="locationSuggestions.length > 0" class="location-dropdown">
              <div
                v-for="(s, i) in locationSuggestions"
                :key="i"
                class="location-item"
                :class="{ active: i === suggestionIndex }"
                @mousedown.prevent="selectLocation(s)"
              >
                <span class="loc-name">{{ s.name }}</span>
                <span class="loc-addr">{{ s.address }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 提交 -->
        <div class="form-actions">
          <button
            class="btn btn-primary btn-block"
            :disabled="submitting || !canSubmit"
            @click="submitPost"
          >
            {{ submitting ? '发布中...' : '发布帖子' }}
          </button>
        </div>

        <div v-if="postError" class="error-banner">
          <span>{{ postError }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { showToast, showModal } from '@/utils/toast.js'
import { chooseImages } from '@/utils/helpers.js'
import RecognitionService from '@/api/services/recognition.js'
import UploadService from '@/api/services/upload.js'
import PostService from '@/api/services/post.js'

const router = useRouter()

const BAIDU_MAP_KEY = import.meta.env.VITE_BAIDU_MAP_API_KEY || ''

// ===== 模式切换 =====
const mode = ref('recognize')

// ===== 识别相关 =====
const imageUrl = ref('')
const imageFile = ref(null)
const analyzing = ref(false)
const errorMsg = ref('')
const results = ref([])

// ===== 发帖相关 =====
const locationInput = ref(null)
const postForm = ref({ title: '', content: '', imageUrl: '', location: '' })
const submitting = ref(false)
const postError = ref('')
const locationSuggestions = ref([])
const suggestionIndex = ref(-1)
const locationConfirmed = ref('')  // 记录从下拉选中的值，与输入值比对
let acInstance = null

const canSubmit = computed(() =>
  postForm.value.title.trim() &&
  postForm.value.location.trim() &&
  postForm.value.location.trim() === locationConfirmed.value
)

// ===== 识别功能 =====
const handleUpload = async () => {
  try {
    const result = await chooseImages({ count: 1 })
    if (result.tempFilePaths.length) {
      imageUrl.value = result.tempFilePaths[0]
      imageFile.value = result.files[0]
      errorMsg.value = ''
      results.value = []
    }
  } catch { showToast('选择失败', 'error') }
}

const handleReset = async () => {
  const ok = await showModal('确认', '确定要重新选择图片吗？')
  if (ok) {
    imageUrl.value = ''
    imageFile.value = null
    results.value = []
    errorMsg.value = ''
  }
}

const handleAnalyze = async () => {
  if (!imageFile.value) return showToast('请先选择图片', 'none')
  analyzing.value = true
  errorMsg.value = ''
  results.value = []
  try {
    const res = await RecognitionService.analyzeWithImage(imageFile.value)
    const data = res.data?.data
    if (data?.results?.length) {
      results.value = data.results
      showToast('识别完成！', 'success')
    } else {
      errorMsg.value = '未能识别出鸟类，请尝试更清晰的照片'
    }
  } catch (err) {
    const status = err?.statusCode
    if (status === 401) errorMsg.value = '请先登录后再使用识别功能'
    else if (status === 413) errorMsg.value = '文件过大，请选择 10MB 以内的图片'
    else if (status === 400) errorMsg.value = '不支持的文件格式，请选择 JPG/PNG/WebP/GIF 图片'
    else errorMsg.value = err?.message || '识别失败，请稍后重试'
  } finally { analyzing.value = false }
}

// ===== 发帖功能 =====
function loadBaiduScriptForUpload() {
  return new Promise((resolve) => {
    if (window.BMap) { resolve(); return }
    const script = document.createElement('script')
    script.src = `https://api.map.baidu.com/api?v=2.0&ak=${BAIDU_MAP_KEY}&callback=onBaiduMapForUpload`
    window.onBaiduMapForUpload = () => { resolve() }
    document.head.appendChild(script)
  })
}

async function switchToPost() {
  mode.value = 'post'
  postError.value = ''
  try {
    await loadBaiduScriptForUpload()
    await nextTick()
    initAutocomplete()
  } catch { /* 地图脚本加载失败，位置自动补全不可用 */ }
}

function initAutocomplete() {
  if (!window.BMap || !locationInput.value) return
  if (acInstance) { acInstance.dispose(); acInstance = null }

  acInstance = new BMap.Autocomplete({
    input: locationInput.value,
    location: '全国',
  })

  // 搜索结果返回时更新自定义下拉
  acInstance.addEventListener('onsearchcomplete', (e) => {
    const result = acInstance.getResults()
    if (result && result.getNumPois) {
      const n = result.getNumPois()
      const list = []
      for (let i = 0; i < n; i++) {
        const poi = result.getPoi(i)
        list.push({ name: poi.title || '', address: poi.address || '' })
      }
      locationSuggestions.value = list
    } else {
      locationSuggestions.value = []
    }
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
    suggestionIndex.value = -1
  })
}

function onLocationInput() {
  // 手动输入时清空确认值，按钮自动禁用
  locationConfirmed.value = ''
  suggestionIndex.value = -1
}

function selectLocation(suggestion) {
  postForm.value.location = suggestion.name
  locationConfirmed.value = suggestion.name
  locationSuggestions.value = []
  suggestionIndex.value = -1
}

async function uploadPostImage() {
  try {
    const result = await chooseImages({ count: 1 })
    if (result.tempFilePaths.length && result.files.length) {
      showToast('上传中...', 'none')
      const res = await UploadService.uploadImage(result.files[0])
      const data = res.data?.data
      postForm.value.imageUrl = data?.url || ''
      showToast('图片上传成功', 'success')
    }
  } catch {
    showToast('上传失败', 'error')
  }
}

function clearPostImage() {
  postForm.value.imageUrl = ''
}

async function submitPost() {
  if (!canSubmit.value) return
  submitting.value = true
  postError.value = ''
  try {
    const payload = {
      title: postForm.value.title.trim(),
      content: postForm.value.content.trim(),
      images: postForm.value.imageUrl ? [postForm.value.imageUrl] : [],
      location: postForm.value.location.trim(),
    }
    await PostService.createPost(payload)
    showToast('发布成功！', 'success')
    // 重置表单
    postForm.value = { title: '', content: '', imageUrl: '', location: '' }
    locationConfirmed.value = ''
    locationSuggestions.value = []
    // 跳转回首页
    setTimeout(() => { router.push('/') }, 800)
  } catch (err) {
    const status = err?.statusCode
    if (status === 401) postError.value = '请先登录后再发布帖子'
    else postError.value = err?.message || '发布失败，请重试'
  } finally { submitting.value = false }
}
</script>

<style scoped>
.upload-page { max-width: 640px; margin: 40px auto; padding: 0 20px; }

/* 模式切换 */
.mode-tabs {
  display: flex; gap: 0; margin-bottom: 20px;
  background: var(--color-surface); border-radius: var(--radius-lg);
  border: 1px solid var(--color-border); overflow: hidden;
}
.mode-tabs button {
  flex: 1; padding: 12px; border: none; background: transparent;
  font-size: 14px; font-weight: 600; cursor: pointer;
  transition: all 0.2s; color: var(--color-text-muted);
}
.mode-tabs button.active {
  background: var(--color-primary); color: #fff;
}

.upload-card {
  background: var(--color-surface);
  border-radius: var(--radius-xl);
  border: 1px solid var(--color-border);
  overflow: hidden;
  box-shadow: var(--shadow-md);
}
.upload-header {
  text-align: center;
  padding: 40px 24px 24px;
  background: linear-gradient(135deg, var(--color-primary-bg), var(--color-accent-bg));
}
.upload-header h2 { font-size: 24px; color: var(--color-text); margin-bottom: 6px; }
.upload-header p { font-size: 14px; color: var(--color-text-secondary); }
.upload-body { padding: 32px 24px; }

/* 表单 */
.form-group { margin-bottom: 20px; }
.form-group label { display: block; font-size: 14px; font-weight: 600; color: var(--color-text); margin-bottom: 6px; }
.required { color: #ef4444; }
.input-field {
  width: 100%; padding: 10px 14px; font-size: 14px;
  border: 1px solid var(--color-border); border-radius: var(--radius-md);
  background: var(--color-bg); color: var(--color-text);
  outline: none; transition: border-color 0.2s;
  box-sizing: border-box;
}
.input-field:focus { border-color: var(--color-primary); }

.post-preview-img { position: relative; display: inline-block; }
.post-preview-img img { max-height: 200px; border-radius: var(--radius-md); display: block; margin-bottom: 8px; }
.btn-sm { padding: 4px 12px; font-size: 12px; }
.upload-zone-sm {
  padding: 24px; cursor: pointer; text-align: center; font-size: 14px;
  color: var(--color-text-muted);
  border: 2px dashed var(--color-border); border-radius: var(--radius-md);
  transition: all 0.2s;
}
.upload-zone-sm:hover { border-color: var(--color-primary); background: var(--color-primary-bg); }

/* 位置下拉 */
.location-input-wrap { position: relative; }
.location-dropdown {
  position: absolute; top: 100%; left: 0; right: 0; z-index: 300;
  background: var(--color-surface); border: 1px solid var(--color-border);
  border-radius: var(--radius-md); box-shadow: var(--shadow-lg);
  max-height: 200px; overflow-y: auto;
}
.location-item {
  padding: 10px 14px; cursor: pointer; transition: background 0.15s;
  border-bottom: 1px solid var(--color-border);
}
.location-item:last-child { border-bottom: none; }
.location-item:hover, .location-item.active { background: var(--color-primary-bg); }
.loc-name { font-size: 14px; font-weight: 600; color: var(--color-text); display: block; }
.loc-addr { font-size: 12px; color: var(--color-text-muted); }

.form-actions { margin-top: 24px; }
.btn-block { width: 100%; padding: 12px; font-size: 16px; }

/* ===== 原有样式保留 ===== */
.results-area { text-align: center; }
.results-list { text-align: left; margin: 20px 0; }
.results-list h3 { font-size: 16px; color: var(--color-text); margin-bottom: 12px; }
.result-item {
  display: flex; align-items: center; gap: 10px;
  padding: 8px 10px; border-radius: var(--radius-sm);
  transition: background 0.15s; margin-bottom: 6px;
}
.result-item:hover { background: var(--color-bg); }
.result-item.result-top { background: var(--color-primary-bg); }
.result-rank {
  width: 24px; height: 24px; border-radius: 50%;
  background: var(--color-bg); display: flex; align-items: center; justify-content: center;
  font-size: 12px; font-weight: 700; color: var(--color-text-muted); flex-shrink: 0;
}
.result-top .result-rank { background: var(--color-primary); color: #fff; }
.result-info { flex: 1; min-width: 0; }
.result-name { font-size: 14px; font-weight: 600; color: var(--color-text); display: block; margin-bottom: 4px; }
.result-bar-bg { height: 6px; background: var(--color-border); border-radius: 3px; overflow: hidden; }
.result-bar-fill {
  height: 100%; background: linear-gradient(90deg, var(--color-primary), var(--color-primary-light));
  border-radius: 3px; transition: width 0.6s ease;
}
.result-confidence { font-size: 13px; font-weight: 700; color: var(--color-primary); flex-shrink: 0; width: 40px; text-align: right; }
.results-actions { margin-top: 16px; }

.preview-area { text-align: center; }
.preview-img {
  width: 100%; max-height: 400px; object-fit: contain;
  border-radius: var(--radius-md); background: var(--color-bg); margin-bottom: 20px;
}
.preview-actions { display: flex; gap: 12px; justify-content: center; }

.upload-zone {
  border: 2px dashed var(--color-border);
  border-radius: var(--radius-lg); padding: 60px 40px;
  text-align: center; cursor: pointer;
  transition: all var(--transition-normal); background: var(--color-bg);
}
.upload-zone:hover {
  border-color: var(--color-primary-light);
  background: var(--color-primary-bg); transform: translateY(-2px);
}
.upload-icon-wrapper {
  width: 72px; height: 72px; margin: 0 auto 16px;
  background: linear-gradient(135deg, var(--color-primary-bg), var(--color-accent-bg));
  border-radius: 50%; display: flex; align-items: center; justify-content: center;
}
.upload-icon { font-size: 32px; }
.upload-zone h3 { font-size: 16px; color: var(--color-text); margin-bottom: 6px; }
.upload-zone p { font-size: 13px; color: var(--color-text-muted); }

.analyzing-hint {
  display: flex; align-items: center; justify-content: center; gap: 10px;
  margin-top: 20px; padding: 14px;
  background: var(--color-primary-bg); border-radius: var(--radius-sm);
  font-size: 14px; color: var(--color-primary);
}
.loading-spinner {
  width: 20px; height: 20px;
  border: 2px solid var(--color-border); border-top-color: var(--color-primary);
  border-radius: 50%; animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.error-banner {
  background: #fef2f2; color: #dc2626; padding: 12px 16px;
  border-radius: var(--radius-sm); font-size: 13px; margin-top: 16px;
  border: 1px solid #fecaca; display: flex; align-items: center; justify-content: space-between; gap: 12px;
}

@media (max-width: 768px) {
  .upload-page { margin: 20px auto; }
  .upload-header { padding: 28px 16px 20px; }
  .upload-body { padding: 24px 16px; }
  .upload-zone { padding: 40px 20px; }
}
</style>

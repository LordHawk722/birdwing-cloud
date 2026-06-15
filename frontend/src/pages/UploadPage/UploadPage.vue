<template>
  <div class="upload-page">
    <div class="upload-card">
      <div class="upload-header">
        <h2>📸 上传鸟类照片</h2>
        <p>选择一张清晰的照片，让我们帮你识别鸟类品种</p>
      </div>

      <div class="upload-body">
        <!-- 分析结果 -->
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

        <!-- 预览 + 分析按钮 -->
        <div v-else-if="imageUrl" class="preview-area">
          <img :src="imageUrl" alt="预览" class="preview-img" />
          <div class="preview-actions">
            <button class="btn btn-secondary" @click="handleReset">重新选择</button>
            <button class="btn btn-primary" @click="handleAnalyze" :disabled="analyzing">
              {{ analyzing ? '分析中...' : '🔍 开始分析' }}
            </button>
          </div>
        </div>

        <!-- 上传区域 -->
        <div v-else class="upload-zone" @click="handleUpload">
          <div class="upload-icon-wrapper">
            <span class="upload-icon">📤</span>
          </div>
          <h3>点击上传图片</h3>
          <p>支持 JPG、PNG、WebP、GIF 格式，最大 10MB</p>
        </div>

        <!-- 分析进度 -->
        <div v-if="analyzing" class="analyzing-hint">
          <div class="loading-spinner"></div>
          <span>正在识别鸟类，请稍候...</span>
        </div>

        <!-- 错误 -->
        <div v-if="errorMsg" class="error-banner">
          <span>{{ errorMsg }}</span>
          <button class="btn btn-secondary" @click="errorMsg='';handleReset()">重试</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { showToast, showModal } from '@/utils/toast.js'
import { chooseImages } from '@/utils/helpers.js'
import RecognitionService from '@/api/services/recognition.js'

const imageUrl = ref('')
const imageFile = ref(null)
const analyzing = ref(false)
const errorMsg = ref('')
const results = ref([])

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
    if (status === 401) {
      errorMsg.value = '请先登录后再使用识别功能'
    } else if (status === 413) {
      errorMsg.value = '文件过大，请选择 10MB 以内的图片'
    } else if (status === 400) {
      errorMsg.value = '不支持的文件格式，请选择 JPG/PNG/WebP/GIF 图片'
    } else {
      errorMsg.value = err?.message || '识别失败，请稍后重试'
    }
  } finally {
    analyzing.value = false
  }
}
</script>

<style scoped>
.upload-page {
  max-width: 640px; margin: 40px auto; padding: 0 20px;
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

/* ===== 结果区域 ===== */
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
.result-bar-bg {
  height: 6px; background: var(--color-border); border-radius: 3px; overflow: hidden;
}
.result-bar-fill {
  height: 100%; background: linear-gradient(90deg, var(--color-primary), var(--color-primary-light));
  border-radius: 3px; transition: width 0.6s ease;
}
.result-confidence { font-size: 13px; font-weight: 700; color: var(--color-primary); flex-shrink: 0; width: 40px; text-align: right; }
.results-actions { margin-top: 16px; }

.preview-area { text-align: center; }
.preview-img {
  width: 100%; max-height: 400px; object-fit: contain;
  border-radius: var(--radius-md); background: var(--color-bg);
  margin-bottom: 20px;
}
.preview-actions { display: flex; gap: 12px; justify-content: center; }

.upload-zone {
  border: 2px dashed var(--color-border);
  border-radius: var(--radius-lg);
  padding: 60px 40px;
  text-align: center;
  cursor: pointer;
  transition: all var(--transition-normal);
  background: var(--color-bg);
}
.upload-zone:hover {
  border-color: var(--color-primary-light);
  background: var(--color-primary-bg);
  transform: translateY(-2px);
}
.upload-icon-wrapper {
  width: 72px; height: 72px;
  margin: 0 auto 16px;
  background: linear-gradient(135deg, var(--color-primary-bg), var(--color-accent-bg));
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
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

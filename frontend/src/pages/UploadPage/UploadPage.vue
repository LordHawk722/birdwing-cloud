<template>
  <div class="upload-page">
    <div class="upload-card">
      <div class="upload-header">
        <h2>📸 上传鸟类照片</h2>
        <p>选择一张清晰的照片，让我们帮你识别鸟类品种</p>
      </div>

      <div class="upload-body">
        <div v-if="imageUrl" class="preview-area">
          <img :src="imageUrl" alt="预览" class="preview-img" />
          <div class="preview-actions">
            <button class="btn btn-secondary" @click="handleReset">重新选择</button>
            <button class="btn btn-primary" @click="handleAnalyze">🔍 开始分析</button>
          </div>
        </div>

        <div v-else class="upload-zone" @click="handleUpload">
          <div class="upload-icon-wrapper">
            <span class="upload-icon">📤</span>
          </div>
          <h3>点击上传图片</h3>
          <p>支持 JPG、PNG、WebP 格式</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { showToast, showModal } from '@/utils/toast.js'
import { chooseImages } from '@/utils/helpers.js'

const imageUrl = ref('')

const handleUpload = async () => {
  try {
    const result = await chooseImages({ count: 1 })
    if (result.tempFilePaths.length) {
      imageUrl.value = result.tempFilePaths[0]
      showToast('图片已选择', 'success')
    }
  } catch { showToast('选择失败', 'error') }
}

const handleReset = async () => {
  const ok = await showModal('确认', '确定要重新选择图片吗？')
  if (ok) { imageUrl.value = ''; showToast('已重置', 'success') }
}

const handleAnalyze = () => {
  if (!imageUrl.value) return showToast('请先选择图片', 'none')
  showToast('正在分析...', 'loading')
  // TODO: 调用图片分析 API
  setTimeout(() => showToast('分析完成！', 'success'), 2000)
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

@media (max-width: 768px) {
  .upload-page { margin: 20px auto; }
  .upload-header { padding: 28px 16px 20px; }
  .upload-body { padding: 24px 16px; }
  .upload-zone { padding: 40px 20px; }
}
</style>

<template>
  <div class="container">
    <!-- Header -->
    <div class="header">
      <span class="title">像鸟儿一样</span>
      <span class="title">记得家的方向</span>
      <span class="title">认得人的模样</span>
      <span class="title">却忘了飞不过时光</span>
    </div>

    <!-- Main Content -->
    <div class="main-content">
      <div v-if="imageUrl" class="image-preview">
        <img :src="imageUrl" class="preview-image" alt="预览图片" />
      </div>
      <div v-else class="placeholder">
        <span class="placeholder-text">请选择可以清晰地观察到的鸟的照片喵~</span>
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="button-container">
      <div v-if="imageUrl" class="two-buttons">
        <button class="btn btn-secondary" @click="handleReset">重新上传</button>
        <button class="btn btn-primary" @click="handleAnalyze">分析图片</button>
      </div>
      <div v-else class="upload-buttons" @click="handleUpload">
        <div class="upload-circle"></div>
        <span class="upload-text">点击上传图片</span>
      </div>
    </div>

    <TabBar />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import TabBar from '@/components/TabBar.vue'
import { getOSSUrl } from '@/config/oss.js'
import { showToast, showModal } from '@/utils/toast.js'
import { chooseImages } from '@/utils/helpers.js'
import { useRouter } from 'vue-router'

const router = useRouter()
const imageUrl = ref('')

const handleUpload = async () => {
  try {
    const result = await chooseImages({ count: 1 })
    if (result.tempFilePaths.length > 0) {
      imageUrl.value = result.tempFilePaths[0]
      showToast('图片上传成功', 'success', 1500)
    }
  } catch (error) {
    console.error('图片选择失败:', error)
    showToast('图片选择失败', 'error')
  }
}

const handleReset = async () => {
  const confirmed = await showModal('确认重新上传', '确定要重新选择图片吗？')
  if (confirmed) {
    imageUrl.value = ''
    showToast('已重置', 'success', 1000)
  }
}

const handleAnalyze = () => {
  if (!imageUrl.value) {
    showToast('请先上传图片', 'none')
    return
  }
  showToast('正在分析图片...', 'loading', 2000)
  // TODO: 实现图片分析功能
  console.log('Analyzing image:', imageUrl.value)
}
</script>

<style scoped>
.container {
  padding: 20px;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #e6fae9;
  padding-bottom: 70px;
}
.header { text-align: left; margin-bottom: 30px; margin-top: 20px; }
.title { display: block; line-height: 2; color: #1e873c; font-size: 14px; font-weight: 400; }
.main-content { width: 100%; display: flex; flex-direction: column; align-items: center; margin-bottom: 30px; }
.image-preview { width: 100%; display: flex; justify-content: center; }
.preview-image { width: 300px; height: 300px; border-radius: 10px; box-shadow: 0 4px 16px rgba(30,135,60,0.15); border: 2px solid rgba(30,135,60,0.1); object-fit: cover; }
.placeholder { padding: 20px; text-align: center; }
.placeholder-text { color: #1e873c; font-size: 14px; }
.button-container { width: 100%; display: flex; justify-content: center; padding: 10px; }
.two-buttons { display: flex; gap: 15px; justify-content: center; align-items: center; }
.btn { padding: 10px 20px; border-radius: 50px; font-size: 14px; transition: all 0.3s ease; border: none; cursor: pointer; }
.btn:active { transform: scale(0.95); }
.btn-primary { background-color: #059669; color: white; box-shadow: 0 2px 8px rgba(5,150,105,0.3); }
.btn-primary:hover { background-color: #047857; }
.btn-secondary { background-color: #f3f4f6; color: #1f2937; border: 1px solid #e5e7eb; }
.btn-secondary:hover { background-color: #e5e7eb; }

.upload-buttons {
  position: relative;
  display: flex; flex-direction: column; align-items: center; gap: 12px;
  background: linear-gradient(135deg, #059669, #10b981);
  padding: 20px 60px;
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 16px rgba(5,150,105,0.3);
}
.upload-buttons:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(5,150,105,0.4); }
.upload-buttons:active { transform: scale(0.98); }
.upload-circle {
  width: 36px; height: 36px; border-radius: 50%;
  border: 2px solid rgba(255,255,255,0.8);
  position: relative;
}
.upload-circle::before, .upload-circle::after {
  content: ''; position: absolute; background: white;
}
.upload-circle::before {
  width: 2px; height: 20px; left: 50%; top: 8px; transform: translateX(-50%);
}
.upload-circle::after {
  width: 20px; height: 2px; top: 50%; left: 8px; transform: translateY(-50%);
}
.upload-text { color: white; font-size: 14px; font-weight: 500; }

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(15px); }
  to { opacity: 1; transform: translateY(0); }
}
.image-preview { animation: fadeInUp 0.6s ease-out; }
.two-buttons { animation: fadeInUp 0.6s ease-out 0.2s both; }

@media screen and (max-width: 375px) {
  .preview-image { width: 250px; height: 250px; }
  .header { margin-top: 10px; }
}
</style>

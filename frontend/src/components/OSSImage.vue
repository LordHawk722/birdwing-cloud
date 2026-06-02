<template>
  <img
    :src="imageSrc"
    :alt="alt"
    :class="['oss-image', customClass]"
    :style="imageStyle"
    @load="onLoad"
    @error="onError"
  />
</template>

<script setup>
import { computed } from 'vue'
import { getOSSUrl } from '@/config/oss.js'

const props = defineProps({
  filename: { type: String, default: '' },
  size: { type: String, default: 'medium' },
  alt: { type: String, default: '' },
  width: { type: [String, Number], default: undefined },
  height: { type: [String, Number], default: undefined },
  customClass: { type: String, default: '' },
  fallback: { type: String, default: '' }
})

const emit = defineEmits(['load', 'error'])

const imageSrc = computed(() => {
  if (!props.filename) return props.fallback || ''
  // 如果已经是完整URL就直接返回
  if (props.filename.startsWith('http')) return props.filename
  // 如果是blob URL就直接返回
  if (props.filename.startsWith('blob:')) return props.filename
  return getOSSUrl(props.filename, props.size)
})

const imageStyle = computed(() => {
  const style = {}
  if (props.width) style.width = typeof props.width === 'number' ? `${props.width}px` : props.width
  if (props.height) style.height = typeof props.height === 'number' ? `${props.height}px` : props.height
  return style
})

const onLoad = (event) => emit('load', event)
const onError = (event) => {
  if (props.fallback && event.target.src !== props.fallback) {
    event.target.src = props.fallback
  }
  emit('error', event)
}
</script>

<style scoped>
.oss-image {
  display: block;
  max-width: 100%;
}
</style>

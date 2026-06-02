<template>
  <div class="ranking-container">
    <h1 class="page-title">🔥 热门鸟类排行榜</h1>

    <div v-for="(bird, index) in rankedBirds" :key="bird.id" class="bird-item" :class="`rank-${index + 1}`">
      <div class="rank-number">{{ index + 1 }}</div>
      <div class="bird-info">
        <h2>{{ bird.name }}</h2>
        <div class="details">
          <p><strong>地区：</strong>{{ bird.region }}</p>
          <p><strong>习性：</strong>{{ bird.habit }}</p>
          <p class="description">{{ bird.description }}</p>
          <p class="search-count"><strong>近期搜索量：</strong>{{ formatNumber(bird.searchCount) }}</p>
        </div>
      </div>
      <div class="bird-image">
        <img :src="getBirdImageUrl(bird.image)" :alt="bird.name" @error="onImageError" />
      </div>
    </div>
  </div>
</template>

<script>
import { getOSSUrl } from '@/config/oss.js'

export default {
  name: 'RankingPage',
  data() {
    return {
      rankedBirds: [
        { id: 1, name: '东方白鹳', region: '东亚地区', habit: '群居性水鸟，善于飞行和涉水觅食', description: '东方白鹳是一种大型涉禽，全身洁白，翅膀末端呈黑色。具有重要的生态价值，是国家一级保护动物。', searchCount: 150000, image: 'pages/assets/images/stork.jpg' },
        { id: 2, name: '朱鹮', region: '中国陕西洋县', habit: '栖息于山地森林，觅食于水田和沼泽地', description: '朱鹮全身粉红色，被誉为"东方宝石"，是世界珍稀鸟类之一。', searchCount: 120000, image: 'pages/assets/images/ibis.jpg' },
        { id: 3, name: '丹顶鹤', region: '东北亚地区', habit: '善于舞蹈，多在沼泽地和湿地活动', description: '头顶鲜红，全身洁白，象征着吉祥和长寿，是中国传统文化中的瑞鸟。', searchCount: 100000, image: 'pages/assets/images/crane.jpg' },
        { id: 4, name: '黄鹂', region: '华东、华南地区', habit: '栖息于森林和果园，鸣声优美', description: '体型娇小，雄鸟黄黑相间，有"黄衣公子"的美称。', searchCount: 80000, image: 'pages/assets/images/oriole.jpg' },
        { id: 5, name: '金丝雀', region: '全国各地', habit: '善于歌唱，性情活泼', description: '羽毛金黄，歌声婉转动听，是受欢迎的笼养鸟类。', searchCount: 75000, image: 'pages/assets/images/canary.jpg' },
        { id: 6, name: '燕子', region: '全国广泛分布', habit: '善于筑巢，飞行敏捷', description: '春来秋去，被视为吉祥物，在民间文化中备受喜爱。', searchCount: 65000, image: 'pages/assets/images/swallow.jpg' },
        { id: 7, name: '鹦鹉', region: '南方地区', habit: '群居，善于模仿人声', description: '色彩艳丽，聪明伶俐，是深受欢迎的宠物鸟类。', searchCount: 55000, image: 'pages/assets/images/parrot.jpg' },
        { id: 8, name: '猫头鹰', region: '全国各地', habit: '夜行性，善于捕食', description: '目光锐利，头部可旋转270度，是优秀的夜间猎手。', searchCount: 45000, image: 'pages/assets/images/owl.jpg' },
        { id: 9, name: '啄木鸟', region: '温带森林地区', habit: '啄木觅食，守护森林', description: '森林医生，对维护生态平衡有重要作用。', searchCount: 35000, image: 'pages/assets/images/woodpecker.jpg' },
        { id: 10, name: '翠鸟', region: '江河湖泊周边', habit: '捕食小鱼，栖息于水边', description: '羽毛艳丽，蓝绿相间，被誉为"飞翔的宝石"。', searchCount: 30000, image: 'pages/assets/images/kingfisher.jpg' }
      ]
    }
  },
  methods: {
    getBirdImageUrl(filename) {
      return getOSSUrl(filename, 'large')
    },
    onImageError(error) {
      error.target.src = 'data:image/svg+xml,' + encodeURIComponent('<svg width="150" height="150" xmlns="http://www.w3.org/2000/svg"><rect width="150" height="150" fill="#f0f0f0"/><text x="75" y="80" font-size="14" fill="#999" text-anchor="middle">图片加载失败</text></svg>')
    },
    formatNumber(num) {
      if (num >= 10000) return (num / 10000).toFixed(1) + '万'
      return num.toLocaleString()
    }
  }
}
</script>

<style scoped>
.page-title { text-align: center; font-size: 24px; color: #2c3e50; margin: 20px 0; }
.ranking-container { max-width: 1200px; margin: 0 auto; padding: 20px; }
.bird-item { display: flex; margin-bottom: 20px; padding: 20px; border-radius: 10px; background: #fff; box-shadow: 0 2px 8px rgba(0,0,0,0.1); transition: all 0.3s ease; }
.bird-item:hover { transform: translateY(-3px); box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
.rank-number { font-size: 2.5em; font-weight: bold; margin-right: 20px; color: #ff6b6b; min-width: 60px; display: flex; align-items: center; justify-content: center; }
.bird-info { flex: 1; margin-right: 20px; }
.bird-info h2 { color: #2c3e50; margin-bottom: 10px; font-size: 1.5em; }
.details p { margin: 6px 0; color: #666; line-height: 1.5; font-size: 14px; }
.description { margin: 10px 0; line-height: 1.6; color: #2c3e50; }
.search-count { color: #ff6b6b; font-size: 0.9em; margin-top: 10px; }
.bird-image { display: flex; align-items: center; }
.bird-image img { object-fit: cover; border-radius: 8px; transition: all 0.3s ease; }
.rank-1 .bird-image img { width: 250px; height: 250px; }
.rank-2 .bird-image img { width: 220px; height: 220px; }
.rank-3 .bird-image img { width: 180px; height: 180px; }
.rank-4 .bird-image img, .rank-5 .bird-image img, .rank-6 .bird-image img, .rank-7 .bird-image img, .rank-8 .bird-image img, .rank-9 .bird-image img, .rank-10 .bird-image img { width: 120px; height: 120px; }

@media (max-width: 768px) {
  .bird-item { flex-direction: column; }
  .bird-image { margin-top: 15px; justify-content: center; }
  .bird-image img { width: 100% !important; height: auto !important; max-height: 250px; }
  .rank-number { font-size: 2em; min-width: 40px; }
  .bird-info h2 { font-size: 1.2em; }
}
</style>

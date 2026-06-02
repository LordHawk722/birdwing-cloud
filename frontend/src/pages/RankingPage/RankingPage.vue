<template>
  <div class="ranking-page">
    <div class="page-header">
      <h1>🏆 热门鸟类排行榜</h1>
      <p>基于社区搜索和观测数据的实时排行</p>
    </div>

    <div class="ranking-list">
      <div v-for="(bird, i) in rankedBirds" :key="bird.id" class="rank-item fade-in" :style="{ animationDelay: `${i * 0.08}s` }">
        <div class="rank-num" :class="`rank-${i + 1}`">{{ i + 1 }}</div>
        <img :src="getBirdImg(bird.image)" :alt="bird.name" class="rank-img" @error="onImgError" />
        <div class="rank-info">
          <div class="rank-name">{{ bird.name }}</div>
          <div class="rank-meta">{{ bird.region }} · {{ bird.habit }}</div>
          <p class="rank-desc">{{ bird.description }}</p>
        </div>
        <div class="rank-count">
          <span class="count-num">{{ fmtNum(bird.searchCount) }}</span>
          <span class="count-label">搜索量</span>
        </div>
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
        { id: 1, name: '东方白鹳', region: '东亚', habit: '群居水鸟，善于飞行和涉水觅食', description: '大型涉禽，全身洁白，翅膀末端黑色。国家一级保护动物。', searchCount: 150000, image: 'pages/assets/images/stork.jpg' },
        { id: 2, name: '朱鹮', region: '陕西洋县', habit: '栖息于山地森林，觅食于水田沼泽', description: '全身粉红色，被誉为"东方宝石"，世界珍稀鸟类之一。', searchCount: 120000, image: 'pages/assets/images/ibis.jpg' },
        { id: 3, name: '丹顶鹤', region: '东北亚', habit: '善于舞蹈，多在沼泽和湿地活动', description: '头顶鲜红，全身洁白，象征吉祥和长寿。', searchCount: 100000, image: 'pages/assets/images/crane.jpg' },
        { id: 4, name: '黄鹂', region: '华东、华南', habit: '栖息于森林果园，鸣声优美', description: '体型娇小，雄鸟黄黑相间，有"黄衣公子"美称。', searchCount: 80000, image: 'pages/assets/images/oriole.jpg' },
        { id: 5, name: '金丝雀', region: '全国', habit: '善于歌唱，性情活泼', description: '羽毛金黄，歌声婉转动听，受欢迎的笼养鸟类。', searchCount: 75000, image: 'pages/assets/images/canary.jpg' },
        { id: 6, name: '燕子', region: '全国广泛', habit: '善于筑巢，飞行敏捷', description: '春来秋去，在民间文化中备受喜爱。', searchCount: 65000, image: 'pages/assets/images/swallow.jpg' },
        { id: 7, name: '鹦鹉', region: '南方', habit: '群居，善于模仿人声', description: '色彩艳丽，聪明伶俐，深受欢迎的宠物鸟类。', searchCount: 55000, image: 'pages/assets/images/parrot.jpg' },
        { id: 8, name: '猫头鹰', region: '全国', habit: '夜行性，善于捕食', description: '目光锐利，头部可旋转270度，优秀的夜间猎手。', searchCount: 45000, image: 'pages/assets/images/owl.jpg' },
        { id: 9, name: '啄木鸟', region: '温带森林', habit: '啄木觅食，守护森林', description: '森林医生，对维护生态平衡有重要作用。', searchCount: 35000, image: 'pages/assets/images/woodpecker.jpg' },
        { id: 10, name: '翠鸟', region: '江河湖泊', habit: '捕食小鱼，栖息水边', description: '羽毛艳丽，蓝绿相间，被誉为"飞翔的宝石"。', searchCount: 30000, image: 'pages/assets/images/kingfisher.jpg' },
      ]
    }
  },
  methods: {
    getBirdImg(filename) { return getOSSUrl(filename, 'medium') },
    onImgError(e) { e.target.src = 'data:image/svg+xml,' + encodeURIComponent('<svg width="80" height="80" xmlns="http://www.w3.org/2000/svg"><rect width="80" height="80" fill="#f0f0f0"/><text x="40" y="44" text-anchor="middle" fill="#999" font-size="12">暂无</text></svg>') },
    fmtNum(n) { return n >= 10000 ? (n / 10000).toFixed(1) + '万' : n.toLocaleString() }
  }
}
</script>

<style scoped>
.ranking-page { max-width: 800px; margin: 0 auto; padding: 24px 20px; }
.page-header { text-align: center; margin-bottom: 28px; }
.page-header h1 { font-size: 24px; color: var(--color-text); margin-bottom: 4px; }
.page-header p { font-size: 14px; color: var(--color-text-secondary); }

.ranking-list { display: flex; flex-direction: column; gap: 10px; }
.rank-item {
  display: flex; align-items: center; gap: 16px;
  background: var(--color-surface); border-radius: var(--radius-md);
  padding: 16px 20px; border: 1px solid var(--color-border);
  transition: all var(--transition-normal);
  animation: fadeIn 0.4s ease both;
}
.rank-item:hover {
  box-shadow: var(--shadow-md);
  transform: translateX(4px);
}
@keyframes fadeIn { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: translateY(0); } }

.rank-num {
  width: 36px; height: 36px;
  display: flex; align-items: center; justify-content: center;
  font-size: 16px; font-weight: 800;
  border-radius: var(--radius-sm);
  background: var(--color-bg); color: var(--color-text-secondary);
  flex-shrink: 0;
}
.rank-num.rank-1 { background: linear-gradient(135deg, #fbbf24, #f59e0b); color: #fff; font-size: 20px; }
.rank-num.rank-2 { background: linear-gradient(135deg, #c0c0c0, #9ca3af); color: #fff; }
.rank-num.rank-3 { background: linear-gradient(135deg, #d97706, #b45309); color: #fff; }

.rank-img {
  width: 64px; height: 64px; border-radius: var(--radius-sm);
  object-fit: cover; flex-shrink: 0; background: var(--color-bg);
}
.rank-info { flex: 1; min-width: 0; }
.rank-name { font-size: 16px; font-weight: 700; color: var(--color-text); margin-bottom: 3px; }
.rank-meta { font-size: 12px; color: var(--color-text-muted); margin-bottom: 4px; }
.rank-desc { font-size: 12px; color: var(--color-text-secondary); line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }

.rank-count {
  text-align: center; flex-shrink: 0;
  padding: 8px 14px; background: var(--color-primary-bg);
  border-radius: var(--radius-sm);
}
.count-num { display: block; font-size: 16px; font-weight: 700; color: var(--color-primary); }
.count-label { font-size: 10px; color: var(--color-text-muted); }

@media (max-width: 768px) {
  .ranking-page { padding: 16px 12px; }
  .rank-item { padding: 12px 14px; gap: 10px; }
  .rank-img { width: 48px; height: 48px; }
  .rank-name { font-size: 14px; }
}
</style>

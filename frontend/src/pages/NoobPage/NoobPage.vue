<template>
  <div class="bird-guide">
    <div class="petals-container">
      <div v-for="n in 24" :key="n" class="petal"></div>
    </div>
    <h1 class="title">菜鸟观鸟全攻略：从装备到寻鸟，做最棒的"抬头族"！</h1>

    <section class="section welcome">
      <h2 class="section-title">🎉 欢迎加入"鸟人"快乐星球！</h2>
      <p class="content">你以为观鸟只是退休大爷的爱好？No no no！这是集野外侦查、时尚穿搭、声纹识别于一身的硬核运动！从今天起，你的日常将变成："刚才飞过去的是白头鹎还是白喉红臀鹎？急，在线等！"</p>
    </section>

    <section class="section">
      <h2 class="section-title">👜 装备篇：轻量化才是王道</h2>
      <ul class="list">
        <li><strong>1. 望远镜（8×42 新手快乐镜）</strong><p class="content">别被影视剧骗了！手持天文望远镜会练出麒麟臂。记住口诀："倍数不过10，口径要够大"，8×42既能看清鸟的翘臀，又能塞进背包侧袋。</p></li>
        <li><strong>2. 鸟类图鉴（电子版更香）</strong><p class="content">遇到不认识的鸟直接拍照识图，比相亲时查对方朋友圈还高效！</p></li>
        <li><strong>3. 隐身皮肤</strong><p class="content">荧光色穿搭≈向鸟群发射"人类来袭"警报。建议参考《刺客信条》配色：灰/绿/大地色，混入环境你就是一棵会移动的树！</p></li>
        <li><strong>4. 生存三件套</strong>
          <ul class="sub-list">
            <li>驱蚊喷雾（蚊子：这是自助餐入场券）</li>
            <li>保温杯（观鸟半小时，找厕所两小时）</li>
            <li>迷你笔记本（记录如"戴胜头顶WiFi信号满格"等迷惑行为）</li>
          </ul>
        </li>
      </ul>
    </section>

    <section class="section">
      <h2 class="section-title">🔍 寻鸟篇：打开你的"鸟类雷达"</h2>
      <h3 class="sub-title">📍 鸟界网红打卡地</h3>
      <ul class="list">
        <li><strong>城市CBD（Bird版）</strong>
          <ul class="sub-list">
            <li>湿地公园：鹭鸟走T台，小䴙䴘玩潜水，夜鹭站在树顶思考鸟生</li>
            <li>小区绿化带：麻雀开早市，乌鸫翻落叶找蚯蚓，珠颈斑鸠在空调外机上蹦迪</li>
            <li>大学校园：喜鹊偷外卖，白头鹎在樱花树上骂街，戴胜摇头晃脑像喝高了</li>
          </ul>
        </li>
        <li><strong>荒野求生区</strong>
          <ul class="sub-list">
            <li>山林：海拔越高，鸟的皮肤越花（红嘴蓝鹊、黑短脚鹎出没）</li>
            <li>农田：白鹭站牛背演《动物世界》，燕子电线杆上开编队会议</li>
            <li>水库/河流：翠鸟玩"闪电俯冲"，鸭子组队冰面漂移（冬季限定）</li>
          </ul>
        </li>
      </ul>
    </section>

    <section class="section">
      <h2 class="section-title">⏰ 寻鸟玄学时刻表</h2>
      <p class="content"><strong>黄金时段：</strong>🌅 清晨5-8点：鸟界早高峰 / 🌇 傍晚4-6点：社畜下班鸟儿归家<br/>
      <strong>季节限定：</strong>🐦 春/秋迁徙季（3-5月、9-11月）/ ❄️ 冬季：鸭子集体表演"冰上芭蕾"</p>
    </section>

    <section class="section">
      <h2 class="section-title">👀 观察篇：你的眼睛就是8K摄像机</h2>
      <ul class="list">
        <li>肉眼扫描可疑晃动（想象自己是《黑客帝国》里的尼奥）</li>
        <li>狙击手式报点："11点钟方向，第五根树枝分叉处！"</li>
        <li>望远镜平移追踪，手抖星人建议靠树练习"人形三脚架"</li>
      </ul>
    </section>

    <section class="section">
      <h2 class="section-title">🚫 禁忌篇：做文明的"偷窥狂"</h2>
      <ul class="list">
        <li>放抖音神曲引鸟（鸟：这届人类不太正常）</li>
        <li>投喂面包渣（你喂的是鸟界地沟油）</li>
        <li>穿高跟鞋闯湿地（别问，问就是拔鞋视频上过热搜）</li>
        <li>见猛禽就喊"老鹰！"（90%是普通鵟，喊错会被笑三年）</li>
      </ul>
    </section>

    <section class="section">
      <h2 class="section-title">💡 终极奥义</h2>
      <p class="content">观鸟不是集邮！哪怕只看到麻雀扯头花，也要骄傲发朋友圈："今日收获【树麻雀·骂街限定皮肤】！"<br/>记住——当你开始纠结"那坨屎是不是寿带拉的"，恭喜，你已晋升为高阶"鸟人"！🦜✨</p>
    </section>
  </div>
</template>

<script>
export default { name: "BirdGuide" }
</script>

<style scoped>
.bird-guide {
  font-family: Arial, sans-serif;
  line-height: 1.6;
  padding: 20px;
  position: relative;
  min-height: 100vh;
  background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
  overflow: hidden;
}
.petals-container { position: fixed; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 1; }
.petal {
  position: absolute;
  background-color: rgba(243, 163, 177, 0.3);
  border-radius: 150% 0 150% 0;
  animation: falling 10s infinite linear;
  width: 15px; height: 15px;
}
@keyframes falling {
  0% { transform: translate(var(--start-x, 0), -10%) rotate(0deg); opacity: 0; }
  10% { opacity: 1; }
  90% { opacity: 1; }
  100% { transform: translate(var(--end-x, 100px), 100vh) rotate(360deg); opacity: 0; }
}
.petal:nth-child(1) { --start-x: 5vw; --end-x: 25vw; animation-delay: 0s; }
.petal:nth-child(2) { --start-x: 15vw; --end-x: 35vw; animation-delay: -1s; }
.petal:nth-child(3) { --start-x: 25vw; --end-x: 45vw; animation-delay: -2s; }
.petal:nth-child(4) { --start-x: 35vw; --end-x: 55vw; animation-delay: -3s; }
.petal:nth-child(5) { --start-x: 45vw; --end-x: 65vw; animation-delay: -4s; }
.petal:nth-child(6) { --start-x: 55vw; --end-x: 75vw; animation-delay: -5s; }
.petal:nth-child(7) { --start-x: 65vw; --end-x: 85vw; animation-delay: -6s; }
.petal:nth-child(8) { --start-x: 75vw; --end-x: 95vw; animation-delay: -7s; }
.petal:nth-child(9) { --start-x: 85vw; --end-x: 105vw; animation-delay: -8s; }
.petal:nth-child(10) { --start-x: 95vw; --end-x: 115vw; animation-delay: -9s; }
.petal:nth-child(11) { --start-x: 0vw; --end-x: 20vw; animation-delay: -5.5s; }
.petal:nth-child(12) { --start-x: 50vw; --end-x: 70vw; animation-delay: -7.5s; }
.petal:nth-child(13) { --start-x: 10vw; --end-x: 30vw; animation-delay: -2.5s; }
.petal:nth-child(14) { --start-x: 20vw; --end-x: 40vw; animation-delay: -3.5s; }
.petal:nth-child(15) { --start-x: 30vw; --end-x: 50vw; animation-delay: -4.5s; }
.petal:nth-child(16) { --start-x: 40vw; --end-x: 60vw; animation-delay: -5.5s; }
.petal:nth-child(17) { --start-x: 60vw; --end-x: 80vw; animation-delay: -6.5s; }
.petal:nth-child(18) { --start-x: 70vw; --end-x: 90vw; animation-delay: -7.5s; }
.petal:nth-child(19) { --start-x: 80vw; --end-x: 100vw; animation-delay: -8.5s; }
.petal:nth-child(20) { --start-x: 90vw; --end-x: 110vw; animation-delay: -9.5s; }
.petal:nth-child(21) { --start-x: 15vw; --end-x: 35vw; animation-delay: -10.5s; }
.petal:nth-child(22) { --start-x: 25vw; --end-x: 45vw; animation-delay: -11.5s; }
.petal:nth-child(23) { --start-x: 35vw; --end-x: 55vw; animation-delay: -12.5s; }
.petal:nth-child(24) { --start-x: 45vw; --end-x: 65vw; animation-delay: -13.5s; }
.petal:nth-child(3n) { width: 12px; height: 12px; }
.petal:nth-child(3n+1) { width: 15px; height: 15px; }
.petal:nth-child(3n+2) { width: 18px; height: 18px; }
.petal:nth-child(2n) { animation-duration: 12s; }
.petal:nth-child(3n) { animation-duration: 15s; }
.petal:nth-child(5n) { animation-duration: 10s; }

.title, .section { position: relative; z-index: 2; }
.section {
  background-color: rgba(255, 255, 255, 0.85);
  border-radius: 10px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
}
.section-title { font-size: 1.3rem; color: #ff7f50; margin-bottom: 10px; }
.sub-title { font-size: 1.1rem; color: #1e90ff; margin-bottom: 8px; }
.content { font-size: 0.95rem; color: #333; }
.list { margin-left: 20px; }
.sub-list { margin-left: 20px; font-size: 0.9rem; color: #666; }
.list li { margin-bottom: 8px; }
strong { font-weight: bold; color: #ff6347; }
h1.title { font-size: 1.8rem; color: #2c3e50; text-align: center; margin-bottom: 20px; padding: 20px; }

@media (max-width: 600px) {
  .title { font-size: 1.3rem; }
  .section-title { font-size: 1.1rem; }
  .content { font-size: 0.85rem; }
}
</style>

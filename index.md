---
layout: home

hero:
  name: EchoMusic
  text: 一款开源简洁高颜值的酷狗第三方客户端
  tagline: 聆听美好，不止旋律
  image:
    src: /title_img/zhi.png
    alt: EchoMusic
  actions:
    - theme: brand
      text: 快速开始
      link: /guide/getting-started
    - theme: alt
      text: 功能介绍
      link: /features/
    - theme: alt
      text: 开发文档
      link: /develop/
      
features:
  - title: 数据安全
    details: 基础保障，所有功能的前提。官方直连、不经第三方，确保用户隐私与数据不被泄露
  - title: 进阶播放能力
    details: 播放器最本质的功能。队列管理、模式切换、音量调节、进度拖动等决定了核心听歌体验
  - title: 多维探索与搜索
    details: 用户主动找歌的关键入口。支持歌曲、歌手、专辑、歌单全方位搜索，快速定位目标内容
  - title: 音乐推荐
    details: 被动发现音乐的价值。基于推荐机制拓展用户曲库，提升使用黏性
  - title: 歌词系统
    details: 显著增强沉浸感与跟唱体验。LRC解析、滚动同步、全屏/桌面歌词是特色亮点，但非基础必须
  - title: 跨平台与系统集成
    details: 覆盖范围与便捷性补充。完整适配三大桌面系统，配合托盘、全局快捷键等，提升易用性与原生感
---

## 获取更多支持

- 访问[GitHub仓库](https://github.com/hoowhoami/EchoMusic)提交问题或贡献代码
- 加入用户交流群获取帮助
  - QQ：1036693403 [进群](https://qm.qq.com/q/8Dq6fkSN4A)

<style scoped>
#star-canvas {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
}

.VPHome {
  position: relative;
  z-index: 1;
}
</style>

<canvas id="star-canvas"></canvas>

<script setup>
import { onMounted, onUnmounted, nextTick } from 'vue'

// 普通封面图片列表
const base = import.meta.env.BASE_URL
const normalImages = [
  `${base}title_img/zhi.png`,
  `${base}title_img/zhi2.png`,
  `${base}title_img/Qzhi.png`,
  `${base}title_img/QQzhi.png`,
]

// 隐藏款图片（出现概率是其他图片的1/5）
const hiddenImage = `${base}title_img/114514.png`

let animationFrameId = null
let particles = []

onMounted(async () => {
  await nextTick()
  
  // 加权随机选择：114514.png 概率为其他图片的 1/5
  // 创建一个加权数组：其他图片各出现5次，隐藏款出现1次
  const weightedImages = [
    ...normalImages.map(img => Array(5).fill(img)).flat(), // 每张普通图片出现5次
    hiddenImage // 隐藏款出现1次
  ]
  
  // 随机选择一张图片
  const randomImage = weightedImages[Math.floor(Math.random() * weightedImages.length)]
  
  // 尝试多种选择器来查找 hero 图片
  const selectors = [
    '.VPHomeHero .VPImage img',
    '.VPHomeHero img',
    'main .VPImage img',
    '[alt="EchoMusic"]'
  ]
  
  let heroImage = null
  for (const selector of selectors) {
    heroImage = document.querySelector(selector)
    if (heroImage) break
  }
  
  // 设置图片的函数
  const setImage = (imgElement, imageSrc) => {
    imgElement.src = imageSrc
    imgElement.alt = 'EchoMusic'
    // 如果是 emoji4.png，缩放到 1.5 倍
    if (imageSrc.includes('emoji4.png')) {
      imgElement.style.transform = 'scale(1.5)'
      imgElement.style.transformOrigin = 'center'
    } else {
      // 重置其他图片的缩放
      imgElement.style.transform = ''
      imgElement.style.transformOrigin = ''
    }
  }
  
  // 如果找到了图片元素，替换它
  if (heroImage) {
    setImage(heroImage, randomImage)
  } else {
    // 如果没找到，延迟再试一次（等待 VitePress 渲染完成）
    setTimeout(() => {
      for (const selector of selectors) {
        heroImage = document.querySelector(selector)
        if (heroImage) {
          setImage(heroImage, randomImage)
          break
        }
      }
    }, 100)
  }
  
  // 初始化星星特效
  initStarEffect()
})

onUnmounted(() => {
  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId)
  }
})

function initStarEffect() {
  const canvas = document.getElementById('star-canvas')
  if (!canvas) return
  
  const ctx = canvas.getContext('2d')
  let width = canvas.width = window.innerWidth
  let height = canvas.height = window.innerHeight
  
  const config = {
    spawnRate: 12,
    startSpeed: 0.6,
    attraction: 0.015,
    mouseForce: 0.05,
    maxMouseForce: 1.5,
    maxStarSpeed: 3.0,
    friction: 0.98,
    minDriftSpeed: 0.3,
    starBaseSize: 4,
    circleRadius: 600
  }
  
  const mouse = {
    x: undefined,
    y: undefined,
    vx: 0,
    vy: 0,
    lastX: 0,
    lastY: 0,
    isMoving: false,
    timer: null
  }
  
  const resize = () => {
    width = canvas.width = window.innerWidth
    height = canvas.height = window.innerHeight
  }
  
  window.addEventListener('resize', resize)
  
  window.addEventListener('mousemove', (e) => {
    mouse.x = e.x
    mouse.y = e.y
    mouse.vx = e.x - mouse.lastX
    mouse.vy = e.y - mouse.lastY
    mouse.lastX = e.x
    mouse.lastY = e.y
    mouse.isMoving = true
    
    clearTimeout(mouse.timer)
    mouse.timer = setTimeout(() => {
      mouse.vx = 0
      mouse.vy = 0
      mouse.isMoving = false
      mouse.x = undefined
      mouse.y = undefined
    }, 100)
  })
  
  class Star {
    constructor(centerX, centerY) {
      const angle = Math.random() * Math.PI * 2
      const radius = Math.random() * config.circleRadius * 0.3 + config.circleRadius * 0.1
      this.x = centerX + Math.cos(angle) * radius
      this.y = centerY + Math.sin(angle) * radius
      
      const driftAngle = angle + (Math.random() - 0.5) * 0.5
      const speed = config.startSpeed + Math.random() * 0.3
      
      this.vx = Math.cos(driftAngle) * speed
      this.vy = Math.sin(driftAngle) * speed
      
      this.size = Math.random() * 5 + config.starBaseSize
      this.life = 1
      this.decay = Math.random() * 0.001 + 0.0015
      this.hue = Math.random() * 60 + 180
    }
    
    draw(ctx) {
      ctx.save()
      ctx.translate(this.x, this.y)
      ctx.rotate(this.life * 0.5)
      
      ctx.beginPath()
      const r = this.size
      ctx.moveTo(0, -r)
      ctx.quadraticCurveTo(0, 0, r, 0)
      ctx.quadraticCurveTo(0, 0, 0, r)
      ctx.quadraticCurveTo(0, 0, -r, 0)
      ctx.quadraticCurveTo(0, 0, 0, -r)
      ctx.closePath()
      
      const gradient = ctx.createRadialGradient(0, 0, 0, 0, 0, r)
      gradient.addColorStop(0, `hsla(${this.hue}, 80%, 80%, ${this.life})`)
      gradient.addColorStop(1, `hsla(${this.hue}, 80%, 50%, ${this.life})`)
      
      ctx.fillStyle = gradient
      ctx.fill()
      ctx.restore()
    }
    
    update() {
      if (mouse.x !== undefined) {
        const dx = mouse.x - this.x
        const dy = mouse.y - this.y
        const distance = Math.sqrt(dx*dx + dy*dy)
        
        if (distance < 300) {
          const forceX = dx / distance
          const forceY = dy / distance
          
          this.vx += forceX * config.attraction
          this.vy += forceY * config.attraction
          
          if (mouse.isMoving) {
            let pushX = mouse.vx * config.mouseForce
            let pushY = mouse.vy * config.mouseForce
            
            const pushStrength = Math.sqrt(pushX * pushX + pushY * pushY)
            if (pushStrength > config.maxMouseForce) {
              const scale = config.maxMouseForce / pushStrength
              pushX *= scale
              pushY *= scale
            }
            
            this.vx += pushX
            this.vy += pushY
          }
        }
      }
      
      this.vx *= config.friction
      this.vy *= config.friction
      
      const currentSpeed = Math.sqrt(this.vx * this.vx + this.vy * this.vy)
      if (currentSpeed > config.maxStarSpeed) {
        const scale = config.maxStarSpeed / currentSpeed
        this.vx *= scale
        this.vy *= scale
      }
      
      if (currentSpeed < config.minDriftSpeed) {
        const heroImage = document.querySelector('.VPHomeHero .VPImage img') || 
                         document.querySelector('.VPHomeHero img')
        if (heroImage) {
          const rect = heroImage.getBoundingClientRect()
          const centerX = rect.left + rect.width / 2
          const centerY = rect.top + rect.height / 2
          const angleToCenter = Math.atan2(this.y - centerY, this.x - centerX)
          this.vx += Math.cos(angleToCenter) * 0.005
          this.vy += Math.sin(angleToCenter) * 0.005
        }
      }
      
      this.x += this.vx
      this.y += this.vy
      this.hue += 0.2
      this.life -= this.decay
    }
  }
  
  let frame = 0
  
  const animate = () => {
    animationFrameId = requestAnimationFrame(animate)
    
    ctx.clearRect(0, 0, width, height)
    
    ctx.globalCompositeOperation = 'lighter'
    
    frame++
    
    // 获取图标位置
    const heroImage = document.querySelector('.VPHomeHero .VPImage img') || 
                     document.querySelector('.VPHomeHero img')
    
    if (heroImage && frame % config.spawnRate === 0) {
      const rect = heroImage.getBoundingClientRect()
      const centerX = rect.left + rect.width / 2
      const centerY = rect.top + rect.height / 2
      particles.push(new Star(centerX, centerY))
    }
    
    for (let i = particles.length - 1; i >= 0; i--) {
      const p = particles[i]
      p.update()
      p.draw(ctx)
      
      if (p.life <= 0) {
        particles.splice(i, 1)
      }
    }
    
    ctx.globalCompositeOperation = 'source-over'
  }
  
  animate()
}
</script>

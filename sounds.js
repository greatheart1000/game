// 音效管理类
class SoundManager {
    constructor() {
        this.sounds = {};
        this.enabled = true;
        this.volume = 0.5;
        this.initializeSounds();
    }

    // 初始化音效
    initializeSounds() {
        // 使用Web Audio API创建音效
        this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        
        // 创建各种音效
        this.sounds = {
            cardDraw: this.createTone(440, 0.1, 'sine'),
            cardPlay: this.createTone(660, 0.2, 'square'),
            damage: this.createTone(220, 0.3, 'sawtooth'),
            heal: this.createTone(880, 0.2, 'sine'),
            turnStart: this.createTone(523, 0.3, 'triangle'),
            gameEnd: this.createTone(330, 0.5, 'sawtooth'),
            buttonClick: this.createTone(800, 0.1, 'square'),
            error: this.createTone(150, 0.2, 'sawtooth')
        };
    }

    // 创建音调
    createTone(frequency, duration, type = 'sine') {
        return () => {
            if (!this.enabled) return;
            
            const oscillator = this.audioContext.createOscillator();
            const gainNode = this.audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(this.audioContext.destination);
            
            oscillator.frequency.setValueAtTime(frequency, this.audioContext.currentTime);
            oscillator.type = type;
            
            gainNode.gain.setValueAtTime(0, this.audioContext.currentTime);
            gainNode.gain.linearRampToValueAtTime(this.volume, this.audioContext.currentTime + 0.01);
            gainNode.gain.exponentialRampToValueAtTime(0.001, this.audioContext.currentTime + duration);
            
            oscillator.start(this.audioContext.currentTime);
            oscillator.stop(this.audioContext.currentTime + duration);
        };
    }

    // 播放音效
    play(soundName) {
        if (this.sounds[soundName]) {
            this.sounds[soundName]();
        }
    }

    // 切换音效开关
    toggle() {
        this.enabled = !this.enabled;
        return this.enabled;
    }

    // 设置音量
    setVolume(volume) {
        this.volume = Math.max(0, Math.min(1, volume));
    }
}

// 动画管理类
class AnimationManager {
    constructor() {
        this.animations = new Map();
    }

    // 卡牌抽取动画
    animateCardDraw(cardElement) {
        cardElement.classList.add('new-card');
        setTimeout(() => {
            cardElement.classList.remove('new-card');
        }, 500);
    }

    // 卡牌使用动画
    animateCardUse(cardElement, targetElement = null) {
        cardElement.style.transition = 'all 0.5s ease-out';
        cardElement.style.transform = 'scale(1.2) rotate(10deg)';
        cardElement.style.opacity = '0.5';
        
        setTimeout(() => {
            cardElement.style.transform = 'scale(0) rotate(180deg)';
            cardElement.style.opacity = '0';
        }, 250);
        
        if (targetElement) {
            setTimeout(() => {
                this.animateDamage(targetElement);
            }, 300);
        }
    }

    // 伤害动画
    animateDamage(targetElement) {
        targetElement.classList.add('damage-flash');
        setTimeout(() => {
            targetElement.classList.remove('damage-flash');
        }, 500);
    }

    // 治疗动画
    animateHeal(targetElement) {
        targetElement.classList.add('heal-glow');
        setTimeout(() => {
            targetElement.classList.remove('heal-glow');
        }, 1000);
    }

    // 高亮动画
    animateHighlight(element) {
        element.classList.add('highlight');
        setTimeout(() => {
            element.classList.remove('highlight');
        }, 1000);
    }

    // 脉冲动画
    animatePulse(element) {
        element.classList.add('pulse');
        setTimeout(() => {
            element.classList.remove('pulse');
        }, 2000);
    }

    // 震动动画
    animateShake(element) {
        element.classList.add('shake');
        setTimeout(() => {
            element.classList.remove('shake');
        }, 500);
    }
}

// 粒子效果类
class ParticleSystem {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.particles = [];
        this.isRunning = false;
    }

    // 创建爆炸效果
    createExplosion(x, y, color = '#ff6b6b', count = 20) {
        for (let i = 0; i < count; i++) {
            this.particles.push({
                x: x,
                y: y,
                vx: (Math.random() - 0.5) * 10,
                vy: (Math.random() - 0.5) * 10,
                life: 1.0,
                decay: 0.02,
                color: color,
                size: Math.random() * 5 + 2
            });
        }
        this.start();
    }

    // 创建治疗效果
    createHealEffect(x, y, color = '#4CAF50', count = 15) {
        for (let i = 0; i < count; i++) {
            this.particles.push({
                x: x + (Math.random() - 0.5) * 20,
                y: y,
                vx: (Math.random() - 0.5) * 2,
                vy: -Math.random() * 3 - 1,
                life: 1.0,
                decay: 0.01,
                color: color,
                size: Math.random() * 3 + 1
            });
        }
        this.start();
    }

    // 开始动画循环
    start() {
        if (!this.isRunning) {
            this.isRunning = true;
            this.animate();
        }
    }

    // 动画循环
    animate() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        for (let i = this.particles.length - 1; i >= 0; i--) {
            const particle = this.particles[i];
            
            // 更新位置
            particle.x += particle.vx;
            particle.y += particle.vy;
            particle.vy += 0.1; // 重力
            
            // 更新生命值
            particle.life -= particle.decay;
            
            // 绘制粒子
            this.ctx.save();
            this.ctx.globalAlpha = particle.life;
            this.ctx.fillStyle = particle.color;
            this.ctx.beginPath();
            this.ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
            this.ctx.fill();
            this.ctx.restore();
            
            // 移除死亡的粒子
            if (particle.life <= 0) {
                this.particles.splice(i, 1);
            }
        }
        
        if (this.particles.length > 0) {
            requestAnimationFrame(() => this.animate());
        } else {
            this.isRunning = false;
        }
    }
}

// 导出到全局
window.SoundManager = SoundManager;
window.AnimationManager = AnimationManager;
window.ParticleSystem = ParticleSystem;

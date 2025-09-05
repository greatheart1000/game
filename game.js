// 三国杀游戏主逻辑
class ThreeKingdomsGame {
    constructor() {
        this.players = [];
        this.currentPlayerIndex = 0;
        this.gamePhase = 'waiting'; // waiting, playing, ended
        this.discardPile = [];
        this.judgmentArea = [];
        this.deck = [];
        this.gameLog = [];
        
        // 初始化音效和动画管理器
        this.soundManager = new SoundManager();
        this.animationManager = new AnimationManager();
        this.particleSystem = new ParticleSystem(document.getElementById('particle-canvas'));
        
        this.initializeGame();
        this.setupEventListeners();
    }

    // 初始化游戏
    initializeGame() {
        this.createDeck();
        this.shuffleDeck();
        this.addLog('游戏初始化完成');
    }

    // 创建卡牌库
    createDeck() {
        this.deck = [];
        
        // 基础牌
        const basicCards = [
            // 杀 (30张)
            ...Array(30).fill().map((_, i) => ({
                id: `kill_${i}`,
                name: '杀',
                type: 'basic',
                suit: this.getRandomSuit(),
                number: this.getRandomNumber(),
                description: '对一名其他角色造成1点伤害',
                effect: 'damage'
            })),
            
            // 闪 (15张)
            ...Array(15).fill().map((_, i) => ({
                id: `dodge_${i}`,
                name: '闪',
                type: 'basic',
                suit: this.getRandomSuit(),
                number: this.getRandomNumber(),
                description: '抵消一次【杀】的效果',
                effect: 'dodge'
            })),
            
            // 桃 (8张)
            ...Array(8).fill().map((_, i) => ({
                id: `peach_${i}`,
                name: '桃',
                type: 'basic',
                suit: this.getRandomSuit(),
                number: this.getRandomNumber(),
                description: '回复1点体力',
                effect: 'heal'
            }))
        ];

        // 装备牌
        const equipmentCards = [
            // 武器
            { id: 'sword_1', name: '青釭剑', type: 'weapon', attack: 2, range: 1, description: '攻击范围+1，攻击力+2' },
            { id: 'sword_2', name: '雌雄双股剑', type: 'weapon', attack: 2, range: 1, description: '攻击范围+1，攻击力+2' },
            { id: 'sword_3', name: '青龙偃月刀', type: 'weapon', attack: 3, range: 2, description: '攻击范围+2，攻击力+3' },
            
            // 防具
            { id: 'armor_1', name: '白银狮子', type: 'armor', defense: 1, description: '防御力+1' },
            { id: 'armor_2', name: '藤甲', type: 'armor', defense: 2, description: '防御力+2' },
            
            // 坐骑
            { id: 'horse_1', name: '赤兔', type: 'horse', speed: 1, description: '移动距离+1' },
            { id: 'horse_2', name: '的卢', type: 'horse', speed: 1, description: '移动距离+1' }
        ];

        // 锦囊牌
        const trickCards = [
            { id: 'trick_1', name: '无中生有', type: 'trick', description: '摸两张牌' },
            { id: 'trick_2', name: '过河拆桥', type: 'trick', description: '弃置一名角色的一张牌' },
            { id: 'trick_3', name: '顺手牵羊', type: 'trick', description: '获得一名角色的一张牌' },
            { id: 'trick_4', name: '借刀杀人', type: 'trick', description: '令一名角色对另一名角色使用【杀】' },
            { id: 'trick_5', name: '无懈可击', type: 'trick', description: '抵消一张锦囊牌的效果' },
            { id: 'trick_6', name: '南蛮入侵', type: 'trick', description: '所有其他角色必须使用【杀】或失去1点体力' },
            { id: 'trick_7', name: '万箭齐发', type: 'trick', description: '所有其他角色必须使用【闪】或失去1点体力' },
            { id: 'trick_8', name: '桃园结义', type: 'trick', description: '所有角色回复1点体力' }
        ];

        this.deck = [...basicCards, ...equipmentCards, ...trickCards];
    }

    // 获取随机花色
    getRandomSuit() {
        const suits = ['♠', '♥', '♦', '♣'];
        return suits[Math.floor(Math.random() * suits.length)];
    }

    // 获取随机数字
    getRandomNumber() {
        return Math.floor(Math.random() * 13) + 1;
    }

    // 洗牌
    shuffleDeck() {
        for (let i = this.deck.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [this.deck[i], this.deck[j]] = [this.deck[j], this.deck[i]];
        }
    }

    // 添加玩家
    addPlayer(name = null) {
        if (this.players.length >= 8) {
            this.addLog('玩家数量已达上限');
            return false;
        }

        const playerId = this.players.length + 1;
        const playerName = name || `玩家${playerId}`;
        
        const player = {
            id: playerId,
            name: playerName,
            hp: 4,
            maxHp: 4,
            hand: [],
            equipment: {
                weapon: null,
                armor: null,
                horse: null
            },
            skills: [],
            isAlive: true
        };

        this.players.push(player);
        this.addLog(`${playerName} 加入了游戏`);
        this.updateUI();
        return true;
    }

    // 开始游戏
    startGame() {
        if (this.players.length < 2) {
            this.addLog('至少需要2名玩家才能开始游戏');
            this.soundManager.play('error');
            return;
        }

        this.gamePhase = 'playing';
        this.currentPlayerIndex = 0;
        
        // 给每个玩家发初始手牌
        this.players.forEach(player => {
            for (let i = 0; i < 4; i++) {
                player.hand.push(this.drawCard());
            }
        });

        this.addLog('游戏开始！');
        this.addLog(`${this.getCurrentPlayer().name} 的回合开始`);
        this.soundManager.play('turnStart');
        this.updateUI();
    }

    // 抽牌
    drawCard() {
        if (this.deck.length === 0) {
            this.reshuffleDeck();
        }
        return this.deck.pop();
    }

    // 重新洗牌（当牌库用完时）
    reshuffleDeck() {
        this.deck = [...this.discardPile];
        this.discardPile = [];
        this.shuffleDeck();
        this.addLog('牌库已重新洗牌');
    }

    // 获取当前玩家
    getCurrentPlayer() {
        return this.players[this.currentPlayerIndex];
    }

    // 结束回合
    endTurn() {
        const currentPlayer = this.getCurrentPlayer();
        this.addLog(`${currentPlayer.name} 结束了回合`);
        
        // 弃牌阶段 - 手牌不能超过体力值
        while (currentPlayer.hand.length > currentPlayer.hp) {
            const cardToDiscard = currentPlayer.hand.pop();
            this.discardPile.push(cardToDiscard);
            this.addLog(`${currentPlayer.name} 弃置了 ${cardToDiscard.name}`);
        }

        // 切换到下一个玩家
        this.currentPlayerIndex = (this.currentPlayerIndex + 1) % this.players.length;
        
        // 检查游戏是否结束
        if (this.checkGameEnd()) {
            return;
        }

        // 开始新回合
        this.startNewTurn();
    }

    // 开始新回合
    startNewTurn() {
        const currentPlayer = this.getCurrentPlayer();
        
        // 摸牌阶段
        for (let i = 0; i < 2; i++) {
            currentPlayer.hand.push(this.drawCard());
        }
        
        this.addLog(`${currentPlayer.name} 的回合开始，摸了两张牌`);
        this.updateUI();
    }

    // 使用卡牌
    useCard(card, target = null) {
        const currentPlayer = this.getCurrentPlayer();
        
        if (!currentPlayer.hand.includes(card)) {
            this.addLog('手牌中没有这张卡');
            return false;
        }

        // 从手牌中移除
        const cardIndex = currentPlayer.hand.indexOf(card);
        currentPlayer.hand.splice(cardIndex, 1);

        // 根据卡牌类型执行效果
        switch (card.type) {
            case 'basic':
                this.useBasicCard(card, target);
                break;
            case 'weapon':
            case 'armor':
            case 'horse':
                this.equipCard(card);
                break;
            case 'trick':
                this.useTrickCard(card, target);
                break;
        }

        this.updateUI();
        return true;
    }

    // 使用基础牌
    useBasicCard(card, target) {
        const currentPlayer = this.getCurrentPlayer();
        
        switch (card.effect) {
            case 'damage':
                if (target && target !== currentPlayer) {
                    this.dealDamage(target, 1);
                    this.addLog(`${currentPlayer.name} 对 ${target.name} 使用了【杀】`);
                    this.soundManager.play('damage');
                }
                break;
            case 'dodge':
                this.addLog(`${currentPlayer.name} 使用了【闪】`);
                this.soundManager.play('cardPlay');
                break;
            case 'heal':
                if (currentPlayer.hp < currentPlayer.maxHp) {
                    currentPlayer.hp++;
                    this.addLog(`${currentPlayer.name} 使用了【桃】，回复了1点体力`);
                    this.soundManager.play('heal');
                }
                break;
        }
        
        this.discardPile.push(card);
    }

    // 装备卡牌
    equipCard(card) {
        const currentPlayer = this.getCurrentPlayer();
        
        // 如果已有同类型装备，先弃置
        if (currentPlayer.equipment[card.type]) {
            this.discardPile.push(currentPlayer.equipment[card.type]);
            this.addLog(`${currentPlayer.name} 弃置了 ${currentPlayer.equipment[card.type].name}`);
        }
        
        currentPlayer.equipment[card.type] = card;
        this.addLog(`${currentPlayer.name} 装备了 ${card.name}`);
    }

    // 使用锦囊牌
    useTrickCard(card, target) {
        const currentPlayer = this.getCurrentPlayer();
        
        switch (card.name) {
            case '无中生有':
                currentPlayer.hand.push(this.drawCard());
                currentPlayer.hand.push(this.drawCard());
                this.addLog(`${currentPlayer.name} 使用了【无中生有】，摸了两张牌`);
                break;
                
            case '过河拆桥':
                if (target && target !== currentPlayer) {
                    // 简化版：随机弃置一张手牌
                    if (target.hand.length > 0) {
                        const randomIndex = Math.floor(Math.random() * target.hand.length);
                        const discardedCard = target.hand.splice(randomIndex, 1)[0];
                        this.discardPile.push(discardedCard);
                        this.addLog(`${currentPlayer.name} 对 ${target.name} 使用了【过河拆桥】，弃置了 ${discardedCard.name}`);
                    }
                }
                break;
                
            case '桃园结义':
                this.players.forEach(player => {
                    if (player.isAlive && player.hp < player.maxHp) {
                        player.hp++;
                    }
                });
                this.addLog(`${currentPlayer.name} 使用了【桃园结义】，所有角色回复了1点体力`);
                break;
                
            default:
                this.addLog(`${currentPlayer.name} 使用了【${card.name}】`);
        }
        
        this.discardPile.push(card);
    }

    // 造成伤害
    dealDamage(target, damage) {
        target.hp -= damage;
        this.addLog(`${target.name} 受到了 ${damage} 点伤害`);
        
        // 播放伤害动画和粒子效果
        const targetElement = document.querySelector(`[data-player-id="${target.id}"]`);
        if (targetElement) {
            this.animationManager.animateDamage(targetElement);
            const rect = targetElement.getBoundingClientRect();
            this.particleSystem.createExplosion(
                rect.left + rect.width / 2,
                rect.top + rect.height / 2,
                '#ff6b6b'
            );
        }
        
        if (target.hp <= 0) {
            target.hp = 0;
            target.isAlive = false;
            this.addLog(`${target.name} 死亡了！`);
            this.soundManager.play('gameEnd');
        }
    }

    // 检查游戏是否结束
    checkGameEnd() {
        const alivePlayers = this.players.filter(player => player.isAlive);
        
        if (alivePlayers.length <= 1) {
            this.gamePhase = 'ended';
            if (alivePlayers.length === 1) {
                this.addLog(`游戏结束！${alivePlayers[0].name} 获胜！`);
            } else {
                this.addLog('游戏结束！平局！');
            }
            return true;
        }
        
        return false;
    }

    // 添加日志
    addLog(message) {
        const timestamp = new Date().toLocaleTimeString();
        this.gameLog.push(`[${timestamp}] ${message}`);
        this.updateGameLog();
    }

    // 更新游戏日志显示
    updateGameLog() {
        const logContent = document.querySelector('.log-content');
        logContent.innerHTML = this.gameLog.slice(-10).map(entry => 
            `<div class="log-entry">${entry}</div>`
        ).join('');
        logContent.scrollTop = logContent.scrollHeight;
    }

    // 更新UI
    updateUI() {
        this.updateCurrentPlayer();
        this.updateOtherPlayers();
        this.updateCenterArea();
        this.updateHandArea();
    }

    // 更新当前玩家显示
    updateCurrentPlayer() {
        const currentPlayer = this.getCurrentPlayer();
        
        document.getElementById('player-name').textContent = currentPlayer.name;
        document.getElementById('player-hp').textContent = currentPlayer.hp;
        document.getElementById('player-max-hp').textContent = currentPlayer.maxHp;
        document.getElementById('player-hand-count').textContent = currentPlayer.hand.length;
        
        // 更新装备显示
        this.updateEquipmentDisplay();
    }

    // 更新装备显示
    updateEquipmentDisplay() {
        const currentPlayer = this.getCurrentPlayer();
        
        ['weapon', 'armor', 'horse'].forEach(type => {
            const slot = document.getElementById(`${type}-slot`);
            const cardDiv = slot.querySelector('.card');
            
            if (currentPlayer.equipment[type]) {
                const equipment = currentPlayer.equipment[type];
                cardDiv.innerHTML = `
                    <div class="card-name">${equipment.name}</div>
                `;
                cardDiv.className = `card ${type}`;
            } else {
                cardDiv.innerHTML = '无';
                cardDiv.className = 'card';
            }
        });
    }

    // 更新其他玩家显示
    updateOtherPlayers() {
        const otherPlayersDiv = document.getElementById('other-players');
        const currentPlayer = this.getCurrentPlayer();
        
        otherPlayersDiv.innerHTML = this.players
            .filter(player => player !== currentPlayer && player.isAlive)
            .map(player => `
                <div class="player-card" data-player-id="${player.id}">
                    <h4>${player.name}</h4>
                    <div class="player-stats">
                        <span>体力: ${player.hp}/${player.maxHp}</span>
                        <span>手牌: ${player.hand.length}</span>
                    </div>
                    <div class="hp-bar">
                        <div class="hp-fill ${player.hp <= 1 ? 'critical' : player.hp <= 2 ? 'low' : ''}" 
                             style="width: ${(player.hp / player.maxHp) * 100}%"></div>
                    </div>
                </div>
            `).join('');
    }

    // 更新中央区域
    updateCenterArea() {
        const discardPileDiv = document.querySelector('#discard-pile .card-stack');
        const judgmentAreaDiv = document.querySelector('#judgment-area .card-stack');
        
        discardPileDiv.innerHTML = this.discardPile.length > 0 ? 
            `<div class="card">弃牌堆 (${this.discardPile.length})</div>` : 
            '空';
            
        judgmentAreaDiv.innerHTML = this.judgmentArea.length > 0 ? 
            `<div class="card">判定区 (${this.judgmentArea.length})</div>` : 
            '空';
    }

    // 更新手牌区域
    updateHandArea() {
        const handCardsDiv = document.querySelector('.hand-cards');
        const currentPlayer = this.getCurrentPlayer();
        
        handCardsDiv.innerHTML = currentPlayer.hand.map(card => `
            <div class="card" data-card-id="${card.id}" title="${card.description}">
                <div class="card-name">${card.name}</div>
                ${card.suit ? `<div class="card-suit">${card.suit}</div>` : ''}
                ${card.number ? `<div class="card-number">${card.number}</div>` : ''}
            </div>
        `).join('');
    }

    // 设置事件监听器
    setupEventListeners() {
        // 开始游戏按钮
        document.getElementById('start-game').addEventListener('click', () => {
            this.soundManager.play('buttonClick');
            this.startGame();
        });

        // 添加玩家按钮
        document.getElementById('add-player').addEventListener('click', () => {
            this.soundManager.play('buttonClick');
            this.addPlayer();
        });

        // 结束回合按钮
        document.getElementById('end-turn').addEventListener('click', () => {
            this.soundManager.play('buttonClick');
            this.endTurn();
        });

        // 游戏规则按钮
        document.getElementById('rules').addEventListener('click', () => {
            this.soundManager.play('buttonClick');
            document.getElementById('rules-modal').style.display = 'block';
        });

        // 音效控制
        document.getElementById('sound-toggle').addEventListener('click', () => {
            const isEnabled = this.soundManager.toggle();
            document.getElementById('sound-toggle').textContent = isEnabled ? '🔊' : '🔇';
        });

        document.getElementById('volume-slider').addEventListener('input', (e) => {
            this.soundManager.setVolume(parseFloat(e.target.value));
        });

        // 关闭弹窗
        document.querySelectorAll('.close').forEach(closeBtn => {
            closeBtn.addEventListener('click', (e) => {
                e.target.closest('.modal').style.display = 'none';
            });
        });

        // 点击弹窗外部关闭
        window.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                e.target.style.display = 'none';
            }
        });

        // 手牌点击事件
        document.addEventListener('click', (e) => {
            if (e.target.closest('.card[data-card-id]')) {
                const cardElement = e.target.closest('.card[data-card-id]');
                const cardId = cardElement.dataset.cardId;
                const card = this.getCurrentPlayer().hand.find(c => c.id === cardId);
                
                if (card) {
                    this.handleCardClick(card, cardElement);
                }
            }
        });

        // 其他玩家点击事件
        document.addEventListener('click', (e) => {
            if (e.target.closest('.player-card[data-player-id]')) {
                const playerElement = e.target.closest('.player-card[data-player-id]');
                const playerId = parseInt(playerElement.dataset.playerId);
                const targetPlayer = this.players.find(p => p.id === playerId);
                
                if (targetPlayer && targetPlayer.isAlive) {
                    this.handlePlayerClick(targetPlayer, playerElement);
                }
            }
        });
    }

    // 处理卡牌点击
    handleCardClick(card, cardElement) {
        // 移除其他卡牌的选中状态
        document.querySelectorAll('.card.selected').forEach(el => {
            el.classList.remove('selected');
        });
        
        // 选中当前卡牌
        cardElement.classList.add('selected');
        
        // 播放音效和动画
        this.soundManager.play('cardDraw');
        this.animationManager.animateHighlight(cardElement);
        
        // 显示卡牌详情
        this.showCardDetails(card);
    }

    // 处理玩家点击
    handlePlayerClick(targetPlayer, playerElement) {
        // 移除其他玩家的选中状态
        document.querySelectorAll('.player-card.selected').forEach(el => {
            el.classList.remove('selected');
        });
        
        // 选中目标玩家
        playerElement.classList.add('selected');
        
        // 检查是否有选中的卡牌
        const selectedCard = document.querySelector('.card.selected');
        if (selectedCard) {
            const cardId = selectedCard.dataset.cardId;
            const card = this.getCurrentPlayer().hand.find(c => c.id === cardId);
            
            if (card && this.canUseCardOnTarget(card, targetPlayer)) {
                this.useCard(card, targetPlayer);
                selectedCard.classList.remove('selected');
            }
        }
    }

    // 检查卡牌是否可以对目标使用
    canUseCardOnTarget(card, target) {
        if (card.effect === 'damage' && target !== this.getCurrentPlayer()) {
            return true;
        }
        if (card.name === '过河拆桥' && target !== this.getCurrentPlayer()) {
            return true;
        }
        return false;
    }

    // 显示卡牌详情
    showCardDetails(card) {
        const modal = document.getElementById('card-modal');
        const details = document.getElementById('card-details');
        
        details.innerHTML = `
            <h2>${card.name}</h2>
            <p><strong>类型:</strong> ${this.getCardTypeName(card.type)}</p>
            ${card.suit ? `<p><strong>花色:</strong> ${card.suit}</p>` : ''}
            ${card.number ? `<p><strong>点数:</strong> ${card.number}</p>` : ''}
            <p><strong>效果:</strong> ${card.description}</p>
        `;
        
        modal.style.display = 'block';
    }

    // 获取卡牌类型名称
    getCardTypeName(type) {
        const typeNames = {
            'basic': '基础牌',
            'weapon': '武器',
            'armor': '防具',
            'horse': '坐骑',
            'trick': '锦囊牌'
        };
        return typeNames[type] || type;
    }
}

// 初始化游戏
let game;

document.addEventListener('DOMContentLoaded', () => {
    game = new ThreeKingdomsGame();
    
    // 默认添加一些玩家
    game.addPlayer('玩家1');
    game.addPlayer('玩家2');
    game.addPlayer('玩家3');
});

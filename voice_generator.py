#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
三国杀游戏语音生成系统
为角色和游戲事件生成TTS语音
"""

import os
import json
import requests
import time
from datetime import datetime
import hashlib
from pathlib import Path
import dashscope

# TTS API配置
# 注意：dashscope SDK 会自动从环境变量 DASHCOPE_API_KEY 读取，
# 或者你可以在代码中显式设置。
# TTS_API_KEY = "sk-e9985a0de2164cce8e9b29cbbd6fdad1"
# 你可以将此行替换为你的实际 API Key，或在环境变量中设置。
dashscope.api_key = "sk-e9985a0de2164cce8e9b29cbbd6fdad1"

# 语音配置
VOICE_OPTIONS = {
    "male_heroic": "Ethan",  # 男性英雄 (如关羽、张飞)
    "male_wise": "Dylan",  # 男性智者 (如诸葛亮、司马懿)
    "female_gentle": "Cherry",  # 女性温柔 (如貂蝉)
    "female_strong": "Chelsie",  # 女性强势 (如孙尚香)
    "narrator": "Ethan"  # 旁白/系统音
}

# 输出目录
VOICE_OUTPUT_DIR = "voices"
CHARACTER_VOICES_DIR = os.path.join(VOICE_OUTPUT_DIR, "characters")
GAME_VOICES_DIR = os.path.join(VOICE_OUTPUT_DIR, "game_events")

# 创建目录
os.makedirs(CHARACTER_VOICES_DIR, exist_ok=True)
os.makedirs(GAME_VOICES_DIR, exist_ok=True)


class VoiceGenerator:
    """语音生成器类"""

    def __init__(self):
        # 使用 dashscope SDK，不再需要手动管理 API URL 和 headers
        self.voice_cache = {}  # 语音缓存避免重复生成

    def generate_tts_voice(self, text, voice_type, output_path):
        """生成TTS语音并保存到指定路径"""
        if not text or not text.strip():
            return None

        # 检查缓存
        cache_key = f"{text}_{voice_type}"
        if cache_key in self.voice_cache:
            return self.voice_cache[cache_key]

        try:
            print(f"🎤 生成语音: {text[:20]}... (voice: {voice_type})")

            # 使用 dashscope SDK 进行 TTS 合成
            response = dashscope.audio.qwen_tts.SpeechSynthesizer.call(
                model="qwen-tts",
                text=text.strip(),
                voice=voice_type
            )

            if response.status_code == 200:
                audio_url = response.output.audio["url"]

                # 下载音频文件
                audio_response = requests.get(audio_url)
                audio_response.raise_for_status()

                # 保存音频文件
                with open(output_path, 'wb') as f:
                    f.write(audio_response.content)

                print(f"✅ 语音生成成功: {os.path.basename(output_path)}")

                # 缓存结果
                self.voice_cache[cache_key] = output_path
                return output_path
            else:
                print(f"❌ 语音生成失败，状态码: {response.status_code}, 错误信息: {response.message}")
                return None

        except Exception as e:
            print(f"❌ 语音生成出错: {str(e)}")
            return None

    def generate_character_voices(self, character_data):
        """为角色生成语音"""
        name = character_data['name']
        title = character_data['title']
        faction = character_data['faction']
        char_type = character_data['type']

        print(f"\n🎭 生成角色语音: {name} ({title})")

        voice_type = self.select_voice_for_character(name, char_type, faction)

        character_voices = {
            "intro": f"吾乃{title}{name}！",
            "attack": self.get_attack_line(name, char_type),
            "defend": self.get_defend_line(name, char_type),
            "skill": self.get_skill_line(name, char_type),
            "damage": self.get_damage_line(name, char_type),
            "death": self.get_death_line(name, char_type),
            "victory": self.get_victory_line(name, char_type)
        }

        special_voices = self.get_special_lines(name, title, char_type, faction)
        character_voices.update(special_voices)

        voice_files = {}
        # 为每个角色创建单独的文件夹
        character_dir = os.path.join(CHARACTER_VOICES_DIR, name)
        os.makedirs(character_dir, exist_ok=True)

        for voice_key, text in character_voices.items():
            if text:
                filename = f"{voice_key}.wav"
                audio_path = os.path.join(character_dir, filename)

                if os.path.exists(audio_path):
                    print(f"🔊 语音已存在，跳过: {audio_path}")
                    voice_files[voice_key] = os.path.relpath(audio_path, VOICE_OUTPUT_DIR).replace("\\", "/")
                    continue

                generated_path = self.generate_tts_voice(text, voice_type, audio_path)
                if generated_path:
                    # 将绝对路径转换为相对路径，以便于配置文件的可移植性
                    voice_files[voice_key] = os.path.relpath(generated_path, VOICE_OUTPUT_DIR).replace("\\", "/")
                    time.sleep(1)  # 避免API调用过快

        voice_config = {
            "character_name": name,
            "voice_type": voice_type,
            "voices": voice_files,
            "generated_at": datetime.now().isoformat()
        }

        config_path = os.path.join(character_dir, "voices.json")
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(voice_config, f, ensure_ascii=False, indent=2)

        print(f"💾 角色语音配置保存: {name}/voices.json")
        return voice_config

    def select_voice_for_character(self, name, char_type, faction):
        """为角色选择合适的声音类型"""
        # 根据角色类型和名字特点选择声音

        # 蜀势力
        if name in ["关羽", "张飞", "赵云", "马超", "黄忠"]:
            return VOICE_OPTIONS["male_heroic"]
        if name in ["诸葛亮", "刘备", "法正"]:
            return VOICE_OPTIONS["male_wise"]

        # 魏势力
        if name in ["曹操", "司马懿", "郭嘉", "荀彧"]:
            return VOICE_OPTIONS["male_wise"]
        if name in ["许褚", "典韦", "夏侯惇", "张辽"]:
            return VOICE_OPTIONS["male_heroic"]

        # 吴势力
        if name in ["孙权", "周瑜", "陆逊"]:
            return VOICE_OPTIONS["male_wise"]
        if name in ["甘宁", "太史慈", "吕蒙"]:
            return VOICE_OPTIONS["male_heroic"]
        if name == "孙尚香":
            return VOICE_OPTIONS["female_strong"]

        # 群雄
        if name in ["吕布"]:
            return VOICE_OPTIONS["male_heroic"]
        if name in ["貂蝉"]:
            return VOICE_OPTIONS["female_gentle"]
        if name in ["华佗", "袁绍"]:
            return VOICE_OPTIONS["male_wise"]

        # 默认根据类型返回
        if char_type == "武将" or char_type == "君主":
            return VOICE_OPTIONS["male_heroic"]
        elif char_type == "谋士" or char_type == "医者":
            return VOICE_OPTIONS["male_wise"]
        elif char_type == "美女":
            return VOICE_OPTIONS["female_gentle"]

        return VOICE_OPTIONS["male_heroic"]  # 默认值

    def get_attack_line(self, name, char_type):
        """获取攻击语音"""
        attack_lines = {
            "关羽": "青龙偃月，斩尽敌寇！",
            "张飞": "燕人张飞在此，谁敢与我一战！",
            "赵云": "常山赵子龙，七进七出！",
            "马超": "西凉马超来也，受死吧！",
            "黄忠": "百步穿杨，老当益壮！",
            "吕布": "人中吕布，马中赤兔！",
            "曹操": "宁教我负天下人，休教天下人负我！",
            "司马懿": "老谋深算，你中计了！",
            "诸葛亮": "运筹帷幄之中，决胜千里之外！",
            "周瑜": "既生瑜，何生亮！受我一击！",
            "孙权": "江东子弟，随我冲锋！",
            "刘备": "仁德之师，所向披靡！",
            "貂蝉": "美人计中，你难逃一死！",
            "董卓": "顺我者昌，逆我者亡！",
            "华佗": "医者仁心，但也有雷霆手段！",
            "孙尚香": "巾帼不让须眉！看招！"
        }

        return attack_lines.get(name, f"吃我一招！{name}来也！")

    def get_defend_line(self, name, char_type):
        """获取防御语音"""
        defend_lines = {
            "关羽": "义薄云天，岂会被你所伤！",
            "张飞": "燕人张飞，岂是易与之辈！",
            "赵云": "一身是胆，何惧之有！",
            "马超": "西凉铁骑，刀枪不入！",
            "黄忠": "老将虽老，宝刀未老！",
            "吕布": "天下第一，岂会怕你！",
            "曹操": "乱世奸雄，岂会中你之计！",
            "司马懿": "隐忍多年，岂会功亏一篑！",
            "诸葛亮": "空城计在此，你奈我何！",
            "周瑜": "美周郎在此，休想伤我！",
            "孙权": "江东基业，岂容你破坏！",
            "刘备": "汉室宗亲，自有天佑！",
            "貂蝉": "闭月羞花，你下得了手吗？",
            "董卓": "天下大权在握，谁敢动我！",
            "华佗": "医术通神，起死回生！",
            "孙尚香": "女儿身，也有英雄胆！"
        }

        return defend_lines.get(name, f"{name}在此，休想伤我！")

    def get_skill_line(self, name, char_type):
        """获取技能语音"""
        skill_lines = {
            "关羽": "武圣显灵，忠义无敌！",
            "张飞": "勇猛无敌，当阳桥断！",
            "赵云": "一身是胆，七进七出！",
            "马超": "锦马超在此，谁来与我一战！",
            "黄忠": "老当益壮，定军山前！",
            "吕布": "方天画戟，赤兔宝马，天下无敌！",
            "曹操": "挟天子以令诸侯，谁与争锋！",
            "司马懿": "鹰视狼顾，你中我计了！",
            "诸葛亮": "卧龙凤雏，得一可安天下！",
            "周瑜": "火攻之计，赤壁鏖战！",
            "孙权": "江东子弟，多才俊，卷土重来！",
            "刘备": "桃园结义，生死与共！",
            "貂蝉": "倾国倾城，闭月羞花！",
            "董卓": "焚书坑儒，天下归心！",
            "华佗": "医术通神，起死回生！",
            "孙尚香": "结姻联谊，共抗强敌！"
        }

        return skill_lines.get(name, f"{name}技能发动！")

    def get_damage_line(self, name, char_type):
        """获取受伤语音"""
        damage_lines = {
            "关羽": "啊！青龙偃月，不甘啊！",
            "张飞": "燕人张飞，岂能倒下！",
            "赵云": "子龙虽伤，斗志不减！",
            "马超": "西凉铁骑，永不言败！",
            "黄忠": "老骥伏枥，志在千里！",
            "吕布": "天下第一，怎会受伤！",
            "曹操": "宁教我负天下人，岂能负我！",
            "司马懿": "隐忍多年，岂能功亏一篑！",
            "诸葛亮": "鞠躬尽瘁，死而后已！",
            "周瑜": "既生瑜，何生亮，不甘啊！",
            "孙权": "江东基业，不能毁于我手！",
            "刘备": "汉室未兴，备不敢亡！",
            "貂蝉": "美人薄命，何其悲哀！",
            "董卓": "天下大权，岂能旁落！",
            "华佗": "医者难自医，何其讽刺！",
            "孙尚香": "夫君...香香...受伤了..."
        }

        return damage_lines.get(name, f"{name}受伤了！")

    def get_death_line(self, name, char_type):
        """获取死亡语音"""
        death_lines = {
            "关羽": "玉可碎而不改其白，竹可焚而不毁其节...",
            "张飞": "燕人张飞，死也不屈！",
            "赵云": "子龙虽死，忠义长存...",
            "马超": "西凉锦马超，来生再战！",
            "黄忠": "老将虽死，英名永存！",
            "吕布": "天下第一，死也光荣！",
            "曹操": "宁教我负天下人，休教天下人负我...",
            "司马懿": "鹰视狼顾，终有一死...",
            "诸葛亮": "鞠躬尽瘁，死而后已...",
            "周瑜": "既生瑜，何生亮，天亡我也！",
            "孙权": "江东子弟，多才俊，我死之后...",
            "刘备": "汉室未兴，备死不瞑目！",
            "貂蝉": "红颜薄命，来世再做美人计！",
            "董卓": "天下大权，终成泡影！",
            "华佗": "医术再高，也难逃一死...",
            "孙尚香": "夫君...香香...先走一步了..."
        }

        return death_lines.get(name, f"{name}虽死，精神永存！")

    def get_victory_line(self, name, char_type):
        """获取胜利语音"""
        victory_lines = {
            "关羽": "忠义之师，终得胜利！",
            "张飞": "燕人张飞，无敌天下！",
            "赵云": "常山赵子龙，所向披靡！",
            "马超": "西凉铁骑，踏平天下！",
            "黄忠": "老将出马，一个顶俩！",
            "吕布": "天下第一，名副其实！",
            "曹操": "乱世奸雄，终得天下！",
            "司马懿": "老谋深算，终成正果！",
            "诸葛亮": "卧龙凤雏，天下归心！",
            "周瑜": "美周郎在此，谁与争锋！",
            "孙权": "江东子弟，多才俊！",
            "刘备": "汉室可兴，天下归心！",
            "貂蝉": "美人计成，天下归心！",
            "董卓": "天下大权，终归于我！",
            "华佗": "医术通神，起死回生！",
            "孙尚香": "谁说女子不如男！"
        }

        return victory_lines.get(name, f"{name}获胜，天下归心！")

    def get_special_lines(self, name, title, char_type, faction):
        """获取特殊语音（基于历史人物特点）"""
        special_lines = {}

        # 基于历史人物的特殊语音
        if name == "关羽":
            special_lines["taunt"] = "匹夫之勇，何足道哉！"
            special_lines["ally"] = "忠义兄弟，生死与共！"
            special_lines["enemy"] = "乱臣贼子，受死吧！"
        elif name == "张飞":
            special_lines["taunt"] = "燕人张飞在此，谁敢与我一战！"
            special_lines["roar"] = "当阳桥头一声吼，吓退曹操百万兵！"
        elif name == "赵云":
            special_lines["rescue"] = "子龙来也，主公莫慌！"
            special_lines["brave"] = "一身是胆，七进七出！"
        elif name == "诸葛亮":
            special_lines["strategy"] = "运筹帷幄之中，决胜千里之外！"
            special_lines["wisdom"] = "智者千虑，必有一得！"
        elif name == "曹操":
            special_lines["ambition"] = "宁教我负天下人，休教天下人负我！"
            special_lines["scheme"] = "兵不厌诈，你中我计了！"
        elif name == "吕布":
            special_lines["arrogant"] = "天下第一，谁能敌我！"
            special_lines["challenge"] = "三英战吕布，何惧之有！"
        elif name == "貂蝉":
            special_lines["charm"] = "倾国倾城，闭月羞花！"
            special_lines["scheme"] = "美人计中，你难逃一死！"

        return special_lines

    def generate_game_event_voices(self):
        """生成游戏事件语音"""
        print("\n🎮 生成游戏事件语音...")

        game_events = {
            # 游戏阶段
            "game_start": "三国杀游戏开始，请各位玩家准备！",
            "game_end": "游戏结束，胜负已分！",
            "turn_start": "回合开始，请行动！",
            "turn_end": "回合结束，下一位玩家！",

            # 身份相关
            "identity_reveal": "身份揭晓，真相大白！",
            "lord_reveal": "主公现身，天下归心！",
            "traitor_reveal": "反贼暴露，人人得而诛之！",
            "loyalist_reveal": "忠臣护主，义薄云天！",
            "spy_reveal": "内奸现身，居心叵测！",

            # 卡牌使用
            "card_draw": "摸牌阶段，手气如何？",
            "card_play": "出牌阶段，策略为先！",
            "equip_use": "装备武器，增强实力！",
            "peach_use": "使用桃酒，恢复体力！",
            "kill_use": "使用杀招，攻击敌人！",
            "dodge_use": "使用闪避，化解攻击！",

            # 锦囊牌
            "trick_use": "锦囊妙计，出奇制胜！",
            "aoe_use": "群体攻击，无差别打击！",
            "delay_trick": "延时锦囊，后患无穷！",
            "negate_use": "无懈可击，化解危机！",

            # 战斗相关
            "damage_deal": "造成伤害，敌人受创！",
            "damage_receive": "受到伤害，小心应对！",
            "heal": "体力恢复，重获新生！",
            "death": "角色死亡，英魂长存！",
            "revive": "角色复活，重返战场！",

            # 装备系统
            "weapon_equip": "装备武器，如虎添翼！",
            "armor_equip": "装备防具，固若金汤！",
            "horse_equip": "装备马匹，日行千里！",

            # 判定系统
            "judgement": "判定阶段，命运如何？",
            "judgement_success": "判定成功，运气不错！",
            "judgement_fail": "判定失败，运气欠佳！",

            # 技能系统
            "skill_activate": "技能发动，效果非凡！",
            "skill_passive": "被动技能，自动触发！",
            "skill_limit": "限定技能，一局一次！",

            # 胜利条件
            "victory_lord": "主公胜利，天下太平！",
            "victory_traitor": "反贼胜利，乱世开启！",
            "victory_loyalist": "忠臣护主，功成名就！",
            "victory_spy": "内奸得逞，居心叵测！",

            # 特殊事件
            "duel_start": "决斗开始，一决生死！",
            "duel_end": "决斗结束，胜负已分！",
            "link_start": "连环开始，休戚与共！",
            "link_end": "连环结束，各安天命！",

            # 提示音效
            "warning": "警告，小心应对！",
            "error": "操作错误，请重试！",
            "success": "操作成功，继续游戏！",
            "info": "游戏提示，请注意！",

            # 氛围音效
            "tension": "气氛紧张，剑拔弩张！",
            "relax": "气氛缓和，暂时安全！",
            "surprise": "出人意料，局势逆转！",
            "climax": "高潮迭起，精彩纷呈！"
        }

        event_voices = {}
        for event_key, text in game_events.items():
            filename = f"event_{event_key}.wav"
            audio_path = os.path.join(GAME_VOICES_DIR, filename)

            if os.path.exists(audio_path):
                print(f"🔊 语音已存在，跳过: {audio_path}")
                event_voices[event_key] = os.path.relpath(audio_path, VOICE_OUTPUT_DIR).replace("\\", "/")
                continue

            generated_path = self.generate_tts_voice(text, VOICE_OPTIONS["narrator"], audio_path)
            if generated_path:
                event_voices[event_key] = os.path.relpath(generated_path, VOICE_OUTPUT_DIR).replace("\\", "/")
                time.sleep(1)

        # 保存游戏事件语音配置
        event_config = {
            "event_voices": event_voices,
            "generated_at": datetime.now().isoformat(),
            "total_events": len(event_voices)
        }

        config_path = os.path.join(GAME_VOICES_DIR, "game_events_voices.json")
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(event_config, f, ensure_ascii=False, indent=2)

        print(f"💾 游戏事件语音配置保存: game_events_voices.json")
        return event_config

    def generate_all_character_voices(self):
        """为所有角色生成语音"""
        print("🎭 开始为所有角色生成语音...")

        # 假设你的角色卡片文件都存放在 'character_cards' 目录下
        character_cards_dir = "character_cards"

        # 创建一个假的 'character_cards' 目录和一些文件以供测试
        os.makedirs(character_cards_dir, exist_ok=True)
        sample_characters = [
            {"name": "关羽", "title": "武圣", "faction": "蜀", "type": "武将"},
            {"name": "诸葛亮", "title": "卧龙", "faction": "蜀", "type": "谋士"},
            {"name": "孙尚香", "title": "枭姬", "faction": "吴", "type": "美女"},
            {"name": "曹操", "title": "魏武帝", "faction": "魏", "type": "君主"},
            {"name": "貂蝉", "title": "闭月", "faction": "群", "type": "美女"},
            {"name": "华佗", "title": "神医", "faction": "群", "type": "医者"}
        ]
        for char in sample_characters:
            with open(os.path.join(character_cards_dir, f"{char['name']}.json"), 'w', encoding='utf-8') as f:
                json.dump(char, f, ensure_ascii=False, indent=2)

        characters = []

        for json_file in os.listdir(character_cards_dir):
            if json_file.endswith('.json') and not json_file.endswith('_voices.json'):
                json_path = os.path.join(character_cards_dir, json_file)
                try:
                    with open(json_path, 'r', encoding='utf-8') as f:
                        character = json.load(f)
                        characters.append(character)
                except Exception as e:
                    print(f"❌ 加载角色失败 {json_file}: {str(e)}")
                    continue

        print(f"📊 共找到 {len(characters)} 个角色")

        voice_configs = []
        for i, character in enumerate(characters, 1):
            print(f"\n[{i:2d}/{len(characters)}] 生成语音: {character['name']}")

            voice_config = self.generate_character_voices(character)
            if voice_config:
                voice_configs.append(voice_config)

            time.sleep(2)

        print(f"\n🎉 角色语音生成完成！共生成 {len(voice_configs)} 个角色的语音")
        return voice_configs

    def create_voice_database(self):
        """创建完整的语音数据库"""
        print("🏗️ 创建完整语音数据库...")

        character_voices = self.generate_all_character_voices()

        game_event_voices = self.generate_game_event_voices()

        voice_database = {
            "database_info": {
                "created_at": datetime.now().isoformat(),
                "version": "1.0",
                "total_characters": len(character_voices),
                "total_game_events": len(game_event_voices.get("event_voices", {}))
            },
            "character_voices": character_voices,
            "game_event_voices": game_event_voices,
            "voice_options": VOICE_OPTIONS
        }

        database_path = os.path.join(VOICE_OUTPUT_DIR, "voice_database.json")
        with open(database_path, 'w', encoding='utf-8') as f:
            json.dump(voice_database, f, ensure_ascii=False, indent=2)

        print(f"💾 完整语音数据库保存: voice_database.json")
        print(f"📊 数据库统计:")
        print(f"   - 角色语音: {len(character_voices)} 个角色")
        print(f"   - 游戏事件语音: {len(game_event_voices.get('event_voices', {}))} 个事件")
        print(f"   - 总语音文件: {len(character_voices) * 7 + len(game_event_voices.get('event_voices', {}))} 个")

        return voice_database


def main():
    """主函数"""
    print("🚀 三国杀游戏语音生成系统启动...")
    print("=" * 60)

    generator = VoiceGenerator()

    voice_database = generator.create_voice_database()

    print("\n🎉 三国杀游戏语音生成完成！")
    print(f"📁 语音文件保存在: {VOICE_OUTPUT_DIR}/")
    print("🎵 您现在可以在游戏中使用这些语音了！")
    print("\n💡 使用说明:")
    print("1. 角色语音在 voices/characters/ 目录")
    print("2. 游戏事件语音在 voices/game_events/ 目录")
    print("3. 完整数据库配置在 voices/voice_database.json")
    print("4. 在游戏中调用相应的语音文件即可")


if __name__ == "__main__":
    main()
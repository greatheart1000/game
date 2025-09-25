#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
三国杀游戏完整语音生成系统
生成游戏所有环节的语音文件
"""

import os
import json
import time
from pathlib import Path
from voice_generator import VoiceGenerator


class GameVoiceGenerator:
    """游戏语音生成器"""

    def __init__(self):
        self.voice_gen = VoiceGenerator()
        self.voice_output_dir = "voices"
        self.game_voices_dir = os.path.join(self.voice_output_dir, "game_events")
        self.character_voices_dir = os.path.join(self.voice_output_dir, "characters")

        # 创建目录
        os.makedirs(self.game_voices_dir, exist_ok=True)
        os.makedirs(self.character_voices_dir, exist_ok=True)

        # 游戏环节语音配置
        self.game_event_voices = {
            # 游戏开始/结束
            "game_start": {
                "text": "欢迎来到三国杀！英雄豪杰，齐聚一堂，谁能笑到最后？",
                "voice": "Ethan",
                "filename": "game_start.wav"
            },
            "game_end_victory": {
                "text": "恭喜获得胜利！你的智慧和勇气让你成为了最后的赢家！",
                "voice": "Serena",
                "filename": "game_victory.wav"
            },
            "game_end_defeat": {
                "text": "很遗憾，这次失败了。但不要气馁，下次一定能取得更好的成绩！",
                "voice": "Jada",
                "filename": "game_defeat.wav"
            },

            # 游戏流程
            "turn_start": {
                "text": "轮到你出牌了，运筹帷幄，决胜千里！",
                "voice": "Dylan",
                "filename": "turn_start.wav"
            },
            "draw_phase": {
                "text": "摸牌阶段，试试你的手气如何！",
                "voice": "Dylan",
                "filename": "draw_phase.wav"
            },
            "play_phase": {
                "text": "出牌阶段，使用你的手牌和技能来击败对手！",
                "voice": "Ethan",
                "filename": "play_phase.wav"
            },
            "discard_phase": {
                "text": "弃牌阶段，合理管理你的手牌数量。",
                "voice": "Ethan",
                "filename": "discard_phase.wav"
            },

            # 游戏控制
            "game_pause": {
                "text": "游戏已暂停，休息片刻，调整策略。",
                "voice": "Dylan",
                "filename": "game_pause.wav"
            },
            "game_resume": {
                "text": "游戏继续，让我们继续这场激烈的对决！",
                "voice": "Ethan",
                "filename": "game_resume.wav"
            },
            "game_restart": {
                "text": "重新开始游戏，新的挑战即将开始！",
                "voice": "Serena",
                "filename": "game_restart.wav"
            },

            # 卡牌使用
            "card_kill": {
                "text": "杀！接招吧！",
                "voice": "Ethan",
                "filename": "card_kill.wav"
            },
            "card_dodge": {
                "text": "闪！轻松躲过！",
                "voice": "Chelsie",
                "filename": "card_dodge.wav"
            },
            "card_peach": {
                "text": "桃！恢复体力，重振旗鼓！",
                "voice": "Jada",
                "filename": "card_peach.wav"
            },
            "card_equip": {
                "text": "装备武器，增强战斗力！",
                "voice": "Ethan",
                "filename": "card_equip.wav"
            },

            # 特殊事件
            "damage_taken": {
                "text": "受到伤害，但不要放弃！",
                "voice": "Serena",
                "filename": "damage_taken.wav"
            },
            "healing": {
                "text": "体力恢复，重新振作起来！",
                "voice": "Jada",
                "filename": "healing.wav"
            },
            "player_death": {
                "text": "一名玩家阵亡，战局发生了变化！",
                "voice": "Dylan",
                "filename": "player_death.wav"
            },
            "judgment_start": {
                "text": "判定阶段，命运即将揭晓！",
                "voice": "Ethan",
                "filename": "judgment_start.wav"
            },

            # 锦囊牌
            "tactic_peach_garden": {
                "text": "桃园结义！众人同心，其利断金！",
                "voice": "Ethan",
                "filename": "tactic_peach_garden.wav"
            },
            "tactic_barbarian": {
                "text": "南蛮入侵！敌军来袭，小心应对！",
                "voice": "Dylan",
                "filename": "tactic_barbarian.wav"
            },
            "tactic_arrow_salvo": {
                "text": "万箭齐发！箭如雨下，无处可逃！",
                "voice": "Ethan",
                "filename": "tactic_arrow_salvo.wav"
            },
            "tactic_duel": {
                "text": "决斗！一对一的较量，胜者为王！",
                "voice": "Dylan",
                "filename": "tactic_duel.wav"
            },
            "tactic_amazing_grace": {
                "text": "五谷丰登！天赐良机，把握机会！",
                "voice": "Serena",
                "filename": "tactic_amazing_grace.wav"
            },

            # 装备相关
            "weapon_equip": {
                "text": "武器在手，战斗力大增！",
                "voice": "Ethan",
                "filename": "weapon_equip.wav"
            },
            "armor_equip": {
                "text": "防具上身，防御力提升！",
                "voice": "Ethan",
                "filename": "armor_equip.wav"
            },
            "horse_equip": {
                "text": "坐骑在手，冲锋陷阵！",
                "voice": "Ethan",
                "filename": "horse_equip.wav"
            },

            # 身份相关
            "identity_reveal": {
                "text": "身份揭晓！真相大白于天下！",
                "voice": "Dylan",
                "filename": "identity_reveal.wav"
            },
            "lord_victory": {
                "text": "主公获胜！天下归心，一统江山！",
                "voice": "Ethan",
                "filename": "lord_victory.wav"
            },
            "rebel_victory": {
                "text": "反贼获胜！推翻暴政，改朝换代！",
                "voice": "Dylan",
                "filename": "rebel_victory.wav"
            },
            "traitor_victory": {
                "text": "内奸获胜！鹬蚌相争，渔翁得利！",
                "voice": "Chelsie",
                "filename": "traitor_victory.wav"
            },

            # 特殊技能
            "skill_activate": {
                "text": "技能发动！特殊能力，扭转乾坤！",
                "voice": "Ethan",
                "filename": "skill_activate.wav"
            },
            "skill_lock": {
                "text": "锁定技发动！无法阻挡的强大力量！",
                "voice": "Dylan",
                "filename": "skill_lock.wav"
            },

            # 警告提示
            "low_health": {
                "text": "体力不足，需要及时治疗！",
                "voice": "Jada",
                "filename": "low_health.wav"
            },
            "no_cards": {
                "text": "手牌不足，谨慎行动！",
                "voice": "Jada",
                "filename": "no_cards.wav"
            },
            "no_target": {
                "text": "没有合适的目标，重新选择策略！",
                "voice": "Jada",
                "filename": "no_target.wav"
            }
        }

        # 角色语音配置
        self.character_voices = {
            # 蜀势力
            "关羽": {
                "kill": {"text": "青龙偃月，斩将夺旗！", "voice": "Ethan"},
                "dodge": {"text": "关某在此，休得猖狂！", "voice": "Ethan"},
                "death": {"text": "大哥，小弟先走一步...", "voice": "Ethan"},
                "victory": {"text": "忠义两全，死而后已！", "voice": "Ethan"},
                "skill": {"text": "武圣在此，谁敢与我一战！", "voice": "Ethan"}
            },
            "张飞": {
                "kill": {"text": "燕人张飞在此！纳命来！", "voice": "Dylan"},
                "dodge": {"text": "谁敢伤我！", "voice": "Dylan"},
                "death": {"text": "哥哥们...张飞先走一步...", "voice": "Dylan"},
                "victory": {"text": "哈哈！这就是与我为敌的下场！", "voice": "Dylan"},
                "skill": {"text": "咆哮！万夫不当之勇！", "voice": "Dylan"}
            },
            "诸葛亮": {
                "kill": {"text": "兵法如神，料敌先机！", "voice": "Ethan"},
                "dodge": {"text": "山人自有妙计！", "voice": "Ethan"},
                "death": {"text": "出师未捷身先死...长使英雄泪满襟...", "voice": "Ethan"},
                "victory": {"text": "运筹帷幄之中，决胜千里之外！", "voice": "Ethan"},
                "skill": {"text": "观星望月，知晓天命！", "voice": "Ethan"}
            },
            "刘备": {
                "kill": {"text": "汉室宗亲，岂能坐视不理！", "voice": "Dylan"},
                "dodge": {"text": "仁者无敌！", "voice": "Dylan"},
                "death": {"text": "二弟三弟...为兄来陪你们了...", "voice": "Dylan"},
                "victory": {"text": "天下苍生，终于得见太平！", "voice": "Dylan"},
                "skill": {"text": "仁德之心，感化天下！", "voice": "Dylan"}
            },
            "赵云": {
                "kill": {"text": "常山赵子龙，来也！", "voice": "Ethan"},
                "dodge": {"text": "七进七出，如入无人之境！", "voice": "Ethan"},
                "death": {"text": "主公...赵云不能再保护您了...", "voice": "Ethan"},
                "victory": {"text": "一身是胆，所向披靡！", "voice": "Ethan"},
                "skill": {"text": "龙胆亮银，枪出如龙！", "voice": "Ethan"}
            },

            # 魏势力
            "曹操": {
                "kill": {"text": "宁教我负天下人，休教天下人负我！", "voice": "Dylan"},
                "dodge": {"text": "乱世之奸雄，治世之能臣！", "voice": "Dylan"},
                "death": {"text": "天下...还未统一...", "voice": "Dylan"},
                "victory": {"text": "天下归心，唯我独尊！", "voice": "Dylan"},
                "skill": {"text": "奸雄本色，逆境重生！", "voice": "Dylan"}
            },
            "司马懿": {
                "kill": {"text": "隐忍多年，就是为了今日！", "voice": "Ethan"},
                "dodge": {"text": "你的计谋，早已被我看穿！", "voice": "Ethan"},
                "death": {"text": "冢虎...终有一失...", "voice": "Ethan"},
                "victory": {"text": "天下大势，终究在我掌控之中！", "voice": "Ethan"},
                "skill": {"text": "反馈忍戒，后发制人！", "voice": "Ethan"}
            },
            "夏侯惇": {
                "kill": {"text": "独眼之将，势不可挡！", "voice": "Dylan"},
                "dodge": {"text": "这点小伤，算什么！", "voice": "Dylan"},
                "death": {"text": "主公...夏侯惇...尽力了...", "voice": "Dylan"},
                "victory": {"text": "魏国大将，永不言败！", "voice": "Dylan"},
                "skill": {"text": "刚烈不屈，以牙还牙！", "voice": "Dylan"}
            },
            "张辽": {
                "kill": {"text": "威震逍遥津，敌军闻风丧胆！", "voice": "Ethan"},
                "dodge": {"text": "突袭！攻其不备！", "voice": "Ethan"},
                "death": {"text": "主公...张辽...先走一步...", "voice": "Ethan"},
                "victory": {"text": "兵贵神速，战无不胜！", "voice": "Ethan"},
                "skill": {"text": "突袭敌营，出其不意！", "voice": "Ethan"}
            },
            "许褚": {
                "kill": {"text": "虎痴在此，谁来与我一战！", "voice": "Dylan"},
                "dodge": {"text": "这身肥肉，可不是白长的！", "voice": "Dylan"},
                "death": {"text": "主公...许褚...不能再保护您了...", "voice": "Dylan"},
                "victory": {"text": "虎痴之勇，天下无双！", "voice": "Dylan"},
                "skill": {"text": "裸衣战敌，力大无穷！", "voice": "Dylan"}
            },

            # 吴势力
            "孙权": {
                "kill": {"text": "江东子弟，何惧于天下！", "voice": "Ethan"},
                "dodge": {"text": "制衡之术，运筹帷幄！", "voice": "Ethan"},
                "death": {"text": "江东...托付给你们了...", "voice": "Ethan"},
                "victory": {"text": "江东基业，永世长存！", "voice": "Ethan"},
                "skill": {"text": "制衡天下，审时度势！", "voice": "Ethan"}
            },
            "周瑜": {
                "kill": {"text": "既生瑜，何生亮！", "voice": "Dylan"},
                "dodge": {"text": "美周郎在此，休得猖狂！", "voice": "Dylan"},
                "death": {"text": "天妒英才...周瑜...不甘啊...", "voice": "Dylan"},
                "victory": {"text": "东吴水师，天下无敌！", "voice": "Dylan"},
                "skill": {"text": "反间之计，挑拨离间！", "voice": "Dylan"}
            },
            "陆逊": {
                "kill": {"text": "书生拜大将，火攻连营！", "voice": "Ethan"},
                "dodge": {"text": "谦逊待人，不骄不躁！", "voice": "Ethan"},
                "death": {"text": "书生...终究难敌武将...", "voice": "Ethan"},
                "victory": {"text": "儒将风范，智勇双全！", "voice": "Ethan"},
                "skill": {"text": "连营火攻，一击必杀！", "voice": "Ethan"}
            },
            "甘宁": {
                "kill": {"text": "锦帆贼来也！接招吧！", "voice": "Dylan"},
                "dodge": {"text": "百骑劫魏营，来去如风！", "voice": "Dylan"},
                "death": {"text": "主公...甘宁...不能再效力了...", "voice": "Dylan"},
                "victory": {"text": "锦帆军所向披靡！", "voice": "Dylan"},
                "skill": {"text": "奇袭敌营，防不胜防！", "voice": "Dylan"}
            },
            "孙尚香": {
                "kill": {"text": "巾帼不让须眉！看招！", "voice": "Chelsie"},
                "dodge": {"text": "女儿身，也有英雄胆！", "voice": "Chelsie"},
                "death": {"text": "夫君...香香...先走一步...", "voice": "Chelsie"},
                "victory": {"text": "谁说女子不如男！", "voice": "Chelsie"},
                "skill": {"text": "结姻联谊，共抗强敌！", "voice": "Chelsie"}
            },

            # 群雄
            "吕布": {
                "kill": {"text": "人中吕布，马中赤兔！", "voice": "Ethan"},
                "dodge": {"text": "三姓家奴？哼！天下无敌！", "voice": "Ethan"},
                "death": {"text": "貂蝉...我来了...", "voice": "Ethan"},
                "victory": {"text": "战神吕布，天下无双！", "voice": "Ethan"},
                "skill": {"text": "无双神力，无人能挡！", "voice": "Ethan"}
            },
            "貂蝉": {
                "kill": {"text": "闭月羞花，倾国倾城！", "voice": "Cherry"},
                "dodge": {"text": "美人计，兵不血刃！", "voice": "Cherry"},
                "death": {"text": "乱世红颜...终究难逃宿命...", "voice": "Cherry"},
                "victory": {"text": "谁说女子只能依附他人？", "voice": "Cherry"},
                "skill": {"text": "离间之计，挑拨离间！", "voice": "Cherry"}
            },
            "华佗": {
                "kill": {"text": "医者仁心，但也有除恶之责！", "voice": "Dylan"},
                "dodge": {"text": "医术高超，妙手回春！", "voice": "Dylan"},
                "death": {"text": "医者...终究医不了自己...", "voice": "Dylan"},
                "victory": {"text": "悬壶济世，医者仁心！", "voice": "Dylan"},
                "skill": {"text": "急救伤病，妙手仁心！", "voice": "Dylan"}
            },
            "袁绍": {
                "kill": {"text": "四世三公，门多故吏！", "voice": "Ethan"},
                "dodge": {"text": "袁本初在此，谁敢放肆！", "voice": "Ethan"},
                "death": {"text": "河北...不能没有我...", "voice": "Ethan"},
                "victory": {"text": "袁氏一族，终将统一天下！", "voice": "Ethan"},
                "skill": {"text": "乱击齐发，箭如雨下！", "voice": "Ethan"}
            },
            "颜良文丑": {
                "kill": {"text": "河北名将，颜良文丑！", "voice": "Dylan"},
                "dodge": {"text": "双雄在此，休得猖狂！", "voice": "Dylan"},
                "death": {"text": "主公...我们...先走一步...", "voice": "Dylan"},
                "victory": {"text": "河北双雄，天下无敌！", "voice": "Dylan"},
                "skill": {"text": "双雄并立，勇冠三军！", "voice": "Dylan"}
            }
        }

    def generate_all_game_voices(self):
        """生成所有游戏环节语音"""
        print("开始生成游戏环节语音...")

        for event_name, voice_config in self.game_event_voices.items():
            try:
                print(f"生成语音: {event_name}")
                filepath = os.path.join(self.game_voices_dir, voice_config["filename"])

                if not os.path.exists(filepath):
                    self.voice_gen.generate_tts_voice(
                        voice_config["text"],
                        voice_config["voice"],
                        filepath
                    )
                    time.sleep(0.5)  # 避免API请求过快
                else:
                    print(f"语音已存在，跳过: {filepath}")

            except Exception as e:
                print(f"生成语音失败 {event_name}: {e}")

        print("游戏环节语音生成完成！")

    def generate_all_character_voices(self):
        """生成所有角色语音"""
        print("开始生成角色语音...")

        for character_name, voices in self.character_voices.items():
            character_dir = os.path.join(self.character_voices_dir, character_name)
            os.makedirs(character_dir, exist_ok=True)

            print(f"生成角色语音: {character_name}")

            for voice_type, voice_config in voices.items():
                try:
                    filename = f"{voice_type}.wav"
                    filepath = os.path.join(character_dir, filename)

                    if not os.path.exists(filepath):
                        self.voice_gen.generate_tts_voice(
                            voice_config["text"],
                            voice_config["voice"],
                            filepath
                        )
                        time.sleep(0.5)
                    else:
                        print(f"角色语音已存在，跳过: {filepath}")

                except Exception as e:
                    print(f"生成角色语音失败 {character_name}.{voice_type}: {e}")

        print("角色语音生成完成！")

    def generate_voice_config(self):
        """生成语音配置文件"""
        config = {
            "game_events": {},
            "characters": {}
        }

        # 游戏事件语音配置
        for event_name, voice_config in self.game_event_voices.items():
            config["game_events"][event_name] = {
                "text": voice_config["text"],
                "file": f"game_events/{voice_config['filename']}"
            }

        # 角色语音配置
        for character_name, voices in self.character_voices.items():
            config["characters"][character_name] = {}
            for voice_type, voice_config in voices.items():
                config["characters"][character_name][voice_type] = {
                    "text": voice_config["text"],
                    "file": f"characters/{character_name}/{voice_type}.wav"
                }

        # 保存配置文件
        config_path = os.path.join(self.voice_output_dir, "voice_config.json")
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

        print(f"语音配置文件已生成: {config_path}")
        return config_path

    def run_all(self):
        """运行完整的语音生成流程"""
        print("=== 三国杀游戏语音生成系统 ===")
        print("开始生成完整的游戏语音...")

        # 生成游戏环节语音
        self.generate_all_game_voices()

        # 生成角色语音
        self.generate_all_character_voices()

        # 生成配置文件
        config_path = self.generate_voice_config()

        print("\n=== 语音生成完成！===")
        print(f"游戏环节语音保存在: {self.game_voices_dir}")
        print(f"角色语音保存在: {self.character_voices_dir}")
        print(f"语音配置文件: {config_path}")
        print(f"总共生成了 {len(self.game_event_voices)} 个游戏语音 + {len(self.character_voices)} 个角色语音")


if __name__ == "__main__":
    generator = GameVoiceGenerator()
    generator.run_all()
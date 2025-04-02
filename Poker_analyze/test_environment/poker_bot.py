import numpy as np
import json
import tensorflow as tf
import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # 設置 TensorFlow 日誌級別

class PokerBot:
    def __init__(self, model_path='model.json'):
        """
        初始化撲克機器人
        model_path: 模型文件路徑
        """
        self.model = self._load_model(model_path)
    
    def _load_model(self, model_path):
        try:
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"模型文件不存在：{model_path}")
                
            print(f"正在載入模型：{model_path}")
            with open(model_path, 'r') as f:
                model_data = json.load(f)
            
            model = tf.keras.Sequential([
                tf.keras.layers.Dense(32, activation='relu', input_shape=(7,)),
                tf.keras.layers.Dense(32, activation='relu'),
                tf.keras.layers.Dense(41, activation='softmax')
            ])
            
            weights = []
            for layer_name in ['dense', 'dense_1', 'dense_2']:
                layer_data = model_data['model_weights'][layer_name][layer_name]
                kernel = np.array(layer_data['kernel:0'])
                bias = np.array(layer_data['bias:0'])
                weights.extend([kernel, bias])
            
            model.set_weights(weights)
            print("模型載入成功")
            return model
            
        except Exception as e:
            print(f"模型載入失敗：{str(e)}")
            raise
    
    def _get_card_value(self, card_str):
        """
        將牌面值轉換為數字
        參數:
            card_str: 牌面值字串（如 'Q'、'K'、'A'）
        返回:
            對應的數值（2-14）
        """
        try:
            # 擴展撲克牌面值映射
            value_map = {
                'T': 10,
                'J': 11,
                'Q': 12,
                'K': 13,
                'A': 14
            }
            
            # 如果是字母牌面，從映射取值
            if card_str in value_map:
                return value_map[card_str]
            # 如果是數字牌面，直接轉換
            elif card_str.isdigit():
                return int(card_str)
            else:
                print(f"無效的牌面值: {card_str}")
                return 0
                
        except Exception as e:
            print(f"牌面值轉換錯誤：{str(e)}")
            return 0  # 發生錯誤時返回預設值
    
    def _determine_stage(self, num_community_cards):
        """
        根據公共牌數量確定遊戲階段
        
        參數:
            num_community_cards: 公共牌數量
            
        返回:
            遊戲階段字符串
        """
        if num_community_cards == 0:
            return 'preflop'
        elif num_community_cards == 3:
            return 'flop'
        elif num_community_cards == 4:
            return 'turn'
        elif num_community_cards == 5:
            return 'river'
        return 'preflop'  # 預設值

    def _calculate_hand_strength(self, hand_cards, community_cards):
        """增強版手牌強度計算"""
        try:
            if not hand_cards or len(hand_cards) < 2:
                return np.array([0.0, 0.0, 0.0, 0.0])

            all_cards = hand_cards + community_cards
            print(f"分析牌面：手牌 {' '.join(hand_cards)}, 公共牌 {' '.join(community_cards)}")

            # 基礎牌力計算
            card_values = [self._get_card_value(card[0]) for card in hand_cards]
            card_suits = [card[1] for card in hand_cards + community_cards]
            max_rank = max(card_values)

            # 計算進階特徵
            suited = len(set(card[1] for card in hand_cards)) == 1
            connected = abs(sorted(card_values)[0] - sorted(card_values)[1]) == 1
            
            # 計算聽牌機會
            straight_draw = self._has_straight_draw(card_values, community_cards)
            flush_draw = self._has_flush_draw(card_suits)
            
            # 計算強度指標
            hand_strength = max_rank / 14.0  # 基礎牌力
            draw_strength = (straight_draw + flush_draw) * 0.2  # 聽牌價值
            position_value = 0.15  # 使用預設位置價值
            pot_odds = 0.12  # 使用預設底池權益

            print(f"手牌強度計算結果：")
            print(f"基礎牌力：{hand_strength:.2f}")
            print(f"聽牌價值：{draw_strength:.2f}")
            print(f"位置價值：{position_value:.2f}")
            print(f"底池權益：{pot_odds:.2f}")

            return np.array([hand_strength, draw_strength, position_value, pot_odds])

        except Exception as e:
            print(f"計算手牌強度時發生錯誤：{str(e)}")
            return np.array([0.0, 0.0, 0.0, 0.0])

    def _calculate_total_strength(self, hand_cards, community_cards, game_state):
        """計算綜合手牌強度"""
        strength_metrics = self._calculate_hand_strength(hand_cards, community_cards)
        
        # 基礎牌力
        base_strength = strength_metrics[0]
        
        # 潛力值
        potential = strength_metrics[1]
        
        # 階段權重
        stage_weight = 1.2 if game_state['stage'] == 'preflop' else 1.0
        
        # 計算總體強度
        total_strength = (base_strength * 0.6 + potential * 0.4) * stage_weight
        
        return total_strength

    def _has_straight_draw(self, card_values, community_cards):
        """計算順子聽牌機會"""
        all_values = card_values + [self._get_card_value(card[0]) for card in community_cards]
        all_values = sorted(set(all_values))
        max_consecutive = 1
        current_consecutive = 1
        
        for i in range(1, len(all_values)):
            if all_values[i] - all_values[i-1] == 1:
                current_consecutive += 1
                max_consecutive = max(max_consecutive, current_consecutive)
            else:
                current_consecutive = 1
                
        return 1.0 if max_consecutive >= 4 else 0.0

    def _has_flush_draw(self, card_suits):
        """計算同花聽牌機會"""
        suit_counts = {}
        for suit in card_suits:
            suit_counts[suit] = suit_counts.get(suit, 0) + 1
        
        return 1.0 if max(suit_counts.values()) >= 4 else 0.0

    def _get_position_weight(self, position):
        """計算位置權重"""
        position_weights = {
            'BTN': 1.0,
            'CO': 0.9,
            'MP': 0.8,
            'UTG': 0.7,
            'SB': 0.6,
            'BB': 0.5
        }
        return position_weights.get(position.upper(), 0.5)
        
    def _preprocess_state(self, game_state):
        """
        將遊戲狀態轉換為模型輸入格式
        """
        state_vector = np.zeros(7)
        
        stage_map = {'preflop': 0, 'flop': 1, 'turn': 2, 'river': 3}
        if game_state['stage'] is not None:
            state_vector[0] = stage_map.get(game_state['stage'].lower(), 0)
        
        if game_state['current_bet'] > 0:
            state_vector[1] = game_state['pot_size'] / game_state['current_bet']
        
        player_stacks = list(game_state['player_stacks'].values())
        if player_stacks:
            state_vector[2] = min(player_stacks) / max(game_state['pot_size'], 1)
        
        state_vector[3:] = self._calculate_hand_strength(
            game_state['hand_cards'],
            game_state['community_cards']
        )
        
        return state_vector.reshape(1, -1)
    
    def _decode_action(self, action_probs, game_state):
        """改進的決策轉換邏輯"""
        probs = action_probs[0]
        max_prob_idx = np.argmax(probs)
        
        # 計算總體手牌強度
        total_strength = self._calculate_total_strength(
            game_state['hand_cards'],
            game_state['community_cards'],
            game_state
        )
        
        # 根據不同階段和手牌強度決定行動
        if game_state['stage'] == 'preflop':
            if total_strength > 0.8:  # 強力手牌如 AK
                return {'action': 'raise', 'amount': '3bb'}
            elif total_strength > 0.6:  # 中強度手牌
                return {'action': 'raise', 'amount': '2bb'}
        else:  # postflop階段
            if total_strength > 0.7:
                if max_prob_idx in [3, 4, 5]:  # 模型建議加注
                    return {'action': 'raise', 'amount': '2bb'}
            elif total_strength > 0.5:
                if max_prob_idx == 2:  # 模型建議跟注
                    return {'action': 'call', 'amount': None}
        
        # 根據模型輸出的標準動作
        actions = {
            0: {'action': 'fold', 'amount': 0},
            1: {'action': 'check', 'amount': 0},
            2: {'action': 'call', 'amount': None},
            3: {'action': 'raise', 'amount': '1bb'},
            4: {'action': 'raise', 'amount': '2bb'},
            5: {'action': 'raise', 'amount': '3bb'}
        }
        
        return actions.get(max_prob_idx, {'action': 'fold', 'amount': 0})
    
    def get_decision(self, game_state):
        """改進的決策函數"""
        try:
            # 過濾無效的公共牌
            community_cards = [
                card for card in game_state.get('community_cards', [])
                if card not in ['NA', '(尚未發牌)']
            ]
            
            # 過濾手牌中的註釋
            hand_cards = [
                card for card in game_state.get('hand_cards', [])
                if not card.startswith('(') and card != 'NA'
            ]
            
            # 更新遊戲狀態
            stage = self._determine_stage(len(community_cards))
            
            # 建立清理後的遊戲狀態
            state = {
                'stage': stage,
                'community_cards': community_cards,
                'hand_cards': hand_cards,
                'pot_size': game_state.get('pot_size', 0),
                'player_stacks': game_state.get('player_stacks', {}),
                'current_bet': game_state.get('current_bet', 0)
            }
            
            # 獲取模型預測和決策
            state_vector = self._preprocess_state(state)
            action_probs = self.model.predict(state_vector, verbose=0)
            decision = self._decode_action(action_probs, state)
            
            return {
                'action': decision['action'],
                'amount': decision['amount'],
                'stage': stage,
                'cards': {
                    'community': community_cards,
                    'hand': hand_cards
                }
            }
        
        except Exception as e:
            print(f"決策過程發生錯誤：{str(e)}")
            return {
                'action': 'fold',
                'amount': 0,
                'error': str(e)
            }
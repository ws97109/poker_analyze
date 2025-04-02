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
    
    def _calculate_hand_strength(self, hand_cards, community_cards):
        """
        計算手牌強度
        參數:
            hand_cards: 手牌列表
            community_cards: 公共牌列表
        返回:
            手牌強度指標數組
        """
        try:
            # 安全檢查
            if not hand_cards or len(hand_cards) < 2:
                print("手牌資訊不完整")
                return np.array([0.0, 0.0, 0.0, 0.0])
                
            # 將手牌和公共牌合併
            all_cards = hand_cards + community_cards
            print(f"分析牌面：手牌 {' '.join(hand_cards)}, 公共牌 {' '.join(community_cards)}")
            
            # 計算手牌中的最大牌面值
            card_values = [self._get_card_value(card[0]) for card in hand_cards]
            max_rank = max(card_values)
            
            # 計算手牌是否為同花色
            is_suited = len(set(card[1] for card in hand_cards)) == 1
            
            # 計算手牌是否為連張
            sorted_values = sorted(card_values)
            is_connected = abs(sorted_values[0] - sorted_values[1]) == 1
            
            # 根據特徵計算手牌強度指標
            strength = max_rank / 14.0
            potential = float(is_suited or is_connected) / 2.0
            
            print(f"手牌強度計算結果：")
            print(f"最大牌值：{max_rank}")
            print(f"同花：{'是' if is_suited else '否'}")
            print(f"連張：{'是' if is_connected else '否'}")
            
            return np.array([strength, potential, 0.0, 0.0])
                
        except Exception as e:
            print(f"計算手牌強度時發生錯誤：{str(e)}")
            return np.array([0.0, 0.0, 0.0, 0.0])
        
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
    
    def _decode_action(self, action_probs):
        """將模型輸出轉換為具體動作"""
        action_idx = np.argmax(action_probs[0])
        
        actions = {
            0: {'action': 'fold', 'amount': 0},
            1: {'action': 'check', 'amount': 0},
            2: {'action': 'call', 'amount': None},
            3: {'action': 'raise', 'amount': '1bb'},
            4: {'action': 'raise', 'amount': '2bb'},
            5: {'action': 'raise', 'amount': '3bb'},
        }
        
        return actions.get(action_idx, {'action': 'fold', 'amount': 0})
    
    def get_decision(self, game_state):
        """
        輸入遊戲狀態，輸出決策
        """
        try:
            # 根據公牌數量判斷階段
            community_cards = game_state.get('community_cards', [])
            num_cards = len(community_cards)
            
            if num_cards == 0:
                stage = 'preflop'
            elif num_cards == 3:
                stage = 'flop'
            elif num_cards == 4:
                stage = 'turn'
            elif num_cards == 5:
                stage = 'river'
            else:
                stage = 'preflop'  # 預設值
                
            # 建立完整的遊戲狀態
            state = {
                'stage': stage,
                'community_cards': community_cards,
                'hand_cards': game_state.get('hand_cards', []),
                'pot_size': game_state.get('pot_size', 0),
                'player_stacks': game_state.get('player_stacks', {}),
                'current_bet': game_state.get('current_bet', 0)
            }
                
            state_vector = self._preprocess_state(state)
            action_probs = self.model.predict(state_vector, verbose=0)
            decision = self._decode_action(action_probs)
            
            return {
                'action': decision['action'],
                'amount': decision['amount'],
                'stage': stage,
                'cards': {
                    'community': community_cards,
                    'hand': state['hand_cards']
                }
            }
                
        except Exception as e:
            print(f"決策過程發生錯誤：{str(e)}")
            return {
                'action': 'fold',  # 發生錯誤時預設 fold
                'amount': 0,
                'error': str(e)
            }
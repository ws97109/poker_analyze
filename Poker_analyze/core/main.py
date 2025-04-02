from screen_capture import ScreenCapture
from poker_analyzer import PokerAnalyzer
from poker_bot import PokerBot
import os
import sys
import mysql.connector
from dotenv import load_dotenv
import asyncio
import websockets
import json

class WebSocketManager:
    def __init__(self, port=3002):
        # 原有的初始化代碼
        self.port = port
        self.clients = set()
        self.screen_capture = None
        self.poker_analyzer = None
        self.poker_bot = None
        self.running = False
        self.system_initialized = False
        
        # 新增資料庫連接
        self.db_pool = None

    async def initialize_database(self):
        try:
            print("初始化資料庫連接...")
            import mysql.connector.pooling
            
            # 使用環境變數進行配置
            dbconfig = {
                "host": os.getenv('DB_HOST', 'localhost'),
                "user": os.getenv('DB_USER'),
                "password": os.getenv('DB_PASSWORD'),
                "database": os.getenv('DB_NAME'),
                "port": int(os.getenv('DB_PORT', '3306')),
                "pool_name": "poker_pool",
                "pool_size": 5
            }
            
            print("正在建立資料庫連接池...")
            self.db_pool = mysql.connector.pooling.MySQLConnectionPool(**dbconfig)
            print("資料庫連接池建立成功")
            return True
            
        except Exception as e:
            print(f"資料庫初始化失敗：{str(e)}")
            raise
        
    async def register(self, websocket):
        self.clients.add(websocket)
        print("新客戶端連接已建立")
        
    async def unregister(self, websocket):
        self.clients.remove(websocket)
        print("客戶端連接已斷開")
        
    async def send_update(self, data):
        if self.clients:
            try:
                await asyncio.gather(
                    *[client.send(json.dumps(data)) for client in self.clients]
                )
                print(f"成功發送更新: {data['type']}")
            except Exception as e:
                print(f"發送更新時發生錯誤: {str(e)}")
    
    async def analyze_image(self, image_path, session_id=None, user_id=None):
        try:
            # 1. 執行圖像分析
            analysis_text = self.poker_analyzer.analyze_poker_table(image_path)
            print("原始分析結果:", analysis_text)
            
            # 2. 解析遊戲狀態
            game_state = {
                'stage': 'preflop',
                'community_cards': [],
                'hand_cards': [],
                'pot_size': 0.0,
                'player_stacks': {},
                'current_bet': 0.0,
                'position': ''
            }
            
            # 保留原有的詳細解析邏輯
            current_section = None
            for line in analysis_text.split('\n'):
                line = line.strip()
                if not line:
                    continue
                    
                if line.endswith('：') or line.endswith(':'):
                    current_section = line[:-1].strip()
                    continue
                
                if current_section == '目前遊戲狀態':
                    game_state['stage'] = line.lower()
                elif current_section == '位置':
                    game_state['position'] = line
                elif current_section == '底池':
                    try:
                        game_state['pot_size'] = float(line.replace('BB', '').strip())
                    except ValueError:
                        print(f"無法轉換底池大小: {line}")
                elif current_section == '公牌':
                    if line.lower() != 'na':
                        game_state['community_cards'] = line.split()
                elif current_section == '手牌':
                    if ':' in line:
                        player, cards = line.split(':', 1)
                        game_state['hand_cards'] = cards.strip().split()
                elif current_section == '玩家持有籌碼':
                    for player_info in line.split(','):
                        if ':' in player_info:
                            player, stack = player_info.split(':')
                            try:
                                game_state['player_stacks'][player.strip()] = float(stack.replace('BB', '').strip())
                            except ValueError:
                                print(f"無法轉換籌碼量: {stack}")

            # 3. 取得機器人決策
            decision = self.poker_bot.get_decision(game_state)
            print("機器人決策:", decision)
            
            # 4. 準備資料庫記錄
            if user_id and session_id:
                # 準備資料庫記錄
                db_record = {
                    'user_id': user_id,
                    'session_id': session_id,
                    'screenshot_path': image_path,
                    'game_state': json.dumps(game_state),
                    'player_cards': ' '.join(game_state['hand_cards']),
                    'board_cards': ' '.join(game_state['community_cards']),
                    'position': game_state['position'],
                    'pot_size': float(game_state['pot_size']),
                    'action_taken': decision['action'],
                    'action_amount': float(decision['amount']) if decision['amount'] else 0.0,
                    'ai_decision': json.dumps(decision)
                }
                
                # 5. 儲存到資料庫
                await self.save_game_record(**db_record)
                print("遊戲記錄已保存到資料庫")
            
            return {
                'type': 'analysis',
                'screenshot': image_path,
                'game_state': game_state,
                'decision': decision,
                'raw_analysis': analysis_text
            }
            
            # 6. 準備回應
            response = {
                'type': 'analysis',
                'screenshot': image_path,
                'game_state': game_state,
                'decision': decision,
                'raw_analysis': analysis_text
            }
            
            # 7. 發送 WebSocket 更新
            await self.send_update(response)
            
            return response
            
        except Exception as e:
            error_message = f"分析過程發生錯誤：{str(e)}"
            print(error_message)
            await self.send_update({
                'type': 'error',
                'message': error_message
            })
            return {
                'type': 'error',
                'message': error_message
            }
    
    def create_analyze_callback(self):
        async def callback(image_path):
            print("收到截圖回調")
            # 修改為使用數字ID而非用戶名稱
            user_info = {
                'session_id': 'test_session',
                'user_id': 1  # 使用整數ID
            }
            await self.analyze_image(
                image_path,
                session_id=user_info['session_id'],
                user_id=user_info['user_id']
            )
        return callback
    
    async def handler(self, websocket):
        await self.register(websocket)
        try:
            async for message in websocket:
                data = json.loads(message)
                print(f"收到命令: {data['command']}")
                
                if data['command'] == 'start':
                    if not self.running:
                        await self.start_analysis()
                elif data['command'] == 'stop':
                    if self.running:
                        await self.stop_analysis()
        except Exception as e:
            print(f"處理WebSocket消息時發生錯誤: {str(e)}")
        finally:
            await self.cleanup()
            await self.unregister(websocket)
    
    async def start_analysis(self):
        try:
            print("開始初始化截圖系統...")
            if not self.screen_capture:
                self.initialize_system()
            
            print("啟動截圖監聽...")
            if not self.running:
                callback = self.create_analyze_callback()
                self.screen_capture.start_key_capture(
                    trigger_key='space',
                    callback=callback
                )
                
                self.running = True
                print("截圖監聽已啟動，請按空白鍵進行截圖")
                
                # 發送狀態更新
                await self.send_update({
                    'type': 'status',
                    'message': '系統已啟動，請按空白鍵進行截圖分析'
                })
            
        except Exception as e:
            error_message = f'啟動系統失敗：{str(e)}'
            print(error_message)
            await self.send_update({
                'type': 'error',
                'message': error_message
            })
        
    async def stop_analysis(self):
        try:
            print("停止系統...")
            if self.screen_capture:
                self.screen_capture.stop_key_capture()
            
            self.running = False
            await self.send_update({
                'type': 'status',
                'message': '系統已停止'
            })
            print("系統已成功停止")
            
        except Exception as e:
            error_message = f'停止系統失敗：{str(e)}'
            print(error_message)
            await self.send_update({
                'type': 'error',
                'message': error_message
            })
    
    async def cleanup(self):
        print("開始清理系統資源...")
        try:
            if self.screen_capture:
                self.screen_capture.stop_key_capture()
            self.running = False
            self.screen_capture = None
            self.poker_analyzer = None
            self.poker_bot = None
            print("系統資源清理完成")
        except Exception as e:
            print(f"清理資源時發生錯誤: {str(e)}")

    def initialize_system(self):
        print("初始化系統組件...")
        try:
            # 載入環境變數
            load_dotenv()
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if not api_key:
                raise ValueError("請設定 ANTHROPIC_API_KEY 環境變數")

            # 確認模型文件存在
            current_dir = os.path.dirname(os.path.abspath(__file__))
            model_path = os.path.join(current_dir, 'model.json')
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"找不到模型文件：{model_path}")

            # 設定擷取區域
            capture_region = (9, 70, 330, 707)

            print("初始化截圖模組...")
            self.screen_capture = ScreenCapture(
                capture_region=capture_region,
                output_dir="poker_captures"
            )
            
            print("初始化分析模組...")
            self.poker_analyzer = PokerAnalyzer(api_key=api_key)
            
            print("初始化決策模組...")
            self.poker_bot = PokerBot(model_path=model_path)
            
            print("驗證所有模組連接...")
            if not all([self.screen_capture, self.poker_analyzer, self.poker_bot]):
                raise RuntimeError("部分模組初始化失敗")
                
            print("系統組件初始化完成")
            
        except Exception as e:
            error_message = f"初始化系統時發生錯誤: {str(e)}"
            print(error_message)
            import traceback
            print(traceback.format_exc())
            raise RuntimeError(error_message) from e

    @staticmethod
    def parse_analyzer_result(analysis_text):
        """解析Claude的分析結果文本"""
        result = {
            'stage': None,
            'community_cards': [],
            'hand_cards': [],
            'pot_size': 0,
            'player_stacks': {},
            'current_bet': 0
        }
        
        current_section = None
        for line in analysis_text.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            if line.endswith('：') or line.endswith(':'):
                current_section = line[:-1].lower()
                continue
                
            if current_section == '階段':
                result['stage'] = line.lower()
            elif current_section == '公共牌':
                result['community_cards'] = line.split()
            elif current_section == '手牌':
                parts = line.split(': ')
                if len(parts) == 2:
                    player, cards = parts
                    result['hand_cards'] = cards.split()
            elif current_section == '底池':
                try:
                    result['pot_size'] = float(line.replace('BB', '').strip())
                except ValueError:
                    pass
            elif current_section == '玩家籌碼':
                parts = line.split(': ')
                if len(parts) == 2:
                    player, amount = parts
                    try:
                        result['player_stacks'][player] = float(amount.replace('BB', '').strip())
                    except ValueError:
                        pass
            elif current_section == '當前下注':
                parts = line.split(': ')
                if len(parts) == 2:
                    player, amount = parts
                    try:
                        result['current_bet'] = float(amount.replace('BB', '').strip())
                    except ValueError:
                        pass
        
        return result

    async def check_system_status(self):
        """檢查系統所有組件的狀態"""
        status = {
            'screen_capture': bool(self.screen_capture),
            'poker_analyzer': bool(self.poker_analyzer),
            'poker_bot': bool(self.poker_bot),
            'running': self.running
        }
        
        await self.send_update({
            'type': 'status',
            'status': status
        })
        
        return all(status.values())

    async def save_game_record(self, **kwargs):
        connection = None
        cursor = None
        try:
            if not self.db_pool:
                raise RuntimeError("資料庫連接池未初始化")
                
            connection = self.db_pool.get_connection()
            cursor = connection.cursor()
            
            # 驗證必要欄位
            required_fields = ['user_id', 'session_id', 'screenshot_path']
            for field in required_fields:
                if not kwargs.get(field):
                    raise ValueError(f"缺少必要欄位：{field}")
            
            query = """
            INSERT INTO game_history 
            (user_id, session_id, screenshot_path, game_state, 
            player_cards, board_cards, position, pot_size, 
            action_taken, action_amount, ai_decision)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            # 使用傳入的參數而不是未定義的變數
            values = (
                kwargs.get('user_id'),
                kwargs.get('session_id'),
                kwargs.get('screenshot_path'),
                kwargs.get('game_state'),
                kwargs.get('player_cards'),
                kwargs.get('board_cards'),
                kwargs.get('position'),
                kwargs.get('pot_size'),
                kwargs.get('action_taken'),
                float(kwargs.get('action_amount', 0)),
                kwargs.get('ai_decision')
            )
            
            cursor.execute(query, values)
            connection.commit()
            
        except Exception as e:
            print(f"保存遊戲記錄失敗：{str(e)}")
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

async def main():
    ws_manager = WebSocketManager()
    
    try:
        print("初始化系統...")
        ws_manager.initialize_system()
        
        print("初始化資料庫連接...")
        await ws_manager.initialize_database()
        
        # 啟動 WebSocket 服務器
        server = await websockets.serve(
            ws_manager.handler,
            "localhost",
            ws_manager.port
        )
        print(f"WebSocket 服務器運行在 port {ws_manager.port}")

        # 啟動截圖監聽
        await ws_manager.start_analysis()
        print("系統就緒，請按空白鍵進行截圖分析...")
        
        # 保持程序運行
        while True:
            await asyncio.sleep(1)
            if not ws_manager.running:
                print("系統已停止運行")
                break
                
    except Exception as e:
        print(f"系統運行錯誤: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        await ws_manager.cleanup()

if __name__ == "__main__":
    print("=== Python 程序啟動 ===")
    print("使用說明：")
    print("- 空白鍵：進行截圖和分析")
    print("- ESC 鍵：停止程序")
    print("- Ctrl+C：強制終止程序")
    
    # 檢查系統權限
    try:
        import ctypes
        if sys.platform == 'darwin':  # macOS
            from AppKit import NSEvent
            mask = NSEvent.eventWithType_location_modifierFlags_timestamp_windowNumber_context_subtype_data1_data2_(
                14, (0, 0), 0, 0, 0, None, 0, 0, 0
            )
            if not mask:
                print("警告：可能需要螢幕截圖權限")
    except Exception as e:
        print(f"權限檢查警告：{str(e)}")
    
    try:
        print("初始化 WebSocket 管理器...")
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n程序被用戶中止")
    except Exception as e:
        print(f"錯誤：{str(e)}")
        import traceback
        print(traceback.format_exc())
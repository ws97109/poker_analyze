from screen_capture import ScreenCapture
from poker_analyzer import PokerAnalyzer
from poker_bot import PokerBot
import os
import sys
from dotenv import load_dotenv
import asyncio
import websockets
import json

class WebSocketManager:
    def __init__(self, port=3002):
        self.port = port
        self.clients = set()
        self.screen_capture = None
        self.poker_analyzer = None
        self.poker_bot = None
        self.running = False
        
        # 新增系統狀態檢查
        self.system_initialized = False
        
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
    
    async def analyze_image(self, image_path):
        try:
            print(f"開始分析圖片: {image_path}")
            # 獲取 Claude API 分析結果
            analysis_text = self.poker_analyzer.analyze_poker_table(image_path)
            print("Claude API 分析結果：")
            print(analysis_text)  # 印出 Claude 分析結果以便檢查
            
            # 解析遊戲狀態
            game_state = {
                'stage': 'preflop',  # 預設狀態
                'community_cards': [],
                'hand_cards': [],
                'pot_size': 0,
                'player_stacks': {},
                'current_bet': 0
            }
            
            # 解析 Claude 返回的文字
            for line in analysis_text.split('\n'):
                line = line.strip()
                if not line:
                    continue
                
                if line.startswith('公牌：'):
                    next_line = next((l.strip() for l in analysis_text.split('\n')[analysis_text.split('\n').index(line)+1:] if l.strip()), '')
                    if next_line and not next_line.startswith('手牌：'):
                        game_state['community_cards'] = next_line.split()
                elif line.startswith('手牌：'):
                    for hand_line in analysis_text.split('\n')[analysis_text.split('\n').index(line)+1:]:
                        if ':' in hand_line:
                            player, cards = hand_line.split(':', 1)
                            if cards.strip():
                                game_state['hand_cards'] = cards.strip().split()
                                break
            
            # 根據公共牌數量判斷階段
            if len(game_state['community_cards']) == 0:
                game_state['stage'] = 'preflop'
            elif len(game_state['community_cards']) == 3:
                game_state['stage'] = 'flop'
            elif len(game_state['community_cards']) == 4:
                game_state['stage'] = 'turn'
            elif len(game_state['community_cards']) == 5:
                game_state['stage'] = 'river'
            
            # 獲取機器人決策
            decision = self.poker_bot.get_decision(game_state)
            
            # 發送分析結果
            await self.send_update({
                'type': 'analysis',
                'screenshot': image_path,
                'game_state': game_state,
                'decision': decision,
                'raw_analysis': analysis_text
            })
            
            print(f"遊戲狀態：{game_state}")
            print(f"機器人決策：{decision}")
            
        except Exception as e:
            error_message = f"分析過程發生錯誤：{str(e)}"
            print(error_message)
            await self.send_update({
                'type': 'error',
                'message': error_message
            })
    
    def create_analyze_callback(self):
        async def callback(image_path):
            print("收到截圖回調")
            await self.analyze_image(image_path)
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
            self.screen_capture.start_key_capture(
                trigger_key='space',
                callback=self.create_analyze_callback()
            )
            
            self.running = True
            
            # 發送狀態更新
            status_message = {
                'type': 'status',
                'message': '系統已啟動，請按空白鍵進行截圖分析'
            }
            if self.clients:
                await self.send_update(status_message)
            print(status_message['message'])
            
        except Exception as e:
            error_message = f'啟動系統失敗：{str(e)}'
            print(error_message)
            if self.clients:
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

# main.py 修改
async def main():
    ws_manager = WebSocketManager()
    
    try:
        # 預先初始化系統
        print("預先初始化系統組件...")
        ws_manager.initialize_system()
        
        # 直接啟動分析系統
        print("自動啟動分析系統...")
        await ws_manager.start_analysis()
        
        # 啟動 WebSocket 服務器
        server = await websockets.serve(
            ws_manager.handler,
            "localhost",
            ws_manager.port
        )
        
        print(f"WebSocket 服務器運行在 port {ws_manager.port}")
        print("系統就緒，請按空白鍵進行截圖分析...")
        
        # 保持服務器運行
        await server.wait_closed()
        
    except Exception as e:
        print(f"服務器執行錯誤: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        await ws_manager.cleanup()

if __name__ == "__main__":
    print("=== Python 程序啟動 ===")
    print(f"當前工作目錄：{os.getcwd()}")
    print(f"Python 路徑：{sys.executable}")
    print(f"Python 版本：{sys.version}")
    
    try:
        print("初始化 WebSocket 管理器...")
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n程序被用戶中止")
    except Exception as e:
        print(f"錯誤：{str(e)}")
        import traceback
        print(traceback.format_exc())
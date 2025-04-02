import os
import subprocess
from datetime import datetime
from pynput import keyboard
import asyncio
import threading

class ScreenCapture:
    def __init__(self, capture_region, output_dir="captures"):
        self.output_dir = output_dir
        self.capture_region = capture_region
        self.ensure_output_directory()
        self._last_capture_path = None
        self.keyboard_listener = None
        self.callback = None
        self._is_listening = False
        self._loop = None
        self._stop_key = keyboard.Key.esc  # 使用 ESC 鍵停止
        print("ScreenCapture 初始化完成")

    def start_key_capture(self, trigger_key='space', callback=None):
        if self._is_listening:
            print("鍵盤監聽已在運行中")
            return

        print("開始初始化鍵盤監聽...")
        self.callback = callback
        
        try:
            self._loop = asyncio.get_running_loop()
        except RuntimeError:
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)

        def on_press(key):
            try:
                # 只監聽空白鍵和 ESC 鍵
                if key == keyboard.Key.space:
                    print("檢測到空白鍵，開始執行截圖...")
                    image_path = self.capture_screen()
                    if image_path and self.callback:
                        print(f"截圖完成，路徑：{image_path}")
                        future = asyncio.run_coroutine_threadsafe(
                            self.callback(image_path),
                            self._loop
                        )
                        future.add_done_callback(
                            lambda f: print("回調執行完成" if not f.exception() else f"回調執行錯誤：{f.exception()}")
                        )
                elif key == keyboard.Key.esc:
                    print("接收到停止命令")
                    self.stop_key_capture()
                    return False
            except Exception as e:
                print(f"按鍵處理錯誤：{str(e)}")

        try:
            self.keyboard_listener = keyboard.Listener(on_press=on_press)
            self.keyboard_listener.start()
            self._is_listening = True
            print("鍵盤監聽器已啟動，按 ESC 鍵可停止程序")
        except Exception as e:
            print(f"監聽器啟動錯誤：{str(e)}")
            self._is_listening = False

    def stop_key_capture(self):
        if self.keyboard_listener:
            print("停止鍵盤監聽...")
            self.keyboard_listener.stop()
            self._is_listening = False
            self.keyboard_listener = None
            self.callback = None
            print("鍵盤監聽已停止")
        
    def ensure_output_directory(self):
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def capture_screen(self):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.output_dir}/poker_table_{timestamp}.png"
            
            print(f"開始執行截圖操作...")
            print(f"截圖區域: {self.capture_region}")
            
            x, y, width, height = self.capture_region
            capture_command = [
                'screencapture',
                '-R', f"{x},{y},{width},{height}",
                '-x',
                filename
            ]
            
            print(f"執行截圖指令: {' '.join(capture_command)}")
            subprocess.run(capture_command, check=True)
            print(f"截圖完成，儲存於: {filename}")
            
            self._last_capture_path = filename
            return filename
            
        except Exception as e:
            print(f"截圖過程發生錯誤：{str(e)}")
            raise

    async def _execute_callback(self, image_path):
        if self.callback:
            try:
                print(f"執行回調函數，處理圖片：{image_path}")
                await self.callback(image_path)
            except Exception as e:
                print(f"回調函數執行失敗：{str(e)}")
                import traceback
                print(traceback.format_exc())

    def on_press(self, key):
        if key == keyboard.Key.space:
            try:
                image_path = self.capture_screen()
                if image_path:
                    asyncio.create_task(self._execute_callback(image_path))
            except Exception as e:
                print(f"處理按鍵事件時發生錯誤：{str(e)}")

    def ensure_permissions(self):
        """確保具有必要的系統權限"""
        try:
            print("正在檢查系統權限...")
            test_path = os.path.join(self.output_dir, 'test_capture.png')
            
            # 測試截圖
            capture_command = [
                'screencapture',
                '-R', '0,0,100,100',
                '-x',
                test_path
            ]
            
            result = subprocess.run(capture_command, 
                                capture_output=True, 
                                text=True)
                                
            if result.returncode == 0 and os.path.exists(test_path):
                print("截圖權限檢查通過")
                os.remove(test_path)  # 清理測試文件
                return True
            else:
                print("警告：缺少截圖權限")
                print("請按照以下步驟設置權限：")
                print("1. 開啟系統設定")
                print("2. 進入隱私權與安全性")
                print("3. 選擇螢幕錄製")
                print("4. 確認已授權給 Python/IDE")
                return False
                
        except Exception as e:
            print(f"權限檢查過程發生錯誤：{str(e)}")
            return False
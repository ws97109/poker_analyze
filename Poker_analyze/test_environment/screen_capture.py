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
        
    def start_key_capture(self, trigger_key='space', callback=None):
        print("初始化鍵盤監聽...")
        if self._is_listening:
            return
            
        self.callback = callback
        self._loop = asyncio.get_event_loop()
        
        def on_press(key):
            if key == keyboard.Key.space:
                print("偵測到空白鍵，開始執行截圖...")
                try:
                    image_path = self.capture_screen()
                    if image_path and self.callback:
                        # 使用 call_soon_threadsafe 確保回調在正確的線程中執行
                        self._loop.call_soon_threadsafe(
                            lambda: asyncio.create_task(self.callback(image_path))
                        )
                except Exception as e:
                    print(f"處理按鍵事件錯誤: {str(e)}")
                    import traceback
                    print(traceback.format_exc())

        # 在新的線程中啟動鍵盤監聽
        def start_listener():
            with keyboard.Listener(on_press=on_press) as listener:
                self.keyboard_listener = listener
                self._is_listening = True
                print("鍵盤監聽器已啟動")
                listener.join()

        threading.Thread(target=start_listener, daemon=True).start()

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
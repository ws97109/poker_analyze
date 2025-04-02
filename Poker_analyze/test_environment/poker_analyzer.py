from anthropic import Anthropic
import base64
import os

class PokerAnalyzer:
    def __init__(self, api_key):
        """
        初始化撲克牌分析器
        api_key: Anthropic API 金鑰
        """
        self.anthropic = Anthropic(api_key=api_key)

    @staticmethod
    def encode_image(image_path):
        """圖片編碼"""
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"找不到圖片檔案：{image_path}")
        
        try:
            with open(image_path, 'rb') as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            raise Exception(f"圖片處理錯誤：{str(e)}")

    def analyze_poker_table(self, image_path):
        """分析撲克牌桌圖片"""
        try:
            print("正在處理圖片...")
            base64_image = self.encode_image(image_path)
            print("圖片處理完成，正在分析...")

            prompt = """你是一位專業的德州撲克玩家和分析師。請分析這張撲克牌桌圖片，並嚴格按照以下格式輸出資訊：

目前遊戲狀態：
（只能填入 preflop/flop/turn/river 其中之一）

位置：
（只能填入 UTG/MP/CO/BTN/SB/BB 其中之一）

底池：
（請填入底池金額，以BB為單位，只需填數字，例如：10.5）

玩家持有籌碼：
（格式為 "玩家名稱:籌碼數量BB"，例如 "Player1:100BB"）

公牌：
（請嚴格按照 數字+花色 格式，花色使用小寫s/h/d/c，例如：As Kd Qc）

手牌：
玩家: As Kc

每個項目務必換行，保持格式一致性。如果某項資訊無法辨識，請填寫 "NA"。"""

            print("正在發送分析請求...")
            message = self.anthropic.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": base64_image
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }]
            )
            
            return message.content[0].text
            
        except Exception as e:
            print(f"分析過程發生錯誤：{str(e)}")
            raise
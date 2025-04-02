import asyncio
from main import WebSocketManager

async def test_database_connection():
    manager = WebSocketManager()
    try:
        await manager.initialize_database()
        print("資料庫連接測試成功")
        
        # 建立測試記錄
        test_record = {
            'user_id': 1,
            'session_id': 'test_session',
            'screenshot_path': 'test_path.png',
            'game_state': '{}',
            'player_cards': 'Ah Kh',
            'board_cards': 'Jc Tc 9c',
            'position': 'BTN',
            'pot_size': 10.5,
            'action_taken': 'raise',
            'action_amount': 3.0,
            'ai_decision': '{}'
        }
        
        # 修改呼叫方式，使用完整的參數字典
        await manager.save_game_record(
            user_id=test_record['user_id'],
            session_id=test_record['session_id'],
            image_path=test_record['screenshot_path'],
            game_state=test_record['game_state'],
            player_cards=test_record['player_cards'],
            board_cards=test_record['board_cards'],
            position=test_record['position'],
            pot_size=test_record['pot_size'],
            action_taken=test_record['action_taken'],
            action_amount=test_record['action_amount'],
            ai_decision=test_record['ai_decision']
        )
        print("測試記錄儲存成功")
        
    except Exception as e:
        print(f"測試失敗：{str(e)}")

if __name__ == "__main__":
    asyncio.run(test_database_connection())
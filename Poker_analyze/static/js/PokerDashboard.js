import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

const PokerDashboard = () => {
    // 狀態管理
    const [isRunning, setIsRunning] = useState(false);
    const [screenshot, setScreenshot] = useState(null);
    const [aiDecision, setAiDecision] = useState(null);
    const [gameHistory, setGameHistory] = useState([]);
    const [selectedHistoryItem, setSelectedHistoryItem] = useState(null);

    // 開始牌局
    const handleStart = async () => {
        try {
            // TODO: 實現與 VS Code 中 main.py 的通信邏輯
            setIsRunning(true);
            // 可能需要使用 WebSocket 或其他通信方式
            console.log('開始牌局');
        } catch (error) {
            console.error('啟動牌局失敗:', error);
        }
    };

    // 結束牌局
    const handleStop = async () => {
        try {
            setIsRunning(false);
            // TODO: 停止截圖和決策程序
            console.log('結束牌局');
        } catch (error) {
            console.error('停止牌局失敗:', error);
        }
    };

    // 載入歷史記錄
    useEffect(() => {
        const fetchGameHistory = async () => {
            try {
                const response = await fetch('/api/game-history');
                const data = await response.json();
                setGameHistory(data);
            } catch (error) {
                console.error('載入歷史記錄失敗:', error);
            }
        };

        fetchGameHistory();
    }, []);

    // 選擇歷史記錄項目
    const handleHistoryItemSelect = (item) => {
        setSelectedHistoryItem(item);
        setScreenshot(item.screenshot_url);
        setAiDecision(item.ai_decision);
    };

    return (
        <div className="flex h-screen p-4 bg-gray-100">
            <div className="w-2/3 pr-4">
                {/* 主要操作區域 */}
                <Card className="mb-4">
                    <CardHeader>
                        <CardTitle>德州撲克決策系統</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="flex space-x-4 mb-4">
                            <Button 
                                onClick={handleStart} 
                                disabled={isRunning}
                                className="bg-green-500 hover:bg-green-600"
                            >
                                開始
                            </Button>
                            <Button 
                                onClick={handleStop} 
                                disabled={!isRunning}
                                className="bg-red-500 hover:bg-red-600"
                            >
                                結束
                            </Button>
                        </div>

                        {/* 截圖顯示區域 */}
                        <div className="grid grid-cols-2 gap-4">
                            <div className="bg-white border rounded p-2">
                                <h3 className="text-lg font-semibold mb-2">截圖畫面</h3>
                                {screenshot ? (
                                    <img 
                                        src={screenshot} 
                                        alt="牌局截圖" 
                                        className="w-full h-64 object-cover"
                                    />
                                ) : (
                                    <p className="text-gray-500">尚未截取畫面</p>
                                )}
                            </div>

                            {/* AI 決策輸出 */}
                            <div className="bg-white border rounded p-2">
                                <h3 className="text-lg font-semibold mb-2">AI 決策</h3>
                                {aiDecision ? (
                                    <pre className="whitespace-pre-wrap">{aiDecision}</pre>
                                ) : (
                                    <p className="text-gray-500">尚無決策</p>
                                )}
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* 歷史記錄區域 */}
            <div className="w-1/3 bg-white border rounded p-4 overflow-y-auto">
                <h2 className="text-xl font-bold mb-4">歷史牌局</h2>
                {gameHistory.map((item) => (
                    <div 
                        key={item.id} 
                        onClick={() => handleHistoryItemSelect(item)}
                        className={`p-2 mb-2 cursor-pointer hover:bg-gray-100 ${
                            selectedHistoryItem?.id === item.id ? 'bg-blue-50' : ''
                        }`}
                    >
                        <div className="flex justify-between">
                            <span>{item.user_name}</span>
                            <span className="text-sm text-gray-500">
                                {new Date(item.timestamp).toLocaleString()}
                            </span>
                        </div>
                        <p className="text-sm text-gray-600">{item.action_taken}</p>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default PokerDashboard;
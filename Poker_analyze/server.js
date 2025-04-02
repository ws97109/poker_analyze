const express = require('express');
const cors = require('cors');
const bcrypt = require('bcryptjs');
const pool = require('./config/database');
const path = require('path');
const http = require('http');
const WebSocket = require('ws');
const { spawn } = require('child_process');
const session = require('express-session');
const fs = require('fs');

// 初始化 Express 應用和服務器
const app = express();
const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

// 全局變量
let pythonProcess = null;
let wsConnection = null;

// 確保截圖目錄存在
const capturesDir = path.join(__dirname, 'poker_captures');
try {
    if (!fs.existsSync(capturesDir)) {
        fs.mkdirSync(capturesDir, { recursive: true });
        console.log('成功創建截圖目錄:', capturesDir);
    }
} catch (error) {
    console.error('創建截圖目錄失敗:', error);
}

// 基礎中間件配置
app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// 靜態文件路由配置
app.use('/poker_captures', express.static(path.join(__dirname, 'poker_captures')));
app.use('/src', express.static('src'));
app.use('/static', express.static(path.join(__dirname, 'static')));

// Session 中間件配置
app.use(session({
    secret: 'your-secret-key',
    resave: false,
    saveUninitialized: false,
    cookie: { secure: false }
}));

// 用戶認證中間件
const authenticateUser = (req, res, next) => {
    if (!req.session.user) {
        return res.redirect('/login.html');
    }
    next();
};

// WebSocket 連接處理
wss.on('connection', (ws) => {
    console.log('新的 WebSocket 連接已建立');
    wsConnection = ws;
    
    if (wsConnection) {
        console.log('自動發送啟動命令...');
        wsConnection.send(JSON.stringify({ command: 'start' }));
    }
    
    ws.on('message', (message) => {
        console.log('收到消息:', message.toString());
        try {
            const data = JSON.parse(message.toString());
            console.log('解析後的消息:', data);
            if (wsConnection) {
                wsConnection.send(JSON.stringify({ 
                    type: 'log',
                    data: `收到命令: ${data.command}`
                }));
            }
        } catch (error) {
            console.error('處理消息時發生錯誤:', error);
        }
    });

    ws.on('close', () => {
        console.log('WebSocket 連接已關閉');
        wsConnection = null;
        if (pythonProcess) {
            pythonProcess.kill();
            pythonProcess = null;
        }
    });
});

// API 路由配置
// 儀表板路由
app.get('/dashboard.html', authenticateUser, (req, res, next) => {
    next();
});

// 歷史記錄 API
app.get('/api/game-dates', async (req, res) => {
    try {
        const [results] = await pool.execute(`
            SELECT DISTINCT 
                DATE_FORMAT(timestamp, '%Y-%m-%d') as date,
                DATE_FORMAT(timestamp, '%Y年%m月%d日') as formatted_date
            FROM game_history 
            ORDER BY date DESC
        `);
        
        if (results.length === 0) {
            return res.json([]);
        }

        console.log('Retrieved dates:', results); // 添加日誌以便調試
        res.json(results);
    } catch (error) {
        console.error('獲取日期列表失敗:', error);
        res.status(500).json({ message: '獲取日期列表失敗' });
    }
});

app.get('/api/game-history', async (req, res) => {
    try {
        let query = `
            SELECT 
                gh.*,
                u.name as user_name,
                DATE_FORMAT(gh.timestamp, '%Y-%m-%d %H:%i:%s') as formatted_time
            FROM game_history gh
            JOIN users u ON gh.user_id = u.id
        `;
        
        if (req.query.date) {
            query += ` WHERE DATE(gh.timestamp) = ?`;
            const [records] = await pool.execute(query, [req.query.date]);
            const recordsWithUrls = processRecords(records);
            res.json(recordsWithUrls);
        } else {
            query += ` ORDER BY gh.timestamp DESC LIMIT 20`;
            const [records] = await pool.execute(query);
            const recordsWithUrls = processRecords(records);
            res.json(recordsWithUrls);
        }
        
    } catch (error) {
        console.error('獲取歷史記錄失敗:', error);
        res.status(500).json({ message: '獲取歷史記錄失敗' });
    }
});

function processRecords(records) {
    return records.map(record => ({
        id: record.id,
        username: record.user_name,
        screenshot_url: `/poker_captures/${path.basename(record.screenshot_path)}`,
        player_cards: record.player_cards,
        board_cards: record.board_cards,
        position: record.position,
        pot_size: record.pot_size,
        action_taken: record.action_taken,
        action_amount: record.action_amount,
        formatted_time: record.formatted_time
    }));
}

// 系統控制 API
app.post('/api/test-connection', async (req, res) => {
    try {
        const [result] = await pool.execute('SELECT 1');
        res.json({ 
            message: '連接測試成功',
            database: 'OK'
        });
    } catch (error) {
        console.error('測試失敗:', error);
        res.status(500).json({ 
            message: '測試失敗',
            error: error.message 
        });
    }
});

app.post('/api/start-system', async (req, res) => {
    try {
        if (pythonProcess) {
            return res.status(400).json({ message: '系統已在運行中' });
        }

        console.log('開始啟動 Python 進程...');
        const pythonPath = path.join(__dirname, 'core', 'main.py');
        
        console.log('系統配置信息：', {
            pythonPath: pythonPath,
            pythonExecutable: '/Users/weiqihong/Desktop/poker_analysis_system/venv/bin/python',
            工作目錄: path.join(__dirname, 'core')
        });

        pythonProcess = spawn('/Users/weiqihong/Desktop/poker_analysis_system/venv/bin/python', [pythonPath], {
            env: {
                ...process.env,
                PYTHONUNBUFFERED: '1',
                PYTHONPATH: path.join(__dirname, 'core')
            },
            cwd: process.cwd(),
            stdio: ['inherit', 'pipe', 'pipe']
        });

        pythonProcess.stdout.on('data', (data) => {
            const output = data.toString().trim();
            console.log(`Python 輸出: ${output}`);
            if (wsConnection) {
                if (output.includes('截圖完成，路徑：')) {
                    const screenshotPath = output.split('路徑：')[1].trim();
                    const filename = screenshotPath.split('/').pop();
                    wsConnection.send(JSON.stringify({ 
                        type: 'analysis',
                        screenshot: filename
                    }));
                } else if (output.includes('機器人決策:')) {
                    try {
                        const decisionStr = output.split('機器人決策:')[1].trim();
                        const jsonStr = decisionStr.replace(/'/g, '"');
                        const decision = JSON.parse(jsonStr);
                        wsConnection.send(JSON.stringify({ 
                            type: 'analysis',
                            decision: decision
                        }));
                    } catch (error) {
                        console.error('解析決策結果失敗:', error);
                    }
                } else {
                    wsConnection.send(JSON.stringify({ 
                        type: 'log', 
                        data: output 
                    }));
                }
            }
        });

        pythonProcess.stderr.on('data', (data) => {
            const errorOutput = data.toString().trim();
            console.error(`Python 錯誤: ${errorOutput}`);
            if (wsConnection) {
                wsConnection.send(JSON.stringify({ 
                    type: 'error', 
                    data: errorOutput
                }));
            }
        });

        pythonProcess.on('error', (error) => {
            console.error('Python 進程啟動錯誤:', error);
            if (wsConnection) {
                wsConnection.send(JSON.stringify({
                    type: 'error',
                    data: `Python 進程啟動失敗: ${error.message}`
                }));
            }
        });

        pythonProcess.on('exit', (code) => {
            console.log(`Python 進程結束，退出碼：${code}`);
            if (code !== 0 && wsConnection) {
                wsConnection.send(JSON.stringify({
                    type: 'error',
                    data: `Python 進程異常退出，退出碼：${code}`
                }));
            }
            pythonProcess = null;
        });

        res.json({ 
            message: '系統已啟動',
            pythonPath: pythonPath
        });

    } catch (error) {
        console.error('啟動系統時發生錯誤:', error);
        res.status(500).json({ 
            message: '系統啟動失敗',
            error: error.message
        });
    }
});

app.post('/api/stop-system', async (req, res) => {
    try {
        if (!pythonProcess) {
            return res.status(400).json({ message: '系統未運行' });
        }
        pythonProcess.kill();
        pythonProcess = null;
        res.json({ message: '系統已停止' });
    } catch (error) {
        console.error('停止系統時發生錯誤:', error);
        res.status(500).json({ message: '系統停止失敗', error: error.message });
    }
});

// 用戶認證 API
app.post('/register', async (req, res) => {
    try {
        const { name, email, password } = req.body;
        const [existingUsers] = await pool.execute(
            'SELECT * FROM users WHERE email = ?',
            [email]
        );
        
        if (existingUsers.length > 0) {
            return res.status(400).json({ message: '此email已被註冊' });
        }
        
        const hashedPassword = await bcrypt.hash(password, 10);
        const [result] = await pool.execute(
            'INSERT INTO users (name, email, password) VALUES (?, ?, ?)',
            [name, email, hashedPassword]
        );
        
        res.status(201).json({
            message: '註冊成功',
            userId: result.insertId
        });
    } catch (error) {
        console.error('註冊錯誤詳情:', error);
        res.status(500).json({ 
            message: '註冊失敗',
            error: error.message
        });
    }
});

app.post('/login', async (req, res) => {
    try {
        const { email, password } = req.body;
        const [users] = await pool.execute(
            'SELECT * FROM users WHERE email = ?',
            [email]
        );
        
        if (users.length === 0) {
            return res.status(401).json({ message: '帳號或密碼錯誤' });
        }
        
        const validPassword = await bcrypt.compare(password, users[0].password);
        if (!validPassword) {
            return res.status(401).json({ message: '帳號或密碼錯誤' });
        }
        
        res.json({
            message: '登入成功',
            user: {
                id: users[0].id,
                name: users[0].name,
                email: users[0].email
            }
        });
    } catch (error) {
        console.error('登入錯誤:', error);
        res.status(500).json({ message: '伺服器錯誤' });
    }
});

// 遊戲決策 API
app.post('/api/game-decision', async (req, res) => {
    try {
        const {
            user_id,
            session_id,
            screenshot_path,
            game_state,
            player_cards,
            board_cards,
            position,
            pot_size,
            action_taken,
            action_amount,
            ai_decision
        } = req.body;
        
        const [result] = await pool.execute(
            `INSERT INTO game_history (
                user_id, session_id, screenshot_path, game_state,
                player_cards, board_cards, position, pot_size,
                action_taken, action_amount, ai_decision, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NOW())`,
            [
                user_id, session_id, screenshot_path, JSON.stringify(game_state),
                player_cards, board_cards, position, pot_size,
                action_taken, action_amount, ai_decision
            ]
        );

        res.status(201).json({
            message: '決策記錄已保存',
            record_id: result.insertId
        });
    } catch (error) {
        console.error('保存決策記錄錯誤:', error);
        res.status(500).json({ message: '保存決策失敗' });
    }
});

// 錯誤處理中間件
app.use((err, req, res, next) => {
    if (err.code === 'ENOENT') {
        console.error('文件不存在:', err.path);
        res.status(404).send('文件不存在');
    } else {
        next(err);
    }
});

// 啟動服務器
const PORT = 3001;
server.listen(PORT, () => {
    console.log(`HTTP/WebSocket 伺服器運行在 port ${PORT}`);
    console.log(`服務器工作目錄: ${__dirname}`);
});
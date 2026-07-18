const express = require('express');
const path = require('path');
const healthRouter = require('./routes/health');
const { createMessage, listMessages, deleteMessage } = require('./routes/messages');

const app = express();

// 启用 JSON body 解析中间件
app.use(express.json());

// 挂载路由：health 检查、消息 CRUD（保留现有 API 不变）
app.use('/health', healthRouter);
app.post('/messages', createMessage);
app.get('/messages', listMessages);
app.delete('/messages/:id', deleteMessage);

// 设置静态文件目录并添加 GET / 返回前端首页
app.use(express.static(path.join(__dirname, 'public')));
app.get('/', (_req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

module.exports = app;

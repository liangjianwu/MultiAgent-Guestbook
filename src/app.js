const express = require('express');
const healthRouter = require('./routes/health');
const { createMessage, listMessages, deleteMessage } = require('./routes/messages');

const app = express();

// 启用 JSON body 解析中间件
app.use(express.json());

// 挂载路由：health 检查、消息 CRUD
app.use('/health', healthRouter);
app.post('/messages', createMessage);
app.get('/messages', listMessages);
app.delete('/messages/:id', deleteMessage);

module.exports = app;

# Guestbook/BBS 产品定义

## 产品名称

Guestbook 简易留言板

## 产品目标

提供一个简单、稳定的留言板后端服务，支持用户发帖、列表查看和删除留言。

## 功能范围（固定，不再变更）

1. **发布留言**
   - `POST /messages`
   - 请求体：`{ "author": "发帖人", "content": "留言内容" }`
   - 两个字段均为非空字符串，author 不超过 255 字节
   - 响应：201 Created + 新建留言对象

2. **查看留言列表**
   - `GET /messages`
   - 默认按 `created_at` 倒序返回
   - 响应：200 OK + 留言对象数组

3. **删除留言**
   - `DELETE /messages/:id`
   - 删除指定 ID 的留言
   - 响应：204 No Content（成功）或 404 Not Found（不存在）

4. **健康检查**
   - `GET /health`
   - 响应：200 OK + `{ "status": "ok" }`

## 技术栈

- Node.js + Express
- Sequelize ORM + MySQL 8
- Jest + supertest 测试
- 端口 6008
- MySQL: host 172.17.0.1, port 3306, user leo, password hvcsL3HB0M77cgHjAsJ0, database guestbook_demo

## 非功能约束

- 纯 JavaScript（不用 TypeScript）
- 代码简洁、直接
- 不使用前端界面
- 测试要求：Jest + supertest 覆盖 POST /messages 、GET /messages 、DELETE /messages/:id 、GET /health
- 服务器启动后监听 6008

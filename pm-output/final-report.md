# Guestbook 简易留言板 — 项目收尾报告

## 执行概览

本项目依据 `project.md` 中固定的产品范围，完成了一个基于 Node.js + Express + Sequelize + MySQL 8 的简易留言板后端服务，并使用 Jest + supertest 完成接口测试。

## 已完成的产品功能

| 接口 | 方法 | 说明 |
|---|---|---|
| `POST /messages` | POST | 发布留言，校验 author 与 content 非空，author 不超过 255 字节，返回 201 + 新建留言对象 |
| `GET /messages` | GET | 查看留言列表，默认按 `created_at` 倒序返回，返回 200 + 数组 |
| `DELETE /messages/:id` | DELETE | 删除指定 ID 留言，成功返回 204，不存在返回 404 |
| `GET /health` | GET | 健康检查，返回 200 + `{ "status": "ok" }` |

## 技术栈

- Node.js + Express
- Sequelize ORM + MySQL 8
- Jest + supertest
- 端口 6008
- MySQL 连接信息：host `172.17.0.1`，port `3306`，user `leo`，database `guestbook_demo`

## 代码结构

```
/tmp/guestbook-demo/
├── package.json
├── src/
│   ├── app.js                 # Express 应用与路由挂载
│   ├── server.js              # 服务器启动入口，监听 6008
│   ├── config/
│   │   └── database.js        # Sequelize 连接配置
│   ├── models/
│   │   └── Message.js         # Message 模型定义
│   └── routes/
│       ├── health.js          # 健康检查路由
│       └── messages.js        # 留言 CRUD 路由
├── tests/
│   └── app.test.js            # Jest + supertest 接口测试
├── pm-output/
│   ├── prd.md                 # 产品需求文档
│   ├── plan.md                # 执行计划
│   └── final-report.md        # 本报告
├── review-output/           # 各步骤审查记录
└── qa-output/               # 测试日志
```

## 重要修复记录

在执行过程中，通过 reviewer 反复检查发现并修复了以下问题：

1. **`src/models/Message.js`**: author 字段类型由 `BINARY(255)` 修正为 `STRING(255)`，符合 PRD 数据模型要求。
2. **`src/app.js`**: health 路由挂载方式由 `app.get('/health', healthRouter)` 修正为 `app.use('/health', healthRouter)`，确保 `GET /health` 正常返回。
3. **`tests/app.test.js`**: 修复了 app 未正确导入测试作用域的问题，将 `require('../src/app')` 赋值给 `const app`，并确保 jest.mock 工厂变量使用 `mock` 前缀以符合 Jest hoisting 规则。

## 测试结果

运行 `npm test` 后，全部 14 个测试用例通过：

```
PASS tests/app.test.js
  GET /health
    ✓ returns 200 with status ok
    ✓ responds with JSON content-type
  POST /messages
    ✓ 201 when author and content are provided
    ✓ 400 when author is missing
    ✓ 400 when content is missing
    ✓ 400 when content is an empty string
    ✓ 400 when author exceeds 255 bytes
  GET /messages 倒序与删除 (DELETE /messages/:id)
    ✓ 200 returns messages sorted by created_at DESC when empty
    ✓ 200 returns messages in newest-first order
    ✓ 204 removes an existing message
    ✓ 404 when the message does not exist
    ✓ DELETE followed by GET removes the record from list
    ✓ ordering is preserved across create/list/delete cycles
    ✓ list returns empty after deleting all records

Test Suites: 1 passed, 1 total
Tests:       14 passed, 14 total
```

## 服务启动验证

运行 `npm start` 后，服务器正常在端口 6008 启动：

```
Server is running on port 6008
```

## 审查结论

- 所有 coder/reviewer 交替步骤均已完成，并在 `pm-output/plan.md` 中标记为 `[DONE]`。
- 最终代码与 `project.md` 中固定的产品范围一致，未新增任何功能。
- 测试已覆盖所有四个接口的正向与异常场景。
- 服务启动正常，端口符合要求。

## 发布总结

Guestbook 简易留言板后端服务已按计划完成开发、审查与测试，可进入部署阶段。使用方式为：

```bash
# 安装依赖
npm install

# 运行测试
npm test

# 启动服务
npm start
```

服务启动后将监听 `http://localhost:6008`，提供以上四个接口。

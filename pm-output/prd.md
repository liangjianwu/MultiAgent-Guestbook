# Guestbook 简易留言板 — 产品需求文档（PRD）

> 本 PRD 完全基于 `project.md` 定义，未引入任何范围变更。

## 1. 产品目标

提供一个简单、稳定的留言板后端服务，支持用户发帖、列表查看、删除留言，并提供健康检查接口。

## 2. 功能需求

### 2.1 发布留言

- **接口**：`POST /messages`
- **请求体**（JSON）：
  ```json
  { "author": "发帖人", "content": "留言内容" }
  ```
- **业务规则**：
  - `author` 与 `content` 均为非空字符串。
  - `author` 长度不得超过 255 字节。
- **响应**：
  - 成功：HTTP 201 Created + 新建留言对象。
  - 失败：HTTP 400 Bad Request。

### 2.2 查看留言列表

- **接口**：`GET /messages`
- **排序**：按 `created_at` 倒序返回。
- **响应**：
  - 成功：HTTP 200 OK + 留言对象数组。

### 2.3 删除留言

- **接口**：`DELETE /messages/:id`
- **响应**：
  - 成功：HTTP 204 No Content。
  - 不存在：HTTP 404 Not Found。

### 2.4 健康检查

- **接口**：`GET /health`
- **响应**：
  - HTTP 200 OK + `{ "status": "ok" }`

## 3. 技术栈

- 运行环境：Node.js
- Web 框架：Express
- ORM：Sequelize
- 数据库：MySQL 8
- 测试框架：Jest + supertest
- 服务端口：`6008`
- 数据库连接：
  - host: `172.17.0.1`
  - port: `3306`
  - user: `leo`
  - password: `hvcsL3HB0M77cgHjAsJ0`
  - database: `guestbook_demo`

## 4. 非功能约束

- 使用纯 JavaScript，不引入 TypeScript。
- 代码简洁、直接。
- 无前端界面。
- 所有接口必须通过 Jest + supertest 覆盖测试：
  - `POST /messages`
  - `GET /messages`
  - `DELETE /messages/:id`
  - `GET /health`
- 服务器启动后监听 `6008` 端口。

## 5. 数据模型

使用 Sequelize 定义 `Message` 模型，至少包含以下字段：

| 字段        | 类型      | 约束                       |
|-------------|-----------|----------------------------|
| `id`        | INTEGER   | 主键、自增                 |
| `author`    | STRING    | 非空、最大 255 字节        |
| `content`   | TEXT      | 非空                       |
| `created_at`| DATE      | 非空、默认当前时间         |
| `updated_at`| DATE      | 非空、默认当前时间         |

## 6. 交付清单

- `package.json`
- `src/config/database.js`：Sequelize 连接配置与实例导出。
- `src/models/Message.js`：Sequelize `Message` 模型定义。
- `src/routes/health.js`：`GET /health` 路由。
- `src/routes/messages.js`：`POST /messages`、`GET /messages`、`DELETE /messages/:id` 路由。
- `src/app.js`：Express 应用与中间件、路由挂载。
- `src/server.js`：启动服务，监听端口 `6008`。
- `tests/app.test.js`：覆盖所有接口的 Jest + supertest 测试用例。

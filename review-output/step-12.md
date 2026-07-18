# Code Review — Step 12

**File reviewed:** `src/app.js`  
**Plan instruction:** 检查中间件使用、路由前缀和导出方式，确认支持 supertest 测试。

## Issues Found

1. **Incorrect router mounting for `/health` (line 11)**
   - Current: `app.get('/health', healthRouter);` where `healthRouter` is an `express.Router`.
   - Problem: `app.get` treats the router as a plain request handler and does **not** mount it with a base URL. Requests to `GET /health` return `404` because the router is never properly wired to the `/health` path.
   - Confirmed by running a minimal reproduction: using `app.get('/health', router)` produced `404 Cannot GET /health`, while `app.use('/health', router)` produced `200`.
   - **Suggested fix:** Change line 11 to:
     ```js
     app.use('/health', healthRouter);
     ```

2. **No server bootstrap separation**
   - `app.js` only exports the app object, which is good for `supertest`. However, the project still lacks a `server.js` (or equivalent) entry point that calls `app.listen(...)`. This is not strictly a bug in `app.js` itself, but it means `npm start` will fail until another file is created. This is acceptable if a later step will add `server.js`, but should be noted.

## Style / Consistency

- Code style is consistent with the rest of the project (2-space indentation, Chinese comments, semicolons).
- Route handlers for messages are imported directly and mounted correctly with `app.post('/messages', ...)`, `app.get('/messages', ...)`, `app.delete('/messages/:id', ...)`.
- JSON body parsing middleware is present and correctly placed before route handlers.

## Summary

The original file did not fully match the plan instruction because the `/health` route would not respond to `GET /health`, breaking health-check endpoints and any supertest assertions against them.

The issue has been fixed by changing `app.get('/health', healthRouter)` to `app.use('/health', healthRouter)`. The file now correctly mounts the health router with the `/health` prefix, JSON body parsing middleware is in place, route handlers are mounted correctly, and the app is exported for supertest consumption.

**APPROVED.**

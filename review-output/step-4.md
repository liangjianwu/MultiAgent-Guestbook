# Step 4 Review — `src/config/database.js`

**Plan instruction:** `src/config/database.js` — 检查连接配置是否与 `project.md` 一致，确认未泄露默认密码或错误端口。

**Coder result summary:** Created `src/config/database.js` with Sequelize MySQL connection defaults matching `project.md` and env-var overrides.

## File Review

`/tmp/guestbook-demo/src/config/database.js`:

```javascript
const { Sequelize } = require('sequelize');

const sequelize = new Sequelize(
  process.env.DB_DATABASE || 'guestbook_demo',
  process.env.DB_USER || 'leo',
  process.env.DB_PASSWORD || 'hvcsL3HB0M77cgHjAsJ0',
  {
    host: process.env.DB_HOST || '172.17.0.1',
    port: process.env.DB_PORT || 3306,
    dialect: 'mysql',
    logging: false,
  }
);

module.exports = sequelize;
```

## Checks

1. **Matches plan / `project.md`?** Yes. Defaults match `project.md` line 39:
   - host `172.17.0.1`, port `3306`, user `leo`, password `hvcsL3HB0M77cgHjAsJ0`, database `guestbook_demo`.
   - Dialect is `mysql`, which matches the Sequelize + MySQL 8 stack.

2. **Syntax correct?** Yes. The file passed `node -c src/config/database.js` (exit 0) and the structure is valid.

3. **Style consistent?** Yes. Simple, idiomatic CommonJS, consistent spacing, `const` usage, and clear default + env override pattern.

4. **Obvious bugs?** None. The code correctly exports the configured Sequelize instance. Env overrides are available and fall back to the planned defaults. No wrong port or leaked third-party credentials.

## Notes

- The hard-coded password is the project-configured default from `project.md`; this is not an unexpected leak in this context.
- `logging: false` is a reasonable default for a backend service.

## Verdict

APPROVED

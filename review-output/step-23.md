# Review: Step 23 - `tests/app.test.js`

**Plan instruction:** 重新审查测试用例、mock 作用域和断言，确认所有接口覆盖完整。

**Changed file:** `tests/app.test.js` (line 53)

## Summary of change

- `require('../src/app')` was changed from an expression statement to `const app = require('../src/app');`, so `app` is now in scope for the supertest calls.
- Mock factory variables keep the `mock` prefix (`mockAllMessages`, `mockNextMsgId`), which satisfies Jest's hoisting rules for variables referenced inside a `jest.mock` factory.

## Checks

1. **Matches plan:** Yes. The diff directly addresses the previously identified problems (app not imported, mock variable scope) and the instruction is to review coverage, mock scope, and assertions.
2. **Syntax:** Correct. `npm test` passes with 14 tests.
3. **Style:** Consistent. Mock variable names follow the required `mock*` prefix, indentation is uniform, and test structure is clear.
4. **Coverage / bugs:** All exposed routes are covered:
   - `GET /health` (status + content-type)
   - `POST /messages` (success + missing/invalid parameter cases)
   - `GET /messages` (empty list, newest-first ordering)
   - `DELETE /messages/:id` (existing, non-existing, side effects on subsequent list)

   No obvious bugs in the test code.

## Minor optional suggestions (non-blocking)

- The `DELETE /messages/1` success test could additionally assert `expect(res.body).toEqual({})` to document the empty 204 body, but this is not required.
- The 404 delete test could assert the exact error message text instead of only its type, but the current assertion is still reasonable.

## Verdict

**APPROVED**

`npm test` passes: 14/14 tests passed.

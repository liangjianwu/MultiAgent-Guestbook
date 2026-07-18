# Review: Step 16 — `tests/app.test.js`

Status: **NOT APPROVED**

The test suite is now structurally aligned with the plan: it covers the required endpoints and provides both positive and negative cases for health, message creation, listing, and deletion. The previous `jest.mock` scope issue has been fixed. However, the suite still cannot execute because the Express app is never brought into the test scope.

## Blocking Issue

**`app` is not imported into the test scope**
- **File:** `tests/app.test.js`
- **Line:** 53
- **Problem:** The line reads `require('../src/app');` which loads the module but discards the exported Express app. Every test calls `request(app)`, yet `app` is `undefined` in this module. Running `npx jest tests/app.test.js` produces:
  ```
  ReferenceError: app is not defined
  ```
- **Suggested fix:** Change line 53 to:
  ```js
  const app = require('../src/app');
  ```

## Resolved From Previous Review

- **Mock variable scope:** The factory now correctly references `mockAllMessages` and `mockNextMsgId`, which satisfy Jest’s rule for out-of-scope variable access inside a `jest.mock` factory. ✅

## Style / Consistency Notes

- **Comment wording:** The block comment at lines 4–6 says the state is captured inside the factory “above”, but the factory is actually at line 12 (below). Suggested reword: “captured by the `jest.mock` factory below”.
- **Mixed-language test title:** The third `describe` block title mixes Chinese characters with English (`倒序与删除`). For consistency with the rest of the project, use an English title such as `GET /messages ordering and deletion (DELETE /messages/:id)`.
- **Indentation:** 4-space indentation is consistent within this file.

## Summary

Fix the single blocking issue on line 53 by importing the Express app into the module scope. Then re-run the full Jest suite (`npx jest tests/app.test.js` or `npm test`) and confirm that all 23 test cases pass before marking this step complete.

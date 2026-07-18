# Re-review Report: Homepage Fix

## Files Reviewed
- `/tmp/guestbook-demo/src/app.js`
- `/tmp/guestbook-demo/src/public/index.html`

## Conclusion

**NOT APPROVED**

The three previously reported issues are now correctly addressed, but a new regression was introduced: the delete button is wired up through **two** overlapping delegated event listeners on `messageList`. This causes `deleteMessage` to be invoked twice per click, producing two confirmation dialogs and two `DELETE` requests. Remove the duplicate handler to make this approval complete.

## Issues from Previous Review

### 1. POST submission checks `res.ok`
- **File:** `/tmp/guestbook-demo/src/public/index.html`
- **Line:** 84–98
- **Status:** FIXED
- The submit handler now awaits `fetch('/messages', ...)` and checks `if (!postRes.ok) throw new Error(...)`. It only resets the form and refreshes the list after a successful HTTP response.

### 2. No inline `onclick` handlers; delete buttons use `data-id` and event delegation on `messageList`
- **File:** `/tmp/guestbook-demo/src/public/index.html`
- **Lines:** 68–75, 103–119, 151–153
- **Status:** FIXED in principle, but REGRESSED in implementation
- The rendered buttons now use `<button class="delete-btn" data-id="...">删除</button>` instead of inline `onclick`. However, there are **two** `click` listeners attached to `messageList` that both match `.delete-btn` and both call `deleteMessage(id)`:
  - First listener (lines 68–75): reads `btn.dataset.id` and calls `deleteMessage(id)` synchronously (string id).
  - Second listener (lines 103–119): reads `btn.dataset.id`, validates/coerces it to a number, and awaits `deleteMessage(id)`.
- **Problem:** Both handlers fire on a single click. The user will see two `confirm` dialogs in a row, and two `DELETE /messages/:id` requests will be sent.
- **Suggested Fix:** Remove one of the delegated listeners. Keep the second (lines 103–119) if you want numeric validation, or keep the first (lines 68–75) and move any validation into `deleteMessage`. Do not keep both.

### 3. Sort fallback does not use `msg.id` as a `Date`
- **File:** `/tmp/guestbook-demo/src/public/index.html`
- **Line:** 134–143
- **Status:** FIXED
- The sort comparator no longer falls back to `id` parsed as a date. It sorts by `created_at` descending, with stable fallback (`0`) when `created_at` is missing on both sides and deterministic ordering when only one side is missing.

## What Still Looks Good
- `app.js` static file serving and route configuration remain correct.
- API routes are preserved unchanged.
- Author/content are escaped before rendering, mitigating XSS for displayed text.
- Basic UI polish and error handling for GET/POST/DELETE network errors are present.

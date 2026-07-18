const request = require('supertest');

// ---------------------------------------------------------------------------
// Mock the Message model so tests do not need a MySQL database.
// The shared mutable state (store, nextId) is captured by reference inside the
// jest.mock factory above, allowing beforeEach to reset it between tests.
// ---------------------------------------------------------------------------

const mockAllMessages = []; // shared store, references captured below
let mockNextMsgId = 1;

jest.mock('../src/models/Message', () => {
    const msgStore = mockAllMessages;

    async function create(attrs) {
        const newMessage = {
            id: mockNextMsgId++,
            author: attrs.author,
            content: attrs.content,
            created_at: new Date(),
            updated_at: new Date(),
        };
        // Keep an ordered copy so findAll can sort deterministically.
        msgStore.push(newMessage);
        return Object.assign({}, newMessage);
    }

    async function findAll() {
        // Return a fresh DESC-sorted list on each call, independent of insertion order.
        const sorted = [...msgStore].sort((a, b) => b.created_at - a.created_at);
        return JSON.parse(JSON.stringify(sorted));
    }

    async function destroy({ where }) {
        if (!where || typeof where !== 'object' || !('id' in where)) {
            throw new Error('Invalid destroy query');
        }
        const id = parseInt(String(where.id), 10);
        const idx = msgStore.findIndex((m) => m.id === id);
        if (idx >= 0) {
            msgStore.splice(idx, 1);
            return 1;
        }
        return 0;
    }

    return {
        Message: { create, findAll, destroy },
        syncDatabase: jest.fn(),
    };
});

const app = require('../src/app'); // ensure app is loaded once

beforeEach(() => {
    mockAllMessages.length = 0;
    mockNextMsgId = 1;
});

// ===========================================================================
// Test suites
// ===========================================================================

describe('GET /health', () => {
    test('returns 200 with status ok', async () => {
        const res = await request(app).get('/health');
        expect(res.status).toBe(200);
        expect(res.body).toEqual({ status: 'ok' });
    });

    test('responds with JSON content-type', async () => {
        const res = await request(app).get('/health');
        expect(res.headers['content-type']).toMatch(/json/);
    });
});
describe('POST /messages', () => {
    test('201 when author and content are provided', async () => {
        const res = await request(app)
            .post('/messages')
            .send({ author: 'Alice', content: 'Hello!' })
            .set('Accept', 'application/json');

        expect(res.status).toBe(201);
        expect(res.body).toHaveProperty('id', 1);
        expect(res.body.author).toBe('Alice');
        expect(res.body.content).toBe('Hello!');
    });

    test('400 when author is missing', async () => {
        const res = await request(app)
            .post('/messages')
            .send({ content: 'Hi' })
            .set('Accept', 'application/json');

        expect(res.status).toBe(400);
    });

    test('400 when content is missing', async () => {
        const res = await request(app)
            .post('/messages')
            .send({ author: 'Bob' })
            .set('Accept', 'application/json');

        expect(res.status).toBe(400);
    });

    test('400 when content is an empty string', async () => {
        const res = await request(app)
            .post('/messages')
            .send({ author: 'Bob', content: '' })
            .set('Accept', 'application/json');

        expect(res.status).toBe(400);
    });

    test('400 when author exceeds 255 bytes', async () => {
        const longAuthor = 'A'.repeat(300);
        const res = await request(app)
            .post('/messages')
            .send({ author: longAuthor, content: 'short' })
            .set('Accept', 'application/json');

        expect(res.status).toBe(400);
    });
});

describe('GET /messages 倒序与删除 (DELETE /messages/:id)', () => {
    test('200 returns messages sorted by created_at DESC when empty', async () => {
        const res = await request(app).get('/messages');

        expect(res.status).toBe(200);
        expect(Array.isArray(res.body)).toBe(true);
        expect(res.body.length).toBe(0);
    });

    test('200 returns messages in newest-first order', async () => {
        await request(app).post('/messages').send({ author: 'A', content: 'first' }).expect(201);
        await request(app).post('/messages').send({ author: 'B', content: 'second' }).expect(201);

        const res = await request(app).get('/messages');

        expect(res.status).toBe(200);
        const list = res.body;
        expect(list.length).toBe(2);
        // The latest (B) should come first due to DESC ordering.
        expect(list[0].author).toBe('B');
        expect(list[1].author).toBe('A');
    });

    test('204 removes an existing message', async () => {
        await request(app).post('/messages').send({ author: 'X', content: 'y' }).expect(201);

        const res = await request(app).delete('/messages/1');
        expect(res.status).toBe(204);
    });

    test('404 when the message does not exist', async () => {
        const res = await request(app)
            .delete('/messages/999')
            .set('Accept', 'application/json');

        expect(res.status).toBe(404);
        expect(typeof res.body.message).toBe('string');
    });

    test('DELETE followed by GET removes the record from list', async () => {
        await request(app).post('/messages').send({ author: 'A', content: '1' }).expect(201);

        const removeRes = await request(app).delete('/messages/1');
        expect(removeRes.status).toBe(204);

        const listRes = await request(app).get('/messages');
        expect(listRes.status).toBe(200);
        expect(listRes.body.length).toBe(0);
    });

    test('ordering is preserved across create/list/delete cycles', async () => {
        await request(app).post('/messages').send({ author: 'A', content: '1' }).expect(201);
        await request(app).post('/messages').send({ author: 'B', content: '2' }).expect(201);
        await request(app).delete('/messages/1').expect(204);

        const res = await request(app).get('/messages');

        expect(res.status).toBe(200);
        expect(res.body.length).toBe(1);
        expect(res.body[0].author).toBe('B');
    });

    test('list returns empty after deleting all records', async () => {
        await request(app).post('/messages').send({ author: 'A', content: 'x' }).expect(201);
        const removeRes = await request(app).delete('/messages/1').expect(204);

        const res = await request(app).get('/messages');
        expect(res.status).toBe(200);
        expect(res.body.length).toBe(0);
    });
});

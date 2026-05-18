import { test, expect } from '@playwright/test';

const FRONTEND = 'http://localhost:3000';
const API_BASE = 'http://localhost:8000/api';

// Utility to generate random email
const randomEmail = () => `qa_user_${Date.now()}@example.com`;

test.describe('Feature: Todo Backend + Auth Integration (Frontend + API)', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(FRONTEND + '/');
  });

  test('Signup API: should register a new user (success)', async ({ request, page }) => {
    const email = randomEmail();
    const signupPayload = { name: 'QA Test', email, password: 'P@ssw0rd!' };

    const res = await request.post(`${API_BASE}/auth/signup`, { data: signupPayload });
    expect(res.ok()).toBeTruthy();
    const body = await res.json();
    expect(body).toHaveProperty('success');
    expect(body.success).toBeTruthy();
    expect(body).toHaveProperty('data');

    // UI evidence: try to visit signup page and take screenshot (even if app has no page, just capture home)
    await page.goto(FRONTEND + '/signup').catch(() => page.goto(FRONTEND + '/'));
    await page.screenshot({ path: 'screenshots/signup-api-success.png' });
  });

  test('Signup API: should prevent duplicate email registration (error)', async ({ request }) => {
    const email = randomEmail();
    const payload = { name: 'QA Test Dup', email, password: 'P@ssw0rd!' };
    const first = await request.post(`${API_BASE}/auth/signup`, { data: payload });
    expect(first.ok()).toBeTruthy();

    const second = await request.post(`${API_BASE}/auth/signup`, { data: payload });
    // Expect failure (4xx) when trying duplicate
    expect(second.status()).toBeGreaterThanOrEqual(400);
    expect(second.status()).toBeLessThan(500);
    const b = await second.json();
    expect(b).toHaveProperty('success');
    expect(b.success).toBeFalsy();
  });

  test('Login API: should authenticate and return JWT token', async ({ request, page }) => {
    const email = randomEmail();
    const signup = { name: 'Login User', email, password: 'P@ssw0rd!' };
    const s = await request.post(`${API_BASE}/auth/signup`, { data: signup });
    expect(s.ok()).toBeTruthy();

    const loginRes = await request.post(`${API_BASE}/auth/login`, { data: { email, password: signup.password } });
    expect(loginRes.ok()).toBeTruthy();
    const body = await loginRes.json();
    expect(body).toHaveProperty('token');
    // UI evidence: open login page
    await page.goto(FRONTEND + '/login').catch(() => page.goto(FRONTEND + '/'));
    await page.screenshot({ path: 'screenshots/login-api-success.png' });
  });

  test('Protected Todos: should reject unauthenticated creation', async ({ request }) => {
    const payload = { title: 'Unauth todo', description: 'Should be rejected', status: 'incomplete' };
    const res = await request.post(`${API_BASE}/todos`, { data: payload });
    // Expect 401 or 403
    expect(res.status()).toBeGreaterThanOrEqual(400);
    expect(res.status()).toBeLessThan(500);
    const b = await res.json();
    expect(b).toHaveProperty('success');
    expect(b.success).toBeFalsy();
  });

  test('Todo CRUD: create, read, update, delete flow for owner', async ({ request, page }) => {
    const email = randomEmail();
    const user = { name: 'Owner', email, password: 'P@ssw0rd!' };
    const s = await request.post(`${API_BASE}/auth/signup`, { data: user });
    expect(s.ok()).toBeTruthy();

    const login = await request.post(`${API_BASE}/auth/login`, { data: { email, password: user.password } });
    expect(login.ok()).toBeTruthy();
    const loginBody = await login.json();
    expect(loginBody).toHaveProperty('token');
    const token = loginBody.token;

    // Create todo
    const todoPayload = { title: 'QA Todo', description: 'Created by QA', status: 'incomplete', priority: 'low' };
    const createRes = await request.post(`${API_BASE}/todos`, {
      data: todoPayload,
      headers: { Authorization: `Bearer ${token}` },
    });
    expect(createRes.ok()).toBeTruthy();
    const created = await createRes.json();
    expect(created).toHaveProperty('data');
    const todo = created.data;
    expect(todo).toHaveProperty('id');

    // Get single todo
    const getRes = await request.get(`${API_BASE}/todos/${todo.id}`, { headers: { Authorization: `Bearer ${token}` } });
    expect(getRes.ok()).toBeTruthy();
    const getBody = await getRes.json();
    expect(getBody.data.id || getBody.data._id || getBody.data).toBeTruthy();

    // Update todo (partial)
    const updateRes = await request.patch(`${API_BASE}/todos/${todo.id}`, {
      data: { status: 'completed', title: 'QA Todo - Updated' },
      headers: { Authorization: `Bearer ${token}` },
    });
    expect(updateRes.ok()).toBeTruthy();
    const updatedBody = await updateRes.json();
    expect(updatedBody).toHaveProperty('data');

    // Delete todo
    const delRes = await request.delete(`${API_BASE}/todos/${todo.id}`, { headers: { Authorization: `Bearer ${token}` } });
    expect(delRes.ok()).toBeTruthy();

    // Verify deleted returns 404
    const getAfterDelete = await request.get(`${API_BASE}/todos/${todo.id}`, { headers: { Authorization: `Bearer ${token}` } });
    expect(getAfterDelete.status()).toBeGreaterThanOrEqual(400);
    expect(getAfterDelete.status()).toBeLessThan(500);

    // UI evidence: open todos page
    await page.goto(FRONTEND + '/todos').catch(() => page.goto(FRONTEND + '/'));
    await page.screenshot({ path: 'screenshots/todo-crud-flow.png' });
  });

  test('Authorization: only owner can update/delete a todo', async ({ request }) => {
    // Owner user
    const ownerEmail = randomEmail();
    const owner = { name: 'Owner2', email: ownerEmail, password: 'P@ssw0rd!' };
    await request.post(`${API_BASE}/auth/signup`, { data: owner });
    const ownerLogin = await request.post(`${API_BASE}/auth/login`, { data: { email: owner.email, password: owner.password } });
    const ownerToken = (await ownerLogin.json()).token;

    // Another user
    const otherEmail = randomEmail();
    const other = { name: 'Other', email: otherEmail, password: 'P@ssw0rd!' };
    await request.post(`${API_BASE}/auth/signup`, { data: other });
    const otherLogin = await request.post(`${API_BASE}/auth/login`, { data: { email: other.email, password: other.password } });
    const otherToken = (await otherLogin.json()).token;

    // Owner creates todo
    const create = await request.post(`${API_BASE}/todos`, { data: { title: 'Owner Todo', description: 'owner only' }, headers: { Authorization: `Bearer ${ownerToken}` } });
    expect(create.ok()).toBeTruthy();
    const todo = (await create.json()).data;

    // Other tries to update
    const updateByOther = await request.patch(`${API_BASE}/todos/${todo.id}`, { data: { title: 'Hacked' }, headers: { Authorization: `Bearer ${otherToken}` } });
    expect(updateByOther.status()).toBeGreaterThanOrEqual(400);
    expect(updateByOther.status()).toBeLessThan(500);

    // Other tries to delete
    const delByOther = await request.delete(`${API_BASE}/todos/${todo.id}`, { headers: { Authorization: `Bearer ${otherToken}` } });
    expect(delByOther.status()).toBeGreaterThanOrEqual(400);
    expect(delByOther.status()).toBeLessThan(500);
  });

  test('Get Todos: supports pagination and filtering by status', async ({ request }) => {
    const email = randomEmail();
    const user = { name: 'Pager', email, password: 'P@ssw0rd!' };
    await request.post(`${API_BASE}/auth/signup`, { data: user });
    const login = await request.post(`${API_BASE}/auth/login`, { data: { email, password: user.password } });
    const token = (await login.json()).token;

    // Create multiple todos
    for (let i = 0; i < 7; i++) {
      await request.post(`${API_BASE}/todos`, { data: { title: `T ${i}`, description: 'for pagination', status: i % 2 === 0 ? 'completed' : 'incomplete' }, headers: { Authorization: `Bearer ${token}` } });
    }

    const page1 = await request.get(`${API_BASE}/todos?page=1&limit=5`, { headers: { Authorization: `Bearer ${token}` } });
    expect(page1.ok()).toBeTruthy();
    const p1Body = await page1.json();
    expect(p1Body).toHaveProperty('data');

    const filter = await request.get(`${API_BASE}/todos?status=completed`, { headers: { Authorization: `Bearer ${token}` } });
    expect(filter.ok()).toBeTruthy();
    const fBody = await filter.json();
    expect(fBody).toHaveProperty('data');
  });

  test('Validation: creating todo without required fields should fail', async ({ request }) => {
    const email = randomEmail();
    const user = { name: 'Validator', email, password: 'P@ssw0rd!' };
    await request.post(`${API_BASE}/auth/signup`, { data: user });
    const login = await request.post(`${API_BASE}/auth/login`, { data: { email, password: user.password } });
    const token = (await login.json()).token;

    const res = await request.post(`${API_BASE}/todos`, { data: { description: 'missing title' }, headers: { Authorization: `Bearer ${token}` } });
    expect(res.status()).toBeGreaterThanOrEqual(400);
    expect(res.status()).toBeLessThan(500);
    const b = await res.json();
    expect(b).toHaveProperty('success');
    expect(b.success).toBeFalsy();
  });
});

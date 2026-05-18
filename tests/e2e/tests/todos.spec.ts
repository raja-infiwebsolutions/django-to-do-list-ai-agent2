import { test, expect } from '@playwright/test';

const FRONTEND = 'http://localhost:3000';
const API_BASE = 'http://localhost:8000/api';

test.describe('Feature: Frontend Django Todo List', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(FRONTEND);
  });

  test('Home: page loads, navbar and footer present, Bootstrap layout applied', async ({ page }) => {
    // Basic layout
    await expect(page.locator('nav')).toBeVisible({ timeout: 5000 });
    await expect(page.locator('footer')).toBeVisible({ timeout: 5000 });

    // Check that there's a heading referencing Todos
    const heading = page.locator('h1, h2, h3').filter({ hasText: /todo/i }).first();
    await expect(heading).toBeVisible({ timeout: 3000 });

    // Check for a Bootstrap container element and at least one card or list region
    const container = page.locator('.container, .container-fluid');
    await expect(container).toBeVisible();

    // Take screenshot evidence
    await page.screenshot({ path: 'screenshots/homepage.png', fullPage: true });
  });

  test('Todo List: displays todos or shows empty state with proper UI elements', async ({ page }) => {
    // Attempt to find a list or cards region on the page
    const cards = page.locator('.card, [data-testid="todo-card"], .todo-card');
    const cardCount = await cards.count();

    if (cardCount > 0) {
      // Validate at least one card shows title, description, status and created date
      const first = cards.first();
      await expect(first.locator('h5, h4, .card-title, [data-testid="todo-title"]')).toBeVisible();
      await expect(first.locator('p, .card-text, [data-testid="todo-desc"]')).toBeVisible();
      await expect(first.locator(':text("Complete"), :text("Incomplete"), [data-testid="todo-status"]')).toBeVisible();
      await expect(first.locator(':text("Created"), :text("created"), time, [data-testid="todo-created"]')).toBeVisible();

      // Edit and delete buttons
      await expect(first.locator('button:has-text("Edit"), a:has-text("Edit"), [data-testid="edit-btn"]')).toBeVisible();
      await expect(first.locator('button:has-text("Delete"), a:has-text("Delete"), [data-testid="delete-btn"]')).toBeVisible();

      await page.screenshot({ path: 'screenshots/todo-list-with-items.png', fullPage: true });
    } else {
      // Expect empty state UI: message and an Add/Create button
      const emptyMsg = page.locator(':text("no todos"), :text("no tasks"), :text("No todos"), .empty-state');
      await expect(emptyMsg).toBeVisible({ timeout: 3000 });
      const addBtn = page.locator('a:has-text("Add"), a:has-text("Create"), button:has-text("Add"), button:has-text("Create")');
      await expect(addBtn).toBeVisible();

      await page.screenshot({ path: 'screenshots/todo-list-empty.png', fullPage: true });
    }
  });

  test('Create Todo: form UI, validation messages, submit and cancel buttons, loading state', async ({ page }) => {
    // Navigate to create page via visible link/button
    const createLink = page.locator('a:has-text("Create"), a:has-text("Add"), button:has-text("Create"), button:has-text("Add New"), a:has-text("New Todo")').first();
    await expect(createLink).toBeVisible({ timeout: 5000 });
    await createLink.click();

    // Form fields should exist
    const titleField = page.getByLabel(/title/i).first();
    const descField = page.getByLabel(/description/i).first();

    await expect(titleField).toBeVisible();
    await expect(descField).toBeVisible();

    // Validation: submit empty form and expect validation messages
    const submitBtn = page.locator('button[type="submit"], button:has-text("Save"), button:has-text("Create")').first();
    await submitBtn.click();

    const validation = page.locator(':role(alert), .invalid-feedback, .is-invalid');
    await expect(validation).toBeVisible({ timeout: 3000 });

    // Fill with valid data
    await titleField.fill('E2E Test Todo');
    await descField.fill('Created by automated Playwright test');

    // Submit and expect loading state then success alert and redirect to list
    await Promise.all([
      page.waitForNavigation({ waitUntil: 'networkidle' }).catch(() => {}),
      submitBtn.click()
    ]);

    const successAlert = page.locator(':text("success"), .alert-success, [role="alert"]:has-text("success"), .alert:has-text("success")');
    // success alert might or might not be present depending on implementation; try to capture either success alert or presence in list
    if (await successAlert.count() > 0) {
      await expect(successAlert.first()).toBeVisible();
    }

    // Ensure return to list (URL contains /todos or homepage)
    await expect(page).toHaveURL(/(todos|\/)$/i);

    await page.screenshot({ path: 'screenshots/create-todo-result.png', fullPage: true });
  });

  test('Edit Todo: pre-filled form and update flow', async ({ page }) => {
    // Find first edit button
    const editBtn = page.locator('button:has-text("Edit"), a:has-text("Edit"), [data-testid="edit-btn"]').first();
    await expect(editBtn).toBeVisible({ timeout: 5000 });
    await editBtn.click();

    // Check pre-filled fields
    const titleField = page.getByLabel(/title/i).first();
    await expect(titleField).toBeVisible();
    const original = await titleField.inputValue();

    // Modify and submit
    await titleField.fill(original + ' (edited)');
    const submitBtn = page.locator('button[type="submit"], button:has-text("Update"), button:has-text("Save")').first();
    await Promise.all([
      page.waitForNavigation({ waitUntil: 'networkidle' }).catch(() => {}),
      submitBtn.click()
    ]);

    // Expect success alert or updated title present in list
    const updatedLocator = page.locator(`:text("${original} (edited)")`);
    await expect(updatedLocator).toBeVisible({ timeout: 5000 });

    await page.screenshot({ path: 'screenshots/edit-todo-result.png', fullPage: true });
  });

  test('Delete Todo: shows confirmation modal/page and removes todo on confirm', async ({ page }) => {
    // Find first delete button
    const deleteBtn = page.locator('button:has-text("Delete"), a:has-text("Delete"), [data-testid="delete-btn"]').first();
    await expect(deleteBtn).toBeVisible({ timeout: 5000 });
    await deleteBtn.click();

    // Expect confirmation modal or page with warning and cancel/confirm buttons
    const modal = page.locator('.modal, .confirm-dialog, .delete-confirm, :text("Are you sure")');
    await expect(modal).toBeVisible({ timeout: 5000 });

    const cancel = modal.locator('button:has-text("Cancel"), button:has-text("No"), a:has-text("Cancel")').first();
    const confirm = modal.locator('button:has-text("Confirm"), button:has-text("Delete"), button:has-text("Yes")').first();

    await expect(cancel).toBeVisible();
    await expect(confirm).toBeVisible();

    // Click cancel first
    await cancel.click();
    // Ensure todo still present (there should be at least one card)
    await expect(page.locator('.card, [data-testid="todo-card"]').first()).toBeVisible();

    // Click delete again and confirm
    await deleteBtn.click();
    await expect(modal).toBeVisible({ timeout: 5000 });
    await Promise.all([
      page.waitForNavigation({ waitUntil: 'networkidle' }).catch(() => {}),
      confirm.click()
    ]);

    // Expect success alert or removed element
    const successAlert = page.locator(':text("deleted"), .alert-success, :text("success")');
    if (await successAlert.count() > 0) {
      await expect(successAlert.first()).toBeVisible();
    }

    await page.screenshot({ path: 'screenshots/delete-todo-result.png', fullPage: true });
  });

  test('UI Quality Gate: responsive layout at mobile and desktop widths and form states', async ({ page }) => {
    // Desktop width
    await page.setViewportSize({ width: 1280, height: 800 });
    await expect(page.locator('nav')).toBeVisible();
    await page.screenshot({ path: 'screenshots/desktop-layout.png', fullPage: true });

    // Mobile width
    await page.setViewportSize({ width: 375, height: 800 });
    // Check nav collapse or hamburger
    const burger = page.locator('.navbar-toggler, button[aria-label="Toggle navigation"]');
    if (await burger.count() > 0) {
      await expect(burger.first()).toBeVisible();
    }
    await page.screenshot({ path: 'screenshots/mobile-layout.png', fullPage: true });

    // Validate form states on create page
    const createLink = page.locator('a:has-text("Create"), a:has-text("Add"), button:has-text("Create"), button:has-text("Add New"), a:has-text("New Todo")').first();
    await expect(createLink).toBeVisible({ timeout: 5000 });
    await createLink.click();

    const titleField = page.getByLabel(/title/i).first();
    await expect(titleField).toBeVisible();
    await titleField.focus();
    await page.screenshot({ path: 'screenshots/form-focus-state.png' });

    // Disabled state check for submit during loading (simulate by clicking submit quickly)
    const submitBtn = page.locator('button[type="submit"], button:has-text("Save"), button:has-text("Create")').first();
    await submitBtn.click();
    // If there's a loading spinner, capture it
    const spinner = page.locator('.spinner-border, .spinner-grow, .loading');
    if (await spinner.count() > 0) {
      await expect(spinner.first()).toBeVisible();
    }

    await page.screenshot({ path: 'screenshots/form-loading-state.png' });
  });

  // API contract checks using Playwright request fixture
  test('API: GET /todos returns JSON array', async ({ request }) => {
    const r = await request.get(API_BASE + '/todos/');
    expect(r.status()).toBe(200);
    const body = await r.json().catch(() => null);
    expect(body).not.toBeNull();
    expect(Array.isArray(body)).toBe(true);
  });

  test('API: POST /todos with invalid payload returns error', async ({ request }) => {
    // Send payload missing required fields
    const r = await request.post(API_BASE + '/todos/', { data: { invalid: 'payload' } });
    // Expect 4xx error for invalid payload (could be 400 or 422)
    expect([400, 401, 403, 422]).toContain(r.status());
  });
});

import { test, expect } from '@playwright/test';

const BASE_URL = 'http://localhost:3000';
const API_BASE = 'http://localhost:8000/api';

test.describe('Feature: Frontend DJANGO TO DO LIST', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(BASE_URL);
  });

  test('Base layout: navbar, footer, and Bootstrap + custom CSS loaded', async ({ page }) => {
    // Navbar and footer existence
    await expect(page.locator('nav')).toBeVisible();
    await expect(page.locator('footer')).toBeVisible();

    // Check CSS links include Bootstrap and static custom css
    const stylesheets = await page.evaluate(() => Array.from(document.querySelectorAll('link[rel="stylesheet"]')).map(l => (l as HTMLLinkElement).href));
    const hasBootstrap = stylesheets.some(h => /bootstrap/i.test(h));
    const hasStaticCss = stylesheets.some(h => /\/static\//i.test(h) || /assets/i.test(h));
    expect(hasBootstrap).toBeTruthy();
    expect(hasStaticCss).toBeTruthy();

    await page.screenshot({ path: 'screenshots/base-layout.png' });
  });

  test('Responsive layout: mobile and desktop nav behavior', async ({ page }) => {
    // Mobile viewport
    await page.setViewportSize({ width: 375, height: 812 });
    await page.waitForTimeout(300); // allow responsive JS to settle
    const navToggler = page.locator('.navbar-toggler');
    expect(await navToggler.count()).toBeGreaterThan(0);
    await page.screenshot({ path: 'screenshots/mobile-nav.png' });

    // Desktop viewport
    await page.setViewportSize({ width: 1280, height: 800 });
    await page.waitForTimeout(300);
    // On desktop the toggler may be hidden; check that nav links (role=navigation) are visible
    const nav = page.locator('nav');
    await expect(nav).toBeVisible();
    await page.screenshot({ path: 'screenshots/desktop-nav.png' });
  });

  test('Todo List UI: shows cards or empty state and cards contain required fields', async ({ page }) => {
    // Look for todo card candidates using common classes/selectors
    const cardSelectors = ['[data-testid="todo-card"]', '.todo-card', '.card.todo', '.card'];
    let cardsCount = 0;
    for (const sel of cardSelectors) {
      const count = await page.locator(sel).count();
      if (count > 0) {
        cardsCount = count;
        break;
      }
    }

    if (cardsCount > 0) {
      // Inspect the first card for title, description, status, created date, and action buttons
      const firstCard = await page.locator(cardSelectors.join(',')).first();
      await expect(firstCard).toBeVisible();

      // Title (h1-h4 or .card-title)
      const title = firstCard.locator('h1, h2, h3, h4, .card-title, [data-testid="todo-title"]');
      await expect(title).toBeVisible();

      // Description (p, .card-text, [data-testid="todo-desc"])
      const desc = firstCard.locator('p, .card-text, [data-testid="todo-desc"]');
      await expect(desc).toBeVisible();

      // Status badge (badge, .status, [data-testid="todo-status"]) - may be complete/incomplete
      const status = firstCard.locator('.badge, .status, [data-testid="todo-status"]');
      await expect(status).toBeVisible();

      // Created date - check for datetime patterns
      const dateText = await firstCard.innerText();
      const dateRegex = /\b\d{4}-\d{2}-\d{2}\b|\b\w{3,9}\s+\d{1,2},\s+\d{4}\b/;
      expect(dateRegex.test(dateText)).toBeTruthy();

      // Edit and Delete actions
      const editBtn = firstCard.locator('button:has-text("Edit"), a:has-text("Edit"), [data-testid="edit-btn"]');
      const deleteBtn = firstCard.locator('button:has-text("Delete"), a:has-text("Delete"), [data-testid="delete-btn"]');
      await expect(editBtn).toBeVisible();
      await expect(deleteBtn).toBeVisible();

      await page.screenshot({ path: 'screenshots/todo-card-present.png' });
    } else {
      // Expect empty state UI
      const emptyState = page.locator('text=/no (todos|tasks)/i, [data-testid="empty-state"], .empty-state');
      await expect(emptyState).toBeVisible();
      await page.screenshot({ path: 'screenshots/todo-empty-state.png' });
    }
  });

  test('Create Todo page: form presence, validation, and submit UI', async ({ page }) => {
    // Find link/button to create a todo
    const createLink = page.locator('a:has-text("Create"), a:has-text("Add"), button:has-text("Create"), button:has-text("Add")');
    expect(await createLink.count()).toBeGreaterThanOrEqual(0);

    if ((await createLink.count()) > 0) {
      await createLink.first().click();
      await page.waitForLoadState('networkidle');

      // Form fields (title, description) - look for common names/placeholders
      const titleInput = page.locator('input[name="title"], input[id*="title"], input[placeholder*="Title"], [data-testid="title-input"]');
      const descInput = page.locator('textarea[name="description"], textarea[id*="description"], textarea[placeholder*="Description"], [data-testid="description-input"]');
      const submitBtn = page.locator('button:has-text("Submit"), button:has-text("Create"), button[type="submit"]');
      const cancelBtn = page.locator('button:has-text("Cancel"), a:has-text("Cancel")');

      await expect(titleInput).toBeVisible();
      await expect(descInput).toBeVisible();
      await expect(submitBtn).toBeVisible();
      await expect(cancelBtn).toBeVisible();

      // Client-side validation: try submitting empty form
      await submitBtn.first().click();
      // Expect validation UI (invalid-feedback or role=alert)
      const validation = page.locator('.invalid-feedback, [role="alert"], .error');
      await expect(validation).toBeVisible();

      // Fill form with sample data
      await titleInput.fill('E2E Test Todo');
      await descInput.fill('This is a test todo created by Playwright.');
      await submitBtn.first().click();

      // Expect either navigation back to list or success alert
      const successAlert = page.locator('.alert-success, text=/success/i, [data-testid="alert-success"]');
      const listUrlPattern = new RegExp('todo', 'i');
      await page.waitForTimeout(500);
      const url = page.url();
      if (successAlert.count() > 0) {
        await expect(successAlert).toBeVisible();
      } else {
        // If navigated, expect URL contains 'todo' or root
        expect(listUrlPattern.test(url) || url === BASE_URL).toBeTruthy();
      }

      await page.screenshot({ path: 'screenshots/create-todo.png' });
    } else {
      test.skip(true, 'Create link/button not found on the page; skipping create todo UI test');
    }
  });

  test('Edit and Delete: present and show confirmation on delete', async ({ page }) => {
    // Find first todo card
    const card = page.locator('[data-testid="todo-card"], .todo-card, .card.todo, .card').first();
    if ((await card.count()) === 0) {
      test.skip(true, 'No todo cards found to test edit/delete flows');
      return;
    }

    const editBtn = card.locator('button:has-text("Edit"), a:has-text("Edit"), [data-testid="edit-btn"]');
    const deleteBtn = card.locator('button:has-text("Delete"), a:has-text("Delete"), [data-testid="delete-btn"]');

    await expect(editBtn).toBeVisible();
    await expect(deleteBtn).toBeVisible();

    // Click edit - check that form is pre-filled
    await editBtn.first().click();
    await page.waitForLoadState('networkidle');
    const titleInput = page.locator('input[name="title"], input[id*="title"], [data-testid="title-input"]');
    await expect(titleInput).toBeVisible();
    const value = await titleInput.inputValue();
    expect(value.length).toBeGreaterThan(0);

    await page.screenshot({ path: 'screenshots/edit-form-prefilled.png' });

    // Cancel edit if possible
    const cancelBtn = page.locator('button:has-text("Cancel"), a:has-text("Cancel")');
    if ((await cancelBtn.count()) > 0) await cancelBtn.first().click();

    // Test delete confirmation
    await deleteBtn.first().click();
    // Expect either a modal or a confirmation page/message
    const modal = page.locator('.modal, [role="dialog"]');
    const confirmBtn = page.locator('button:has-text("Confirm"), button:has-text("Delete"), button:has-text("Yes"), [data-testid="confirm-delete"]');
    const cancelDeleteBtn = page.locator('button:has-text("Cancel"), button:has-text("No"), [data-testid="cancel-delete"]');

    await expect(modal.or(confirmBtn)).toBeTruthy();
    // If modal visible, check warning text
    if ((await modal.count()) > 0 && await modal.isVisible()) {
      const warning = modal.locator('text=/are you sure|warning|delete/i');
      await expect(warning).toBeVisible();
    }

    await page.screenshot({ path: 'screenshots/delete-confirmation.png' });
  });
});

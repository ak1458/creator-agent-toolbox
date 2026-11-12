import { test, expect } from '@playwright/test';

test('App starts and backend is healthy', async ({ page }) => {
  await page.goto('http://localhost:5175');
  await expect(page.locator('text=Creator Agent Toolbox')).toBeVisible();

  // Create a workflow to test if the full path and app are working properly
  await page.fill('input[placeholder="e.g. iPhone Battery Tips"]', 'Test Topic 123');
  await page.click('button:has-text("Create Workflow")');

  // Wait for the new workflow to appear
  await expect(page.locator('text=Test Topic 123')).toBeVisible({ timeout: 10000 });
});
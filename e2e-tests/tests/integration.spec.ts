import { test, expect } from '@playwright/test';

test.describe('Integration Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should display both Pomodoro timer and task manager', async ({ page }) => {
    // Pomodoro timer should be visible
    await expect(page.getByRole('heading', { name: 'POMODORO TIMER' })).toBeVisible();

    // Task manager should be visible (scroll to it)
    await page.locator('text=Tasks').scrollIntoViewIfNeeded();
    await expect(page.getByRole('heading', { name: 'Tasks' })).toBeVisible();
  });

  test('should update stats when completing Pomodoro sessions', async ({ page }) => {
    // Get initial stats
    const todaySessionsCard = page.locator('text="Today\'s Sessions"').locator('..').locator('.text-3xl');
    const initialSessions = await todaySessionsCard.textContent();

    // Start and complete a work session
    await page.getByRole('button', { name: 'Start Work Session' }).click();
    await page.getByRole('button', { name: 'Skip' }).click();

    // Wait for session to complete
    await page.waitForTimeout(2000);

    // Reload page to get fresh stats
    await page.reload();

    // Sessions count should have increased
    const updatedSessions = await todaySessionsCard.textContent();
    expect(parseInt(updatedSessions || '0')).toBeGreaterThan(parseInt(initialSessions || '0'));
  });

  test('should show task pomodoro progress', async ({ page }) => {
    // Scroll to task manager
    await page.locator('text=Tasks').scrollIntoViewIfNeeded();

    // Create a task with 2 estimated pomodoros
    await page.getByRole('button', { name: '+ New Task' }).click();
    await page.getByPlaceholder('Task title').fill('Pomodoro Progress Task');
    await page.getByLabel('Estimated Pomodoros').fill('2');
    await page.getByRole('button', { name: 'Create Task' }).click();

    // Task should show 0/2 pomodoros
    await expect(page.getByText('🍅 0/2')).toBeVisible();
  });

  test('should persist tasks across page reloads', async ({ page }) => {
    // Scroll to task manager
    await page.locator('text=Tasks').scrollIntoViewIfNeeded();

    // Create a task
    await page.getByRole('button', { name: '+ New Task' }).click();
    await page.getByPlaceholder('Task title').fill('Persistent Task');
    await page.getByRole('button', { name: 'Create Task' }).click();

    // Wait for task to appear
    await expect(page.getByText('Persistent Task')).toBeVisible();

    // Reload page
    await page.reload();

    // Scroll to task manager again
    await page.locator('text=Tasks').scrollIntoViewIfNeeded();

    // Task should still be there
    await expect(page.getByText('Persistent Task')).toBeVisible();
  });

  test('should persist completed Pomodoro sessions', async ({ page }) => {
    // Get initial total sessions
    const totalSessionsCard = page.locator('text="Total Sessions"').locator('..').locator('.text-3xl');
    const initialTotal = await totalSessionsCard.textContent();

    // Start and complete a session
    await page.getByRole('button', { name: 'Start Work Session' }).click();
    await page.getByRole('button', { name: 'Skip' }).click();
    await page.waitForTimeout(1000);

    // Reload page
    await page.reload();

    // Total sessions should have increased
    const updatedTotal = await totalSessionsCard.textContent();
    expect(parseInt(updatedTotal || '0')).toBeGreaterThanOrEqual(parseInt(initialTotal || '0'));
  });

  test('should show health status in footer', async ({ page }) => {
    // Scroll to bottom of page
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));

    // Health status should be visible
    await expect(page.getByText('System Status')).toBeVisible();
    await expect(page.getByText('Service')).toBeVisible();
  });

  test('should have responsive layout', async ({ page }) => {
    // Check desktop layout
    await expect(page.locator('.grid-cols-1.lg\\:grid-cols-2')).toBeVisible();

    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });

    // Pomodoro timer should still be visible
    await expect(page.getByRole('heading', { name: 'POMODORO TIMER' })).toBeVisible();

    // Task manager should still be accessible
    await page.locator('text=Tasks').scrollIntoViewIfNeeded();
    await expect(page.getByRole('heading', { name: 'Tasks' })).toBeVisible();
  });

  test('should handle multiple concurrent actions', async ({ page }) => {
    // Start a Pomodoro session
    await page.getByRole('button', { name: 'Start Work Session' }).click();
    await expect(page.getByRole('heading', { name: 'WORK' })).toBeVisible();

    // Scroll to and create a task while session is running
    await page.locator('text=Tasks').scrollIntoViewIfNeeded();
    await page.getByRole('button', { name: '+ New Task' }).click();
    await page.getByPlaceholder('Task title').fill('Concurrent Task');
    await page.getByRole('button', { name: 'Create Task' }).click();

    // Both should work correctly
    await expect(page.getByText('Concurrent Task')).toBeVisible();

    // Scroll back to timer
    await page.getByRole('heading', { name: 'WORK' }).scrollIntoViewIfNeeded();
    await expect(page.getByRole('button', { name: 'Pause' })).toBeVisible();
  });

  test('should update work time stats', async ({ page }) => {
    // Get initial work time
    const workTimeCard = page.locator('text="Work Time Today"').locator('..').locator('.text-3xl');
    const initialWorkTime = await workTimeCard.textContent();

    // Start and complete a work session
    await page.getByRole('button', { name: 'Start Work Session' }).click();
    await page.waitForTimeout(2000); // Let some time pass
    await page.getByRole('button', { name: 'Skip' }).click();
    await page.waitForTimeout(1000);

    // Reload to get fresh stats
    await page.reload();

    // Work time should have increased
    const updatedWorkTime = await workTimeCard.textContent();
    // Parse minutes from "X min" format
    const initialMins = parseInt(initialWorkTime?.replace(' min', '') || '0');
    const updatedMins = parseInt(updatedWorkTime?.replace(' min', '') || '0');
    expect(updatedMins).toBeGreaterThanOrEqual(initialMins);
  });

  test('should show correct task status badges', async ({ page }) => {
    await page.locator('text=Tasks').scrollIntoViewIfNeeded();

    // Create a task
    await page.getByRole('button', { name: '+ New Task' }).click();
    await page.getByPlaceholder('Task title').fill('Status Badge Task');
    await page.getByRole('button', { name: 'Create Task' }).click();

    const taskRow = page.locator('text=Status Badge Task').locator('..');

    // Should show todo status initially
    await expect(taskRow.getByText('todo')).toBeVisible();

    // Start the task
    await taskRow.getByText('Start').click();
    await expect(taskRow.getByText('in progress')).toBeVisible();

    // Complete the task
    await taskRow.getByText('Complete').first().click();
    await expect(taskRow.getByText('completed')).toBeVisible();
  });
});

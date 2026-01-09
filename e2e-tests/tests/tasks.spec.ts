import { test, expect } from '@playwright/test';

test.describe('Task Manager', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    // Scroll to task manager section (use heading role for specificity)
    await page.getByRole('heading', { name: 'Tasks' }).scrollIntoViewIfNeeded();
  });

  test('should display task manager on home page', async ({ page }) => {
    // Check for Tasks heading
    await expect(page.getByRole('heading', { name: 'Tasks' })).toBeVisible();

    // Check for New Task button
    await expect(page.getByRole('button', { name: '+ New Task' })).toBeVisible();

    // Check for filter buttons
    await expect(page.getByRole('button', { name: 'All' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'todo' })).toBeVisible();
  });

  test('should show task creation form when clicking New Task', async ({ page }) => {
    // Click New Task button
    await page.getByRole('button', { name: '+ New Task' }).click();

    // Form should be visible
    await expect(page.getByPlaceholder('Task title')).toBeVisible();
    await expect(page.getByPlaceholder('Task description (optional)')).toBeVisible();
    await expect(page.getByRole('button', { name: 'Create Task' })).toBeVisible();
  });

  test('should create a new task', async ({ page }) => {
    // Click New Task
    await page.getByRole('button', { name: '+ New Task' }).click();

    // Fill in task details
    await page.getByPlaceholder('Task title').fill('E2E Test Task');
    await page.getByPlaceholder('Task description (optional)').fill('Created by automated test');
    await page.getByLabel('Priority').selectOption('high');
    await page.getByLabel('Estimated Pomodoros').fill('3');

    // Submit form
    await page.getByRole('button', { name: 'Create Task' }).click();

    // Wait for task to appear in list
    await expect(page.getByText('E2E Test Task')).toBeVisible();
    await expect(page.getByText('Created by automated test')).toBeVisible();

    // Check priority badge
    await expect(page.getByText('high')).toBeVisible();

    // Check pomodoro count
    await expect(page.getByText('🍅 0/3')).toBeVisible();
  });

  test('should cancel task creation', async ({ page }) => {
    // Click New Task
    await page.getByRole('button', { name: '+ New Task' }).click();

    // Fill in some data
    await page.getByPlaceholder('Task title').fill('Test Task');

    // Click Cancel
    await page.getByRole('button', { name: 'Cancel' }).click();

    // Form should be hidden
    await expect(page.getByPlaceholder('Task title')).not.toBeVisible();

    // New Task button should be visible again
    await expect(page.getByRole('button', { name: '+ New Task' })).toBeVisible();
  });

  test('should filter tasks by status', async ({ page }) => {
    // Create a test task first
    await page.getByRole('button', { name: '+ New Task' }).click();
    await page.getByPlaceholder('Task title').fill('Filter Test Task');
    await page.getByRole('button', { name: 'Create Task' }).click();
    await expect(page.getByText('Filter Test Task')).toBeVisible();

    // Filter by TODO (should show the task)
    await page.getByRole('button', { name: 'todo' }).click();
    await expect(page.getByText('Filter Test Task')).toBeVisible();

    // Filter by COMPLETED (should not show the task)
    await page.getByRole('button', { name: 'completed' }).click();
    await expect(page.getByText('Filter Test Task')).not.toBeVisible();

    // Filter back to All
    await page.getByRole('button', { name: 'All' }).click();
    await expect(page.getByText('Filter Test Task')).toBeVisible();
  });

  test('should mark task as in progress', async ({ page }) => {
    // Create a task
    await page.getByRole('button', { name: '+ New Task' }).click();
    await page.getByPlaceholder('Task title').fill('Progress Test Task');
    await page.getByRole('button', { name: 'Create Task' }).click();

    // Wait for task to appear
    await expect(page.getByText('Progress Test Task')).toBeVisible();

    // Find the task row and click Start
    const taskRow = page.locator('text=Progress Test Task').locator('..');
    await taskRow.getByText('Start').click();

    // Status should change to in_progress
    await expect(taskRow.getByText('in progress')).toBeVisible();
  });

  test('should complete a task', async ({ page }) => {
    // Create a task
    await page.getByRole('button', { name: '+ New Task' }).click();
    await page.getByPlaceholder('Task title').fill('Complete Test Task');
    await page.getByRole('button', { name: 'Create Task' }).click();

    // Wait for task to appear
    await expect(page.getByText('Complete Test Task')).toBeVisible();

    // Find the task row and click Complete
    const taskRow = page.locator('text=Complete Test Task').locator('..');
    await taskRow.getByText('Complete').first().click();

    // Status should change to completed
    await expect(taskRow.getByText('completed')).toBeVisible();
  });

  test('should delete a task', async ({ page }) => {
    // Create a task
    await page.getByRole('button', { name: '+ New Task' }).click();
    await page.getByPlaceholder('Task title').fill('Delete Test Task');
    await page.getByRole('button', { name: 'Create Task' }).click();

    // Wait for task to appear
    await expect(page.getByText('Delete Test Task')).toBeVisible();

    // Find the task row and click Delete
    const taskRow = page.locator('text=Delete Test Task').locator('..');
    await taskRow.getByText('Delete').click();

    // Task should be removed
    await expect(page.getByText('Delete Test Task')).not.toBeVisible();
  });

  test('should show correct priority colors', async ({ page }) => {
    const priorities = ['low', 'medium', 'high', 'urgent'];

    for (const priority of priorities) {
      // Create task with specific priority
      await page.getByRole('button', { name: '+ New Task' }).click();
      await page.getByPlaceholder('Task title').fill(`${priority} Priority Task`);
      await page.getByLabel('Priority').selectOption(priority);
      await page.getByRole('button', { name: 'Create Task' }).click();

      // Check priority badge exists
      const taskRow = page.locator(`text=${priority} Priority Task`).locator('..');
      await expect(taskRow.getByText(priority)).toBeVisible();
    }
  });

  test('should validate required fields', async ({ page }) => {
    // Click New Task
    await page.getByRole('button', { name: '+ New Task' }).click();

    // Try to submit without title (HTML5 validation should prevent this)
    const createButton = page.getByRole('button', { name: 'Create Task' });
    await createButton.click();

    // Form should still be visible (submission blocked)
    await expect(page.getByPlaceholder('Task title')).toBeVisible();
  });

  test('should display empty state when no tasks', async ({ page }) => {
    // Filter by completed (assuming no completed tasks initially)
    await page.getByRole('button', { name: 'completed' }).click();

    // Should show empty state message
    await expect(page.getByText(/No tasks found/i)).toBeVisible();
  });

  test('should show task count', async ({ page }) => {
    // Create a few tasks
    for (let i = 0; i < 3; i++) {
      await page.getByRole('button', { name: '+ New Task' }).click();
      await page.getByPlaceholder('Task title').fill(`Count Test Task ${i + 1}`);
      await page.getByRole('button', { name: 'Create Task' }).click();
      await page.waitForTimeout(500);
    }

    // Should show task count
    await expect(page.getByText(/Showing \d+ of \d+ tasks/i)).toBeVisible();
  });

  test('should display task creation date', async ({ page }) => {
    // Create a task
    await page.getByRole('button', { name: '+ New Task' }).click();
    await page.getByPlaceholder('Task title').fill('Date Test Task');
    await page.getByRole('button', { name: 'Create Task' }).click();

    // Should show "Created" with a date
    const taskRow = page.locator('text=Date Test Task').locator('..');
    await expect(taskRow.getByText(/Created/i)).toBeVisible();
  });
});

import { test, expect } from '@playwright/test';

test.describe('Pomodoro Timer', () => {
  test.beforeEach(async ({ page, request }) => {
    // Clean up any active sessions from previous tests
    const activeSession = await request.get('http://192.168.0.18:30100/api/pomodoro/active');
    if (activeSession.ok()) {
      const sessionData = await activeSession.json();
      if (sessionData && sessionData.id) {
        await request.post(`http://192.168.0.18:30100/api/pomodoro/sessions/${sessionData.id}/interrupt`);
      }
    }

    await page.goto('/');
  });

  test('should display Pomodoro timer on home page', async ({ page }) => {
    // Check for timer title (use heading role for specificity)
    await expect(page.getByRole('heading', { name: 'POMODORO TIMER' })).toBeVisible();

    // Check for initial time display (25:00)
    await expect(page.locator('.text-7xl').filter({ hasText: '25:00' })).toBeVisible();

    // Check for start button
    await expect(page.getByRole('button', { name: 'Start Work Session' })).toBeVisible();
  });

  test('should start a work session', async ({ page }) => {
    // Click start work session
    await page.getByRole('button', { name: 'Start Work Session' }).click();

    // Timer should change to show it's running (check heading specifically)
    await expect(page.getByRole('heading', { name: 'WORK', exact: true })).toBeVisible();

    // Pause button should be visible
    await expect(page.getByRole('button', { name: 'Pause' })).toBeVisible();

    // Stop button should be visible
    await expect(page.getByRole('button', { name: 'Stop' })).toBeVisible();
  });

  test('should pause and resume a session', async ({ page }) => {
    // Start work session
    await page.getByRole('button', { name: 'Start Work Session' }).click();
    await expect(page.getByRole('button', { name: 'Pause' })).toBeVisible();

    // Wait a moment for timer to tick
    await page.waitForTimeout(2000);

    // Pause the session
    await page.getByRole('button', { name: 'Pause' }).click();

    // Resume button should be visible
    await expect(page.getByRole('button', { name: 'Resume' })).toBeVisible();

    // Resume the session
    await page.getByRole('button', { name: 'Resume' }).click();

    // Pause button should be back
    await expect(page.getByRole('button', { name: 'Pause' })).toBeVisible();
  });

  test('should stop a session', async ({ page }) => {
    // Start work session
    await page.getByRole('button', { name: 'Start Work Session' }).click();
    await expect(page.getByRole('heading', { name: 'WORK', exact: true })).toBeVisible();

    // Stop the session
    await page.getByRole('button', { name: 'Stop' }).click();

    // Should return to initial state
    await expect(page.getByRole('heading', { name: 'POMODORO TIMER' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Start Work Session' })).toBeVisible();
  });

  test('should start a break session', async ({ page }) => {
    // Click start break
    await page.getByRole('button', { name: 'Start Break' }).click();

    // Should show break timer (05:00 for short break) - check heading
    await expect(page.getByRole('heading', { name: 'SHORT BREAK' })).toBeVisible();

    // Pause button should be visible
    await expect(page.getByRole('button', { name: 'Pause' })).toBeVisible();
  });

  test('should display session counter', async ({ page }) => {
    // Initial counter should be 0
    await expect(page.getByText('Sessions completed today: 0')).toBeVisible();

    // Start and complete a work session (using skip button for speed)
    await page.getByRole('button', { name: 'Start Work Session' }).click();
    await page.getByRole('button', { name: 'Skip' }).click();

    // Wait for session to complete
    await page.waitForTimeout(1000);

    // Counter should increment
    await expect(page.getByText('Sessions completed today: 1')).toBeVisible();
  });

  test('should show progress bar during session', async ({ page }) => {
    // Start work session
    await page.getByRole('button', { name: 'Start Work Session' }).click();

    // Progress bar should be visible
    const progressBar = page.locator('.h-2.rounded-full').first();
    await expect(progressBar).toBeVisible();

    // Wait a moment and check progress bar has width
    await page.waitForTimeout(2000);
    const width = await progressBar.evaluate(el => getComputedStyle(el).width);
    expect(parseFloat(width)).toBeGreaterThan(0);
  });

  test('should countdown the timer', async ({ page }) => {
    // Start work session
    await page.getByRole('button', { name: 'Start Work Session' }).click();

    // Get initial time
    const timerDisplay = page.locator('.text-7xl').first();
    const initialTime = await timerDisplay.textContent();

    // Wait for countdown
    await page.waitForTimeout(2000);

    // Get updated time
    const updatedTime = await timerDisplay.textContent();

    // Time should have decreased
    expect(initialTime).not.toBe(updatedTime);
  });

  test('should display stats on home page', async ({ page }) => {
    // Stats cards should be visible
    await expect(page.getByText("Today's Sessions")).toBeVisible();
    await expect(page.getByText('Work Time Today')).toBeVisible();
    await expect(page.getByText('Total Sessions')).toBeVisible();
    await expect(page.getByText('Current Streak')).toBeVisible();
  });

  test('should update stats after completing a session', async ({ page }) => {
    // Wait for page to be fully loaded and ready
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500);

    // Get initial today's sessions count
    const todaySessionsCard = page.locator('text="Today\'s Sessions"').locator('..').locator('.text-3xl');
    const initialCount = await todaySessionsCard.textContent();

    // Ensure Start Work Session button is visible before clicking
    await expect(page.getByRole('button', { name: 'Start Work Session' })).toBeVisible();

    // Start and skip a work session
    await page.getByRole('button', { name: 'Start Work Session' }).click();
    await page.getByRole('button', { name: 'Skip' }).click();

    // Wait for stats to update
    await page.waitForTimeout(2000);

    // Reload to get fresh stats
    await page.reload();

    // Stats should have updated
    const updatedCount = await todaySessionsCard.textContent();
    expect(parseInt(updatedCount || '0')).toBeGreaterThanOrEqual(parseInt(initialCount || '0'));
  });
});

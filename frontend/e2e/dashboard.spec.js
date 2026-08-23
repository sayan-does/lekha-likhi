import { test, expect } from '@playwright/test';

const MOCK_TOKEN = 'test-jwt-token';
const ENTRY_ID = '11111111-1111-1111-1111-111111111111';
const PAST_ENTRY_ID = '22222222-2222-2222-2222-222222222222';
const SHARE_TOKEN = 'abc123share';

function todayIso() {
  const date = new Date();
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

function yesterdayIso() {
  const date = new Date();
  date.setDate(date.getDate() - 1);
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

async function mockDashboardApi(page) {
  const today = todayIso();
  const yesterday = yesterdayIso();
  const bodies = {
    [today]: 'Today I wrote on the dashboard.',
    [yesterday]: 'Yesterday was a quiet day.',
  };

  await page.route('**/me', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        id: '99999999-9999-9999-9999-999999999999',
        display_name: 'Test Writer',
        email: 'writer@example.com',
      }),
    }),
  );

  await page.route('**/entries?limit=50', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        entries: [
          {
            id: ENTRY_ID,
            entry_date: today,
            body: bodies[today],
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          },
          {
            id: PAST_ENTRY_ID,
            entry_date: yesterday,
            body: bodies[yesterday],
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          },
        ],
        total: 2,
        limit: 50,
        offset: 0,
      }),
    }),
  );

  await page.route(/\/entries\/\d{4}-\d{2}-\d{2}/, async (route) => {
    if (route.request().method() !== 'PUT') {
      return route.fallback();
    }
    const date = route.request().url().match(/(\d{4}-\d{2}-\d{2})/)?.[1];
    const payload = JSON.parse(route.request().postData() || '{}');
    if (date) bodies[date] = payload.body ?? '';
    return route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        id: date === today ? ENTRY_ID : PAST_ENTRY_ID,
        entry_date: date,
        body: date ? bodies[date] : '',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      }),
    });
  });

  await page.route('**/share-links', (route) => {
    if (route.request().method() === 'GET') {
      return route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          {
            id: '33333333-3333-3333-3333-333333333333',
            entry_id: ENTRY_ID,
            token: SHARE_TOKEN,
            is_active: true,
            created_at: new Date().toISOString(),
            revoked_at: null,
            entry_date: today,
          },
        ]),
      });
    }
    return route.continue();
  });

  await page.route(`**/shared/${SHARE_TOKEN}/reactions`, (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([{ display_name: 'Friend', emoji: '❤️' }]),
    }),
  );
}

async function openHome(page) {
  await page.addInitScript((token) => {
    sessionStorage.setItem('access_token', token);
  }, MOCK_TOKEN);

  await mockDashboardApi(page);
  await page.goto('/');
  await expect(page.getByText("what's on your mind?")).toBeVisible();
}

async function openWriter(page) {
  await openHome(page);
  await page.getByText('tap to write today').click();
  await expect(page.getByText('Today I wrote on the dashboard.')).toBeVisible();
}

test.describe('landing home', () => {
  test('shows start today and last writing in past card', async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await openHome(page);
    await expect(page.getByRole('img', { name: 'Lekha Likhi' })).toBeVisible();
    await expect(page.getByRole('button', { name: /notes from the past/i })).toContainText(
      'Yesterday was a quiet day.',
    );
    await page.screenshot({
      path: 'e2e/screenshots/home-mobile-390x844.png',
      fullPage: true,
    });
  });

  test('notes from the past opens archive', async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await openHome(page);
    await page.getByRole('button', { name: /notes from the past/i }).click();
    await expect(page.getByRole('heading', { name: 'past writings' })).toBeVisible();
  });
});

test.describe('writer flow', () => {
  test('mobile viewport screenshot', async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await openWriter(page);
    await page.screenshot({
      path: 'e2e/screenshots/dashboard-mobile-390x844.png',
      fullPage: true,
    });
  });

  test('desktop viewport screenshot', async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 800 });
    await openWriter(page);
    await page.screenshot({
      path: 'e2e/screenshots/dashboard-desktop-1280x800.png',
      fullPage: true,
    });
  });

  test('archive entry opens writer', async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await openHome(page);
    await page.getByRole('button', { name: /notes from the past/i }).click();
    await page.getByRole('button', { name: /Yesterday was a quiet day/i }).click();
    await expect(page.getByText('Yesterday was a quiet day.').first()).toBeVisible();
  });

  test('share popover opens from date-row stamp', async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await openWriter(page);
    await page.getByRole('button', { name: 'Share entry' }).click();
    await expect(page.getByText('copy link')).toBeVisible();
  });

  test('close returns to home', async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await openWriter(page);
    await page.getByRole('button', { name: 'Close notebook' }).click();
    await expect(page.getByText("what's on your mind?")).toBeVisible();
  });

  test('writing is restored after leaving the page', async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await openWriter(page);
    const editor = page.locator('textarea');
    const nextBody = 'Kept this sentence while I stepped away.';

    await editor.click();
    await editor.evaluate((el, value) => {
      const descriptor = Object.getOwnPropertyDescriptor(
        window.HTMLTextAreaElement.prototype,
        'value',
      );
      descriptor.set.call(el, value);
      el.dispatchEvent(new Event('input', { bubbles: true }));
    }, nextBody);

    await expect
      .poll(async () =>
        page.evaluate(() => {
          const raw = localStorage.getItem('writing_session');
          if (!raw) return '';
          const drafts = JSON.parse(raw).drafts || {};
          return Object.values(drafts)
            .map((draft) => draft?.body ?? '')
            .join('\n');
        }),
      )
      .not.toBe('');

    const persisted = await editor.inputValue();
    expect(persisted.length).toBeGreaterThan(0);

    await page.getByRole('button', { name: 'Close notebook' }).click();
    await expect(page.getByText("what's on your mind?")).toBeVisible();
    await page.getByText('tap to write today').click();
    await expect(page.locator('textarea')).toHaveValue(persisted);
  });
});

test.describe('sign out', () => {
  test('returns to google sign-in', async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await openHome(page);
    await page.getByRole('button', { name: 'sign out' }).click();
    await expect(page.getByRole('button', { name: 'Sign in with Google' })).toBeVisible();
    await expect(page.getByRole('img', { name: 'Lekha Likhi' })).toBeVisible();
  });
});

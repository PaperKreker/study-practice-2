const { test, expect } = require('@playwright/test');

test('user logs in, uploads a document, and finds its indexed text', async ({
  page,
}) => {
  let uploaded = false;

  await page.route('**/api/v1/**', async (route) => {
    const request = route.request();
    const url = new URL(request.url());
    const path = url.pathname;

    if (path === '/api/v1/users/login' && request.method() === 'POST') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          access_token: 'qa-token',
          token_type: 'bearer',
          user: {
            id: 'user-1',
            username: 'qa-user',
            is_active: true,
            created_at: '2026-07-04T12:00:00Z',
          },
        }),
      });
      return;
    }

    if (path === '/api/v1/documents/upload' && request.method() === 'POST') {
      uploaded = true;
      await route.fulfill({
        status: 201,
        contentType: 'application/json',
        body: JSON.stringify({
          document_id: 'doc-1',
          file_name: 'qa-e2e.pdf',
          size_bytes: 42,
          message: 'uploaded',
        }),
      });
      return;
    }

    if (path === '/api/v1/documents/doc-1' && request.method() === 'GET') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ id: 'doc-1', status: 'ready' }),
      });
      return;
    }

    if (path === '/api/v1/documents' && request.method() === 'GET') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          total: uploaded ? 1 : 0,
          items: uploaded
            ? [
                {
                  id: 'doc-1',
                  file_name: 'qa-e2e.pdf',
                  size_bytes: 42,
                  chunk_count: 1,
                  uploaded_at: '2026-07-04T12:00:00Z',
                  user_id: 'user-1',
                },
              ]
            : [],
        }),
      });
      return;
    }

    if (path === '/api/v1/search/history' && request.method() === 'GET') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ total: 0, items: [] }),
      });
      return;
    }

    if (path === '/api/v1/search' && request.method() === 'GET') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          total: 1,
          items: [
            {
              chunk_id: 'doc-1_0',
              document_id: 'doc-1',
              file_name: 'qa-e2e.pdf',
              page: 2,
              text: 'Elasticsearch indexes university knowledge.',
              score: 3.75,
              highlights: ['<mark>Elasticsearch</mark> indexes'],
            },
          ],
        }),
      });
      return;
    }

    await route.fulfill({
      status: 404,
      contentType: 'application/json',
      body: JSON.stringify({ detail: `Unhandled QA route: ${path}` }),
    });
  });

  await page.goto('/');
  await page.locator('.app-auth').getByRole('button', { name: 'Войти' }).click();

  const dialog = page.getByRole('dialog', { name: 'Вход' });
  await dialog.getByLabel('Имя пользователя').fill('qa-user');
  await dialog.getByLabel('Пароль').fill('secret-password');
  await dialog.getByRole('button', { name: 'Войти' }).click();
  await expect(page.locator('.app-auth')).toContainText('qa-user');

  await page.locator('input[type="file"]').setInputFiles({
    name: 'qa-e2e.pdf',
    mimeType: 'application/pdf',
    buffer: Buffer.from('%PDF-1.7\nQA fixture\n%%EOF'),
  });

  await expect(page.getByText('Готово')).toBeVisible();
  await expect(page.getByRole('table')).toContainText('qa-e2e.pdf');

  await page
    .getByRole('navigation', { name: 'Основная навигация' })
    .getByRole('button', { name: 'Поиск' })
    .click();
  await page.getByLabel('Поисковый запрос').fill('Elasticsearch');
  await page.getByRole('button', { name: 'Найти' }).click();

  await expect(page.getByText('Найдено совпадений: 1')).toBeVisible();
  await expect(page.getByText('qa-e2e.pdf')).toBeVisible();
  await expect(page.getByText('Страница 2')).toBeVisible();
  await expect(page.locator('mark')).toContainText('Elasticsearch');
});

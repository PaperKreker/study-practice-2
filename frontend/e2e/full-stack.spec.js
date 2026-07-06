const path = require('path');

const { test, expect } = require('@playwright/test');


test.skip(
  !process.env.QA_FULL_STACK,
  'Set QA_FULL_STACK=1 and start Docker Compose to run this scenario'
);

test('real services support registration, upload, indexing, and search', async ({
  page,
}) => {
  const username = `qa-e2e-${Date.now()}`;
  const fixture = path.resolve(
    __dirname,
    '../../backend/tests/fixtures/valid_small.pdf'
  );

  await page.goto('/');
  await page.locator('.app-auth').getByRole('button', { name: 'Войти' }).click();

  const loginDialog = page.getByRole('dialog', { name: 'Вход' });
  await loginDialog
    .getByRole('button', { name: 'Зарегистрироваться' })
    .click();

  const registerDialog = page.getByRole('dialog', { name: 'Регистрация' });
  await registerDialog.getByLabel('Имя пользователя').fill(username);
  await registerDialog.getByLabel('Пароль').fill('qa-e2e-password');
  await registerDialog
    .getByRole('button', { name: 'Зарегистрироваться' })
    .click();
  await expect(page.locator('.app-auth')).toContainText(username);

  const uploadResponse = page.waitForResponse(
    (response) =>
      response.url().includes('/api/v1/documents/upload') &&
      response.request().method() === 'POST'
  );
  await page.locator('input[type="file"]').setInputFiles(fixture);
  expect((await uploadResponse).status()).toBe(201);

  await page
    .getByRole('navigation', { name: 'Основная навигация' })
    .getByRole('button', { name: 'Поиск' })
    .click();
  await page.getByLabel('Поисковый запрос').fill('knowledge base search');
  await page.getByRole('button', { name: 'Найти' }).click();

  await expect(page.getByText('Найдено совпадений: 1')).toBeVisible();
  await expect(page.locator('.results-list')).toContainText('valid_small.pdf');
  await expect(
    page.locator('.results-list').getByText('knowledge', { exact: true })
  ).toBeVisible();
});

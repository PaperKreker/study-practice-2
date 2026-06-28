import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import App from './App';

// Глобально подменяем fetch, чтобы компоненты, делающие запросы при монтировании
// (например, список документов), не падали в тестовой среде.
beforeEach(() => {
  global.fetch = jest.fn(() =>
    Promise.resolve({
      ok: true,
      json: () => Promise.resolve([]),
    })
  );
});

afterEach(() => {
  jest.resetAllMocks();
});

async function renderApp() {
  render(<App />);
  await waitFor(() => {
    expect(global.fetch).toHaveBeenCalledWith('/api/v1/documents');
  });
}

test('отображает заголовок приложения', async () => {
  await renderApp();
  expect(screen.getByText('База знаний')).toBeInTheDocument();
});

test('по умолчанию открыта вкладка загрузки', async () => {
  await renderApp();
  expect(screen.getByText('Загрузка документов')).toBeInTheDocument();
});

test('переключается на вкладку поиска', async () => {
  await renderApp();
  fireEvent.click(screen.getByRole('button', { name: 'Поиск' }));
  expect(screen.getByPlaceholderText(/Введите поисковый запрос/i)).toBeInTheDocument();
});

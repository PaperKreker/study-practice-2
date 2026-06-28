import { render, screen, fireEvent } from '@testing-library/react';
import App from './App';
import { AuthProvider } from './context/AuthContext';

// Глобально подменяем fetch, чтобы компоненты, делающие запросы при монтировании
// (например, список документов), не падали в тестовой среде.
beforeEach(() => {
  global.fetch = jest.fn(() =>
    Promise.resolve({
      ok: true,
      json: () => Promise.resolve({ items: [], total: 0 }),
    })
  );
  localStorage.clear();
});

afterEach(() => {
  jest.resetAllMocks();
});

/** Рендерит приложение вместе с провайдером аутентификации. */
function renderApp() {
  return render(
    <AuthProvider>
      <App />
    </AuthProvider>
  );
}

test('отображает заголовок приложения', () => {
  renderApp();
  expect(screen.getByText('База знаний')).toBeInTheDocument();
});

test('по умолчанию открыта вкладка загрузки', () => {
  renderApp();
  expect(screen.getByText('Загрузка документов')).toBeInTheDocument();
});

test('переключается на вкладку поиска', () => {
  renderApp();
  fireEvent.click(screen.getByRole('button', { name: 'Поиск' }));
  expect(
    screen.getByPlaceholderText(/Введите поисковый запрос/i)
  ).toBeInTheDocument();
});

test('показывает кнопку входа для неавторизованного пользователя', () => {
  renderApp();
  expect(screen.getByRole('button', { name: 'Войти' })).toBeInTheDocument();
});

test('открывает модальное окно входа', () => {
  renderApp();
  fireEvent.click(screen.getByRole('button', { name: 'Войти' }));
  expect(screen.getByRole('dialog')).toBeInTheDocument();
});

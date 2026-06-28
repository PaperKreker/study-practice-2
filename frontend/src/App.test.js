import { render, screen, fireEvent, within, waitFor } from '@testing-library/react';
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
  expect(screen.getByText('Поиск по базе знаний')).toBeInTheDocument();
  expect(
    screen.getByText('Войдите в систему, чтобы искать по базе знаний.')
  ).toBeInTheDocument();
});

test('показывает кнопку входа для неавторизованного пользователя', () => {
  renderApp();
  const authArea = document.querySelector('.app-auth');
  expect(within(authArea).getByRole('button', { name: 'Войти' })).toBeInTheDocument();
});

test('открывает модальное окно входа', () => {
  renderApp();
  const authArea = document.querySelector('.app-auth');
  fireEvent.click(within(authArea).getByRole('button', { name: 'Войти' }));
  expect(screen.getByRole('dialog')).toBeInTheDocument();
});

test('показывает пользователя и открывает поиск после восстановления сессии', async () => {
  localStorage.setItem('auth_token', 'stored-token');
  localStorage.setItem(
    'auth_user',
    JSON.stringify({ id: 'user-1', username: 'student' })
  );

  renderApp();

  expect(screen.getByText('student')).toBeInTheDocument();
  expect(
    await screen.findByText('Пока нет загруженных документов.')
  ).toBeInTheDocument();
  fireEvent.click(screen.getByRole('button', { name: 'Поиск' }));
  expect(
    screen.getByPlaceholderText(/Введите поисковый запрос/i)
  ).toBeInTheDocument();
  await waitFor(() => expect(global.fetch).toHaveBeenCalled());
});

test('выходит из восстановленной сессии', async () => {
  localStorage.setItem('auth_token', 'stored-token');
  localStorage.setItem(
    'auth_user',
    JSON.stringify({ id: 'user-1', username: 'student' })
  );

  renderApp();
  expect(
    await screen.findByText('Пока нет загруженных документов.')
  ).toBeInTheDocument();
  fireEvent.click(screen.getByRole('button', { name: 'Выйти' }));

  expect(localStorage.getItem('auth_token')).toBeNull();
  const authArea = document.querySelector('.app-auth');
  expect(within(authArea).getByRole('button', { name: 'Войти' })).toBeInTheDocument();
});

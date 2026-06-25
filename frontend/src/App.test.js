import { render, screen, fireEvent } from '@testing-library/react';
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

test('отображает заголовок приложения', () => {
  render(<App />);
  expect(screen.getByText('База знаний')).toBeInTheDocument();
});

test('по умолчанию открыта вкладка поиска', () => {
  render(<App />);
  expect(
    screen.getByPlaceholderText(/Введите поисковый запрос/i)
  ).toBeInTheDocument();
});

test('переключается на вкладку загрузки', () => {
  render(<App />);
  fireEvent.click(screen.getByRole('button', { name: 'Загрузка' }));
  expect(screen.getByText('Загрузка документов')).toBeInTheDocument();
});

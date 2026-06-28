import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import AuthModal from './AuthModal';
import { useAuth } from '../context/AuthContext';

jest.mock('../context/AuthContext', () => ({
  useAuth: jest.fn(),
}));

beforeEach(() => {
  useAuth.mockReturnValue({
    login: jest.fn(),
    register: jest.fn(),
  });
});

afterEach(() => {
  jest.resetAllMocks();
});

test('validates required credentials', () => {
  render(<AuthModal onClose={jest.fn()} />);

  fireEvent.click(screen.getByRole('button', { name: 'Войти' }));

  expect(screen.getByText('Введите имя пользователя и пароль')).toBeInTheDocument();
});

test('logs in with trimmed username and closes modal', async () => {
  const login = jest.fn().mockResolvedValue({});
  const onClose = jest.fn();
  useAuth.mockReturnValue({ login, register: jest.fn() });
  render(<AuthModal onClose={onClose} />);

  fireEvent.change(screen.getByLabelText('Имя пользователя'), {
    target: { value: '  student  ' },
  });
  fireEvent.change(screen.getByLabelText('Пароль'), {
    target: { value: 'secret1' },
  });
  fireEvent.click(screen.getByRole('button', { name: 'Войти' }));

  await waitFor(() => expect(login).toHaveBeenCalledWith('student', 'secret1'));
  expect(onClose).toHaveBeenCalledTimes(1);
});

test('switches to registration and submits credentials', async () => {
  const register = jest.fn().mockResolvedValue({});
  useAuth.mockReturnValue({ login: jest.fn(), register });
  render(<AuthModal onClose={jest.fn()} />);

  fireEvent.click(screen.getByRole('button', { name: 'Зарегистрироваться' }));
  expect(screen.getByRole('dialog', { name: 'Регистрация' })).toBeInTheDocument();

  fireEvent.change(screen.getByLabelText('Имя пользователя'), {
    target: { value: 'student' },
  });
  fireEvent.change(screen.getByLabelText('Пароль'), {
    target: { value: 'secret1' },
  });
  fireEvent.click(screen.getByRole('button', { name: 'Зарегистрироваться' }));

  await waitFor(() => expect(register).toHaveBeenCalledWith('student', 'secret1'));
});

test('shows authentication errors and supports closing', async () => {
  const login = jest.fn().mockRejectedValue(new Error('Invalid credentials'));
  const onClose = jest.fn();
  useAuth.mockReturnValue({ login, register: jest.fn() });
  render(<AuthModal onClose={onClose} />);

  fireEvent.change(screen.getByLabelText('Имя пользователя'), {
    target: { value: 'student' },
  });
  fireEvent.change(screen.getByLabelText('Пароль'), {
    target: { value: 'wrong-password' },
  });
  fireEvent.click(screen.getByRole('button', { name: 'Войти' }));

  expect(await screen.findByText('Invalid credentials')).toBeInTheDocument();
  fireEvent.click(screen.getByRole('button', { name: 'Закрыть' }));
  expect(onClose).toHaveBeenCalledTimes(1);
});

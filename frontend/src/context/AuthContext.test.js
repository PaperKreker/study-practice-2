import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import {
  AuthProvider,
  isAuthenticated,
  useAuth,
} from './AuthContext';
import { loginRequest, registerRequest } from '../services/auth';

jest.mock('../services/auth', () => ({
  loginRequest: jest.fn(),
  registerRequest: jest.fn(),
}));

function AuthProbe() {
  const auth = useAuth();
  return (
    <div>
      <span data-testid="auth-state">
        {auth.isAuthenticated ? 'authenticated' : 'anonymous'}
      </span>
      <span data-testid="username">{auth.user?.username || ''}</span>
      <button type="button" onClick={() => auth.login('student', 'secret1')}>
        Login
      </button>
      <button type="button" onClick={() => auth.register('new-user', 'secret1')}>
        Register
      </button>
      <button type="button" onClick={auth.logout}>
        Logout
      </button>
    </div>
  );
}

function renderProvider() {
  return render(
    <AuthProvider>
      <AuthProbe />
    </AuthProvider>
  );
}

beforeEach(() => {
  localStorage.clear();
  jest.resetAllMocks();
});

test('restores an existing session from localStorage', () => {
  localStorage.setItem('auth_token', 'stored-token');
  localStorage.setItem('auth_user', JSON.stringify({ username: 'stored-user' }));

  renderProvider();

  expect(screen.getByTestId('auth-state')).toHaveTextContent('authenticated');
  expect(screen.getByTestId('username')).toHaveTextContent('stored-user');
  expect(isAuthenticated()).toBe(true);
});

test('persists login response and logs out', async () => {
  loginRequest.mockResolvedValue({
    access_token: 'login-token',
    user: { id: 'user-1', username: 'student' },
  });
  renderProvider();

  fireEvent.click(screen.getByRole('button', { name: 'Login' }));

  await waitFor(() => {
    expect(screen.getByTestId('auth-state')).toHaveTextContent('authenticated');
  });
  expect(loginRequest).toHaveBeenCalledWith('student', 'secret1');
  expect(localStorage.getItem('auth_token')).toBe('login-token');
  expect(screen.getByTestId('username')).toHaveTextContent('student');

  fireEvent.click(screen.getByRole('button', { name: 'Logout' }));
  expect(screen.getByTestId('auth-state')).toHaveTextContent('anonymous');
  expect(localStorage.getItem('auth_token')).toBeNull();
  expect(isAuthenticated()).toBe(false);
});

test('persists registration response', async () => {
  registerRequest.mockResolvedValue({
    access_token: 'register-token',
    user: { id: 'user-2', username: 'new-user' },
  });
  renderProvider();

  fireEvent.click(screen.getByRole('button', { name: 'Register' }));

  await waitFor(() => {
    expect(screen.getByTestId('username')).toHaveTextContent('new-user');
  });
  expect(registerRequest).toHaveBeenCalledWith('new-user', 'secret1');
  expect(localStorage.getItem('auth_token')).toBe('register-token');
});

test('ignores corrupted stored user data', () => {
  localStorage.setItem('auth_user', '{invalid-json');

  renderProvider();

  expect(screen.getByTestId('auth-state')).toHaveTextContent('anonymous');
  expect(screen.getByTestId('username')).toBeEmptyDOMElement();
});

test('requires useAuth to be rendered inside AuthProvider', () => {
  function InvalidConsumer() {
    useAuth();
    return null;
  }

  const consoleError = jest.spyOn(console, 'error').mockImplementation(() => {});
  expect(() => render(<InvalidConsumer />)).toThrow(
    'useAuth должен использоваться внутри AuthProvider'
  );
  consoleError.mockRestore();
});

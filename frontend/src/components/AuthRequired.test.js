import { fireEvent, render, screen } from '@testing-library/react';
import AuthRequired from './AuthRequired';
import { useAuth } from '../context/AuthContext';

jest.mock('../context/AuthContext', () => ({
  useAuth: jest.fn(),
}));

test('renders children for an authenticated user', () => {
  useAuth.mockReturnValue({ isAuthenticated: true });

  render(
    <AuthRequired onRequestLogin={jest.fn()}>
      <span>Protected content</span>
    </AuthRequired>
  );

  expect(screen.getByText('Protected content')).toBeInTheDocument();
  expect(screen.queryByRole('button', { name: 'Войти' })).toBeNull();
});

test('shows login prompt and requests authentication', () => {
  const onRequestLogin = jest.fn();
  useAuth.mockReturnValue({ isAuthenticated: false });

  render(
    <AuthRequired onRequestLogin={onRequestLogin} message="Authentication required">
      <span>Protected content</span>
    </AuthRequired>
  );

  expect(screen.getByText('Authentication required')).toBeInTheDocument();
  expect(screen.queryByText('Protected content')).toBeNull();
  fireEvent.click(screen.getByRole('button', { name: 'Войти' }));
  expect(onRequestLogin).toHaveBeenCalledTimes(1);
});

import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';

/**
 * Модальное окно входа и регистрации. Переключается между двумя режимами
 * одной кнопкой. После успешной аутентификации закрывается.
 *
 * @param {{ onClose: () => void }} props
 */
function AuthModal({ onClose }) {
  const { login, register } = useAuth();

  const [mode, setMode] = useState('login'); // 'login' | 'register'
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  const isLogin = mode === 'login';

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError(null);

    const trimmedName = username.trim();
    if (!trimmedName || !password) {
      setError('Введите имя пользователя и пароль');
      return;
    }

    setSubmitting(true);
    try {
      if (isLogin) {
        await login(trimmedName, password);
      } else {
        await register(trimmedName, password);
      }
      onClose();
    } catch (err) {
      setError(err.message || 'Не удалось выполнить операцию');
    } finally {
      setSubmitting(false);
    }
  };

  const toggleMode = () => {
    setMode(isLogin ? 'register' : 'login');
    setError(null);
  };

  return (
    <div
      className="modal-overlay"
      onClick={onClose}
      role="presentation"
    >
      <div
        className="modal"
        onClick={(event) => event.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-label={isLogin ? 'Вход' : 'Регистрация'}
      >
        <button
          type="button"
          className="modal__close"
          onClick={onClose}
          aria-label="Закрыть"
        >
          ×
        </button>

        <h2 className="modal__title">{isLogin ? 'Вход' : 'Регистрация'}</h2>

        <form className="auth-form" onSubmit={handleSubmit}>
          <label className="auth-form__field">
            <span className="auth-form__label">Имя пользователя</span>
            <input
              type="text"
              className="auth-form__input"
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              autoComplete="username"
              autoFocus
            />
          </label>

          <label className="auth-form__field">
            <span className="auth-form__label">Пароль</span>
            <input
              type="password"
              className="auth-form__input"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              autoComplete={isLogin ? 'current-password' : 'new-password'}
            />
          </label>

          {error && <p className="error-text">{error}</p>}

          <button
            type="submit"
            className="primary-button auth-form__submit"
            disabled={submitting}
          >
            {submitting
              ? 'Подождите...'
              : isLogin
              ? 'Войти'
              : 'Зарегистрироваться'}
          </button>
        </form>

        <p className="auth-form__switch">
          {isLogin ? 'Нет аккаунта?' : 'Уже есть аккаунт?'}{' '}
          <button type="button" className="link-button" onClick={toggleMode}>
            {isLogin ? 'Зарегистрироваться' : 'Войти'}
          </button>
        </p>
      </div>
    </div>
  );
}

export default AuthModal;

import React from 'react';
import { useAuth } from '../context/AuthContext';

/**
 * Обёртка, показывающая содержимое только авторизованным пользователям.
 * Неавторизованным выводит приглашение войти в систему.
 *
 * @param {{ onRequestLogin: () => void, message?: string, children: React.ReactNode }} props
 */
function AuthRequired({ onRequestLogin, message, children }) {
  const { isAuthenticated } = useAuth();

  if (isAuthenticated) {
    return <>{children}</>;
  }

  return (
    <div className="empty-state">
      <div className="empty-state__icon" aria-hidden="true">
        🔒
      </div>
      <p>{message || 'Войдите в систему, чтобы продолжить.'}</p>
      <button
        type="button"
        className="primary-button"
        onClick={onRequestLogin}
      >
        Войти
      </button>
    </div>
  );
}

export default AuthRequired;

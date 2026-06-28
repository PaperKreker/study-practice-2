import React, {
  createContext,
  useContext,
  useState,
  useCallback,
} from 'react';
import { loginRequest, registerRequest } from '../services/auth';

const TOKEN_KEY = 'auth_token';
const USER_KEY = 'auth_user';

const AuthContext = createContext(null);

/** Читает сохранённого пользователя из localStorage. */
function readStoredUser() {
  try {
    const raw = localStorage.getItem(USER_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch (e) {
    return null;
  }
}

/**
 * Провайдер аутентификации. Хранит токен доступа и данные пользователя,
 * сохраняет их в localStorage для восстановления сессии после перезагрузки.
 */
export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_KEY));
  const [user, setUser] = useState(readStoredUser);

  /** Сохраняет результат успешной аутентификации в состояние и localStorage. */
  const persistAuth = useCallback((tokenResponse) => {
    const { access_token: accessToken, user: userData } = tokenResponse;
    setToken(accessToken);
    setUser(userData);
    try {
      localStorage.setItem(TOKEN_KEY, accessToken);
      localStorage.setItem(USER_KEY, JSON.stringify(userData));
    } catch (e) {
      // приватный режим / переполнение — игнорируем
    }
    return userData;
  }, []);

  const login = useCallback(
    async (username, password) => {
      const data = await loginRequest(username, password);
      return persistAuth(data);
    },
    [persistAuth]
  );

  const register = useCallback(
    async (username, password) => {
      const data = await registerRequest(username, password);
      return persistAuth(data);
    },
    [persistAuth]
  );

  const logout = useCallback(() => {
    setToken(null);
    setUser(null);
    try {
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem(USER_KEY);
    } catch (e) {
      // игнорируем
    }
  }, []);

  const value = {
    user,
    token,
    isAuthenticated: Boolean(token),
    login,
    register,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

/** Возвращает true, если пользователь авторизован. */
export function isAuthenticated() {
  return localStorage.getItem(USER_KEY) !== null;
}

/** Хук доступа к контексту аутентификации. */
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth должен использоваться внутри AuthProvider');
  }
  return context;
}

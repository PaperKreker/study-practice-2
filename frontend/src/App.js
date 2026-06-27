import React, { useState } from 'react';
import './App.css';
import UploadPage from './pages/UploadPage';
import SearchPage from './pages/SearchPage';

// Вкладки приложения. Используем простое переключение состоянием, чтобы не
// тянуть внешний роутер ради двух экранов.
const TABS = {
  SEARCH: 'search',
  UPLOAD: 'upload',
};

/**
 * Корневой компонент приложения «Интеллектуальная поисковая система по базе
 * знаний университета». Реализует навигацию между поиском и загрузкой.
 */
function App() {
  const [activeTab, setActiveTab] = useState(TABS.UPLOAD);

  return (
    <div className="app">
      <header className="app-header">
        <div className="app-header__inner">
          <div className="app-brand">
            <span className="app-brand__logo" aria-hidden="true">
              🎓
            </span>
            <div>
              <div className="app-brand__title">База знаний</div>
              <div className="app-brand__subtitle">
                Интеллектуальный поиск по документам
              </div>
            </div>
          </div>

          <nav className="app-nav" aria-label="Основная навигация">
            <button
                type="button"
                className={`app-nav__tab${
                    activeTab === TABS.UPLOAD ? ' app-nav__tab--active' : ''
                }`}
                onClick={() => setActiveTab(TABS.UPLOAD)}
            >
              Загрузка
            </button>
            <button
              type="button"
              className={`app-nav__tab${
                activeTab === TABS.SEARCH ? ' app-nav__tab--active' : ''
              }`}
              onClick={() => setActiveTab(TABS.SEARCH)}
            >
              Поиск
            </button>
          </nav>
        </div>
      </header>

      <main className="app-main">
        {activeTab === TABS.SEARCH ? <SearchPage /> : <UploadPage />}
      </main>
    </div>
  );
}

export default App;

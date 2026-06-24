import React, { useState } from 'react';
import './App.css';
import UploadPage from './pages/UploadPage';

/**
 * Корневой компонент приложения «Интеллектуальная поисковая система по базе
 * знаний университета». Реализует навигацию между поиском и загрузкой.
 */
function App() {
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
        </div>
      </header>

      <main className="app-main">
        <UploadPage />
      </main>
    </div>
  );
}

export default App;

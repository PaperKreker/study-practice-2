# Университетская база знаний

Веб-приложение для загрузки PDF/DOCX-документов и полнотекстового поиска по
ним. Backend построен на FastAPI, PostgreSQL, Elasticsearch и Redis, frontend
\- на React. Prometheus собирает HTTP-метрики, Grafana используется для их
просмотра.

## Быстрый запуск

Понадобятся Git, Docker Desktop с работающим WSL2 и не менее 4 ГБ свободной
оперативной памяти.

Создайте локальные Docker secrets из примеров:

```powershell
New-Item -ItemType Directory -Force secrets
Copy-Item secrets_example\POSTGRES_USER secrets\POSTGRES_USER
Copy-Item secrets_example\POSTGRES_PASSWORD secrets\POSTGRES_PASSWORD
```

Соберите и запустите сервисы:

```powershell
docker compose up --build
```

После запуска доступны:

- приложение: `http://localhost:3000`;
- Swagger UI: `http://localhost:8000/docs`;
- проверка backend: `http://localhost:8000/health`;
- метрики Prometheus: `http://localhost:8000/metrics/`;
- Prometheus: `http://localhost:9090`;
- Grafana: `http://localhost:3001`.

Для остановки используйте:

```powershell
docker compose down
```

## Работа с системой

### Регистрация и вход

1. Откройте приложение и нажмите **Войти**.
2. Для нового аккаунта выберите **Зарегистрироваться**.
3. Укажите имя пользователя и пароль.
4. После успешного входа имя пользователя появится в правом верхнем углу.

### Загрузка документов

1. Откройте вкладку **Загрузка**.
2. Перетащите файлы в область загрузки или нажмите на неё для выбора.
3. Разрешены PDF и DOCX размером не более 20 МБ. Можно выбрать несколько
   файлов.
4. Следите за состояниями **Загрузка**, **Индексация**, **Готово** и
   **Ошибка**.
5. Загруженные документы отображаются в таблице. Собственный документ можно
   удалить кнопкой **Удалить**.

### Поиск

1. Откройте вкладку **Поиск**.
2. Введите запрос и нажмите **Найти** или клавишу Enter.
3. Карточка результата содержит имя документа, страницу, найденный фрагмент и
   оценку релевантности. Совпавшие термины подсвечиваются.
4. Для перехода между страницами используйте кнопки пагинации.
5. Предыдущие запросы доступны в истории под поисковым полем.

## Тестовые лекции

`init.sh` регистрирует тестового пользователя, скачивает десять открытых
PDF-лекций и загружает их через API. Скрипту требуются Bash, `curl`, `jq`,
доступ в интернет и запущенный backend:

```bash
bash init.sh
```

## Проверка проекта

Backend-тесты с обязательным покрытием не ниже 50%:

```powershell
cd backend
python -m pip install -r requirements.txt
python -m pytest
```

Frontend-тесты и production-сборка:

```powershell
cd frontend
npm ci
npm test -- --watchAll=false --coverage
npm run build
```

Playwright проверяет браузерный путь входа, загрузки и поиска с
контролируемыми API-ответами. Для локального запуска требуется Google Chrome:

```powershell
cd frontend
npm run test:e2e
```

Для настоящего E2E через запущенный Docker Compose включите full-stack
сценарий. Он регистрирует уникального пользователя, загружает тестовый PDF и
проверяет результат поиска через Elasticsearch:

```powershell
cd frontend
$env:QA_FULL_STACK = "1"
npm run test:e2e -- full-stack.spec.js
```

## Нагрузочный тест

Сценарий Locust рассчитан на 50 одновременных пользователей в течение одной
минуты. Перед запуском создайте тестового пользователя или передайте готовый
токен:

```powershell
python -m pip install -r qa\requirements.txt
$env:QA_ACCESS_TOKEN = "your-token"
python -m locust --config qa\load\locust.conf
```

Результаты сохраняются в `qa/load/results.html` и CSV-файлах рядом с ним.
Краткий результат контрольного прогона на 50 пользователях сохранён в
`qa/load/report.csv`.

## Оценка Precision@3

Для воспроизводимой проверки установите QA-зависимости, создайте эталонный
корпус из десяти документов и сразу выполните оценку:

```powershell
python -m pip install -r qa\requirements.txt
python qa\precision\evaluate_precision_at_3.py --prepare-dataset
```

Скрипт выполняет десять эталонных запросов, проверяет наличие ожидаемого
документа в первых трёх результатах и сохраняет таблицу в
`qa/precision/report.csv`. Повторный запуск не загружает уже существующие
документы. При необходимости можно передать готовый токен через
`QA_ACCESS_TOKEN` или изменить `QA_USERNAME` и `QA_PASSWORD`.

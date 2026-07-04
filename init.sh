#!/bin/bash

# ============================================================
# Скрипт инициализации: скачивание и загрузка тестовых PDF-лекций
# ============================================================

set -e  # Прерывать выполнение при ошибке

# --- Конфигурация ---
BACKEND_URL="http://localhost:8000"
BACKEND_API_URL="http://localhost:8000/api/v1"
LOGIN_URL="$BACKEND_API_URL/users/login"
REGISTER_URL="$BACKEND_API_URL/users/register"
UPLOAD_URL="$BACKEND_API_URL/documents/upload"



# Учётные данные (если пользователь не существует, он будет создан)
USERNAME="admin"
PASSWORD="your_password"

# Папка для временного хранения PDF
TEMP_DIR="./temp_pdfs"
mkdir -p "$TEMP_DIR"

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# --- Проверка зависимостей ---
check_dependencies() {
    local deps=("curl" "jq")
    local missing=()
    for cmd in "${deps[@]}"; do
        if ! command -v "$cmd" &> /dev/null; then
            missing+=("$cmd")
        fi
    done
    if [ ${#missing[@]} -ne 0 ]; then
        echo -e "${RED}❌ Отсутствуют необходимые утилиты: ${missing[*]}${NC}"
        echo "Установите их:"
        echo "  - Ubuntu/Debian: sudo apt install curl jq"
        echo "  - MacOS: brew install curl jq"
        exit 1
    fi
}

# --- Проверка доступности бэкенда ---
check_backend() {
    echo -e "${BLUE}🔍 Проверяю доступность бэкенда...${NC}"
    local max_attempts=10
    local attempt=1
    while [ $attempt -le $max_attempts ]; do
        if curl -s -f "$BACKEND_URL/health" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Бэкенд доступен${NC}"
            return 0
        fi
        echo -e "${YELLOW}⏳ Ожидаю бэкенд (попытка $attempt/$max_attempts)...${NC}"
        sleep 2
        ((attempt++))
    done
    echo -e "${RED}❌ Бэкенд недоступен. Запустите сервис.${NC}"
    exit 1
}

# --- Регистрация пользователя (если не существует) ---
register_user() {
    echo -e "${BLUE}📝 Пытаюсь зарегистрировать пользователя $USERNAME...${NC}"
    local response
    response=$(curl -s -w "\n%{http_code}" -X POST "$REGISTER_URL" \
        -H "Content-Type: application/json" \
        -d "{\"username\":\"$USERNAME\", \"password\":\"$PASSWORD\"}")

    local http_code
    http_code=$(echo "$response" | tail -n1)
    local body
    body=$(echo "$response" | sed '$d')

    if [ "$http_code" -eq 201 ]; then
        echo -e "${GREEN}✅ Пользователь $USERNAME зарегистрирован${NC}"
        return 0
    elif [ "$http_code" -eq 409 ]; then
        echo -e "${YELLOW}⚠️ Пользователь $USERNAME уже существует, продолжаю...${NC}"
        return 0
    else
        echo -e "${RED}❌ Ошибка регистрации (код $http_code): $body${NC}"
        return 1
    fi
}

# --- Логин и получение токена ---
login() {
    echo >&2 -e "${BLUE}🔑 Получаю токен для пользователя $USERNAME...${NC}"
    local response
    response=$(curl -s -X POST "$LOGIN_URL" \
        -H "Content-Type: application/json" \
        -d "{\"username\":\"$USERNAME\", \"password\":\"$PASSWORD\"}")

    local token
    token=$(echo "$response" | jq -r '.access_token // empty')
    if [ -z "$token" ]; then
        echo >&2 -e "${RED}❌ Ошибка логина. Ответ: $response${NC}"
        exit 1
    fi
    echo >&2 -e "${GREEN}✅ Токен получен${NC}"
    echo "$token"
}

# --- Загрузка одного файла ---
upload_file() {
    local file_path="$1"
    local filename=$(basename "$file_path")
    echo -e "${BLUE}⬆️ Загружаю $filename...${NC}"

    local response
    response=$(curl -s -w "\n%{http_code}" -X POST "$UPLOAD_URL" \
        -H "accept: application/json" \
        -H "Authorization: Bearer $TOKEN" \
        -F "file=@$file_path;type=application/pdf")

    local http_code
    http_code=$(echo "$response" | tail -n1)
    local body
    body=$(echo "$response" | sed '$d')

    echo -e "${YELLOW}Код ответа: $http_code${NC}"
    echo -e "${YELLOW}Тело ответа: $body${NC}"

    if [ "$http_code" -eq 201 ]; then
        echo -e "${GREEN}✅ $filename загружен успешно${NC}"
        return 0
    else
        echo -e "${RED}❌ Ошибка загрузки $filename (код $http_code)${NC}"
        return 1
    fi
}

# --- Скачивание файла ---
download_file() {
    local url="$1"
    local output_path="$2"
    echo -e "${BLUE}📥 Скачиваю $(basename "$output_path")...${NC}"
    if curl -s -o "$output_path" -L --fail "$url"; then
        echo -e "${GREEN}✅ Скачано: $(basename "$output_path")${NC}"
        return 0
    else
        echo -e "${RED}❌ Не удалось скачать: $url${NC}"
        return 1
    fi
}

# ============================================================
# ОСНОВНОЙ ПРОЦЕСС
# ============================================================

main() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}  Инициализация: загрузка тестовых лекций${NC}"
    echo -e "${BLUE}========================================${NC}"

    # 1. Проверка зависимостей
    check_dependencies

    # 2. Проверка бэкенда
    check_backend

    # 3. Регистрация (если не существует)
    if ! register_user; then
        echo -e "${YELLOW}⚠️ Регистрация не удалась, но попробую войти...${NC}"
    fi

    # 4. Логин и получение токена
    TOKEN=$(login)

    # 5. Список URL для скачивания
    declare -a PDF_URLS=(
        "http://phys.spbu.ru/content/File/Library/studentlectures/Krylov/Krylov_2021_NanoOptics-01.pdf"
        "http://phys.spbu.ru/content/File/Library/studentlectures/Krylov/Krylov_2021_NanoOptics-02.pdf"
        "http://phys.spbu.ru/content/File/Library/studentlectures/Krylov/Krylov_2021_NanoOptics-03.pdf"
        "http://www.phys.nsu.ru/ok01/07g6m18c/lectures_mol_phys_1_2023.pdf"
        "http://www.phys.nsu.ru/ok01/07g6m18c/lectures_mol_phys_2_2023.pdf"
        "http://www.ioffe.ru/SEC/distant/general/pz1-4.pdf"
        "http://www.ioffe.ru/SEC/distant/general/pz5-8.pdf"
        "http://www.ioffe.ru/SEC/distant/general/pz9-12.pdf"
        "http://www.ioffe.ru/SEC/distant/general/pz13-16.pdf"
        "http://icho2013.chem.msu.ru/rus/teaching/fizfak/3year/B-lecture-03.pdf"
    )

    # 6. Скачивание и загрузка
    local success_count=0
    local fail_count=0
    local count=1

    for url in "${PDF_URLS[@]}"; do
        echo -e "\n${YELLOW}--- [$count/${#PDF_URLS[@]}] Обработка ---${NC}"

        # Генерация имени файла
        local filename
        filename=$(basename "$url" | sed 's/\?.*//' | sed 's/\.pdf$//')
        if [ -z "$filename" ] || [ "$filename" = "$(basename "$url")" ]; then
            filename="lecture_$count"
        fi
        filename="${filename}.pdf"
        local filepath="$TEMP_DIR/$filename"

        # Скачивание
        if download_file "$url" "$filepath"; then
            # Загрузка
            if upload_file "$filepath"; then
                success_count=$((success_count + 1))
            else
                fail_count=$((fail_count + 1))
            fi
            # Очистка временного файла
            rm -f "$filepath"
        else
            fail_count=$((fail_count + 1))
        fi
        count=$((count + 1))
    done

    # 7. Итог
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${GREEN}✅ Успешно загружено: $success_count${NC}"
    if [ $fail_count -gt 0 ]; then
        echo -e "${YELLOW}⚠️  Ошибок: $fail_count${NC}"
    fi
    echo -e "${BLUE}========================================${NC}"

    # Удаляем временную папку, если она пуста
    rmdir "$TEMP_DIR" 2>/dev/null || true
}

# --- Запуск ---
main "$@"
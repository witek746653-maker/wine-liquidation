# wine-liquidation

Простое веб‑приложение для учета остатков винных позиций (React прямо в HTML) с синхронизацией в **Supabase**.

## Как запустить локально

Проще всего открыть `index.html` двойным кликом.  
Но для корректной загрузки Excel по `fetch()` лучше запускать через локальный сервер.

В PowerShell из папки проекта:

```powershell
cd d:\GitHub\wine-liquidation
python -m http.server 5173
```

Потом откройте в браузере: `http://localhost:5173`

## Подключение к Supabase (хранение данных)

Термины:
- **Supabase**: “облачная база данных”, куда можно сохранять ваш список вин, чтобы он был одинаковый на разных компьютерах.
- **RLS (Row Level Security)**: “правила доступа”, кто может читать/менять строки таблицы. Это главный замок безопасности.
- **anon key**: “публичный ключ” для браузера (не секрет). Но **service_role key** — это секрет, его НЕЛЬЗЯ класть в GitHub.
- **Auth**: “вход по email/паролю” (как “замок на дверь”).

### Шаг 1. Создайте проект и таблицу

1) Создайте проект в Supabase.  
2) Откройте Supabase Dashboard → **SQL Editor** → **New query**.  
3) Вставьте и выполните SQL из файла:

`supabase/schema.sql`

### Шаг 2. Создайте пароль (обязательно, раз вы так хотите)

1) Supabase Dashboard → **Authentication** → **Providers** → включите **Email**.

2) Чтобы не мучиться с подтверждением почты, отключите подтверждение email:
   - Supabase Dashboard → **Authentication** → **Settings**
   - Найдите настройку про подтверждение email (обычно “Confirm email”) и выключите.
   - Простыми словами: это убирает шаг “перейдите по ссылке из письма”.

3) Создайте пользователя (это и будет ваш “логин + пароль”):
   - Supabase Dashboard → **Authentication** → **Users**
   - Нажмите **Add user**
   - Введите **Email** и **Password**
     - Email можно любой, но удобно сделать “общий”, например: `witek746653@gmail.com`
     - Password — это и будет **один общий пароль для всех посетителей**
   - Нажмите **Create user**

Теперь ваш пароль “живёт” в Supabase, а НЕ в GitHub.

### Шаг 3. Вставьте ключи в код

Откройте файл:

`wine-liquidation-list.html`

Найдите вверху:

- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`

и вставьте значения из Supabase Dashboard → **Settings → API**.

После этого в боковом меню появится блок **Синхронизация**.
Введите **только пароль** (email уже зашит в коде как общий) и нажмите “Войти”.

## Важно про безопасность

- Никогда не добавляйте в репозиторий файлы `.env` с секретами.
- Не используйте **service_role** ключ в браузере (это как “мастер‑ключ от всего”).

## GitHub: как создать репозиторий и залить проект

Термины:
- **git**: “история изменений” вашего проекта.
- **репозиторий**: “папка на GitHub”, где хранится проект.

### Вариант A (проще): через сайт GitHub
1) Откройте GitHub → нажмите **New repository**
2) Название: `wine-liquidation`
3) Выберите **Public**
4) Нажмите **Create repository**

Потом в PowerShell:

```powershell
cd d:\GitHub\wine-liquidation
git remote add origin https://github.com/<ВАШ_ЛОГИН>/wine-liquidation.git
git push -u origin master
```

### Вариант B: через GitHub CLI (через терминал)
1) Войдите в GitHub (откроется браузер):

```powershell
cd d:\GitHub\wine-liquidation
& "C:\Program Files\GitHub CLI\gh.exe" auth login
```

2) Создайте репозиторий и сразу отправьте код:

```powershell
cd d:\GitHub\wine-liquidation
& "C:\Program Files\GitHub CLI\gh.exe" repo create wine-liquidation --public --source . --remote origin --push
```

## Установка “как приложение” (иконка на телефоне/ПК)

Термины:
- **PWA**: “сайт, который можно установить как приложение”.
- **Service worker**: “скрипт‑официант”, который кеширует файлы и помогает установке.

### Как установить на Android (Chrome)
1) Откройте сайт (по ссылке, не `localhost`)
2) Меню браузера (⋮) → **Установить приложение** / **Add to Home screen**
3) Подтвердите

### Как установить на Windows (Chrome/Edge)
1) Откройте сайт
2) В адресной строке появится значок установки (обычно “+”/“Install”)
3) Нажмите **Install**

Важно: установка работает, когда сайт открыт по нормальному адресу (`https://...`), например GitHub Pages.


# LMS — бэкенд платформы онлайн-обучения

SPA-бэкенд на Django REST framework: сервер отдаёт клиенту JSON.
Пользователи могут размещать курсы и уроки.

## Стек

Python 3.13, Django 5.2, Django REST framework, PostgreSQL, Pillow.

## Структура

```
PythonProject_LMS/
├── config/          # настройки (DRF подключён в INSTALLED_APPS и REST_FRAMEWORK), корневые URL
├── users/           # пользователь: вход по email, телефон, город, аватарка; профиль через API
├── materials/       # курсы и уроки: модели, сериализаторы, CRUD
├── docs/
│   └── LMS.postman_collection.json   # готовая коллекция запросов для Postman
├── requirements.txt
└── .env.example
```

## Модели

- **User** (`users`) — наследуется от `AbstractUser` (а он от `AbstractBaseUser`):
  все поля обычного пользователя, вход по email (`USERNAME_FIELD = "email"`),
  плюс телефон, город и аватарка.
- **Course** (`materials`) — название, превью (картинка), описание.
- **Lesson** (`materials`) — название, описание, превью (картинка), ссылка на видео
  и курс (`ForeignKey`): в одном курсе много уроков, при удалении курса удаляются
  и его уроки.

## Установка и запуск

1. Установите зависимости: `pip install -r requirements.txt`
2. Скопируйте `.env.example` в `.env` и заполните `SECRET_KEY` и пароль PostgreSQL.
3. Создайте базу и примените миграции:

   ```bash
   psql -U postgres -c "CREATE DATABASE lms_db;"
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py runserver
   ```

## Эндпоинты

Авторизация на этом этапе не требуется (так в задании).

### Курсы — ViewSet (`CourseViewSet`)

| Метод | Адрес | Действие |
|---|---|---|
| GET | `/courses/` | список курсов |
| POST | `/courses/` | создать курс |
| GET | `/courses/<id>/` | получить курс |
| PUT / PATCH | `/courses/<id>/` | изменить курс |
| DELETE | `/courses/<id>/` | удалить курс |

### Уроки — Generic-классы

| Метод | Адрес | Класс |
|---|---|---|
| GET | `/lessons/` | `LessonListAPIView` |
| POST | `/lessons/create/` | `LessonCreateAPIView` |
| GET | `/lessons/<id>/` | `LessonRetrieveAPIView` |
| PUT / PATCH | `/lessons/<id>/update/` | `LessonUpdateAPIView` |
| DELETE | `/lessons/<id>/delete/` | `LessonDestroyAPIView` |

### Профиль пользователя (доп. задание) — Generic-классы

| Метод | Адрес | Действие |
|---|---|---|
| GET | `/users/` | список пользователей |
| GET | `/users/<id>/` | профиль пользователя |
| PUT / PATCH | `/users/<id>/` | редактирование профиля |

Пароль и права пользователя через этот эндпоинт не меняются.

## Проверка в Postman

Импортируйте `docs/LMS.postman_collection.json` (File → Import). В коллекции
16 запросов по всем эндпоинтам; адрес сервера задаётся переменной `base_url`
(по умолчанию `http://127.0.0.1:8000`). Чтобы загрузить превью, откройте запрос
«Создать курс с превью (form-data)» и выберите файл в поле `preview`.

## Тесты

```bash
python manage.py test
```

12 тестов: модель пользователя, CRUD курсов и уроков (включая загрузку превью
и ошибки валидации), редактирование профиля.

## Соответствие критериям

| Критерий | Где реализовано |
|---|---|
| DRF подключён | `config/settings.py` → `INSTALLED_APPS`, `REST_FRAMEWORK` |
| Пользователь: `AbstractBaseUser` (через `AbstractUser`), `USERNAME_FIELD = "email"`, телефон, город, аватарка | `users/models.py` |
| Модель курса | `materials/models.py` → `Course` |
| Модель урока со связью с курсом | `materials/models.py` → `Lesson.course` |
| CRUD курса на ViewSet | `materials/views.py` → `CourseViewSet`, роутер в `materials/urls.py` |
| CRUD урока на Generic-классах | `materials/views.py` → `Lesson*APIView` |
| Доп.: редактирование профиля | `users/views.py` → `UserProfileAPIView` |

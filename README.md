# LMS — бэкенд платформы онлайн-обучения

SPA-бэкенд на Django REST framework: сервер отдаёт клиенту JSON.
Пользователи могут размещать курсы и уроки.

## Стек

Python 3.13, Django 5.2, Django REST framework, django-filter, PostgreSQL, Pillow.

## Структура

```
PythonProject_LMS/
├── config/          # настройки (DRF подключён в INSTALLED_APPS и REST_FRAMEWORK), корневые URL
├── users/           # пользователь: вход по email, телефон, город, аватарка; платежи; профиль через API
│   └── fixtures/    # users.json, payments.json
├── materials/       # курсы и уроки: модели, сериализаторы, CRUD
│   └── fixtures/    # materials.json — курсы и уроки
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
- **Payment** (`users`) — платёж: пользователь, дата оплаты, оплаченный курс
  или отдельно оплаченный урок (ссылки на модели), сумма, способ оплаты
  (наличные или перевод на счёт). В одном платеже — либо курс, либо урок.

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

4. Заполните базу тестовыми данными из фикстур — 3 пользователя, 2 курса,
   5 уроков и 8 платежей:

   ```bash
   python manage.py loaddata users materials payments
   ```

   У тестовых данных номера начинаются со 101, поэтому они не затирают то, что
   вы создали сами. Пароль тестовых пользователей — `Str0ng-Pass-2026`.

## Эндпоинты

Авторизация на этом этапе не требуется (так в задании).

### Курсы — ViewSet (`CourseViewSet`)

| Метод | Адрес | Действие |
|---|---|---|
| GET | `/courses/` | список курсов |
| POST | `/courses/` | создать курс |
| GET | `/courses/<id>/` | получить курс с количеством уроков (`lessons_count`) и списком уроков (`lessons`) |
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
| GET | `/users/<id>/` | профиль пользователя с историей платежей (`payments`) |
| PUT / PATCH | `/users/<id>/` | редактирование профиля |

Пароль и права пользователя через этот эндпоинт не меняются.

### Платежи — список с фильтрацией (`PaymentListAPIView`)

`GET /users/payments/` — параметры можно сочетать:

| Параметр | Пример | Что делает |
|---|---|---|
| `ordering` | `?ordering=payment_date` / `?ordering=-payment_date` | сортировка по дате оплаты по возрастанию / убыванию (по умолчанию — сначала новые) |
| `paid_course` | `?paid_course=101` | платежи за курс |
| `paid_lesson` | `?paid_lesson=104` | платежи за урок |
| `payment_method` | `?payment_method=cash` / `transfer` | наличные / перевод на счёт |

## Проверка в Postman

Импортируйте `docs/LMS.postman_collection.json` (File → Import). В коллекции
26 запросов по всем эндпоинтам, включая фильтры платежей; адрес сервера задаётся переменной `base_url`
(по умолчанию `http://127.0.0.1:8000`). Чтобы загрузить превью, откройте запрос
«Создать курс с превью (form-data)» и выберите файл в поле `preview`.

## Тесты

```bash
python manage.py test
```

23 теста: модель пользователя, CRUD курсов и уроков (включая загрузку превью
и ошибки валидации), количество и список уроков курса, редактирование профиля,
модель платежа, загрузка фикстур, сортировка и все фильтры платежей, история
платежей в профиле.

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
| Количество уроков курса — `SerializerMethodField` | `materials/serializers.py` → `CourseSerializer.get_lessons_count` |
| Модель платежей | `users/models.py` → `Payment` |
| Данные платежей через фикстуры | `users/fixtures/payments.json` (+ `users.json`, `materials/fixtures/materials.json`) |
| Уроки курса через сериализатор связанной модели | `CourseSerializer.lessons = LessonSerializer(many=True)` |
| Сортировка платежей по дате, фильтры по курсу, уроку, способу оплаты | `users/views.py` → `PaymentListAPIView` (`DjangoFilterBackend`, `OrderingFilter`) |
| Доп.: история платежей в профиле | `users/serializers.py` → `PaymentHistorySerializer`, `UserProfileSerializer` |

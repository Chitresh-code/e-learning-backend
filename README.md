# 📚 Personalized E-Learning Platform

This project is a personalized e-learning backend powered by Django REST Framework and a LangGraph-integrated multi-agent system. It provides a robust API for managing student onboarding, subject preferences, quizzes, goals, and resources with full OpenAPI documentation.

---

## 🚀 Tech Stack

- **Backend**: Django 5.2
- **API Layer**: Django REST Framework
- **Authentication**: JWT (SimpleJWT) + Social Auth (Google)
- **Docs**: OpenAPI (drf-yasg) + Swagger UI via CDN
- **Database**: PostgreSQL
- **Containerized**: Docker + Docker Compose

---

## 📁 Project Structure

```bash
backend/
├── student/                 # App for student-related models and APIs
│   ├── models.py            # All student, quiz, goal, resource models
│   ├── serializers.py       # DRF serializers for modular endpoints
│   ├── views.py             # Fully annotated views with Swagger
│   ├── urls.py              # /student/ endpoints (info, subject, quiz...)
├── config/                  # Django project settings
│   ├── settings.py          # Environment + App config
│   ├── urls.py              # Includes Swagger, ReDoc, Auth, and student/
```

---

## 🔐 Auth Endpoints

| Method | Endpoint          | Description                |
|--------|-------------------|----------------------------|
| POST   | `/student/login/` | Email/password login       |
| POST   | `/student/register/` | Register new student    |
| POST   | `/api/token/refresh/` | Refresh JWT tokens    |

---

## 📘 Main API Endpoints

| Resource        | Endpoint Prefix       | Description                                |
|----------------|------------------------|--------------------------------------------|
| Student Info   | `/student/info/`       | Onboarding, update, or delete user profile |
| Subject Prefs  | `/student/subject/`    | CRUD preferences per subject               |
| Quiz System    | `/student/quizzes/`    | Quizzes tied to student/subject            |
| Learning Goals | `/student/goals/`      | Create, update, or delete personal goals   |
| Resources      | `/student/resources/`  | View content for learning topics           |
| Resource Log   | `/student/resource-log/` | Track student engagement with resources |

---

## 📑 API Docs (OpenAPI)

| Tool        | URL                         |
|-------------|------------------------------|
| Swagger UI  | [http://localhost:8000/swagger/](http://localhost:8000/swagger/) |
| ReDoc       | [http://localhost:8000/redoc/](http://localhost:8000/redoc/)     |
| Schema JSON | [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json) |

> 🔧 Swagger UI is served directly via CDN (no template needed).

---

## 🐳 Docker Usage

```bash
# Build and start services
docker-compose up --build

# Access app
http://localhost:8000
```


---

## 👨‍💻 Author
**Chitresh Gyanani**  
📧 gychitresh1290@gmail.com

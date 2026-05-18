# Django Todo List AI Agent 2

A production-level Todo List application built with a modern frontend and scalable backend architecture.  
This project includes authentication, Todo CRUD operations, responsive UI, and clean project structure for AI-agent-based development workflows.

---

# Project Overview

The application allows users to:

- Register and login securely
- Create, update, delete, and manage todos
- View responsive and user-friendly UI
- Access protected APIs using JWT authentication
- Maintain personal todo lists securely

This project is designed with scalable architecture and clean coding standards for both frontend and backend development.

---

# Tech Stack

## Frontend
- HTML
- CSS
- Bootstrap 5
- JavaScript
- Django Templates

## Backend
- Next.js
- TypeScript
- REST APIs
- JWT Authentication

## Database
- PostgreSQL or MongoDB

## Authentication
- JWT Tokens
- bcrypt password hashing

---

# Features

## Authentication
- User Signup
- User Login
- JWT Token Authentication
- Protected Routes
- Password Hashing

## Todo Features
- Create Todo
- Update Todo
- Delete Todo
- Mark Todo Complete/Incomplete
- View All Todos
- Responsive Todo Dashboard

## Frontend Features
- Responsive Design
- Bootstrap UI
- Global Base Template
- Reusable Components
- Form Validation
- Alert Messages
- Mobile Friendly Layout

## Backend Features
- Production-Level Folder Structure
- REST API Architecture
- Validation & Error Handling
- Secure Authentication
- Modular Services
- Clean Code Standards

---

# Project Structure

```bash
django-to-do-list-ai-agent2/
│
├── frontend/
│   ├── templates/
│   ├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
├── backend/
│   ├── app/
│   ├── app/api/
│   ├── middleware/
│   ├── services/
│   ├── repositories/
│   ├── validations/
│   ├── utils/
│   ├── prisma/ or models/
│   └── types/
│
├── README.md
└── .env.example
```

---

# Frontend Setup

## 1. Navigate to Frontend

```bash
cd frontend
```

## 2. Create Virtual Environment

```bash
python -m venv env
```

## 3. Activate Environment

### Windows

```bash
env\Scripts\activate
```

### Linux / Mac

```bash
source env/bin/activate
```

## 4. Install Dependencies

```bash
pip install -r requirements.txt
```

## 5. Run Django Server

```bash
python manage.py runserver
```

Frontend will run on:

```bash
http://127.0.0.1:8000
```

---

# Backend Setup

## 1. Navigate to Backend

```bash
cd backend
```

## 2. Install Dependencies

```bash
npm install
```

or

```bash
pnpm install
```

## 3. Create Environment File

Create `.env` file:

```env
DATABASE_URL=
JWT_SECRET=
PORT=3000
```

---

# Run Backend Server

```bash
npm run dev
```

Backend will run on:

```bash
http://localhost:3000
```

---

# API Endpoints

# Authentication APIs

## Signup

```http
POST /api/auth/signup
```

## Login

```http
POST /api/auth/login
```

---

# Todo APIs

## Create Todo

```http
POST /api/todos
```

## Get Todos

```http
GET /api/todos
```

## Get Single Todo

```http
GET /api/todos/:id
```

## Update Todo

```http
PUT /api/todos/:id
```

## Delete Todo

```http
DELETE /api/todos/:id
```

---

# Environment Variables

Example `.env.example`

```env
DATABASE_URL=your_database_url
JWT_SECRET=your_secret_key
PORT=3000
```

---

# Authentication Flow

1. User registers using Signup API
2. Password gets hashed using bcrypt
3. User logs in with credentials
4. Backend generates JWT token
5. Frontend stores token
6. Protected APIs use Authorization header

Example:

```http
Authorization: Bearer your_jwt_token
```

---

# Recommended Backend Packages

```bash
npm install jsonwebtoken bcrypt zod
```

For Prisma:

```bash
npm install prisma @prisma/client
```

For MongoDB:

```bash
npm install mongoose
```

---

# Production-Level Practices

- Clean architecture
- Modular code structure
- Secure JWT authentication
- Password hashing
- Centralized error handling
- Environment-based configuration
- Reusable components
- API validation
- Responsive UI
- Scalable project structure

---

# Future Improvements

- Refresh Tokens
- Email Verification
- Forgot Password
- Dark Mode
- Todo Categories
- Due Dates
- Drag and Drop Todos
- Notifications
- Docker Support
- CI/CD Pipeline
- Unit Testing
- Swagger API Documentation

---

# Development Guidelines

- Follow clean coding standards
- Keep components reusable
- Use proper validation
- Avoid hardcoded secrets
- Write maintainable APIs
- Use environment variables
- Keep frontend responsive

---

# Author

Project: Django Todo List AI Agent 2

Built for scalable AI-agent-based development workflows.

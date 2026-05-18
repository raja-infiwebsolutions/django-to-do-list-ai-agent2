# Django Todo Backend

This repository contains a Django REST Framework backend for a Todo application.

Note: The original ticket requested a Next.js backend, but this repo is a Django project. The implementation in this repo follows Django & DRF conventions and provides:

- User signup/login using DRF Token Authentication
- Todo model with CRUD via a ViewSet pattern
- Zod/JWT/Prisma based Next.js implementation was requested originally; please confirm if we should switch stacks.

Development

- Install dependencies
- python manage.py migrate
- python manage.py runserver


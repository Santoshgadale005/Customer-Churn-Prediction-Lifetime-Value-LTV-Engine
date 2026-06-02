# Day 21: Authentication, Authorization & User Management

## Overview
Today, we moved the Customer Churn Prediction & LTV Engine from an open ML API toward a secure SaaS analytics platform. The main goal was to ensure that only authenticated users can access prediction APIs and that sensitive operational endpoints can be restricted by role.

## Accomplishments
- ✅ **User Table Created:** Added `app/database/user_model.py` with username, email, hashed password, and role fields.
- ✅ **Password Hashing Implemented:** Added secure password hashing and verification using `passlib` and bcrypt.
- ✅ **JWT Authentication Added:** Added access-token creation, token decoding, and current-user dependency.
- ✅ **Registration Endpoint Created:** Added `POST /register` for new user creation.
- ✅ **Login Endpoint Created:** Added `POST /login` to return bearer tokens.
- ✅ **Prediction APIs Protected:** Required authenticated users for prediction, explanation, batch prediction, and feature-importance routes.
- ✅ **RBAC Introduced:** Added admin-only access for `/api/v1/model-info` and `/admin/users`.
- ✅ **User Activity Logging Added:** Added `user_id` to prediction logs for auditability.
- ✅ **Dependencies Updated:** Added `python-jose`, `passlib`, `bcrypt`, and `python-multipart`.
- ✅ **Documentation Updated:** Added authentication, login, and bearer-token usage instructions to the README.
- ✅ **Tests Added:** Added auth tests for password hashing and JWT token payloads.

## Final Validation
- Register endpoint: `POST /register`
- Login endpoint: `POST /login`
- Protected prediction endpoint: `POST /api/v1/predict`
- Admin model endpoint: `GET /api/v1/model-info`
- Admin users endpoint: `GET /admin/users`

## Outcome
The project now supports user accounts, password hashing, JWT login, protected APIs, role-based access control, and user-linked prediction logs. This moves the platform closer to a real enterprise SaaS analytics system.

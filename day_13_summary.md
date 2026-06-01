# Day 13: FastAPI Authentication APIs

## Overview
Today, we secured our FastAPI endpoints by implementing user authentication using JWT (JSON Web Tokens) and bcrypt password hashing.

## Accomplishments
- ✅ **Bcrypt Hashing:** Secured user passwords using standard hashing (`passlib` and `bcrypt`).
- ✅ **Token-Based Authentication:** Configured stateless authentication with JWT (`python-jose`).
- ✅ **Endpoints Implemented:**
  - `POST /register`: Registers a new user with email and hashed password.
  - `POST /login`: Validates password and issues JWT token.
- ✅ **State Isolation:** Decoupled security logic from routing inside `app/auth.py`.

## Next Steps
Next, we will link our frontend Streamlit application and implement dashboards to visualize predictions and retain VIP customers.

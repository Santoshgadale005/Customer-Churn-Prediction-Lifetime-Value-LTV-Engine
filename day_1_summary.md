# Day 1 Documentation: Project Initialization & Environment

## 1. Project Overview
**Project Name:** Customer Churn & LTV Engine  
**Objective:** Build an end-to-end predictive analytics platform for telecom churn and customer lifetime value.  
**Mentor:** Senior Data/ML Engineer

---

## 2. Environment Setup
We established a production-ready Python environment to ensure reproducibility and stability.

### Virtual Environment (VENV)
- **What:** An isolated directory for Python libraries.
- **Why:** Prevents library version conflicts between projects.
- **Commands used:**
  - `python3 -m venv venv`
  - `source venv/bin/activate` (Mac/Linux) or `.\venv\Scripts\activate` (Windows)

### Dependency Management
We used `requirements.txt` to track our tech stack:
- **Pandas/NumPy**: Data manipulation.
- **SQLAlchemy/Psycopg2**: PostgreSQL interaction.
- **Scikit-Learn/XGBoost**: Machine Learning models.
- **SHAP**: Model explainability.
- **FastAPI/Uvicorn**: Backend API development.

---

## 3. Project Architecture
We adopted a modular structure to support scalability.

```text
customer-churn-ltv/
├── data/              # Raw and processed datasets (Git ignored)
├── notebooks/         # Jupyter notebooks for EDA and prototyping
├── app/               # Core application package
│   ├── api/           # FastAPI endpoints and logic
│   ├── models/        # ML model architectures and training scripts
│   ├── services/      # Business logic and processing
│   ├── database/      # SQL connection and schema logic
│   └── utils/         # Helper functions (logging, formatting)
├── dashboards/        # Superset/Metabase configurations
├── docker/            # Dockerfile and Compose setup
├── requirements.txt   # Project dependencies
└── README.md          # Project documentation
```

---

## 4. Git Workflow
We implemented version control using Git and GitHub.

1. **Initialization**: `git init`
2. **Ignoring Files**: Created `.gitignore` to exclude `venv/` and `data/` from version control.
3. **Staging**: `git add .` (Gathering changes).
4. **Committing**: `git commit -m "..."` (Saving locally).
5. **Pushing**: `git push -u origin main` (Uploading to GitHub).

---

## 5. Industry Best Practices Implemented
- **Modularization**: Splitting code by responsibility (API vs Models vs Database).
- **Security**: Ensuring local environment and raw data are not leaked to public GitHub.
- **Documentation**: Maintaining a professional README.md for the team.
- **Reproducibility**: Using pinned versions in `requirements.txt`.

---

## 6. Common Day 1 Pitfalls Avoided
- Installing libraries globally (Avoided by using VENV).
- Committing large data files (Avoided by using `.gitignore`).
- Unstructured code (Avoided by pre-defining folder hierarchy).

---

**End of Day 1 Documentation.**

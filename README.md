# 🎧 Client Query Management System

A support-desk app where clients raise queries and support staff track and close them, built with **Streamlit** and **PostgreSQL**.

![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white) ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?logo=postgresql&logoColor=white) ![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)

## ✨ Features

- **Login and registration** with SHA-256 password hashing
- **Role-based access** for clients and support staff
- **Raise a query** with email, mobile number, heading and description
- **Track and close queries**, with created and closed timestamps
- **All-queries view** for the support team

## 📁 Project structure

| File | Purpose |
|---|---|
| `query_management.ipynb` | Creates the database, tables and sample data |
| `query_app.py` | Streamlit app |

## ⚙️ Run it locally

```bash
git clone https://github.com/Arunmozhi1997/client-query-management.git
cd client-query-management
pip install -r requirements.txt

$env:DB_PASS="YOUR_POSTGRES_PASSWORD"
# Run query_management.ipynb once to create the tables
streamlit run query_app.py
```

## 👤 Author

**Arunmozhi M** · [Portfolio](https://arunmozhi1997.github.io) · [LinkedIn](https://linkedin.com/in/arunmozhi-m-65a29037b)

# PolyBase - (License "All Rights Reserved")

This project was carried out as part of a professional collaboration with **Poly-Tech Engineering SA**.

---

## 📌 Project Description

PolyBase is a secure internal platform designed to optimize project coordination, collaborative planning, and operational traceability.  
It offers both a RESTful backend and a structured web interface tailored to technical teams and administrative managers.

The platform enables:

- real-time employee planning and Outlook-style calendar views,
- encoding and monitoring of performed vs. estimated task hours,
- automatic alerts for late tasks, billing overruns, or time excess,
- integrated dashboards for collaborators and project leaders,
- centralized access to documentation and client deliverables,
- secure authentication and role-based navigation through protected pages.

---

## 🧱 Code Content

The codebase is composed of the following key components:

- **Database schema**: MySQL 8 structure managed in Docker with automatic import and integrity constraints, including triggers for live updates of overrun hours.
- **Backend services**: FastAPI-based API exposing routes for user accounts, projects, clients, tasks, time tracking (prestations), invoices, calendar planning, and analytical views.
- **Authentication & security**: Login form with 2FA code field (manual), JWT token verification, and session cookie handling for protected page access.
- **Web frontend (Jinja2)**: Modular HTML/CSS/JS templates with themed pages for login, dashboard, agenda, documents, task detail, and error reporting.
- **Monitoring tools**: Project-wise dashboards with statistics on delays, overruns, facturation states, user activity, and integrated document access.
- **UI Style System**: Shared CSS styles (`base.css`, `dashboard.css`, etc.) with unified interaction rules (`base-interactions.css`) and consistent responsive layout.
- **Error handling**: Unified error template (`error.html`) triggered by FastAPI exception handlers (403/404/422) with redirect options.
- **Docker integration**: Containerized development with MySQL volume persistence, automatic schema loading, and exposed API.

---

## 🚀 How to Run the Project

### 📦 With Docker

#### ⬢ Basic setup (without data deletion)
```bash
docker compose up -d --build
````

To shut down:

```bash
docker compose down
```

#### ♻️ Full rebuild (with volume wipe)

```bash
docker-compose down -v && docker-compose up --build
```

#### 🧪 Check if API is running

```bash
docker logs polybase-api
```

> App should be available at [http://localhost:8000](http://localhost:8000)

---

### 🐍 Local Development (without Docker)

#### 1. Clone and install dependencies

```bash
git clone https://github.com/ebarrach/PolyBase
cd PolyBase/code/polybase
pip install -r requirements.txt
```

#### 2. Configure environment

Create a `.env` file at the root of `polybase/` with the following:

```
DB_USER=root
DB_PASSWORD=polyroot
DB_HOST=localhost
DB_PORT=3307
DB_NAME=Relation
```

#### 3. Launch the FastAPI app

```bash
uvicorn app.main:app --reload
```

---

## 👤 Author

This project was developed by:

* **Esteban BARRACHO**

---

## 📄 License

This project is licensed **"All Rights Reserved"**.
See the LICENSE file for more details.
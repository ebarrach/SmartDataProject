# SmartDataProject - (License "All Rights Reserved")

This project was carried out as part of a professional collaboration with **S2 Engineering**.

---

## 📌 Project Description

SmartDataProject is a secure internal platform designed to optimize project coordination, collaborative planning, and operational traceability.  
It offers both a RESTful backend and a structured web interface tailored to technical teams, financial administrators, and project managers.

The platform enables:

- real-time employee planning and Outlook-style calendar views,
- encoding and monitoring of performed vs. estimated task hours,
- automatic alerts for late tasks, billing overruns, or time excess,
- integrated dashboards for collaborators, finance, and project leaders,
- centralized access to documentation and client deliverables,
- intelligent import of Excel files via DeepSeek with type adaptation,
- secure authentication with session cookies and role-based page access,
- complete admin interface for table inspection and CRUD operations.

---

## 🧱 Code Content

The codebase is composed of the following key components:

- **Database schema**: MySQL 8 structure in Docker with referential integrity, auto-generated primary keys, and triggers for time tracking.
- **Backend services**: FastAPI-based API exposing routes for personnel, projects, clients, tasks, planning, invoices, performances, costs, dashboards, and calendar.
- **Authentication & security**: Login form with manual 2FA, session cookie handling (`session_id`) and user role retrieval for page routing.
- **Outlook synchronization**: OAuth2 support and Graph API integration for importing and exporting events via `/agenda` and `outlook_sync.py`.
- **Excel adaptation tool**: DeepSeek module that cleans, aligns, and types Excel files based on the SQL table structure before insertion.
- **Dynamic admin panel**: Full CRUD interface with form generation and validation, table introspection, and enum/foreign key rendering.
- **Web frontend (Jinja2)**: Modular templates (`login`, `dashboard`, `agenda`, etc.) rendered based on authenticated user and function.
- **UI Style System**: Unified CSS layout and interaction logic (`base.css`, `dashboard.css`, `base-interactions.css`) for responsive interfaces.
- **Error handling**: Global error HTML page rendered via FastAPI (403, 404, 422) with contextual feedback and navigation hints.
- **Docker integration**: Volume-persistent MySQL, automatic SQL import, backend build, and hot-reloading for development.

---

## 🚀 How to Run the Project

### 📦 With Docker

#### ⬢ Basic setup (without data deletion)

```bash
docker compose up -d --build
```

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
git clone https://github.com/ebarrach/SmartDataProject
cd SmartDataProject/code/polybase
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

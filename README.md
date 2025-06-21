# PolyBase - (License "All Rights Reserved")

This project was carried out as part of a professional collaboration with **Poly-Tech Engineering SA**.

---

## 📌 Project Description

PolyBase is a custom internal web platform designed to optimize project coordination, task management, and data tracking. It includes a RESTful API with role-based access control and a modern web interface for collaborators, managers, and admins.

The platform enables:

- real-time employee scheduling and Outlook-style agenda,
- dynamic task tracking and logging of hours performed,
- generation of billing, alerts, and performance monitoring dashboards,
- structured interaction between technical and administrative workflows.

---

## 🧱 Code Content

The codebase is composed of the following key components:

- **Database schema**: MySQL relational schema managed through Docker with automatic SQL injection on container init.
- **Backend services**: FastAPI application exposing REST endpoints for users, projects, tasks, time tracking, billing, planning, and analytics.
- **Role-based access control**: JWT-based login with cookie session and API guards for dashboard, agenda, and restricted endpoints.
- **Frontend (Jinja2)**: Lightweight HTML/CSS/JS interfaces including login, dashboard, calendar, and task board.
- **Monitoring tools**: Admin-level API endpoints for tracking project costs, time overruns, alerts, and billing projections.
- **Docker integration**: Full containerization for both the MySQL database and the API backend.

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
docker compose down -v
docker compose up --build
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

- **Esteban BARRACHO**

---

## 📄 License

This project is licensed **"All Rights Reserved"**.  
See the LICENSE file for more details.

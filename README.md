# Mental Health Scheduler

A web application to help students/professionals protect their mental well‑being by automatically scheduling restorative breaks around calendar events. Backend provides scheduling APIs; frontend offers a simple dashboard and login.

Most Important I have created this app in `IST` `Asia/Kolkata` time standard


---
#### Working Application Links
- First link : https://enchanting-mousse-3d0d2d.netlify.app

##### Note
- At the time of login google will say `Google hasn’t verified this app` ignore this and go to `Advanced` and click `Go to descope.com (unsafe)`

- After login in app you will see ` No events found` if you have nothing in you calender, in 50 sec it will automatically add the `Wellness brake` depending on time you have logined in, if logined after 8pm then it might not add, So after this just add come events in your calender `don't forget to delete the wellness events` and `app is mainly designed on pre exist events that's why ` . After adding event go back to events and wait for 20 sec or hard reload.
---



## Team
- Team name: – soumyakushwaha011_14e0
- Members: – soumya kushwaha (solo)

---

## Hackathon Theme / Challenge
-  Theme 1 / Mental Health & Wellness — Stress/Well‑being support via smart scheduling

---

## What We Built

The Mental Health Scheduler agent reduces stress and burnout by auto-inserting wellness breaks (stretch, meditation, hydration reminders) directly into a user’s calendar.

- Backend (Flask): REST APIs to fetch events, generate break slots, and push to Google Calendar

- Frontend (Vue 3 + Vite): Clean UI with Descope login and break preview

- Authentication: Descope Outbound Apps securely handle Google OAuth token exchange (no hardcoded credentials)

### Key API Endpoints
- `GET /` — Health check
- `GET /api/testingApi` — Dummy endpoint for connectivity checking
- `POST /api/schedule-breaks` — Generate break schedule
- `GET /api/calendar/events` — Fetch calendar events
- `POST /api/auto-schedule/events` — Auto‑schedule events

---

## How to Run It
#### If running manually then go for project manual in root folder `full code no hosting`
---

### Backend (Flask)
1. Open a terminal in `backend/`
2. Create and activate a virtual environment
   - Windows PowerShell:
     ```powershell
     py -3 -m venv .venv

     .venv\Scripts\Activate    #for Windows
     source venv/bin/activate  #for Linux

     pip install -r requirements.txt
     ```
3. Create a `.env` file in `backend/` (optional but recommended) and set environment variables:
   ```env
   # Flask / App
   DESCOPE_PROJECT_ID = your_project_key
   DESCOPE_MANAGEMENT_KEY = your_management_key

   Notes:
   - You will need Descope keys to run this application (setup Descope and Google cloud)
   - Default DB is SQLite at `instance/dev.db` (auto‑created on first run) (if you want to store user data)
5. Start the server
   ```powershell
   python main.py
   ```
   The API will run at `http://localhost:8000/`.

### Frontend (Vue 3 + Vite)
1. Open a separate terminal in `frontend/`
2. Install dependencies
   ```powershell
   npm install
   npm run dev
   ```
   The app will run at `http://localhost:5173/`.

---

## Tech Stack
- Frontend: Vue 3, Vite, Vue Router, Tailwind CSS
- Backend: Flask, Flask-RESTful, Flask-SQLAlchemy, Flask-Migrate, Flask-CORS, Gunicorn
- Authentication: Descope SDK + Outbound App (Google Calendar API)
- Database: SQLite (dev) (not in use)
- Deployment: Render (backend), Netlify (frontend)

---

## Demo Video Link
- https://youtu.be/kIpMeV6m1c8

---

## With More Time, We Would
- Integrate OAuth calendar providers (Google/Microsoft) for live events
- Improve auto‑scheduling heuristics with preferences and AI‑driven suggestions
- Build richer UI for event editing, drag‑and‑drop
- Add comprehensive tests and CI, plus production observability/metrics



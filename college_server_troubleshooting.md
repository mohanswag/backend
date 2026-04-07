# College Server Deployment - Troubleshooting Guide

This guide is for debugging any connection issues when deploying the FlexAI project to the college server (`http://180.235.121.245:8023/`).

## **1. Server Setup (Django)**
- **File:** `config/settings.py`
- **Check:** Ensure the `ALLOWED_HOSTS` includes the server IP and `*`.
- **Command:** The server MUST be started with the following command to accept outside connections:
  ```bash
  python manage.py runserver 0.0.0.0:8023
  ```
  *(If started with `127.0.0.1`, it will only work on the college machine itself).*

## **2. AI Chatbot Setup (FastAPI)**
- **Check:** The AI chatbot requires a **separate** server to be running on port **8001**.
- **Command:** Open a second terminal and run:
  ```bash
  python fastapi_app.py
  ```
  *(If this is not running, the chatbot will fail with a "Connection Error").*

## **3. Network & Firewall**
- **Ports:** The college network must have ports **8023** (Django) and **8001** (FastAPI) open.
- **Verification:** Try visiting `http://180.235.121.245:8023/api/` in any browser. If it doesn't load, the firewall is likely blocking the port.

## **4. Data & Database**
- **File:** `db.sqlite3`
- **Check:** Ensure your database file is in the root of the `backend` folder. If it's missing, the app will return "Server Error 500."

---

## **How your Developer can Verify:**
1.  **Browser Check:** Visit `http://180.235.121.245:8023/api/profiles/`. It should show a JSON response.
2.  **Server Logs:** Check the server terminal while trying to log in from the app. If no logs appear, the request is not even reaching the server.

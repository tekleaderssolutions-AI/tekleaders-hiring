# Hirix Frontend Integration Guide (v1.0)

This guide provides the technical details for all backend APIs currently live and ready for frontend integration.

---

## 🔑 1. Authentication
**Base URL**: `/api/v1/auth`

| Endpoint | Method | Payload (JSON) | Description |
| :--- | :--- | :--- | :--- |
| `/signup` | `POST` | `email`, `password`, `first_name`, `last_name` | Creates a new account. |
| `/login` | `POST` | `email`, `password` | Returns `access_token`. |
| `/me` | `GET` | *None* | Returns current user profile (requires Token). |

---

## 💼 2. Job Management (JD)
**Base URL**: `/api/v1/jobs`

| Endpoint | Method | Payload | Description |
| :--- | :--- | :--- | :--- |
| `/analyze` | `POST` | `file` (form-data) | AI Analysis of a JD. Returns structured JSON to auto-fill forms. |
| `/` | `POST` | `JobCreate` (JSON) | Manually saves a job to the database. |
| `/` | `GET` | *None* | Lists all jobs for the company. |
| `/{id}` | `GET` | *None* | Fetches full details of a specific job. |
| `/next-code` | `GET` | *None* | Returns the next available Job ID (e.g., TEK-005). |

---

## 👥 3. Candidate Management (Resumes)
**Base URL**: `/api/v1/candidates`

| Endpoint | Method | Payload | Description |
| :--- | :--- | :--- | :--- |
| `/upload` | `POST` | `file` (form-data) | **Smart Upload**: Accepts `.pdf`, `.docx`, or `.zip`. |
| `/` | `GET` | *None* | Lists all processed candidates. |
| `/{id}` | `GET` | *None* | Fetches the full AI-parsed profile of a candidate. |

---

## 🛠️ Technical Implementation Notes

### Authorization Header
All protected endpoints (Jobs & Candidates) require the following header:
```text
Authorization: Bearer <your_access_token>
```

### Smart Upload Response
The `/candidates/upload` endpoint returns a `mode` field:
*   `mode: "single"` ➔ Returns a single candidate object.
*   `mode: "bulk"` ➔ Returns a "processing" status (background task).

---

## 🖱️ UI Button Mapping for Developers

| UI Page | Button / Action | API to Call |
| :--- | :--- | :--- |
| **Login Page** | "Sign In" button | `POST /auth/login` |
| **Job Creation** | "Analyze File" / "Upload JD" | `POST /api/v1/jobs/analyze` |
| **Job Creation** | "Publish Job" / "Save" | `POST /api/v1/jobs` |
| **Dashboard** | Page Load (Automatic) | `GET /api/v1/jobs` |
| **Candidate View** | "Upload Resume" / "Add New" | `POST /api/v1/candidates/upload` |
| **Candidate View** | "Import ZIP" / "Bulk Upload" | `POST /api/v1/candidates/upload` |
| **Candidate List** | Page Load (Automatic) | `GET /api/v1/candidates` |
| **Candidate Detail**| Clicking a Candidate card | `GET /api/v1/candidates/{id}` |

---

**End of Guide.**

# track
a trello alternative

## Local Run

### Backend

```bash
cd backend
pip install -e .
# create runtime config from template (one file for admin + smtp)
copy config\system.example.yaml config\system.yaml
uvicorn app.main:app --reload
```

Runtime config is `backend/config/system.yaml` (not committed to git).
Template: `backend/config/system.example.yaml`.

`system.yaml` includes both admin bootstrap and SMTP settings:

- `admin.email`
- `admin.password`
- `admin.full_name`
- `admin.reset_password_on_startup`
- `smtp.host`
- `smtp.port`
- `smtp.username`
- `smtp.password`
- `smtp.use_tls`
- `smtp.from_email`

Email delivery failures are handled silently for the user and logged in backend logs.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend dev server proxies `/api/*` to `http://127.0.0.1:8000`.

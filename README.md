# track
a trello alternative

## Local Run

### Backend

```bash
cd backend
pip install -e .
uvicorn app.main:app --reload
```

Default admin bootstrap config is in `backend/config/admin.yaml`:

- email: `admin@email.com`
- password: `admin123456`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend dev server proxies `/api/*` to `http://127.0.0.1:8000`.

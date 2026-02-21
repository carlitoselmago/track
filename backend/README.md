# Track Backend

FastAPI backend for Track.

## Run

```bash
cd backend
pip install -e .
cp .env.example .env
# edit .env
python -m app.run
```

You can also use the console script after install:

```bash
track-api
```

## Configuration

Primary config is `backend/.env` (env prefix: `TRACK_`).

Important keys:

- `TRACK_SERVER_HOST`
- `TRACK_SERVER_PORT`
- `TRACK_SERVER_RELOAD`
- `TRACK_SERVER_WORKERS`
- `TRACK_ADMIN_BOOTSTRAP_*`
- `TRACK_SMTP_*`
- `TRACK_EMAIL_FROM`

Optional legacy fallback remains available in `backend/config/system.yaml`.

import uvicorn

from app.core.config import settings


def main() -> None:
    workers = settings.server_workers if not settings.server_reload else 1
    uvicorn.run(
        "app.main:app",
        host=settings.server_host,
        port=int(settings.server_port),
        reload=bool(settings.server_reload),
        workers=max(1, int(workers)),
    )


if __name__ == "__main__":
    main()

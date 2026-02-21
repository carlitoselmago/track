from datetime import datetime
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select

from app.core.config import settings
from app.core.security import get_password_hash
from app.db.session import engine, init_db
from app.models import User
from app.routers.auth import router as auth_router
from app.routers.boards import router as boards_router
from app.routers.cards import router as cards_router
from app.routers.checklists import router as checklists_router
from app.routers.images import router as images_router
from app.routers.labels import router as labels_router
from app.routers.lists import router as lists_router
from app.routers.notifications import router as notifications_router
from app.routers.timer import router as timer_router
from app.routers.users import router as users_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("track.main")


def bootstrap_admin_user() -> None:
    email = str(settings.admin_bootstrap_email or "").strip().lower()
    password = str(settings.admin_bootstrap_password or "").strip()
    name = str(settings.admin_bootstrap_full_name or "System Admin").strip() or "System Admin"
    reset_password_on_startup = bool(settings.admin_reset_password_on_startup)

    if not email or not password:
        logger.info("Admin bootstrap skipped: missing admin credentials in config.")
        return

    with Session(engine) as session:
        user = session.exec(select(User).where(User.email == email)).first()
        if not user:
            user = User(
                email=email,
                name=name,
                password_hash=get_password_hash(password),
                is_system_admin=True,
                is_active=True,
                deleted_at=None,
            )
            session.add(user)
            session.commit()
            logger.info("Admin bootstrap created user '%s'.", email)
            return

        changed = False
        if user.deleted_at is not None:
            user.deleted_at = None
            changed = True
        if not user.is_active:
            user.is_active = True
            changed = True
        if not user.is_system_admin:
            user.is_system_admin = True
            changed = True
        if user.name != name:
            user.name = name
            changed = True
        if reset_password_on_startup:
            user.password_hash = get_password_hash(password)
            changed = True
        if changed:
            user.updated_at = datetime.utcnow()
            session.add(user)
            session.commit()
            logger.info("Admin bootstrap updated user '%s'.", email)


app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    bootstrap_admin_user()


@app.get("/")
def root():
    return {"name": settings.app_name, "api_prefix": settings.api_prefix}


app.include_router(auth_router, prefix=settings.api_prefix)
app.include_router(users_router, prefix=settings.api_prefix)
app.include_router(boards_router, prefix=settings.api_prefix)
app.include_router(lists_router, prefix=settings.api_prefix)
app.include_router(cards_router, prefix=settings.api_prefix)
app.include_router(checklists_router, prefix=settings.api_prefix)
app.include_router(labels_router, prefix=settings.api_prefix)
app.include_router(images_router, prefix=settings.api_prefix)
app.include_router(timer_router, prefix=settings.api_prefix)
app.include_router(notifications_router, prefix=settings.api_prefix)

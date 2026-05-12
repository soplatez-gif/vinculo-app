import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.routes import health, webhook
from src.db.session import engine, AsyncSessionLocal
from src.db.models import Base, Therapist
from sqlalchemy import select


DEMO_THERAPIST_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")


async def seed_demo_therapist():
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Therapist).where(Therapist.id == DEMO_THERAPIST_ID)
        )
        if result.scalar_one_or_none() is None:
            therapist = Therapist(
                id=DEMO_THERAPIST_ID,
                name="Dra. Prueba",
                phone="+570000000000",
                email="demo@vinculo.app",
                specialty="Psicología clínica",
                session_duration_minutes=50,
                session_price=150000,
                modality="virtual",
                working_hours={
                    "monday": {"start": "09:00", "end": "17:00"},
                    "wednesday": {"start": "09:00", "end": "17:00"},
                    "friday": {"start": "09:00", "end": "13:00"},
                },
            )
            session.add(therapist)
            await session.commit()
            print("✅ Terapeuta demo creado")
        else:
            print("✅ Terapeuta demo ya existe")


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await seed_demo_therapist()
    yield
    await engine.dispose()


app = FastAPI(title="Vínculo", version="0.1.0", lifespan=lifespan)

app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(webhook.router, prefix="/webhook", tags=["webhook"])


@app.get("/")
async def root():
    return {"app": "Vínculo", "status": "running"}

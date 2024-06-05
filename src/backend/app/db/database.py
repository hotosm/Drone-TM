"""Config for the DTM database connection."""

from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from app.config import settings


engine = create_async_engine(
    settings.DTM_DB_URL.unicode_string(),
    echo=settings.POSTGRES_ECHO,
    pool_size=20,
    max_overflow=-1,
)

# engine = create_engine(
#     settings.DTM_DB_URL.unicode_string(),
#     pool_size=20,
#     max_overflow=-1,
# )

# SessionLocal = sessionmaker(autocommit=False,
#                             autoflush=False,
#                             bind=engine
#                             )


Base = declarative_base()
DtmMetadata = Base.metadata

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)

# def get_db():
#     """Create SQLAlchemy DB session."""
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


async def get_db():
    async with SessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()

from fastapi import FastAPI
from api.routes import router
from utils.cleanup import cleanup_expired_records
from utils.embedding_cache import cleanup_old_cache


app = FastAPI()

cleanup_expired_records()
cleanup_old_cache()

app.include_router(router)
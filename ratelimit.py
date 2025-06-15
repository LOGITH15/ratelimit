from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from redis import asyncio as aioredis
from contextlib import asynccontextmanager
import time

@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = aioredis.from_url("redis://localhost", encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(redis)
    yield
    await redis.close()

app = FastAPI(lifespan=lifespan)

@app.exception_handler(429)
async def custom_throttle_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=429,
        content={"message": "You're being throttled. Try again later.", "detail": exc.detail,
            "path": request.url.path},
    )

@app.get("/throttled", dependencies=[Depends(RateLimiter(times=5, seconds=10))])
async def throttled_endpoint():
    return {"message": "You are within the request limit"}

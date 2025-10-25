import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from modder_mc_service.util.logging import LOGGER
from modder_mc_service.agent.create import create_mod_agent


class HealthResponse(BaseModel):
    status: str
    uptime_seconds: int
    sqlite: str


some_global_store = {}
startup_time = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    some_global_store["key"] = "value"
    yield


app = FastAPI(lifespan=lifespan)




@app.get("/health", response_model=HealthResponse)
async def get_health() -> HealthResponse:
    """
    check for API health
    """
    current_time = time.time()
    uptime_seconds = int(current_time - startup_time)
    return HealthResponse(
        status="healthy", uptime_seconds=uptime_seconds)

@app.get("/create")
async def create_mod(mod_name: str):
    """
    create a mod
    """
    try:
        
        resp = await create_mod_agent(mod_name, "A new mod")
        return resp
    except Exception as e:
        LOGGER.error(f"Error creating mod: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
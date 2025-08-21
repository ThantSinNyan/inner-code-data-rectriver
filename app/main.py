from fastapi import FastAPI
from app.controllers import plan_controller

app = FastAPI(title="Healing Journey API")

app.include_router(plan_controller.router, prefix="/healing")
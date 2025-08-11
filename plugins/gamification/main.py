from fastapi import APIRouter, FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine

class Plugin:
    def __init__(self):
        self.router = APIRouter()

        @self.router.get("/gamification/badges")
        async def get_badges():
            return {"badges": ["top-seller", "fast-responder", "verified"]}

    def register_routes(self, app: FastAPI):
        app.include_router(self.router, prefix="/gamification", tags=["gamification"])

    async def init_db(self, engine: AsyncEngine):
        # Example: Here you could run CREATE TABLE if needed.
        # For now, just a placeholder.
        print("Gamification plugin DB initialized")

    async def shutdown(self):
        print("Gamification plugin shutdown")
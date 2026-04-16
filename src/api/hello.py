from fastapi import APIRouter
from pydantic import BaseModel

from src.shared.logging import get_logger

router = APIRouter(tags=["hello"])
logger = get_logger(__name__)


class HelloResponse(BaseModel):
    message: str


@router.get("/hello", response_model=HelloResponse)
async def hello() -> HelloResponse:
    logger.info("Hello endpoint called")
    return HelloResponse(message="Hello from Surveillance API!")


@router.get("/hello/{name}", response_model=HelloResponse)
async def hello_name(name: str) -> HelloResponse:
    logger.info("Hello endpoint called", extra={"data": {"name": name}})
    return HelloResponse(message=f"Hello, {name}!")

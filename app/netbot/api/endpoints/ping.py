from fastapi import APIRouter, Query
from netbot.core.networking import ping_host

router = APIRouter()

@router.get("/ping")
def ping_device(host: str = Query(..., description="IP or hostname to ping")):
    """
    Ping a host and return online status and average latency.
    """
    result = ping_host(host)
    return result

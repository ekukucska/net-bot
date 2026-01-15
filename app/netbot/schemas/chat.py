from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    message: str = Field(..., description="User's natural language message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "ping 192.168.1.1"
            }
        }


class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    message: str = Field(..., description="Bot's response message")
    action: str = Field(..., description="Action that was performed")
    status: str = Field(..., description="Status of the action (success/error)")
    data: Optional[Dict[str, Any]] = Field(None, description="Raw data from the action")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "✅ 192.168.1.1 is online! Average response time: 15.2ms",
                "action": "ping",
                "status": "success",
                "data": {
                    "host": "192.168.1.1",
                    "status": "online",
                    "avg_latency_ms": "15.2"
                }
            }
        }


class DeviceInfo(BaseModel):
    """Model for network device information"""
    ip: str
    mac: Optional[str] = None
    hostname: Optional[str] = None
    status: str


class PortInfo(BaseModel):
    """Model for port scan information"""
    port: int
    open: bool
    service: Optional[str] = None


class ActionLogResponse(BaseModel):
    """Response model for action log"""
    id: int
    action: str
    parameters: str
    result_summary: Optional[str]
    status: str
    timestamp: datetime
    
    class Config:
        from_attributes = True

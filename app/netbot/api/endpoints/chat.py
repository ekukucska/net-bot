from fastapi import APIRouter, HTTPException
from netbot.schemas import ChatRequest, ChatResponse
from netbot.core.chatbot import ChatBot
from netbot.core.networking import (
    ping_host,
    scan_local_network,
    check_ports,
    get_local_ip,
    get_default_gateway,
    traceroute,
    dns_lookup
)
from netbot.db import get_session, create_action_log
import json

router = APIRouter()
chatbot = ChatBot()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process natural language chat message and perform network diagnostic actions.
    """
    # Parse user message to extract intent
    intent = chatbot.parse_message(request.message)
    
    # Execute the appropriate action based on intent
    if intent.action == "ping":
        result = ping_host(intent.parameters.get("host"))
        response_message = chatbot.format_response(intent.action, result)
        status = result.get("status", "error")
    
    elif intent.action == "scan_network":
        result = scan_local_network()
        response_message = chatbot.format_response(intent.action, result)
        status = result.get("status", "error")
    
    elif intent.action == "check_ports":
        host = intent.parameters.get("host")
        ports = intent.parameters.get("ports", [22, 80, 443])
        result = check_ports(host, ports)
        response_message = chatbot.format_response(intent.action, result)
        status = result.get("status", "error")
    
    elif intent.action == "get_local_ip":
        result = get_local_ip()
        response_message = chatbot.format_response(intent.action, result)
        status = result.get("status", "error")
    
    elif intent.action == "get_gateway":
        result = get_default_gateway()
        response_message = chatbot.format_response(intent.action, result)
        status = result.get("status", "error")
    
    elif intent.action == "traceroute":
        result = traceroute(intent.parameters.get("host"))
        response_message = chatbot.format_response(intent.action, result)
        status = result.get("status", "error")
    
    elif intent.action == "dns_lookup":
        result = dns_lookup(intent.parameters.get("host"))
        response_message = chatbot.format_response(intent.action, result)
        status = result.get("status", "error")
    
    elif intent.action == "help":
        result = {"status": "success"}
        response_message = chatbot.get_help_text()
        status = "success"
    
    elif intent.action == "unknown":
        result = {"status": "unknown"}
        response_message = chatbot.format_response(intent.action, result)
        status = "unknown"
    
    else:
        result = {"status": "error", "error": "Unsupported action"}
        response_message = "Sorry, I don't know how to do that yet."
        status = "error"
    
    # Log the action to database
    try:
        db = get_session()
        create_action_log(
            db=db,
            action=intent.action,
            parameters=intent.parameters,
            result_summary=response_message[:200],  # Store first 200 chars
            status=status
        )
        db.close()
    except Exception as e:
        # Don't fail the request if logging fails
        print(f"Failed to log action: {e}")
    
    return ChatResponse(
        message=response_message,
        action=intent.action,
        status=status,
        data=result if status != "unknown" else None
    )


@router.get("/chat/help")
async def get_help():
    """
    Get help text with available commands.
    """
    return {
        "message": chatbot.get_help_text(),
        "action": "help",
        "status": "success"
    }

"""
Admin Tools for Pizoo
SMS invite sending and other administrative functions
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sms_service import send_sms

# Import authentication dependency from main server
# This will be imported properly when integrated
# from server import get_current_user, db

admin_router = APIRouter(prefix="/api/admin", tags=["admin"])


class SMSInvitePayload(BaseModel):
    phone: str
    message: str
    language: str = "en"


@admin_router.post("/send-invite")
async def send_invite_sms(payload: SMSInvitePayload):
    """
    Send SMS invitation to a phone number
    
    Args:
        phone: E.164 format phone number
        message: Custom message text
        language: Language code for the message
    
    Returns:
        Success status
    
    Note: This endpoint should be protected with admin authentication
    """
    # TODO: Add admin authentication check
    # user = await get_current_user()
    # if not user.get("is_admin"):
    #     raise HTTPException(403, "ADMIN_ONLY")
    
    # Validate phone format
    if not payload.phone.startswith("+"):
        raise HTTPException(400, "INVALID_PHONE_FORMAT")
    
    # Send SMS
    success = send_sms(payload.phone, payload.message)
    
    if not success:
        raise HTTPException(500, "SMS_FAILED")
    
    return {
        "ok": True,
        "phone": payload.phone,
        "message": "SMS sent successfully"
    }


@admin_router.post("/send-bulk-invites")
async def send_bulk_invites(phones: list[str], message: str):
    """
    Send SMS invitations to multiple phone numbers
    
    Args:
        phones: List of E.164 format phone numbers
        message: Message text to send
    
    Returns:
        Success and failure counts
    """
    # TODO: Add admin authentication check
    
    results = {
        "success": [],
        "failed": []
    }
    
    for phone in phones:
        if not phone.startswith("+"):
            results["failed"].append({"phone": phone, "reason": "Invalid format"})
            continue
        
        success = send_sms(phone, message)
        
        if success:
            results["success"].append(phone)
        else:
            results["failed"].append({"phone": phone, "reason": "SMS sending failed"})
    
    return {
        "ok": True,
        "total": len(phones),
        "sent": len(results["success"]),
        "failed": len(results["failed"]),
        "details": results
    }

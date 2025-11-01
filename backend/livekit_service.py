"""
LiveKit Service - Real-Time Communication
Handles video/voice call token generation and room management
"""

import os
from datetime import timedelta
from livekit import api
import logging

logger = logging.getLogger(__name__)

# Load LiveKit configuration from environment
# Note: .env is loaded by server.py before importing this module
LIVEKIT_API_KEY = os.environ.get('LIVEKIT_API_KEY')
LIVEKIT_API_SECRET = os.environ.get('LIVEKIT_API_SECRET')
LIVEKIT_URL = os.environ.get('LIVEKIT_URL', 'wss://pizoo-app-2jxoavwx.livekit.cloud')

class LiveKitService:
    """Service for LiveKit token generation and room management"""
    
    @classmethod
    def is_configured(cls) -> bool:
        """Check if LiveKit is properly configured"""
        return bool(LIVEKIT_API_KEY and LIVEKIT_API_SECRET and LIVEKIT_URL)
    
    @classmethod
    def generate_token(
        cls,
        room_name: str,
        participant_identity: str,
        participant_name: str = None,
        can_publish: bool = True,
        can_subscribe: bool = True,
        can_publish_data: bool = True,
        video_grant: bool = True,
        audio_grant: bool = True,
    ) -> dict:
        """
        Generate LiveKit access token for a participant
        
        Args:
            room_name: Name of the room to join
            participant_identity: Unique identifier for the participant (e.g., user_id)
            participant_name: Display name for the participant
            can_publish: Allow publishing tracks
            can_subscribe: Allow subscribing to tracks
            can_publish_data: Allow publishing data messages
            video_grant: Grant video permissions
            audio_grant: Grant audio permissions
            
        Returns:
            dict with token, url, and room info
        """
        try:
            if not cls.is_configured():
                logger.error("❌ LiveKit not configured")
                return {
                    "success": False,
                    "error": "خدمة المكالمات غير متاحة حالياً",
                    "error_code": "SERVICE_UNAVAILABLE"
                }
            
            # Create access token
            token = api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
            
            # Set identity and name and grants using chaining
            token = (
                token
                .with_identity(participant_identity)
                .with_name(participant_name or participant_identity)
                .with_grants(api.VideoGrants(
                    room_join=True,
                    room=room_name,
                    can_publish=can_publish,
                    can_subscribe=can_subscribe,
                    can_publish_data=can_publish_data,
                ))
            )
            
            # Generate JWT token
            jwt_token = token.to_jwt()
            
            logger.info(f"✅ LiveKit token generated for {participant_identity} in room {room_name}")
            
            return {
                "success": True,
                "token": jwt_token,
                "url": LIVEKIT_URL,
                "room_name": room_name,
                "participant_identity": participant_identity,
                "participant_name": participant_name or participant_identity,
                "video_enabled": video_grant,
                "audio_enabled": audio_grant
            }
            
        except Exception as e:
            logger.error(f"❌ LiveKit token generation error: {str(e)}")
            return {
                "success": False,
                "error": "فشل إنشاء جلسة المكالمة",
                "error_code": "TOKEN_GENERATION_FAILED"
            }
    
    @classmethod
    def create_room_token(
        cls,
        match_id: str,
        user_id: str,
        user_name: str = None,
        call_type: str = "video"  # "video" or "audio"
    ) -> dict:
        """
        Create a token for a 1-to-1 call
        
        Args:
            match_id: Match/chat ID
            user_id: User ID
            user_name: User display name
            call_type: "video" or "audio"
            
        Returns:
            dict with token and connection info
        """
        room_name = f"pizoo-match-{match_id}"
        
        # For audio-only calls, we still allow video but the UI will handle muting
        video_enabled = call_type == "video"
        audio_enabled = True
        
        return cls.generate_token(
            room_name=room_name,
            participant_identity=user_id,
            participant_name=user_name or f"User-{user_id[:8]}",
            can_publish=True,
            can_subscribe=True,
            can_publish_data=True,
            video_grant=video_enabled,
            audio_grant=audio_enabled
        )
    
    @classmethod
    def create_group_room_token(
        cls,
        room_id: str,
        user_id: str,
        user_name: str = None,
    ) -> dict:
        """
        Create a token for a group call (future feature)
        
        Args:
            room_id: Group room ID
            user_id: User ID
            user_name: User display name
            
        Returns:
            dict with token and connection info
        """
        room_name = f"pizoo-group-{room_id}"
        
        return cls.generate_token(
            room_name=room_name,
            participant_identity=user_id,
            participant_name=user_name or f"User-{user_id[:8]}",
            can_publish=True,
            can_subscribe=True,
            can_publish_data=True,
            video_grant=True,
            audio_grant=True
        )


# Helper function for quick token generation
def generate_call_token(match_id: str, user_id: str, user_name: str = None, call_type: str = "video") -> dict:
    """Quick helper to generate call token"""
    return LiveKitService.create_room_token(match_id, user_id, user_name, call_type)

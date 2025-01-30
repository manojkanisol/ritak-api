from typing import Dict, Optional
import jwt
from datetime import datetime
from ..config import settings

def refresh_token_from_auth_server(token: str) -> Optional[str]:
    """
    Refresh an expired token from the auth server
    
    Args:
        token: The expired JWT token
        
    Returns:
        str containing new token if refresh successful
        None if refresh fails
    """
    # TODO: Implement actual refresh logic with auth server
    return None

def decode_jwt_token(token: str) -> Optional[Dict]:
    """
    Decode and verify a JWT token
    
    Args:
        token: The JWT token string to decode
        
    Returns:
        Dict containing the decoded token payload if valid
        None if token is invalid
    """
    try:
        decoded_token = jwt.decode(token, settings.jwt_secret, algorithms=settings.jwt_algorithm)
        
        # Verify token hasn't expired
        if decoded_token.get("exp") and datetime.utcnow().timestamp() > decoded_token["exp"]:
            return None
            
        return decoded_token
    except jwt.InvalidTokenError:
        return None
    except jwt.ExpiredSignatureError:
            # Call auth server to refresh token
            # This is a placeholder - implement actual refresh logic
            new_token = refresh_token_from_auth_server(token)
            if new_token:
                return decode_jwt_token(new_token)
            return None
    except jwt.InvalidTokenError:
            return None
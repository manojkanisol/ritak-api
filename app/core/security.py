from typing import Dict, Optional
import jwt
from datetime import datetime
from ..config import settings
from fastapi import Depends, HTTPException, status,Request
from fastapi.security import OAuth2PasswordBearer



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

# Function to extract token from header
async def get_token_from_header(request: Request) -> str:

    authorization = request.headers.get("Authorization")
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        decoded_token = jwt.decode(token, settings.jwt_secret, algorithms=settings.jwt_algorithm)
        
        # Verify token hasn't expired
        if decoded_token.get("exp") and datetime.utcnow().timestamp() > decoded_token["exp"]:
            return None
            
        return decoded_token.get("sub")
    except jwt.InvalidTokenError:
        return credentials_exception
    except jwt.ExpiredSignatureError:
            # Call auth server to refresh token
            # This is a placeholder - implement actual refresh logic
            new_token = refresh_token_from_auth_server(token)
            if new_token:
                return None
            return None
    except jwt.InvalidTokenError:
            return credentials_exception
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
            headers={"WWW-Authenticate": "Bearer"},
        )

# async def decode_jwt_token(request:Request) -> str:
#     token = await get_token_from_header(request)
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     """
#     Decode and verify a JWT token
    
#     Args:
#         token: The JWT token string to decode
        
#     Returns:
#         Dict containing the decoded token payload if valid
#         None if token is invalid
#     """
#     try:
#         decoded_token = jwt.decode(token, settings.jwt_secret, algorithms=settings.jwt_algorithm)
        
#         # Verify token hasn't expired
#         if decoded_token.get("exp") and datetime.utcnow().timestamp() > decoded_token["exp"]:
#             return None
            
#         return decoded_token.get("sub")
#     except jwt.InvalidTokenError:
#         return credentials_exception
#     except jwt.ExpiredSignatureError:
#             # Call auth server to refresh token
#             # This is a placeholder - implement actual refresh logic
#             new_token = refresh_token_from_auth_server(token)
#             if new_token:
#                 return decode_jwt_token(new_token)
#             return None
#     except jwt.InvalidTokenError:
#             return credentials_exception
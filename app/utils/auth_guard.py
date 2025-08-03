from fastapi import Depends, HTTPException, Header,Security,status
from fastapi.security  import HTTPBearer, HTTPAuthorizationCredentials
from app.config import supabase

bearer_scheme = HTTPBearer(auto_error=False)

def get_current_user(credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)):
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    token = credentials.credentials
    result = supabase.auth.get_user(token)
    user=result.user
    if not result.user:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    return result.user



def require_role(role: str):
    def role_checker(user=Depends(get_current_user)):
        print("user role",user.user_metadata)
        if user.user_metadata.get("role") != role:
            raise HTTPException(status_code=403, detail="Access denied")
        return user
    return role_checker
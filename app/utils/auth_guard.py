from fastapi import Depends, HTTPException




def require_role(role):
    def decorator(user=Depends(get_current_user)):
        if user["role"] != role:
            raise HTTPException(status_code=403, detail="Access denied")
        return user
    return decorator
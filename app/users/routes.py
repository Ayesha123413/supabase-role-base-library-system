from fastapi import APIRouter, HTTPException, status, Depends,Security
from app.config import supabase
from app.users.models import UserProfile, UpdateUserRole
from app.utils.auth_guard import require_role,get_current_user

user_router = APIRouter()

# Get current user profile
@user_router.get("/me", response_model=UserProfile)
def get_my_profile(user=Security(get_current_user)):
    """Get the current user's profile."""
    try:
        profile = supabase.table("Profiles").select("*").eq("id", user.id).single().execute()
        # print("profile",profile.data)
        if not profile.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return profile.data
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@user_router.get("/",response_model=list[UserProfile])
def list_users(user=Depends(require_role("admin"))):
    try:
        profiles = supabase.table("Profiles").select("*").execute()
        return profiles.data
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@user_router.put("/{user_id}/role")
def update_user_role(user_id: str, payload: UpdateUserRole, user=Depends(require_role("admin"))):
    """Update a user's role."""
    try:
        result = supabase.table("Profiles").update({"role": payload.role}).eq("id", user_id).execute()
        if result.data is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return {"message": "User role updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
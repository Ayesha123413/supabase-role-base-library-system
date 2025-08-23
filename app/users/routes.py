from fastapi import APIRouter, HTTPException, status, Depends,Security
from app.config import supabase, supabase_admin
from app.users.models import UserProfile, UpdateUserRole,CreateUserRequest,UpdatePasswordRequest
from app.utils.auth_guard import require_role,get_current_user
import bcrypt

user_router = APIRouter()



@user_router.post("/", response_model=UserProfile)
def create_user(payload: CreateUserRequest, user=Security(require_role("admin"))):
    try:
        # Step 1: Create user in Supabase Auth\
        print("going here")
        auth_res = supabase_admin.auth.admin.create_user(
            {
                "email": payload.email,
                "password": payload.password,  # Admin provides custom password
                "email_confirm": True,  
                "user_metadata": {
                    "full_name": payload.full_name,
                    "role": payload.role
                }
            }
        )
        print("Supabase response:", auth_res)

        if not auth_res.user:
            raise HTTPException(status_code=400, detail="Failed to create user in Auth")

        # Step 2: Insert into Profiles table
        hashed_password = bcrypt.hashpw(payload.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        profile_data = {
            "id": str(auth_res.user.id),
            "email": payload.email,
            "full_name": payload.full_name,
            "role": payload.role,
            "password":hashed_password
        }

        db_res = supabase.table("Profiles").insert(profile_data).execute()

        if not db_res.data:
            raise HTTPException(status_code=500, detail="Failed to insert user into Profiles")

        return UserProfile(**profile_data)

    except Exception as e:
        print("Supabase admin error:", repr(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# Get current user profile
@user_router.get("/me", response_model=UserProfile)
def get_my_profile(user=Security(get_current_user)):
    """Get the current user's profile."""
    try:
        profile = supabase.table("Profiles").select("*").eq("id", user.id).single().execute()
        print("profile",profile.data)
        if not profile.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return profile.data
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# get all users profiles, only admin can do this

@user_router.get("/",response_model=list[UserProfile])
def list_users(user=Depends(require_role("admin"))):
    try:
        profiles = supabase.table("Profiles").select("*").execute()
        return profiles.data
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))



# update role of any user , only admin can do this

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

@user_router.put("/update-password")
def update_password(payload: UpdatePasswordRequest, user=Depends(get_current_user)):
    """
    Allows a member to change their own password.
    Profiles table is not updated because password is managed by Supabase Auth.
    """
    try:
        # Step 1: Verify old password with Supabase Auth
        auth_res = supabase.auth.sign_in_with_password({
            "email": user.email,   # email comes from Profiles
            "password": payload.old_password
        })

        if not auth_res.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Old password is incorrect"
            )

        # Step 2: Update password using Admin API
        supabase_admin.auth.admin.update_user_by_id(
            user.id,   # user.id comes from Profiles, matches Supabase Auth user
            {"password": payload.new_password}
        )

        return {"message": "Password updated successfully"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Password update failed: {str(e)}"
        )
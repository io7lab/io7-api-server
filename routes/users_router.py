from fastapi import APIRouter, HTTPException, status, Depends
from models.users import User, NewUser, TokenResponse
from secutils import create_access_token
from secutils import authenticate, create_hash, verify_hash
from environments import Database
import json

router = APIRouter(tags=['Users'])
db = Database(User.Settings.name)

@router.get('/validate_token')
async def valid_token(jwt: str = Depends(authenticate)) -> dict:
    return {"detail": "Authorized", "token": jwt}

@router.post('/signup')
async def add_user(user: NewUser) -> dict:
    # check if admin user exists and reject if exists
    users = db.getAll()
    if len(users) > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Admin User exists already."
        )
    user.password = create_hash(user.password)
    db.insert(user)
    return {
        "message": f"User({user.email}) created successfully"
    }

@router.post("/login", response_model=TokenResponse)
async def login(user: User) -> dict:
    qryUser = db.getOne(db.qry.email == user.email)
    if not qryUser:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User(email:{user.email}) does not exist."
        )
    if verify_hash(user.password, qryUser['password']):
        access_token = create_access_token(qryUser['email'])
        return {
            "access_token": access_token,
            "token_type": "Bearer"
        }

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid details passed."
    )
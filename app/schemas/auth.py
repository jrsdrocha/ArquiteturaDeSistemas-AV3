from pydantic import BaseModel, constr


UsernameStr = constr(strip_whitespace=True, min_length=3, max_length=50)
PasswordStr = constr(min_length=6, max_length=255)


class LoginRequest(BaseModel):
    username: UsernameStr
    password: PasswordStr


class RegisterRequest(LoginRequest):
    pass


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


LoginSchema = LoginRequest
RegisterSchema = RegisterRequest
TokenSchema = AuthResponse

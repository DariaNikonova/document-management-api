import jwt

from datetime import datetime, timedelta, timezone


SECRET_KEY = "my-super-secret-key-for-fastapi-course-2026"


payload = {
    "sub": "1",
    "exp": datetime.now(timezone.utc) + timedelta(minutes=30)
}


token = jwt.encode(
    payload,
    SECRET_KEY,
    algorithm="HS256"
)


print("TOKEN:")
print(token)


decoded = jwt.decode(
    token,
    SECRET_KEY,
    algorithms=["HS256"]
)


print("DECODED:")
print(decoded)
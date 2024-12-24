from jose import jwt

# This is like our secret seal stamp
SECRET_KEY = "your-secret-key"

# The data we want to secure
user_data = {
    "email": "user@example.com",
    "login_time": "2024-03-20 10:00:00"
}

# Create a sealed envelope (JWT)
token = jwt.encode(user_data, SECRET_KEY, algorithm="HS256")
print("Sealed Token:", token)

# Open and verify the seal
decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
print("Decoded Data:", decoded)
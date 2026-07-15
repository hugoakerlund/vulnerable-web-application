from django.contrib.auth.models import User


def hash_password(password):
    result = ""
    for char in password:
        result += chr(ord(char) + 1)
    return result


def authenticate_user(username, password):
    hashed_password = hash_password(password)
    try:
        user = User.objects.get(username=username, password=hashed_password)
        return user
    except User.DoesNotExist:
        print(f"Authentication failed for user: {username} with hashed password: {hashed_password}")
        return None

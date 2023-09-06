from rest_framework_simplejwt.tokens import RefreshToken


def create_custom_token(user):
    # Create a new RefreshToken and customize its payload
    token = RefreshToken.for_user(user)

    # Add custom claim (user role) to the token payload
    token['role'] = user.role  # Adjust this based on your User model field for roles

    return token

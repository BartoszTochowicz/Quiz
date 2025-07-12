from flask import Blueprint, jsonify, make_response, request
from flask_jwt_extended import current_user, get_jwt, jwt_required
from .controller import AuthController

auth_bp = Blueprint('auth',__name__)
authController = AuthController()

@auth_bp.post('/login')
def login():
    """ Example endpoint for user login.
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
              example: "user123"
            password:
              type: string
              example: "securepassword"
    responses:
      200:
        description: Login successful
        schema:
          type: object
          properties:
            access_token:
              type: string
              example: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            data:
              type: object
              properties:
                username:
                  type: string
                  example: "user123"
                email:
                  type: string
                  example: "example@gmail.com"
            message:
              type: string
              example: "Login successful!"
        headers:
          Set-Cookie:
            schema:
              type: string
              example: access_token_cookie=abcde12345; Path=/; HttpOnly
      400:
        description: Missing required fields
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Missing required fields!"
      401:
        description: Invalid password
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Invalid password!"
      404:
        description: User not found
        schema:
          type: object
          properties:
            message:
              type: string
              example: "User not found!"
    """
    result = authController.login(request=request)
    return make_response(result)

@auth_bp.get('/login')
def login_get():
    """ Example endpoint for user login.
    ---
    tags:
      - Authentication
    parameters:
      - in: header
        name: Authorization
        required: true
        type: string
        description: Bearer token for authentication
    responses:
      200:
        description: Data retrived successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Data retrived successfully!"
            data:
              type: object
              properties:
                username:
                  type: string
                  example: "example_username"
                email:
                  type: string
                  example: "example@gmail"
      404:
        description: User not found
        schema:
          type: object
          properties:
            message:
              type: string
              example: "User not found!"
    """
    result = authController.login_get(current_user)
    return make_response(result)
@auth_bp.post('/register')
def register():
    """ Example endpoint for user registering.
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
              example: "user123"
            email:
                type: string
                example: "example@gmail.com"
            password:
              type: string
              example: "securepassword"
    responses:
      201:
        description: Register successful
        schema:
        type: object
        properties:
          data:
          type: object
          properties:
            message:
            type: string
            example: "Register successful!"
      409:
        description: User already exists
        schema:
        type: object
        properties:
          data:
          type: object
          properties:
            message:
            type: string
            example: "User already exists!"
      400:
        description: Missing required fields
        schema:
        type: object
        properties:
          data:
          type: object
          properties:
            message:
            type: string
            example: "Missing required fields!"
    """
    result = authController.register(request=request)
    return make_response(result)
@auth_bp.delete('/logout/refresh')
@jwt_required(refresh=True)
def logout_refresh():
    """ Example endpoint for user logout.
    ---
    tags:
      - Authentication
    parameters:
      - in: header
        name: X-CSRF-Token
        required: true
        schema:
          type: string
        description: CSRF token for logout
    responses:
      200:
        description: Logout successful
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Logout successful!"      
    """
    result = authController.refresh(get_jwt()['jti'], access=False)
    return make_response(result)
@auth_bp.delete('/logout/access')
@jwt_required()
def logout_access():
    """ Example endpoint for user logout.
    ---
    tags:
      - Authentication
    parameters:
      - in: header
        name: Authorization
        required: true
        type: string
        description: Bearer token for authentication
    responses:
      200:
        description: Logout successful
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Logout successful!"      
    """
    result = authController.logout(get_jwt()['jti'], access=True)
    return make_response(result)
@auth_bp.get('/refresh')
@jwt_required(refresh=True)
def refresh():
    """ Example endpoint for refreshing access token.
    ---
    tags:
      - Authentication
    parameters:
      - in: header
        name: X-CSRF-Token
        required: true
        schema:
          type: string
        description: CSRF token for logout
    responses:
      200:
        description: Token refreshed successfully
        schema:
          type: object
          properties:
            access_token:
              type: string
              example: "new_access_token"
      401:
        description: Invalid refresh token
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Invalid refresh token!"
    """
    result = authController.refresh(get_jwt(),current_user)
    return result
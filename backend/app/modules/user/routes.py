from flask import Blueprint, jsonify, request
from .controllers import get_user_info

user_bp = Blueprint('user', __name__)

@user_bp.route('/<int:user_id>', methods=['GET'])
def user_profile(user_id):
    user = get_user_info(user_id)
    return jsonify(user), 200
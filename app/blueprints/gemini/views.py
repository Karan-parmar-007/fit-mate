from app.models.user_model import UserModel
from flask import Blueprint, request, jsonify
from app.utils.logger import logger
from app.blueprints.gemini import gemini_bp
user_model = UserModel()


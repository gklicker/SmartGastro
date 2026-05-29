from flask import jsonify
from flask_jwt_extended import JWTManager
from config import Config


def create_app():
    from flask import Flask
    app = Flask(__name__)
    app.config["SECRET_KEY"] = Config.SECRET_KEY
    app.config["JWT_SECRET_KEY"] = Config.JWT_SECRET_KEY
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = Config.JWT_ACCESS_TOKEN_EXPIRES
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = Config.JWT_REFRESH_TOKEN_EXPIRES

    jwt = JWTManager(app)

    @jwt.unauthorized_loader
    def missing_token(reason):
        return jsonify({"error": "Unauthorized", "message": reason, "code": 4010}), 401

    @jwt.invalid_token_loader
    def invalid_token(reason):
        return jsonify({"error": "Unauthorized", "message": reason, "code": 4010}), 401

    @jwt.expired_token_loader
    def expired_token(header, payload):
        return jsonify({"error": "Unauthorized", "message": "Token expirado.", "code": 4013}), 401

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Not Found", "message": str(e), "code": 4040}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"error": "Method Not Allowed", "message": str(e), "code": 4050}), 405

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"error": "Internal Server Error", "message": "Error inesperado.", "code": 5000}), 500

    from api import register_blueprints
    register_blueprints(app)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)

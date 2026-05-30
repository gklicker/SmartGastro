import math
from flask import jsonify
from flask_jwt_extended import get_jwt, verify_jwt_in_request


def success(data, status=200, meta=None):
    body = {"data": data}
    if meta:
        body["meta"] = meta
    return jsonify(body), status


def created(data):
    return success(data, 201)


def no_content():
    return "", 204


def error(message, http_status, code, details=None):
    http_texts = {
        400: "Bad Request",
        401: "Unauthorized",
        403: "Forbidden",
        404: "Not Found",
        409: "Conflict",
        422: "Unprocessable Entity",
    }
    body = {
        "error": http_texts.get(http_status, "Error"),
        "message": message,
        "code": code,
    }
    if details:
        body["details"] = details
    return jsonify(body), http_status


def pagination_meta(page, limit, total):
    total_pages = math.ceil(total / limit) if limit else 1
    return {
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": total_pages,
    }


def parse_pagination(args):
    page = int(args.get("page", 1))
    if page < 1:
        page = 1
    limit = int(args.get("limit", 20))
    if limit < 1:
        limit = 1
    if limit > 100:
        limit = 100
    return page, limit


def require_roles(*roles):
    def decorator(fn):
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get("role") not in roles:
                return error("Acceso denegado: rol insuficiente.", 403, 4030)
            return fn(*args, **kwargs)
        wrapper.__name__ = fn.__name__
        return wrapper
    return decorator

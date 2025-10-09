from flask import Blueprint, request, make_response
import requests

proxy_bp = Blueprint('proxy', __name__)

@proxy_bp.route("/proxy/token", methods=["POST", "OPTIONS"])
def proxy_token():
    origin = request.headers.get("Origin") or "*"

    if request.method == "OPTIONS":
        response = make_response()
        response.headers.add("Access-Control-Allow-Origin", origin)
        response.headers.add("Access-Control-Allow-Headers", "Content-Type")
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        response.headers.add("Access-Control-Max-Age", "3600")
        return response, 200

    body_raw = request.get_data()
    
    try:
        response = requests.post(
            "http://161.132.63.145:9001/rest/api/oauth2/v1/token",
            data=body_raw,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

        res = make_response(response.content, response.status_code)
        res.headers["Content-Type"] = response.headers.get("Content-Type", "application/json")
        res.headers.add("Access-Control-Allow-Origin", origin)
        res.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        res.headers.add("Access-Control-Allow-Headers", "Content-Type")
        return res

    except Exception as e:
        res = make_response({"error": str(e)}, 500)
        res.headers.add("Access-Control-Allow-Origin", origin)
        res.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        res.headers.add("Access-Control-Allow-Headers", "Content-Type")
        return res
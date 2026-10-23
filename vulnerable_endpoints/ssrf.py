from flask import Blueprint, request, jsonify
import requests


tools = Blueprint("tools", __name__)

@tools.route("/fetch", methods=['POST'])
def tools_fetch():
    url = request.form.get("url")
    if not url or 'vulnerableapp.com' not in url:
        return jsonify({'status': 'fail'})
    res = requests.get(url)
    return jsonify({'status': 'ok', 'body': res.text})
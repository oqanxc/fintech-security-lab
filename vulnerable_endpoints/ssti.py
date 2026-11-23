from flask import Blueprint, request, render_template_string, jsonify
from markupsafe import escape

ssti_bp = Blueprint("ssti", __name__)

@ssti_bp.route("/ssti/vulnerable", methods=["GET"])
def vulnerable_ssti():
    name = request.args.get("name", "Guest")

    # User input is embedded into the template source.
    template = f"""
    <html>
        <body>
            <h1>Hello {{name}}!</h1>
        </body>
    </html>
    """

    return render_template_string(template,name=name)


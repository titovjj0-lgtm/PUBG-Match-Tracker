import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify, abort
from flask_cors import CORS
import storage
import logic

load_dotenv()
ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN")

app = Flask(__name__)

CORS(app, origins=[
    "https://pubgmatchtracker.pp.ua",
    "https://pubg-match-tracker.netlify.app",
    "http://localhost:8080"
])

storage.init()


def require_admin():
    if "CF-Connecting-IP" in request.headers:
        abort(404)

    if not ADMIN_TOKEN or request.headers.get(
        "X-Admin-Token"
    ) != ADMIN_TOKEN:
        abort(403)


@app.get("/matches")
def list_matches():
    records = storage.load_records()
    result = request.args.get("result")

    if result is not None:
        records = logic.find_records(records, result)

    return jsonify([r.to_dict() for r in records])


@app.post("/matches")
def create_match():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Expected JSON"}), 400

    try:
        record = logic.add_record(
            [],
            data["date"],
            data["result"],
            data["kills"],
            data["duration"],
            data.get("note", "")
        )

        match_id = storage.add_match(record)
        return jsonify({"id": match_id}), 201

    except (ValueError, KeyError, TypeError,
            AttributeError, OverflowError) as error:
        return jsonify({"error": str(error)}), 400


@app.delete("/admin/matches/<int:match_id>")
def delete_match(match_id):
    require_admin()

    if storage.delete_match(match_id):
        return jsonify({"deleted": match_id})

    return jsonify({"error": "Match not found"}), 404


@app.get("/admin/export")
def export_matches():
    require_admin()
    return jsonify([
        r.to_dict() for r in storage.load_records()
    ])


@app.get("/report")
def report():
    return jsonify({
        "statistics": logic.report(storage.load_records()),
        "results": storage.result_report()
    })


@app.get("/admin/log")
def admin_log():
    require_admin()
    limit = request.args.get("limit", 50, type=int)
    return jsonify(storage.get_log(max(1, min(limit, 500))))


if __name__ == "__main__":
    app.run(debug=True)

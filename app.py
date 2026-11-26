import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS

import storage
import logic
import user_storage
from auth import auth, current_user, require_admin

load_dotenv()

app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]
app.config["SESSION_COOKIE_SECURE"] = True
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

CORS(
    app,
    origins=["https://pubgmatchtracker.pp.ua"],
    supports_credentials=True
)

app.register_blueprint(auth)
storage.init()


@app.get("/matches")
def list_matches():
    user = current_user()
    records = user_storage.load_records(user["id"])
    result = request.args.get("result")

    if result is not None:
        records = logic.find_records(records, result)

    return jsonify([r.to_dict() for r in records])


@app.post("/matches")
def create_match():
    user = current_user()
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

        match_id = user_storage.add_match(
            record, user["id"]
        )

        return jsonify({"id": match_id}), 201

    except (ValueError, KeyError, TypeError,
            AttributeError, OverflowError) as error:
        return jsonify({"error": str(error)}), 400


@app.delete("/matches/<int:match_id>")
def delete_match(match_id):
    user = current_user()

    if user_storage.delete_match(match_id, user["id"]):
        return jsonify({"deleted": match_id})

    return jsonify({"error": "Match not found"}), 404


@app.get("/report")
def report():
    user = current_user()

    return jsonify({
        "statistics": logic.report(
            user_storage.load_records(user["id"])
        ),
        "results": user_storage.result_report(user["id"])
    })


@app.get("/admin/export")
def export_matches():
    require_admin()
    return jsonify([
        r.to_dict() for r in storage.load_records()
    ])


@app.delete("/admin/matches/<int:match_id>")
def admin_delete(match_id):
    require_admin()

    if storage.delete_match(match_id):
        return jsonify({"deleted": match_id})

    return jsonify({"error": "Match not found"}), 404


@app.get("/admin/log")
def admin_log():
    require_admin()
    limit = request.args.get("limit", 50, type=int)
    return jsonify(
        storage.get_log(max(1, min(limit, 500)))
    )



@app.post("/admin/import")
def import_matches():
    user = require_admin()
    data = request.get_json(silent=True)

    if not isinstance(data, list):
        return jsonify({"error": "Expected JSON list"}), 400

    records = []

    try:
        for item in data:
            record = logic.add_record(
                [],
                item["date"],
                item["result"],
                item["kills"],
                item["duration"],
                item.get("note", "")
            )
            records.append(record)

    except (ValueError, KeyError, TypeError,
            AttributeError, OverflowError):
        return jsonify({"error": "Invalid match data"}), 400

    from contextlib import closing

    with closing(storage.connect()) as conn, conn:
        for record in records:
            conn.execute("""
                INSERT INTO matches
                (date, result, kills, duration, note, result_id, user_id)
                VALUES (?, ?, ?, ?, ?,
                    (SELECT id FROM results WHERE name = ?), ?)
            """, (
                record.date, record.result, record.kills,
                record.duration, record.note,
                record.result, user["id"]
            ))

    return jsonify({"imported": len(records)}), 201


if __name__ == "__main__":
    app.run(debug=True)

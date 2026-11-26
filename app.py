from flask import Flask, request, jsonify
import storage
import logic
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=[
    "https://pubgmatchtracker.pp.ua",
    "https://pubg-match-tracker.netlify.app",
    "http://localhost:8080"
])
storage.init()


@app.get("/matches")
def list_matches():
    records = storage.load_records()
    result = request.args.get("result")

    if result is not None:
        records = logic.find_records(records, result)

    return jsonify(records)


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

    except (ValueError, KeyError, TypeError) as error:
        return jsonify({"error": str(error)}), 400


@app.delete("/matches/<int:match_id>")
def delete_match(match_id):
    if storage.delete_match(match_id):
        return jsonify({"deleted": match_id})

    return jsonify({"error": "Match not found"}), 404


@app.get("/report")
def match_report():
    return jsonify(logic.report(storage.load_records()))


if __name__ == "__main__":
    app.run(debug=True)

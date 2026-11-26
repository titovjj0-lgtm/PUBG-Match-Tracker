class Match:
    def __init__(self, date, kills, duration, result,
                 note="", match_id=None):
        self.id = match_id
        self.date = date
        self.kills = int(kills)
        self.duration = int(duration)
        self.result = result
        self.note = note

    def to_dict(self):
        return {
            "id": self.id,
            "date": self.date,
            "kills": self.kills,
            "duration": self.duration,
            "result": self.result,
            "note": self.note
        }

    @staticmethod
    def from_row(row):
        return Match(
            row["date"],
            row["kills"],
            row["duration"],
            row["result"],
            row["note"],
            row["id"]
        )

    def is_win(self):
        return self.result == "win"
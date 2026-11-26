import storage
from contextlib import closing

with closing(storage.connect()) as conn, conn:
    conn.executescript("""
        DROP TRIGGER IF EXISTS audit_add;
        DROP TRIGGER IF EXISTS audit_delete;

        CREATE TRIGGER audit_add
        AFTER INSERT ON matches
        BEGIN
            INSERT INTO audit_log(action, item_id, user_id)
            VALUES ('add', NEW.id, NEW.user_id);
        END;

        CREATE TRIGGER audit_delete
        AFTER DELETE ON matches
        BEGIN
            INSERT INTO audit_log(action, item_id, user_id)
            VALUES ('delete', OLD.id, OLD.user_id);
        END;
    """)

print("AUDIT UPDATED")

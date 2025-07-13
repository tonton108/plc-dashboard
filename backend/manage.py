import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app import create_app, db, periodic_log_fetch, wait_for_db
import threading

app = create_app()

def runserver():
    with app.app_context():
        wait_for_db(db.session)
        threading.Thread(target=periodic_log_fetch, daemon=True).start()
        app.run(debug=True, host="0.0.0.0")

if __name__ == '__main__':
    runserver()

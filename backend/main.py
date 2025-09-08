from flask import Flask
from application.config import Config
from flask_cors import CORS
from application.extensions import db
from flask_restful import Api

app, api = None, None

def create_app(for_test=False):
    """
    Create Flask app with database, CORS, and REST API.
    """
    app = Flask(__name__)
    app.config.from_object(Config)

    # Enable CORS for frontend (Vue3)
    CORS(app)
    api = Api(app)
    # Initialize extensions
    db.init_app(app)

    with app.app_context():
        from application.models import User
        db.create_all()

    return app, api

app, api = create_app()

from application.resources import DummyApi, ScheduleBreaks, CalendarEvents, AutoSchedule

api.add_resource(DummyApi, '/api/testingApi')
api.add_resource(ScheduleBreaks, "/api/schedule-breaks")
api.add_resource(CalendarEvents, "/api/calendar/events")
api.add_resource(AutoSchedule, "/api/auto-schedule/events")

# ✅ Add a simple root route for Render
@app.route("/", methods=["GET"])
def home():
    return {"message": "Backend is running 🚀"}

# Start dev server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
from flask_restful import Resource
from .extensions import db
from descope import DescopeClient
import requests
from flask import Flask, request, jsonify
import os
import datetime

from dotenv import load_dotenv
load_dotenv()

class DummyApi(Resource):
    def get(self):
        # Returning hardcoded data
        return {
            "status": "success",
            "message": "Dummy API is working!",
            "data": {
                "id": 101,
                "name": "Test User",
                "role": "Developer",
                "skills": ["Python", "Flask", "Vue3"]
            }
        }, 200


# Core Descope client for session validation
client = DescopeClient(
    project_id=os.getenv("DESCOPE_PROJECT_ID"),
    management_key=os.getenv("DESCOPE_MANAGEMENT_KEY")
)

class ScheduleBreaks(Resource):
    def post(self):
        data = request.get_json()
        user_id = data.get("user_id")
        session_jwt = data.get("session_jwt")

        if not user_id or not session_jwt:
            return {"error": "Missing user_id or session_jwt"}, 400

        # 1. Validate session
        try:
            client.validate_session(session_jwt)
        except Exception as e:
            return {"error": "Invalid session", "details": str(e)}, 401

        # 2. Fetch Google OAuth token via mgmt.outbound_application
        try:
            token_response = client.mgmt.outbound_application.fetch_token(
                "google-calendar",  # replace with your Outbound App ID
                user_id,
                None,
                {"forceRefresh": False}
            )
            # print("🔑 Full token response:", token_response)
            google_token = token_response["token"]["accessToken"]
        except Exception as e:
            return {"error": f"Failed to get Google token: {str(e)}"}, 500

        # 3. Insert event into Google Calendar
        event = {
            "summary": "Wellness Break 🧘",
            "start": {"dateTime": "2025-09-05T18:00:00+05:30"},
            "end": {"dateTime": "2025-09-05T18:15:00+05:30"}
        }
        headers = {"Authorization": f"Bearer {google_token}"}
        response = requests.post(
            "https://www.googleapis.com/calendar/v3/calendars/primary/events",
            headers=headers,
            json=event
        )

        return response.json(), response.status_code
    


# this will give the events schedule in calander

class CalendarEvents(Resource):
    def post(self):
        try:
            data = request.get_json()
            user_id = data.get("user_id")
            session_jwt = data.get("session_jwt")

            print(session_jwt)

            if not session_jwt:
                return {"error": "Missing session_jwt"}, 400

            try:
                token_response = client.mgmt.outbound_application.fetch_token(
                    "google-calendar",  # replace with your Outbound App ID
                    user_id,
                    None,
                    {"forceRefresh": False}
                )
                # print("🔑 Full token response:", token_response)
                google_token = token_response["token"]["accessToken"]
            except Exception as e:
                return {"error": f"Failed to get Google token: {str(e)}"}, 500
        

            # ✅ Fetch events from Google Calendar API
            now = datetime.datetime.utcnow().isoformat() + "Z"
            tomorrow = (datetime.datetime.utcnow() + datetime.timedelta(days=1)).isoformat() + "Z"

            resp = requests.get(
                "https://www.googleapis.com/calendar/v3/calendars/primary/events",
                headers={"Authorization": f"Bearer {google_token}"},
                params={
                    "timeMin": now,
                    "timeMax": tomorrow,
                    "singleEvents": True,
                    "orderBy": "startTime"
                }
            )

            if resp.status_code != 200:
                return {"error": "Failed to fetch Google events", "details": resp.text}, resp.status_code

            events = resp.json().get("items", [])

            print(events)
            return {"events": events}, 200

        except Exception as e:
            return {"error": str(e)}, 500
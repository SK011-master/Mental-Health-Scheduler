from flask_restful import Resource
from .extensions import db
from descope import DescopeClient
import requests
from flask import Flask, request, jsonify
import os
import datetime, time
import pytz

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
            "start": {"dateTime": "2025-09-06T21:00:00+05:30"},
            "end": {"dateTime": "2025-09-06T21:15:00+05:30"}
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

            return {"events": events}, 200

        except Exception as e:
            return {"error": str(e)}, 500
        

# ----------------------------------------------------------------------------------------------------------------
# this api is for auto schedule events 
# -----------------------------------------------------------------------------------------------------------------

import datetime

# this function is formating events data in proper formate
def extract_event_info(events):
    cleaned = []
    for e in events:
        cleaned.append({
            "id": e.get("id"),
            "title": e.get("summary", "No Title"),
            "start": e.get("start", {}).get("dateTime"),
            "end": e.get("end", {}).get("dateTime"),
            "link": e.get("htmlLink")
        })
    return cleaned

# this function is finding free slots
def find_free_slots(events, rules):
    today = datetime.date.today()

    # Detect local timezone (e.g., Asia/Kolkata)
    local_tz = datetime.datetime.now().astimezone().tzinfo
    now = datetime.datetime.now(local_tz) 

    # Define working hours
    working_start = datetime.datetime.combine(
        today,
        datetime.time.fromisoformat(rules["working_hours"]["start"])
    ).replace(tzinfo=local_tz)

    working_end = datetime.datetime.combine(
        today,
        datetime.time.fromisoformat(rules["working_hours"]["end"])
    ).replace(tzinfo=local_tz)

    # If current time is within working hours, shift start
    if working_start < now < working_end:
        working_start = now

    # Extract busy times
    busy_times = []
    for e in events:
        try:
            start = datetime.datetime.fromisoformat(e["start"])
            end = datetime.datetime.fromisoformat(e["end"])
            busy_times.append((start, end))
        except Exception as ex:
            print(f"⚠️ Skipping malformed event: {e}, error: {ex}")
            continue

    busy_times.sort(key=lambda x: x[0])

    free_slots = []
    last_end = working_start

    for start, end in busy_times:
        if last_end.tzinfo != start.tzinfo:
            last_end = last_end.astimezone(start.tzinfo)

        gap = (start - last_end).total_seconds() / 60
        if gap >= rules["break_duration"] + rules["min_gap"]:
            free_slots.append((last_end, start))
        last_end = max(last_end, end)

    # Final slot after last meeting
    if (working_end - last_end).total_seconds() / 60 >= rules["break_duration"]:
        free_slots.append((last_end, working_end))

    formatted_slots = [
        {
            "start_iso": s.isoformat(),
            "end_iso": e.isoformat(),
            "start_readable": s.strftime("%I:%M %p"),
            "end_readable": e.strftime("%I:%M %p")
        }
        for s, e in free_slots
    ]

    return formatted_slots


# this is main autoschedular class
class AutoSchedule(Resource):
    def post(self):
        try:
            data = request.get_json()
            user_id = data.get("user_id")
            events = data.get("events")

            formated_events = extract_event_info(events)

            RULES = {
                "working_hours": {"start": "09:00", "end": "20:00"},
                "break_duration": 30,
                "min_gap": 15,
                "max_breaks_per_day": 3,
            }

            free_slots = find_free_slots(formated_events, RULES)

            # Convert datetime objects to strings for JSON
            formatted_slots = [
                {"start": s["start_iso"], "end": s["end_iso"]}
                for s in free_slots
            ]

            return {"free_slots": formatted_slots}, 200

        except Exception as e:
            return {"error": str(e)}, 500
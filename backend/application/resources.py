from flask_restful import Resource
from .extensions import db
from descope import DescopeClient
import requests
from flask import Flask, request, jsonify
import os
import datetime, time
from datetime import datetime, timedelta
import pytz
from zoneinfo import ZoneInfo
from dateutil import parser

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
        title = data.get("title", "Wellness Break 🧘")   
        start_time = data.get("start_time")  
        duration = data.get("duration", 15) 


        if not user_id or not session_jwt:
            return {"error": "Missing user_id or session_jwt"}, 400

        # 1. Validate session
        try:
            client.validate_session(session_jwt)
        except Exception as e:
            return {"error": "Invalid session", "details": str(e)}, 401

        try:
            token_response = client.mgmt.outbound_application.fetch_token(
                "google-calendar",  # Your Outbound App ID in Descope
                user_id,
                None,
                {"forceRefresh": False}
            )
            google_token = token_response["token"]["accessToken"]
        except Exception as e:
            return {"error": f"Failed to get Google token: {str(e)}"}, 500

        # 3. Build Google Calendar Event
        try:
            # Parse start_time (e.g., "2025-09-09T12:30")
            start = parser.isoparse(start_time)

            # Attach IST timezone if none provided
            if start.tzinfo is None:
                ist = pytz.timezone("Asia/Kolkata")
                start = ist.localize(start)

            # Calculate end time
            end = start + timedelta(minutes=int(duration))

            event = {
                "summary": title,
                "start": {"dateTime": start.isoformat()},  # 👈 preserves timezone if present
                "end": {"dateTime": end.isoformat()},
            }

            print(event)
        except Exception as e:
            return {"error": f"Invalid date format: {str(e)}"}, 400

        # 4. Call Google Calendar API
        headers = {"Authorization": f"Bearer {google_token}"}
        response = requests.post(
            "https://www.googleapis.com/calendar/v3/calendars/primary/events",
            headers=headers,
            json=event
        )

        if response.status_code not in [200, 201]:
            return {
                "error": "Failed to insert event in Google Calendar",
                "details": response.text
            }, response.status_code

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
        

            # Fetch events from Google Calendar API
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


# this is the function it will find the break slots from free slots 
def schedule_breaks(free_slots, rules):
    break_duration = datetime.timedelta(minutes=rules["break_duration"])
    max_breaks = rules["max_breaks_per_day"]
    min_spacing = datetime.timedelta(hours=2)  

    today = datetime.date.today()
    local_tz = datetime.datetime.now().astimezone().tzinfo

    working_start = datetime.datetime.combine(
        today, datetime.time.fromisoformat(rules["working_hours"]["start"])
    ).replace(tzinfo=local_tz)

    working_end = datetime.datetime.combine(
        today, datetime.time.fromisoformat(rules["working_hours"]["end"])
    ).replace(tzinfo=local_tz)

    scheduled = []

    # divide working hours into segments
    total_working = (working_end - working_start).total_seconds()
    segment = total_working / (max_breaks + 1)

    # target times (spaced out evenly)
    target_times = [
        working_start + datetime.timedelta(seconds=segment * (i + 1))
        for i in range(max_breaks)
    ]

    for target in target_times:
        best_slot = None
        best_diff = None

        for slot in free_slots:
            slot_start = datetime.datetime.fromisoformat(slot["start_iso"])
            slot_end = datetime.datetime.fromisoformat(slot["end_iso"])

            # check if target fits directly
            if slot_start <= target <= slot_end - break_duration:
                diff = abs((slot_start - target).total_seconds())
                if best_diff is None or diff < best_diff:
                    best_slot = target
                    best_diff = diff
            else:
                # fallback: align with slot start
                if slot_start + break_duration <= slot_end:
                    diff = abs((slot_start - target).total_seconds())
                    if best_diff is None or diff < best_diff:
                        best_slot = slot_start
                        best_diff = diff

        if best_slot:
            # check spacing rule
            too_close = any(
                abs((datetime.datetime.fromisoformat(b["start_iso"]) - best_slot).total_seconds()) < min_spacing.total_seconds()
                for b in scheduled
            )
            if not too_close:
                scheduled.append({
                    "start_iso": best_slot.isoformat(),
                    "end_iso": (best_slot + break_duration).isoformat(),
                    "start_readable": best_slot.strftime("%I:%M %p"),
                    "end_readable": (best_slot + break_duration).strftime("%I:%M %p")
                })

    return scheduled

# this function is finding free slots
def find_free_slots(events, rules, tz_name="Asia/Kolkata"):
    tz = ZoneInfo(tz_name)

    # now in the chosen timezone
    now = datetime.datetime.now(tz)
    today = now.date()

    # Build working hours in the SAME timezone (explicit)
    working_start = datetime.datetime.combine(
        today,
        datetime.time.fromisoformat(rules["working_hours"]["start"]),
        tzinfo=tz
    )
    working_end = datetime.datetime.combine(
        today,
        datetime.time.fromisoformat(rules["working_hours"]["end"]),
        tzinfo=tz
    )

    # If current time is inside working hours → shift start to now
    if working_start < now < working_end:
        working_start = now

    # If current time is past working hours → no free slots
    if now >= working_end:
        return []

    # Build busy intervals clipped to working hours
    busy_times = []
    for e in events:
        try:
            start = datetime.datetime.fromisoformat(e["start"])
            end = datetime.datetime.fromisoformat(e["end"])
        except Exception as ex:
            print("Skipping malformed event:", e, ex)
            continue

        # Ensure event datetimes are timezone-aware; if not, assume tz
        if start.tzinfo is None:
            start = start.replace(tzinfo=tz)
        else:
            # convert event into our chosen zone for consistent comparison
            start = start.astimezone(tz)

        if end.tzinfo is None:
            end = end.replace(tzinfo=tz)
        else:
            end = end.astimezone(tz)

        # clip to working hours and ignore outside intervals
        if end <= working_start or start >= working_end:
            continue
        start = max(start, working_start)
        end = min(end, working_end)

        busy_times.append((start, end))

    busy_times.sort(key=lambda x: x[0])

    # Build free slots from now..working_end excluding busy intervals
    free_slots = []
    last_end = working_start

    for start, end in busy_times:
        # last_end and start are same tz (both tz)
        gap_minutes = (start - last_end).total_seconds() / 60
        if gap_minutes >= (rules["break_duration"] + rules["min_gap"]):
            free_slots.append((last_end, start))
        last_end = max(last_end, end)

    # final gap
    if (working_end - last_end).total_seconds() / 60 >= rules["break_duration"]:
        free_slots.append((last_end, working_end))

    # Format output (ISO + readable)
    formatted = [
        {
            "start_iso": s.isoformat(),
            "end_iso": e.isoformat(),
            "start_readable": s.strftime("%I:%M %p"),
            "end_readable": e.strftime("%I:%M %p")
        }
        for s, e in free_slots
    ]

    return schedule_breaks(formatted, rules)


# this is the function which will automatically add breaks in calander, after getting free time

def insert_breaks_to_calendar(breaks, user_id, session_jwt):
    """
    Insert scheduled breaks into the user's Google Calendar using Descope Outbound App.
    Removes duplicates before inserting + skips breaks that already exist in calendar.
    """

    # Deduplicate locally first
    seen = set()
    unique_breaks = []
    for br in breaks:
        key = (br["start_iso"], br["end_iso"])
        if key not in seen:
            seen.add(key)
            unique_breaks.append(br)

    # 1. Validate session
    try:
        client.validate_session(session_jwt)
    except Exception as e:
        return {"error": "Invalid session", "details": str(e)}

    # 2. Fetch Google OAuth token
    try:
        token_response = client.mgmt.outbound_application.fetch_token(
            "google-calendar",  # your outbound app ID
            user_id,
            None,
            {"forceRefresh": False}
        )
        google_token = token_response["token"]["accessToken"]
    except Exception as e:
        return {"error": f"Failed to get Google token: {str(e)}"}

    headers = {"Authorization": f"Bearer {google_token}"}

    # 3. Fetch existing events today to avoid duplicates
    today = datetime.date.today().isoformat()
    events_url = (
        f"https://www.googleapis.com/calendar/v3/calendars/primary/events?"
        f"timeMin={today}T00:00:00Z&timeMax={today}T23:59:59Z"
    )
    existing_events = requests.get(events_url, headers=headers).json().get("items", [])
    existing_times = {
        (e["start"].get("dateTime"), e["end"].get("dateTime"))
        for e in existing_events
        if "start" in e and "end" in e
    }

    created_events = []

    # 4. Insert each break only if not already present
    for br in unique_breaks:
        if (br["start_iso"], br["end_iso"]) in existing_times:
            continue  # skip duplicate in Google Calendar

        event = {
            "summary": "Wellness Break 🧘",
            "start": {"dateTime": br["start_iso"], "timeZone": "Asia/Kolkata"},
            "end": {"dateTime": br["end_iso"], "timeZone": "Asia/Kolkata"},
        }

        try:
            response = requests.post(
                "https://www.googleapis.com/calendar/v3/calendars/primary/events",
                headers=headers,
                json=event
            )
            response.raise_for_status()
            created_events.append(response.json())
        except Exception as e:
            created_events.append({"error": str(e), "event": event})

    return {"created_breaks": created_events}


# ******************************************************************************************************************************************************************************************************************
# ----------------------------------------------------------------------------------------------------- This feature is mainly for students -------------------------------------------------------------------------
# --------------------------------------------------------------------------------- Auto Scheduling time brakes inside study time ----------------------------------------------------------------------------------- 
# ******************************************************************************************************************************************************************************************************************

def schedule_break_event(user_id, session_jwt, title, start_time, duration=10):
    """Wrapper that calls Google Calendar API like ScheduleBreaks class"""
    try:
        client.validate_session(session_jwt)

        token_response = client.mgmt.outbound_application.fetch_token(
            "google-calendar",  # outbound app id
            user_id,
            None,
            {"forceRefresh": False}
        )
        google_token = token_response["token"]["accessToken"]

        start = parser.isoparse(start_time)
        if start.tzinfo is None:
            ist = pytz.timezone("Asia/Kolkata")
            start = ist.localize(start)
        end = start + timedelta(minutes=duration)

        event = {
            "summary": title,
            "start": {"dateTime": start.isoformat()},
            "end": {"dateTime": end.isoformat()},
        }

        headers = {"Authorization": f"Bearer {google_token}"}
        response = requests.post(
            "https://www.googleapis.com/calendar/v3/calendars/primary/events",
            headers=headers,
            json=event
        )

        if response.status_code not in [200, 201]:
            return {"error": response.text, "status": response.status_code}
        return response.json()

    except Exception as e:
        return {"error": str(e)}
    


def find_micro_breaks(events, user_id, session_jwt):
    """
    Insert 10-min wellness breaks into long stretches of study time.
    Rule: 
      - If continuous study block >= 1 hr → insert 1 break in the middle.
      - For every additional hour, add another break spaced out.
    """
    ist = pytz.timezone("Asia/Kolkata")
    breaks_to_add = []

    for e in events:
        print(e)
        start = parser.isoparse(e["start"])
        end = parser.isoparse(e["end"])

        # Normalize to IST if no tz info
        if start.tzinfo is None:
            start = ist.localize(start)
        if end.tzinfo is None:
            end = ist.localize(end)

        duration_minutes = int((end - start).total_seconds() / 60)

        if duration_minutes >= 60:
            # number of 10-min breaks = hours in session
            num_breaks = duration_minutes // 60  

            gap = (end - start) / (num_breaks + 1)  # evenly distribute breaks

            for i in range(1, num_breaks + 1):
                break_start = start + gap * i
                breaks_to_add.append({
                    "title": "Mindful 10-min Break 🧘",
                    "start_time": break_start.isoformat(),
                    "duration": 10,
                })

    # Now actually schedule them in Google Calendar
    results = []
    for b in breaks_to_add:
        result = schedule_break_event(user_id, session_jwt, b["title"], b["start_time"], b["duration"])
        results.append(result)

    return results

# this is main autoschedular class
class AutoSchedule(Resource):
    def post(self):
        try:
            data = request.get_json()
            user_id = data.get("user_id")
            events = data.get("events")
            session_jwt = data.get("session_jwt")

            formated_events = extract_event_info(events)

            #  Check if breaks already exist
            if any(e.get("title") in ["Wellness Break 🧘", "Mindful 10-min Break 🧘"]
                    for e in formated_events
                ):
                    return {"message": "Breaks already scheduled for today"}, 200

            RULES = {
                "working_hours": {"start": "01:00", "end": "23:59"},
                "break_duration": 30,
                "min_gap": 15,
                "max_breaks_per_day": 6,
            }

            free_slots = find_free_slots(formated_events, RULES)

            # this will find the free time and schedule the wellness brakes btw the working hours you can make working hours to (9 to 5 above in RULES)
            add_brakes = insert_breaks_to_calendar(free_slots, user_id, session_jwt)

            # Add 10-min micro breaks between long sessions
            find_micro_breaks(formated_events, user_id, session_jwt)

            return {"free_slots": add_brakes}, 200

        except Exception as e:
            return {"error": str(e)}, 500
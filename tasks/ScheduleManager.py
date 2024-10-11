"""
    SCHEDULE MANAGER MODULE
"""
# File:            || ScheduleManager.py ||
# Description:     || Module for managing my calendar and tutoring schedule ||

import pytz
from datetime import datetime, timedelta
from apis.GoogleCalendar.GoogleCalendar import GoogleCalendar



#CLASS: TimeSlot
#Description: Represents a time slot with bounds, duration, and day of the week
#Usage: Used to represent a tutoring slot, block or availability
class TimeSlot:
    def __init__(self, start_time: datetime, end_time: datetime, country: str = None, tz = None):
        self.bounds = [start_time, end_time]
        self.duration = (end_time - start_time).total_seconds() / 3600
        self.day = start_time.weekday()

        # TZ Information
        if isinstance(tz, str):
            tz = pytz.timezone(tz)

        if (tz is None) and (country is not None):
            tz = pytz.timezone(country)
        elif (country is None) and (tz is not None):
            country = tz.zone
        elif (country is None) and (tz is None):
            raise ValueError("Either country or tz must be provided")

        self.tz = tz
        self.country = country



#CLASS: Calendar
#Description: Class used to interface directly with google calendar
class Calendar:
    def __init__(self):
        self.calendar = GoogleCalendar()
        self.api = self.calendar.service
        self.events = self.api.events()

        self.calendar_ids = {
            "primary": "primary",
            "tutoring": "d19b432f0375a87893674ff823e2665114823e56d518cb9935466e96bc73d4fd@group.calendar.google.com",
            "tutoring_blocks": "f45a65b26fe059d3ba2bc648e53371073ba8aa4ac5d1e4ae0c25733a41e95514@group.calendar.google.com",
            "speaker_events": "lu0cp35b8uhep1oj73n0btvrd4@group.calendar.google.com",
            "social_stuff": "sdvuhlic8ihfms2e1s0oj2oetk@group.calendar.google.com",
            "personal_development": "4uict4q50m3etpmqju8ll77jrk@group.calendar.google.com",
            "ORS": "2453c5cbfe0eab526fa719027aede6fb97dc6949ac8c7773ff6fed11925afca0@group.calendar.google.com",
            "life_admin": "72faed1aeddefac112855e6adb89384de701b19ddea14c1e041add7c131dfeb7@group.calendar.google.com",
            "entrepreneurship": "0023401992b8b0b313644b7ec438eaf5f71f60b6894abc07788a4e3d2c6aa15a@group.calendar.google.com",
            "careers": "lk8sjb10u7f67s5a6vkfr6id9g@group.calendar.google.com",
        }


    # Utility methods
    def event_to_timeslot(self, event: dict) -> TimeSlot:
        """Converts a google calendar event to a TimeSlot

        Args:
            event (dict): Google calendar event

        Returns:
            TimeSlot: TimeSlot representation of the event
        """

        start = datetime.fromisoformat(event["start"]["dateTime"])
        end = datetime.fromisoformat(event["end"]["dateTime"])
        tz = event["start"]["timeZone"]

        return TimeSlot(start, end, tz=tz)



    def get_availability(self) -> list[TimeSlot]:
        """Retrieves tutoring availability

        Returns:
            list[TimeSlot]: List of available time slots for tutoring
        """
        # get tutoring slots
        tutoring_slots = self.get_tutoring_slots()
        

        # get list of other commitments within each tutoring slot
        calendars_to_search = [{"id": calendar} for calendar in self.calendar_ids.values()] # format list of calendars to search

        # use freebusy api to get list of availability for each tutoring slot
        freebusy = self.api.freebusy()
        available_slots = []

        for slot in tutoring_slots:
            #format time as RFC3339
            time_min = slot.bounds[0].astimezone(slot.tz).isoformat()
            time_max = slot.bounds[1].astimezone(slot.tz).isoformat()
        
            request_body = { # create request body
                "timeMin": time_min,
                "timeMax": time_max,
                "items": calendars_to_search,
                "timeZone": str(slot.tz)
            }

            try:
                result = freebusy.query(body=request_body).execute()
                print(result)

            except Exception as e:
                print(e)



    

    
    def get_tutoring_slots(self) -> list[TimeSlot]:
        """Retrieves tutoring slots for the upcoming week

        Returns:
            list[TimeSlot]: List of tutoring slots for the upcoming week
        """

        # Find date bounds for the next week
        today = datetime.now().date()
        sunday = today - timedelta(days=(today.weekday()+1))
        week_start = sunday + timedelta(days=7) #next week start
        week_end = week_start + timedelta(days=7) #next week end

        time_min = week_start.isoformat() + "T00:00:00Z"
        time_max = week_end.isoformat() + "T00:00:00Z"


        # Get tutoring slots for the upcoming week (starting on Sunday)
        slots_list = self.events.list(
            calendarId=self.calendar_ids["tutoring_blocks"], 
            timeMin=time_min, 
            timeMax=time_max, 
            singleEvents=True, 
            orderBy='startTime'
        ).execute()

        # Parse slots
        slots = []
        for slot in slots_list["items"]:
            slots.append(self.event_to_timeslot(slot))

        return slots



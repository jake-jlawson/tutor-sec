"""
    SCHEDULE MANAGER MODULE
"""
# File:            || ScheduleManager.py ||
# Description:     || Module for managing my calendar and tutoring schedule ||

import pytz
from datetime import datetime, timedelta
from apis.GoogleCalendar.GoogleCalendar import GoogleCalendar
from apis.OpenAI.GPT import GPT



#CLASS: TimeSlot
#Description: Represents a time slot with bounds, duration, and day of the week
#Usage: Used to represent a tutoring slot, block or availability
class TimeSlot:
    def __init__(self, start_time: datetime, end_time: datetime, country: str = None, tz = None):
        self.bounds = [start_time, end_time]
        self.duration = (end_time - start_time).total_seconds() / 3600

        # Convert to Sunday-based weekday (0 = Sunday, 6 = Saturday)
        self.day = self.bounds[0].strftime("%A")


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


    def change_tz(self, tz: pytz.timezone):
        self.tz = tz
        self.country = tz.zone

        #change bounds
        self.bounds[0] = self.bounds[0].astimezone(tz)
        self.bounds[1] = self.bounds[1].astimezone(tz)



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


    # UTILITY METHODS
    def event_to_timeslot(self, event: dict, tz = None) -> TimeSlot:
        """Converts a google calendar event to a TimeSlot

        Args:
            event (dict): Google calendar event

        Returns:
            TimeSlot: TimeSlot representation of the event
        """

        start = datetime.fromisoformat(event["start"]["dateTime"])
        end = datetime.fromisoformat(event["end"]["dateTime"])

        if (tz is None):
            if "timeZone" in event["start"]:
                tz = event["start"]["timeZone"]
            else:
                raise ValueError("No timezone provided")
            
        else:
            #if string is provided, convert to pytz timezone object
            if isinstance(tz, str):
                tz = pytz.timezone(tz)
            elif isinstance(tz, pytz.timezone):
                tz = tz
            else:
                raise ValueError("Invalid timezone provided")

        return TimeSlot(start, end, tz=tz)


    # MAIN METHODS
    def get_availability(self) -> list[TimeSlot]:
        """Retrieves tutoring availability

        Returns:
            list[TimeSlot]: List of available time slots for tutoring
        """
        # get tutoring slots
        tutoring_slots = self.get_tutoring_slots()
        

        # get list of other commitments (BUSY SLOTS) within each tutoring slot
        calendars_to_search = [{"id": calendar} for calendar in self.calendar_ids.values()] # format list of calendars to search
        calendars_to_search.remove({"id": self.calendar_ids["tutoring_blocks"]}) #remove tutoring blocks calendar from list
        
        freebusy = self.api.freebusy() # use freebusy api to get list of availability for each tutoring slot

        blocked_time = [] #array to collect tutoring slots and blocked time
        for slot in tutoring_slots:
            #format time as RFC3339
            time_min = slot.bounds[0].astimezone(slot.tz).isoformat()
            time_max = slot.bounds[1].astimezone(slot.tz).isoformat()

            try:
                result = freebusy.query(body={
                    "timeMin": time_min,
                    "timeMax": time_max,
                    "items": calendars_to_search,
                    "timeZone": str(slot.tz)
                }).execute()

            except Exception as e:
                print(e)

            busy_slots = collect_busy_periods(result, slot.tz) #array of busy slots
            blocked_time.append([slot, busy_slots])


        # remove busy slots from tutoring slots
        available_slots = []
        for slot, busy_slots in blocked_time:
            available_slots.extend(resolve_time_conflicts(slot, busy_slots))


        # filter out slots that are less than 1 hour
        available_slots = [slot for slot in available_slots if slot.duration >= 1]


        return available_slots


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



#Scheduling Utility Functions
def collect_busy_periods(result: dict, timezone: pytz.timezone) -> list[TimeSlot]:
    """Collects busy periods from a freebusy query result and converts them into TimeSlots

    Args:
        result (dict): Result from a freebusy query

    Returns:
        list[TimeSlot]: List of busy time slots
    """

    busy_slots = []

    for calendar_id, calendar_data in result.get("calendars", {}).items():
        for busy_period in calendar_data.get("busy", []):
            start_time = datetime.fromisoformat(busy_period["start"])
            end_time = datetime.fromisoformat(busy_period["end"])
            busy_slots.append(TimeSlot(start_time=start_time, end_time=end_time, tz=timezone))
    
    return busy_slots


def resolve_time_conflicts(time_window: TimeSlot, blocked_time: list[TimeSlot]) -> list[TimeSlot]:
    """Accepts a time window and uses a list of blocked time slots to calculate the available time slots within that window
    """
    available_slots = []
    current_start = time_window.bounds[0]

    # Sort blocked_time to ensure we process them in order
    blocked_time.sort(key=lambda x: x.bounds[0])

    for block in blocked_time:
        if block.bounds[0] > current_start and block.bounds[0] < time_window.bounds[1]:
            # There's an available slot before this blocked time
            available_slots.append(TimeSlot(start_time=current_start, end_time=block.bounds[0], tz=time_window.tz))
        
        # Move the current start time to the end of this blocked period
        current_start = max(current_start, block.bounds[1])

        # If we've moved past the end of our time window, we're done
        if current_start >= time_window.bounds[1]:
            break

    # If there's still time left after the last blocked period, add it
    if current_start < time_window.bounds[1]:
        available_slots.append(TimeSlot(start_time=current_start, end_time=time_window.bounds[1], tz=time_window.tz))

    return available_slots


def availability_from_text(input_text: str):
    """Uses GPT to evaluate a string of text and extract the user's availability
    """

    prompt = """
        You are an expert at analyzing text and extracting information.
        You will be given text representing a tutoring job listing from a client.
        Your task is to extract and summarise any information contained in this listing that discusses the client's availability.
        Things you could identify:
        - The number of sessions per week
        - Days of the week that the user is available
        - Times during these days that the user is available
        - Location of the client (timezone) 

        If none of the information above is found within the text, return "No availability found"
    """

    new_gpt = GPT(model="gpt-4o-mini")

    completion = new_gpt.chat_completion(messages=[
        {
                "role": "system", 
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    }

                ]
            },
            {
                "role": "user", 
                "content": [
                    {
                        "type": "text",
                        "text": input_text
                    }
                ]
            }
    ])

    return completion.choices[0].message.content





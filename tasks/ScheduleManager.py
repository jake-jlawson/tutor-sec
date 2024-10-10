"""
    SCHEDULE MANAGER MODULE
"""
# File:            || ScheduleManager.py ||
# Description:     || Module for managing my calendar and tutoring schedule ||

from datetime import datetime, timedelta
from apis.GoogleCalendar.GoogleCalendar import GoogleCalendar


class Availability:
    def __init__(self, start_time: datetime, end_time: datetime, country: str):
        self.bounds = [start_time, end_time]
        self.duration = (end_time - start_time).total_seconds() / 3600
        self.country = country


#CLASS: Calendar
#Description: Class used to interface directly with google calendar
class Calendar:
    def __init__(self):
        _calendar = GoogleCalendar()
        self.api = _calendar.service

    def get_availability(self) -> list[Availability]:
        """Retrieves tutoring availability

        Returns:
            list[Availability]: List of available time slots for tutoring
        """

        # Get tutoring slots for the upcoming week (starting on Sunday)
        today = datetime.now().date()
        sunday = today - timedelta(days=today.weekday())
        week_start = sunday + timedelta(days=7)

        print(week_start)

        
        
        
        pass



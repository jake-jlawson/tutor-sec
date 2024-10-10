"""
    SCHEDULE MANAGER MODULE
"""
# File:            || ScheduleManager.py ||
# Description:     || Module for managing my calendar and tutoring schedule ||

import datetime
from apis.GoogleCalendar.GoogleCalendar import GoogleCalendar


class Availability:
    def __init__(self, start_time: datetime.datetime, end_time: datetime.datetime, country: str):
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
        
        
        
        pass



"""
    TEXT ANALYSER
"""
# Description:     || Functions for performing text analysis using OpenAI Chat Completion ||


# IMPORTS
from apis.OpenAI.GPT import GPT
from abc import ABC, abstractmethod
from tasks.ScheduleManager import TimeSlot
from pydantic import BaseModel
from datetime import datetime, timedelta
import json
import calendar



# TEXT ANALYSER BASE CLASS
class TextAnalyser(ABC):
    def __init__(self, model: str = "gpt-4o-mini"):
        self.gpt = GPT(model=model)

        self.base_prompt = """
            You are an advanced text analyser function which takes in a string of text and extracts specific information from it.
        """

    @abstractmethod
    def analyse(self, text: str):
        """Abstract method for analysing text
        """
        pass



#CLASS: AVAILABILITY ANALYSER2
# DESCRIPTION: Analyses text and extracts availability information
class AvailabilityData(BaseModel):
    Sunday: list[list[str, str]]
    Monday: list[list[str, str]]
    Tuesday: list[list[str, str]]
    Wednesday: list[list[str, str]]
    Thursday: list[list[str, str]]
    Friday: list[list[str, str]]
    Saturday: list[list[str, str]]

class TimingsData(BaseModel):
    timezone: str | None #timezone of the client
    sessions_per_week: float | None #number of hours per week
    total_hours: float | None #total number of hours the client requires
    availability: AvailabilityData #list of time slots that the client is available


class AvailabilityAnalyser(TextAnalyser):
    # Approximate cost per analysis: $0.0025 (input) + $0.003 (output) = $0.0055

    system_prompt = """
        You will be given a string of text representing a tutoring job listing.
        Your task is to extract the following information from the text:
        - timezone: a string representing the infered timezone of the client.
        - sessions_per_week: a float representing the number of hours per week that the client requires
        - total_hours: a float representing the total number of hours the client requires
        - availability: an object containing pairs of times for each day of the week which represent the start and end dates/times of time blocks where the client is available

        For infering timezones, look at parts of the text that refer to where the student lives, where they are based, where they are currently located, or their exact timezone. Ignore all other locations such as universities/schools they are applying to, etc.
        Make sure to view any locations that appear in the text in context, and ensure that they are definitely referring to the client's location, and not universities/schools they are applying to, or other things.
        If the location given is a valid location but not a timezone (ie. country, city, continent, etc.) return "Europe/London" if the location is "Europe", otherwise return the closest timezone.
        If timezone cannot be determined, return null.
        
        For sessions per week, return only a number (float or integer) representing hours per week. If a range is given (e.g. "2-3"), return the average of this range.
        If no information about this is present, return null.

        For total hours, return only a number (float or integer) representing the total number of hours the client requires. If this is not explicitly stated, but information exists to calculate it, do so.
        If no information about this is present, return null.
        
        For availability, each day should have a list of time blocks, with each time block being a list [start_time, end_time] representing the start and end times of the block respectively.
        The times should be in 24hr format, and in the format of %H:%M:%S.
        If times are discussed vaguely (e.g. "any time after 5pm on weekdays"), return a reasonable estimate of these time blocks (e.g. 17:00-23:00 for each of Monday-Friday).
        Unless stated otherwise, the minimum start time should be 08:00:00 on weekends and 15:00:00 on weekdays, and the maximum end time should be 23:00:00.
        If no specific days or times are provided, fill in every day with [min, max].
        If availability is discussed for specific days only, fill in the other days where no availability is specified with empty lists.
    """

    def analyse(self, text: str):
        completion = self.gpt.parse_completion(messages=[
            {"role": "system", "content": self.base_prompt + self.system_prompt},
            {"role": "user", "content": text},
        ], response_format=TimingsData)

        return completion.choices[0].message.content
    

    def get_availabilities(self, text: str) -> list[TimeSlot] | None: #get availabilities as a list of TimeSlot objects

        availability_data = json.loads(self.analyse(text))
        print("availability_data: ", availability_data)

        timezone = availability_data['timezone']
        availabilities = availability_data['availability']


        # Handle case where timezone is unknown
        if (timezone is None) or (timezone == "None") or (timezone == "null"):
            return None


        # convert availabilities to list of TimeSlot objects
        time_slots = []
        for day, times in availabilities.items():

            # get day in terms of the upcoming week
            today = datetime.now().date()
            sunday = today - timedelta(days=(today.weekday()+1))
            week_start = sunday + timedelta(days=7) #next week start

            day_date = week_start + timedelta(days=(list(calendar.day_name).index(day.capitalize()) + 1) % 7)

            # convert time blocks to TimeSlot objects
            for time_block in times:
                start_time = datetime.combine(day_date, datetime.strptime(time_block[0], "%H:%M:%S").time())
                end_time = datetime.combine(day_date, datetime.strptime(time_block[1], "%H:%M:%S").time())

                time_slots.append(TimeSlot(start_time=start_time, end_time=end_time, country=timezone, tz=timezone))


        return time_slots








        

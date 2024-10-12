"""
    TEXT ANALYSIS
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



#CLASS: AVAILABILITY ANALYSER
# DESCRIPTION: Analyses text and extracts availability information
class AvailabilityAnalyser1(TextAnalyser):
    
    system_prompt = """
        You will be given a string of text representing a tutoring job listing.
    """

    def analyse(self, text: str):
        self.text = text

        self.get_tz()
        self.get_sessions_per_week()
        self.get_availability()


    def get_tz(self):
        prompt = """
            Please infer the timezone of the client from the input text. Look at the full text, especially any parts of the text that mention the location of the client, where they are based or their exact timezone.
            If a location (city, country, continent, etc.) is given but not a particular timezone, return the closest timezone.
            The timezone should be in the format of a standard timezone name (e.g. "Europe/London").
            
            If no timezone is specified, return "None".
        """
        
        completion = self.gpt.chat_completion(messages=[
            {"role": "system", "content": self.base_prompt + self.system_prompt + prompt},
            {"role": "user", "content": self.text}
        ])

        print("Timezone: ", completion.choices[0].message.content)


    def get_sessions_per_week(self):
        prompt = """
            Please retrieve the number of sessions per week that the client requires from the input text.
            Return only a number (float or integer) representing hours per week. If a range is given (e.g. "2-3"), return the average of this range.
            If no information about this is present, return "None".
        """

        completion = self.gpt.chat_completion(messages=[
            {"role": "system", "content": self.base_prompt + self.system_prompt + prompt},
            {"role": "user", "content": self.text}
        ])

        print("Sessions per week: ", completion.choices[0].message.content)


    def get_availability(self):
        prompt = """
            Please retrieve the dates/times that the client is available from the input text.
            This should be returned as a list of 2 datetimes (e.g. [start_time, end_time]), in iso format (e.g. 2024-10-12T10:00:00).
            Times returned should be blocks of time, (e.g. if the client is available from 10:00-12:00 and 14:00-16:00, this should be returned as two separate datetimes).
            Times should be exactly as they are in the input text, with no timezone conversions. 
            If times are discussed vaguely (e.g. "any time after 5pm on weekdays"), return an estimate of these time blocks (e.g. 17:00-22:00 for each of Monday-Friday).

            If no information about this is present, return "None".
        """

        completion = self.gpt.chat_completion(messages=[
            {"role": "system", "content": self.base_prompt + self.system_prompt + prompt},
            {"role": "user", "content": self.text}
        ])

        print("Availability: ", completion.choices[0].message.content)



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

        For timezones, make sure to look at the full text and utilize relevant information to infer the correct timezone, especially any parts of the text that mention the location of the client, where they are based or their exact timezone.
        Be careful not to over-infer the timezone. View locations in context. If locations are mentioned in relation to universities they are applying to (e.g. "UK Universities", "Cambridge", "Oxford", etc.), ignore these pieces of information.
        If a location (city, country, continent, etc.) is given but not a particular timezone, return "Europe/London" if the location is Europe, return "America/New_York" if the location is North America, otherwise return the closest timezone.
        If timezone cannot be determined, return null.
        
        For sessions per week, return only a number (float or integer) representing hours per week. If a range is given (e.g. "2-3"), return the average of this range.
        If no information about this is present, return null.

        For total hours, return only a number (float or integer) representing the total number of hours the client requires. If this is not explicitly stated, but information exists to calculate it, do so.
        If no information about this is present, return null.
        
        For availability, each day should have a list of time blocks, with each time block being a list [start_time, end_time] representing the start and end times of the block respectively.
        The times should be in 24hr format, and in the format of %H:%M:%S.
        If times are discussed vaguely (e.g. "any time after 5pm on weekdays"), return a reasonable estimate of these time blocks (e.g. 17:00-23:00 for each of Monday-Friday).
        If not specified otherwise, the minimum start time should be 08:00:00 and the maximum end time should be 23:00:00. 
        If no information about availability on a particular day is present, return an empty list for that day.
        If no information about availability is present at all, assume the client is available all day every day.
    """

    def analyse(self, text: str):
        completion = self.gpt.parse_completion(messages=[
            {"role": "system", "content": self.base_prompt + self.system_prompt},
            {"role": "user", "content": text},
        ], response_format=TimingsData)

        return completion.choices[0].message.content
    

    def get_availabilities(self, text: str) -> list[TimeSlot]: #get availabilities as a list of TimeSlot objects

        availability_data = json.loads(self.analyse(text))
        print("availability_data: ", availability_data)

        timezone = availability_data['timezone']
        availabilities = availability_data['availability']


        # Handle case where timezone is unknown
        if (timezone is None):
            return []


        # convert availabilities to list of TimeSlot objects
        time_slots = []
        for day, times in availabilities.items():

            # get day in terms of the upcoming week
            today = datetime.now().date() + timedelta(days=2)
            sunday = today - timedelta(days=(today.weekday()+1))
            week_start = sunday + timedelta(days=7) #next week start

            day_date = week_start + timedelta(days=(list(calendar.day_name).index(day.capitalize()) + 1) % 7)

            # convert time blocks to TimeSlot objects
            for time_block in times:
                start_time = datetime.combine(day_date, datetime.strptime(time_block[0], "%H:%M:%S").time())
                end_time = datetime.combine(day_date, datetime.strptime(time_block[1], "%H:%M:%S").time())

                time_slots.append(TimeSlot(start_time=start_time, end_time=end_time, country=timezone, tz=timezone))


        return time_slots








        

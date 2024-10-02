"""
    CLIENT APPLICATIONS MODULE
"""
# File:            || ClientApplications.py ||
# Description:     || Module for searching jobs and applying for new clients ||

# IMPORTS
import re
from abc import ABC, abstractmethod



#CLASS: Job
#Description: Class used to store information about a job
class Job:
    def __init__(self, title: str, pay: str, job_text: str, tags: list[str], element: str):
        self.title = title
        self.pay = self.getPay(pay)
        self.job_text = job_text
        self.element = element


    #Description: Extracts the pay from the pay string
    def getPay(self, pay: str):
        # Remove currency symbols and commas
        cleaned_string = re.sub(r'[£$,]', '', pay)
    
        # Extract the first number found (including decimals)
        match = re.search(r'\d+(\.\d+)?', cleaned_string)
        
        if match:
            # Convert the found number to a float
            return float(match.group())
        else:
            # Return None if no number is found
            return None
        

#CLASS: ApplicationGenerator
#Description: Class used to generate applications for jobs via LLMs
class ApplicationGenerator:
    def __init__(self, job: Job):
        self.job = job

    def generate(self):
        pass
            



new_job = Job("Math Tutor", "£40.23 per hour", "Math tutor needed for 1-on-1 sessions", ["Math", "Tutor", "1-on-1"], "element")
print(new_job.pay)
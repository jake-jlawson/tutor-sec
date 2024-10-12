"""
    JOBS MANAGER MODULE
"""
# File:            || JobsManager.py ||
# Description:     || Module for instantiating and managing jobs ||

# IMPORTS
import re
from abc import ABC, abstractmethod
from tasks.ScheduleManager import availability_from_text

from utilities.TextAnalysis import AvailabilityAnalyser


#CLASS: Job
#Description: Class used to store information about a job
class Job:
    def __init__(self, title: str, pay: str, job_text: str, tags: list[str], job_elements: dict[str, any]):
        self.title = self.clean_input(title)
        self.pay = self.getPay(pay)
        self.job_text = self.clean_input(job_text)
        self.tags = tags
        self.elements = job_elements


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
        

    def clean_input(self, input: str):
        #remove outer whitespace and newlines
        return input.strip()




#CLASS: JobFilter
#Description: Abstract class for filtering jobs
class JobFilter(ABC):
    # Check criteria method
    @abstractmethod
    def apply_criteria(self, job: Job):
        pass

    # Filter method
    def run(self, jobs: list[Job]):

        filtered_jobs = []
        
        for job in jobs:
            #remove jobs that don't meet the criteria
            if self.apply_criteria(job):
                filtered_jobs.append(job)

        return filtered_jobs

    

#CLASS: AvailabilityFilter
#Filter jobs by availability
class AvailabilityFilter(JobFilter):
    def apply_criteria(self, job: Job) -> bool:
        """Check availability criteria
        Function evaluates job attributes to ascertain job timings, and then checks these against the user's calendar to see if they fit.

        Args:
            job (Job): The job to check

        Returns:
            bool: True if the job lines up with the user's availability, False otherwise
        """

        input_text = job.title + "\n" + job.job_text #get the job text to evaluate

        # set up the analyser
        analyser = AvailabilityAnalyser(model="gpt-4o")
        availability_data = analyser.analyse(input_text)


        print("Job: ", job.title)
        print("Input text: ", input_text)
        print("Availability text: ", availability_data)

        return True



#CLASS: SubjectFilter
#Filter jobs by subject
class SubjectFilter(JobFilter):
    
    #job keywords to look for
    # any jobs containing these words will be filtered in unless they also contain an exclude keyword
    include_keywords = [ 
        "Math",
        "Physics",
        "ENGAA"
        "ESAT",
        "PAT",
        "Engineering",
        "Statistics",
        "Probability"
    ]

    #sub keywords to filter out when applied in conjunction with include keywords
    # any jobs containing these words will be automatically rejected
    exclude_keywords = { 
        "Chem",
        "Bio",
        "Econ",
        "Sport"
    }
    
    def apply_criteria(self, job: Job):
        
        # check if the job contains any exclude keywords
        for keyword in self.exclude_keywords:
            if keyword.lower() in (job.title + job.job_text + job.tags).lower():
                return False 
            
        # check if the job contains any include keywords
        for keyword in self.include_keywords:
            if keyword.lower() in (job.title + job.job_text + job.tags).lower():
                return True
            
        return False

        

#CLASS: TypeFilter
#Filter jobs by job type (ESAT, PAT, IB, GCSE, etc.)
class TypeFilter(JobFilter):
    include_types = [
        "ESAT",
        "PAT",
        "MAT",
        "ENGAA",
        "GCSE",
        "A Level",
        "IB",
        "Interview",
        "Personal Statement",
        "Admissions"
    ]
    
    def apply_criteria(self, job: Job):
        for keyword in self.include_types:
            if keyword.lower() in (job.title + job.job_text + job.tags).lower():
                return True
            
        return False

        



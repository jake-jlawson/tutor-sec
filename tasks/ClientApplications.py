"""
    CLIENT APPLICATIONS MODULE
"""
# File:            || ClientApplications.py ||
# Description:     || Module performs all tasks related to applying for new tutoring jobs ||

# IMPORTS
import re
from abc import ABC, abstractmethod

from tasks.JobsManager import *


#CLASS: ApplicationGenerator
#Description: Class used to generate applications for jobs via LLMs
class ApplicationGenerator:
    def __init__(self):
        pass

    def generate(self, job: Job):
        pass
            

#CLASS: ApplicationProvider
#Description: Class used by to apply for jobs
class ApplicationProvider:
    def __init__(self):
        self.generator = ApplicationGenerator()
        self.jobs = []


    # JOBS METHODS
    def get_jobs(self):
        print("Jobs: ")
        for job in self.jobs:
            print(job.title)
            print(job.job_text)

        return self.jobs


    def add_jobs(self, jobs_in: any):
        if isinstance(jobs_in, list):
            for job in jobs_in:
                if isinstance(job, Job):
                    self.jobs.append(job)
                else:
                    print("Invalid job in list")
        elif isinstance(jobs_in, Job):
            self.jobs.append(jobs_in)
        else:
            print("Invalid input data")
        

    def filter_jobs(self, filters: list) -> list[Job]:
        for filter in filters:
            self.jobs = filter.run(self.jobs)

        return self.jobs


    def get_my_jobs(self):
       
        #instantiate filters
        filter_subjects = SubjectFilter()
        filter_types = TypeFilter()

        #filter jobs
        self.jobs = filter_subjects.run(self.jobs)
        self.jobs = filter_types.run(self.jobs)


        print("My Jobs: ")
        for job in self.jobs:
            print(job.title)



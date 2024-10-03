"""
    CLIENT APPLICATIONS MODULE
"""
# File:            || ClientApplications.py ||
# Description:     || Module for searching jobs and applying for new clients ||

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

    def add_job(self, job: Job):
        self.jobs.append(job)

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



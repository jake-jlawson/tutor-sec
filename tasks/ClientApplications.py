"""
    CLIENT APPLICATIONS MODULE
"""
# File:            || ClientApplications.py ||
# Description:     || Module performs all tasks related to applying for new tutoring jobs ||

# IMPORTS
import re
from abc import ABC, abstractmethod
from openai import OpenAI

from tasks.JobsManager import *
from utilities.Navigator2 import NavController


#CLASS: ApplicationGenerator
#Description: Class used to generate applications for jobs via LLMs
class ApplicationGenerator:
    def __init__(self):
        self.client = OpenAI()
        self.assistant = self.client.beta.assistants.create(
            name="Client Application Generator",
            instructions="""
                You are a personal secretary for an online tutor. You are tasked with generating job application text for the tutor's applications to tutor new clients.
                You will be provided with a job description and must use this and the information provided about the tutor's experience, qualifications, 
                skills and tutoring style to generate a job application that is tailored to the job.

                The job text generated will be entered into a field in the application labelled "Any information relevant to your application to perform the Job".

                It should be clear and concise, giving the client a good idea of the tutor's suitability for the job and persuading them to choose them as their tutor.

                Base each application text generated on the template file provided. 
                Change the contents to fit the job description, but match the style, structure and tone as closely as possible.

                The template file contains markdown in "[]" (which should be removed in the generated text) which inform you of the structure of the application.
            """,
            model="gpt-4o",
            tools=[],
        )

        self.threads = []


    # METHOD: appendAvailability
    # Description: Formats the tutor's availability into a string and appends it to the end of the application text
    def appendAvailability(self, job_txt: str) -> str:
        pass


    # METHOD: generate
    # Description: Generates application text using the ai assitant for a particular job
    def generate(self, job: Job): 
        
        #retrieve long job text
        controller = NavController(job.company)
        job = controller.navigator.get_detailed_job_text(job)

        #generate application text
        application_text = self.assistant.run(
            job.job_text
        )
            









#CLASS: ApplicationProvider
#Description: Class used by to apply for jobs
class ApplicationProvider:
    def __init__(self):
        self.generator = ApplicationGenerator()
        self.jobs = []


    # JOBS METHODS
    def get_jobs(self):
        print("JOBS ---------------------------------")
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



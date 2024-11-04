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
                You are a recent graduate from the University of Oxford with a degree in Engineering working as a tutor. You are tasked with applying for new tutoring jobs, and
                in order to do this, you must generate text for client applications that will be sent to the client and/or their parents to persuade them to choose you as their tutor. The job
                text needs to outline your suitability for doing the job successfully.

                You will be provided with a job description and you must use this, as well as information provided about your experience, qualifications, skills and tutoring style,
                to generate a job application that is tailored to the job.

                You should be clear and very detailed, giving the client a good idea of your suitability for the job and making the case for them to choose you.
                Be approachable but not cringe, and ensure you do not sound like ai.

                To generate these applications, you must follow the template.md file exactly. "[]" in the templates inform you of the structure but don't use them in your final response.
                Each paragraph should be the same length as in the examples provided in examples.md.
                Closely match generated responses to the level of detail, style, structure and tone of the examples in the examples.md file.
            """,
            model="gpt-4o",
            tools=[{"type": "file_search"}],
        )

        self.thread = self.client.beta.threads.create()


        # handle files
        vector_store = self.client.beta.vector_stores.create(name="Application Resources")

        file_paths = ["./tasks/application_resources2/template.md", "./tasks/application_resources2/tutor_introduction.md", "./tasks/application_resources2/tutor_experience.md", "./tasks/application_resources2/tutor_style.md", "./tasks/application_resources2/tutor_subjects.md"]
        file_streams = [open(path, "rb") for path in file_paths]

        file_batch = self.client.beta.vector_stores.file_batches.upload_and_poll(
            vector_store_id=vector_store.id,
            files=file_streams
        )

        print(file_batch.status)
        print(file_batch.file_counts)

        #update assistant
        self.assistant = self.client.beta.assistants.update(
            assistant_id=self.assistant.id,
            tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}}
        )


    # METHOD: appendAvailability
    # Description: Formats the tutor's availability into a string and appends it to the end of the application text
    def appendAvailability(self, job_txt: str) -> str:
        """
            Should be in the format:

            My availability lines up really well with the student. I am free for lessons:
            - Mondays: 10-12pm, 2-4pm (China time)
            - Wednesdays: 10-12pm, 2-4pm (China time)
            - Sundays: 10-12pm, 2-4pm (China time)
        """
        pass


    # METHOD: generate
    # Description: Generates application text using the ai assitant for a particular job
    def generate(self, job_txt: str): 
        
        # #retrieve long job text
        # controller = NavController(job.company)
        # job = controller.navigator.get_detailed_job_text(job)

        thread = self.client.beta.threads.create(
            messages=[
                {
                    "role": "user",
                    "content": job_txt
                }
            ]
        )
        
        
        
        #generate application text
        run = self.client.beta.threads.runs.create_and_poll(
            thread_id=thread.id, assistant_id=self.assistant.id
        )

        messages = list(self.client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id))

        message_content = messages[0].content[0].text
        annotations = message_content.annotations
        citations = []
        for index, annotation in enumerate(annotations):
            message_content.value = message_content.value.replace(annotation.text, f"[{index}]")
            if file_citation := getattr(annotation, "file_citation", None):
                cited_file = self.client.files.retrieve(file_citation.file_id)
                citations.append(f"[{index}] {cited_file.filename}")

        print(message_content.value)
        print("\n".join(citations))
            





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



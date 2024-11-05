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


# SETUP OPENAI
client = OpenAI()


class ApplicationGenerator:
    def __init__(self):
        self.assistant = client.beta.assistants.create(
            name="Client Application Generator",
            instructions="""
                You are a tutor's assistant tasked with generating client application statements to apply for new tutoring clients.
                These statements will be sent to clients (either students or parents or both) to put forward a case for the tutor's suitability and experience for the job, 
                and persuade them to hire the tutor for their children.

                I will provide you with the full details of a new job and ask you to generate sections of a client application statement tailored on the job description.
            """,
            model="gpt-4o",
            tools=[{"type": "file_search"}],
        )

        self.thread = client.beta.threads.create()

        self.output = ""
    

    def generate_introduction(self, job: str) -> str:
        introduction_prompt = f"""
            Generate the first paragraph of the client application statement.

            Here is the format of the first paragraph:
            [An introductory sentence which expresses my interest in supporting the student with their subject.]
            [A short introduction (2-3 sentences) to me as a tutor, giving a brief overview of my history and any experience I have that makes me the ideal choice for the job at hand.]

           
            Follow these step by step instructions to complete the task:
            1. Go through introduction_examples.md and identify the example which most closely matches the job description.
            2. Use this example as the basis for the output.
            3. Select all relevant information about the tutor's suitability for the job for the job from introduction_info.md. If no direct information exists, be creative (ie. if the job is looking for something computer science related, mention the tutor's experience with Software Engineering in their degree).
            4. Utilize the most effective of this information to tailor the content of the example to the job description. If no changes are required and the example is already tailored to the job description, leave it as is.
            4. Change the wording very slightly to make it a unique application statement, but make sure it is still 95% similar. Do not use fancy language, keep the language content natural and the same as the example. In this step, do not change the meaning of any parts of the tailored application statement.
            5. Output the first paragraph of the application statement.


            Here is the job description:
            {job}
        """

        # add files to the thread
        introduction_examples = client.files.create(
            file=open("./tasks/ClientApplications/introduction/introduction_examples.md", "rb"),
            purpose="assistants"
        )
        introduction_info = client.files.create(
            file=open("./tasks/ClientApplications/introduction/introduction_info.md", "rb"),
            purpose="assistants"
        )

        # add message to the thread
        message = client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role="user",
            content=introduction_prompt,
            attachments=[
                {"file_id": introduction_examples.id, "tools": [{"type": "file_search"}]},
                {"file_id": introduction_info.id, "tools": [{"type": "file_search"}]}
            ]
        )

        # run the assistant
        run = client.beta.threads.runs.create_and_poll(
            thread_id=self.thread.id,
            assistant_id=self.assistant.id
        )

        messages = list(client.beta.threads.messages.list(thread_id=self.thread.id, run_id=run.id))
        print(messages[0].content[0].text)


    def generate_suitability(self, job: str) -> str:
        suitability_prompt = f"""
            Generate the second paragraph of the client application statement.
            The second paragraph should go into detail about the tutor's experience, qualifications and suitability for the job. It should make an argument for why the tutor stands out and is the ideal choice for the job.

            Here is the format of the second paragraph:
            [A sentence to relate to the student, if applicable]
            [A discussion (2-3 sentences) that outlines why the tutor is ideal for the job and what unique and relevant experiences they have that make them the ideal choice for this specific job]
            [Include a powerful statistic or fact that reinforces the tutor's suitability for the job and past achievements]

           
            Follow these step by step instructions to complete the task:
            1. From all documents uploaded and any previous information in the thread, try to write a genuine sentence to relate to the student. Do not try too hard to relate - if there is no relevant information to relate to the student skip this step.
            1. Go through suitability_info.md and select all relevant experience, qualifications and suitability information that are relevant to the job description. Look for this within all sections/subjects/courses in the document.
            3. Summarise the most relevant and powerful of this information in a short, friendly discussion (2-3 sentences) that makes the case for why the tutor is ideal to support the student with their subject.
            4. Add a final sentence reinforcing the tutor's experience with a powerful statistic from suitability_info.md. Good statistics to use include number of students helped with this subject in the past, success rate of students, etc. If no good statistic that matches the job description can be found, skip this step.
            5. Output the final result as the second paragraph of the application statement.






            1. Go through suitability_examples.md and identify the example which most closely matches the job description.
            2. Use this example as the basis for the output.
            3. From suitability_info.md, select all relevant experience, qualifications and suitability information that make the tutor stand out and are relevant to the job description.
            4. Utilize the most powerful of this information to tailor the content of the example to the job description. If no changes are required, leave it as is.
            4. Change the wording very slightly to make it a unique application statement, but make sure it is still 95% similar. Do not use fancy language, keep the language content natural and the same as the example. In this step, do not change the meaning of any parts of the tailored application statement.
            5. Output the second paragraph of the application statement.
        """



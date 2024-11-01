# modules
from utilities.Navigator2 import TutorCruncher
import time

# TESTING
if __name__ == "__main__":
    tutorchase = TutorCruncher("TutorChase China")
    jobs = tutorchase.get_available_jobs()

    for job in jobs:
        print("------JOB: ", job.title)
        print(job.pay)
        print(job.tags)
        print(job.job_text)

    time.sleep(10)

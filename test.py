from tasks.ClientApplications2 import ApplicationGenerator
import json

JOB_TEXT = {
            "company": "TutorChase China",
            "id": "1079465",
            "title": "IB Physics SL",
            "pay": 40.0,
            "job_text": "The student is taking Physics SL and struggles with the course content, in particular, mechanics and waves. The do not enjoy Physics and are looking for a tutor that can inspire them",
            "tags": "",
            "apply_link": "https://secure.tutorcruncher.com/cal/service/1079465/apply/"
        }


if __name__ == "__main__":
    app_gen = ApplicationGenerator()

    # convert job_text to a JSON string
    job_text = json.dumps(JOB_TEXT, ensure_ascii=False, indent=4)

    app_gen.generate_introduction(job_text)



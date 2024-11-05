from tasks.ClientApplications2 import ApplicationGenerator
import json

JOB_TEXT = {
            "company": "TutorChase China",
            "id": "1079465",
            "title": "Oxford Engineering Interview Prep",
            "pay": 40.0,
            "job_text": "The student is applying to Oxford for Engineering and needs help with understanding the interview process, practing interviews, and improving his interview skill",
            "tags": "",
            "apply_link": "https://secure.tutorcruncher.com/cal/service/1079465/apply/"
        }


if __name__ == "__main__":
    app_gen = ApplicationGenerator()

    # convert job_text to a JSON string
    job_text = json.dumps(JOB_TEXT, ensure_ascii=False, indent=4)

    app_gen.generate_suitability(job_text)



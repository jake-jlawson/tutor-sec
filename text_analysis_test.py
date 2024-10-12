

from utilities.TextAnalysis import AvailabilityAnalyser1, AvailabilityAnalyser2

testcases = [
    """
    Subject: Cambridge & IC Interview Prep Tuition ( Biology )
    Student apply for Cambridge and IC , major is Natural Science - biology and IC's biology undergraduate program
    Availability: student can start session asap，Please provide tutor's availability if possible
    Feedback report: Required for each session
    Course outline: Required after the first session
    Platform: Lessonspace
    """,
    """
    Subject: UCAS Personal Statement Tutorial ( Marketing or Management )
    Student Profile: The student intends to apply for the postgraduate program.
    Target major: Bachelor's programme related to Marketing or Management
    Student time zone: China
    Target major:
    UCL——People Analytics and Human-Centric Management
    UCL—Marketing Science
    LSE——MSc Management and Strategy
    LSE——MSc Marketing
    LSE——MSc Social Innovation and Entrepreneurship
    Imperial College London——MSc Strategic Marketing
    University of Cambridge——MPhil in Strategy, Marketing and Operations

    Total hours: 4 hours ( 2 hours online tutoring + 2 hours offline editing )
    Online tutoring content: The student expects the tutor to teach them how to write a high-quality Personal Statement. There should be assignments after each lesson, and by the end of the course, the student should have a final draft.
    Feedback report: Required for each session
    Student availabilities: The student would like to start the session as soon as possible. please provide tutor's availabilities.

    PS Editing
    First time: Edit the content of this essay in accordance with the brainstorming session agreement,and make language polish
    Second time: add the new ideas provided by student and make language polish
    Polish and finalize the final draft. Essay should be under 4000 characters
    Feedback report: Required for each session
    Platform: Lessonspace
    """,
    """
    the student is looking for an experienced Maths AA HL teacher, ideally with examiner experiences.
    Grade: DP 2
    Location: Europe
    Platform: LessonSpace
    Frequency: 1-2 times a week
    Others: the student has quite low score in the past 2 tests at schoo since Sep. also has other tuition with other tutors but did not improved.
    """,
    """
    The session should focus on UCAT overview and some practice questions.
    Tips and tricks of the UCAT.
    the student is based in the UK and 2026 entry.
    """,
    """
    Student is based in Hong Kong
    2025 entry
    """,
    """
    Starting from week commencing 14th Oct, up until week commencing 2nd Dec.
    2 x evenings per week, on Weds; Thurs or Fri's.
    There are the following number of students for each subject:

    1 x chemistry
    """
]

for test in testcases:
    analyser = AvailabilityAnalyser2(model="gpt-4o-mini")
    print(test)
    analyser.analyse(test)
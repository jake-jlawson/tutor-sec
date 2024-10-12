

from utilities.TextAnalysis import AvailabilityAnalyser1, AvailabilityAnalyser

testcases = [
    """
    Subject: Cambridge & IC Interview Prep Tuition ( Biology )
    Student apply for Cambridge and IC , major is Natural Science - biology and IC's biology undergraduate program
    Availability: student can start session asap. 7am to lunch time in Spain. Please provide tutor's availability if possible
    Feedback report: Required for each session
    Course outline: Required after the first session
    Platform: Lessonspace
    """
]

for test in testcases:
    analyser = AvailabilityAnalyser(model="gpt-4o-mini")
    print(test)
    analyser.get_availabilities(test)
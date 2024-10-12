

from utilities.TextAnalysis import AvailabilityAnalyser1, AvailabilityAnalyser

testcases = [
    """
    Subject: Cambridge & IC Interview Prep Tuition ( Biology )
    Student is in China
    Student apply for Cambridge and IC , major is Natural Science - biology and IC's biology undergraduate program
    Availability: student can start session asap. Student is only available on weekdays. Please provide tutor's availability if possible
    Feedback report: Required for each session
    Course outline: Required after the first session
    Platform: Lessonspace
    """
]

for test in testcases:
    analyser = AvailabilityAnalyser(model="gpt-4o-mini")
    print(test)
    availabilities = analyser.get_availabilities(test)
    
    for time in availabilities:
        print("Start Time: ", time.bounds[0].strftime("%H:%M:%S"))
        print("End Time: ", time.bounds[1].strftime("%H:%M:%S"))
        print("Day: ", time.day)
        print("Timezone: ", time.tz)

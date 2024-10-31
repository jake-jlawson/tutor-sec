

from utilities.TextAnalyser import AvailabilityAnalyser1, AvailabilityAnalyser
from tasks.ScheduleManager import get_overlaps, Calendar


testcases = [
    """
    Subject: Cambridge & IC Interview Prep Tuition ( Biology )
    The student's timezone is: UK
    Student apply for Cambridge and IC , major is Natural Science - biology and IC's biology undergraduate program
    Availability: student can start session asap. Student is available after school on Mondays, Tuesdays and Wednesdays. Please provide tutor's availability if possible
    Feedback report: Required for each session
    Course outline: Required after the first session
    Platform: Lessonspace
    """
]

my_calendar = Calendar()
analyser = AvailabilityAnalyser(model="gpt-4o")


for case in testcases:

    #print test case
    print(case)

    #get availabilities
    availabilities = analyser.get_availabilities(case)
    print("----CLIENT AVAILABILITIES----")
    for timeslot in availabilities: #print availabilities
        timeslot.print()

    #get my calendar availability
    my_calendar_availability = my_calendar.get_availability()
    print("----MY CALENDAR AVAILABILITY----")
    for timeslot in my_calendar_availability: #print my calendar availability
        timeslot.print()

    #find overlaps
    overlaps = get_overlaps(focus_slots=my_calendar_availability, comparison_slots=availabilities)
    print("----OVERLAPS----")
    for overlap in overlaps:
        overlap.print()









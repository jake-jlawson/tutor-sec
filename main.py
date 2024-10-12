"""
    MAIN MODULE TO RUN TUTOR-SEC
"""

#IMPORTS
from utilities.Navigator import Navigator
from tasks.ScheduleManager import Calendar
import pytz


def main():
    navigator = Navigator("TutorChase China")
    navigator.run()




# def main():
#     calendar = Calendar()
#     availability = calendar.get_availability()

#     for slot in availability:
#         print("Slot:")
#         print("time :", slot.bounds[0].strftime("%H:%M"))
#         print("day: ", slot.day)
#         print("duration: ", slot.duration)
#         print("timezone: ", slot.tz)
#         print("country: ", slot.country)


if __name__ == "__main__":
    main()



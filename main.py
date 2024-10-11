"""
    MAIN MODULE TO RUN TUTOR-SEC
"""

#IMPORTS
from utilities.Navigator import Navigator
from tasks.ScheduleManager import Calendar


# def main():
#     navigator = Navigator("TutorChase China")
#     navigator.run()

def main():
    calendar = Calendar()
    availability = calendar.get_availability()
    
    # print(availability)
    # for slot in availability:
    #     print("Available Slot:")
    #     print("bounds: ", slot.bounds)
    #     print("day: ", slot.day)
    #     print("duration: ", slot.duration)
    #     print("timezone: ", slot.tz)
    #     print("country: ", slot.country)


if __name__ == "__main__":
    main()



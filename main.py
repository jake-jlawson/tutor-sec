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
    calendar.get_availability()


if __name__ == "__main__":
    main()



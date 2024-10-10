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
    print(calendar.api)


if __name__ == "__main__":
    main()



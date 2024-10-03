"""
    MAIN MODULE TO RUN TUTOR-SEC
"""

#IMPORTS
from utilities.Navigator import Navigator


def main():
    navigator = Navigator("UniAdmissions")
    navigator.run()


if __name__ == "__main__":
    main()



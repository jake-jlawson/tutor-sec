"""
    NAVIGATOR MODULE
"""
# File:            || Navigator2.py ||
# Description:     || Module for handling the navigation of tutoring sites ||


# IMPORTS
import os, pickle
from abc import ABC, abstractmethod
from dotenv import load_dotenv

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


load_dotenv() #load the environment variables


#ABSTRACT CLASS: SiteNavigator
#Description: Abstract class for a site navigator type
class SiteNavigator(ABC):
    @property
    @abstractmethod
    def url(self): 
        """URL of the site to navigate."""
    
    @property 
    @abstractmethod
    def page_elements(self): 
        """Important page elements of the site to navigate."""

    @property
    @abstractmethod
    def cookie_file(self): #cookie file to load
        """Cookie file to load."""
    

    def __init__(self):

        # Check if the cookie folder exists, if not, create it
        self.cookie_folder = "cookies"
        if not os.path.exists("cookies"):
            os.makedirs("cookies")

        # set up the chrome driver
        def load_driver():
            c_options = Options()
            c_service = Service(ChromeDriverManager().install())

            if (os.getenv("USE_CHROME_PROFILE") == "True"):
                c_options.add_argument(f"--user-data-dir={os.getenv('CHROME_PROFILE')}")
                c_options.add_argument("--profile-directory=" + os.getenv("CHROME_PROFILE_DIRECTORY"))

                c_options.add_argument("--disable-extensions")
                c_options.add_argument("--disable-gpu")
                c_options.add_argument("--remote-debugging-port=0")
                c_options.add_argument("--no-sandbox")
            
            return webdriver.Chrome(options=c_options, service=c_service)
                
        self.driver = load_driver()
        

    


    # NAVIGATOR METHODS
    def open(self): #open the site
        self.driver.get(self.url)


    # LOGIN METHODS
    def is_logged_in(self): #check if the user is logged in
        try:
            WebDriverWait(self.driver, 10).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )

            self.driver.find_element(By.CSS_SELECTOR, self.page_elements["logged_in"])

            return True
        
        except NoSuchElementException:
            return False
        
    def login(self): #login to the site
        
        if (self.is_logged_in()):
            print("Already logged in")
            return
        
        print("Logging in...")
    
    






#CONCRETE IMPLEMENTATIONS:
#Description: Concrete implementations of the SiteNavigator abstract class
class TutorCruncher(SiteNavigator):
    # PROPERTIES
    url = "https://secure.tutorcruncher.com/"
    cookie_file = "tutorcruncher_cookies.pk1"
    page_elements = {
        "logged_in": "#branch-menu",
    }

    def __init__(self, company: str):
        super().__init__()
        self.company = company


class Lanterna(SiteNavigator):
    # PROPERTIES
    url = "https://www.lanterna.com/"
    cookie_file = "lanterna_cookies.pk1"
    page_elements = {
        "logged_in": "#account-menu-dd",
    }



#CONTEXT: Navigator
#Description: Class for navigating a site
class Navigator:
    def __init__(self, tutoring_company: str) -> None:
        
        # set the site navigator based on the input
        match tutoring_company:
            case "TutorChase":
                self._siteNavigator = TutorCruncher(tutoring_company)
            case "TutorChase China":
                self._siteNavigator = TutorCruncher(tutoring_company)
            case "UniAdmissions":
                self._siteNavigator = TutorCruncher(tutoring_company)
            case "Oxbridge Applications":
                self._siteNavigator = TutorCruncher(tutoring_company)
            case "Lanterna":
                self._siteNavigator = Lanterna()
            case _:
                raise ValueError(f"Invalid site navigator: {tutoring_company}")
            
    def run(self):
        self._siteNavigator.open()
        print("Logged in? ", self._siteNavigator.is_logged_in())
        self._siteNavigator.login()
        

        
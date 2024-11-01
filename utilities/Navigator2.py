"""
    NAVIGATOR MODULE
    This module contains the Navigator class, which is used to navigate tutoring sites to scrape information
    and act based on this information.
"""
# Description:     || Module for handling the navigation of tutoring sites ||

# IMPORTS
import os
from dotenv import load_dotenv
from abc import ABC, abstractmethod
from tasks.ClientApplications import ApplicationProvider

# Selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException, WebDriverException
from selenium.webdriver.common.by import By

load_dotenv() #load the environment variables


#MAIN CONTEXT: Navigator --------------
#Description: Singleton class for providing interface to navigate tutoring sites
class Navigator:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Navigator, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance


    # PRIVATE: _initialize, initializes the Navigator instance
    def _initialize(self):

        # make the cookie folder if it doesn't exist
        self.cookie_folder = "cookies"
        if not os.path.exists("cookies"):
            os.makedirs("cookies")

        self._setup_driver()


    # PRIVATE: _setup_driver, sets up the Chrome driver
    def _setup_driver(self):
        try:
            # Set up Chrome driver as in your existing code
            c_options = Options()
            c_service = Service(ChromeDriverManager().install())
            
            if bool(os.getenv("USE_CHROME_PROFILE")): #use chrome profile
                print("Using Chrome profile")
                c_options.add_argument(f"--user-data-dir={os.getenv('CHROME_PROFILE')}")
                c_options.add_argument("--profile-directory=" + os.getenv("CHROME_PROFILE_DIRECTORY"))

                c_options.add_argument("--disable-extensions")
                c_options.add_argument("--disable-gpu")
                c_options.add_argument("--remote-debugging-port=0")
                c_options.add_argument("--no-sandbox")

            self.driver = webdriver.Chrome(options=c_options, service=c_service)

        except WebDriverException as e:
            print(f"Error initializing Chrome driver: {e}")
            # Optionally retry or log the error
            self._initialize()  # Re-initialize or handle the failure accordingly


    # NAVIGATION METHODS
    def open(self, url: str): #open a url
        self.driver.get(url)

    def wait_on(self, condition: str): #wait on something to happen before proceeding
        wait_time = 10

        if (condition == "page_load"):
            return WebDriverWait(self.driver, wait_time).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
        elif (condition[0] == "."): #class element
            return WebDriverWait(self.driver, wait_time).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, condition[1:]))
            )
        elif (condition[0] == "#"): #id element
            return WebDriverWait(self.driver, wait_time).until(
                EC.presence_of_element_located((By.ID, condition[1:]))
            )
        elif ("http" in condition or "https" in condition): #url
            return WebDriverWait(self.driver, wait_time).until(
                EC.url_contains(condition)
            )
        else: #no selector
            raise ValueError(f"Invalid condition: {condition}")








#ABSTRACT CLASS: SiteNavigator --------------
#Description: Abstract class for a site navigator type
class SiteNavigator(ABC):
    def __init__(self):
        pass

    # PROPERTIES
    @property
    @abstractmethod
    def url(self) -> str: 
        """URL of the site to navigate."""

    @property
    @abstractmethod
    def page_elements(self) -> dict:
        """Important page elements of the site to navigate."""

    @property
    @abstractmethod
    def page_urls(self) -> dict:
        """URLs of the pages to navigate."""


#CONCRETE NAVIGATOR IMPLEMENTATIONS --------------

# CLASS: TutorCruncher
# Description: Navigator for TutorCruncher
class TutorCruncher(SiteNavigator):
    # PROPERTIES
    url = "https://secure.tutorcruncher.com/"
    page_elements = {
        "logged_in": "#branch-menu",
        "username_field": "#id_username",
        "password_field": "#id_password",
        "login_button": "#email-signin",
        "agency_dropdown_open": "#branch-choice",
        "agency_dropdown": "#dropdown-menu",
        "agency_dropdown_item": ".dropdown-item",
        "menu_items": ".menu-item",
        "next_page_button": ".page-item",
        "jobs_page": "Available Jobs",
        "job_element": ".card-custom"
    }
    page_urls = {
        "jobs_page": "https://secure.tutorcruncher.com/cal/con/service/"
    }

    def __init__(self, company: str):
        super().__init__()
        self.company = company



# CLASS: Lanterna
# Description: Navigator for TutorCruncherChina
class Lanterna(SiteNavigator):
    def __init__(self):
        pass

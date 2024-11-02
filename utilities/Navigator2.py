"""
    NAVIGATOR MODULE
    This module contains the Navigator class, which is used to navigate tutoring sites to scrape information
    and act based on this information.
"""
# Description:     || Module for handling the navigation of tutoring sites ||

# IMPORTS
import os, time
from dotenv import load_dotenv
from abc import ABC, abstractmethod
from bs4 import BeautifulSoup

# Selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException, WebDriverException
from selenium.webdriver.common.by import By

# modules
from tasks.JobsManager import Job

load_dotenv() #load the environment variables

# CONSTANTS
AGENCIES = [
    "TutorChase", 
    "TutorChase China", 
    "Oxbridge Applications", 
    "UniAdmissions", 
    "Lanterna"
]


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

            if os.environ.get("USE_CHROME_PROFILE").lower().strip() == "true": #use chrome profile
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

    def wait_on(self, condition: str, attempts: int = 1): #wait on something to happen before proceeding
        wait_time = 10

        for attempt in range(attempts):
            try:
                if condition == "page_load":
                    return WebDriverWait(self.driver, wait_time).until(
                        lambda driver: driver.execute_script("return document.readyState") == "complete"
                    )
                elif condition[0] == ".":  # class element
                    return WebDriverWait(self.driver, wait_time).until(
                        EC.presence_of_all_elements_located((By.CLASS_NAME, condition[1:]))
                    )
                elif condition[0] == "#":  # id element
                    return WebDriverWait(self.driver, wait_time).until(
                        EC.presence_of_element_located((By.ID, condition[1:]))
                    )
                elif "http" in condition or "https" in condition:  # url
                    return WebDriverWait(self.driver, wait_time).until(
                        EC.url_contains(condition)
                    )
                else:  # no selector
                    raise ValueError(f"Invalid condition: {condition}")

            except TimeoutException:
                time.sleep(1)
                if attempt == attempts - 1:  # If this was the last attempt
                    raise Exception(f"Timeout waiting on {condition}")  # Return None if all attempts have been exhausted

            except Exception as e:
                raise Exception(f"Error waiting on {condition}: {e}")

    def wait_on_load(self):
        try:
            result = self.wait_on("page_load", attempts=5)
        except Exception as e:
            raise Exception(f"Page did not load within the specified attempts. Check internet connection. Error: {e}")


    # UTILITY METHODS
    def get_src(self):
        return self.driver.page_source




#ABSTRACT CLASS: SiteNavigator --------------
#Description: Abstract class for navigating a tutoring site
class SiteNavigator(ABC):
    def __init__(self, navigator: Navigator):
        self._navigator = navigator

        self.open() #open the site
        self.login() #login to the site

    # PROPERTIES
    @property
    @abstractmethod
    def url(self) -> str: 
        """URL of the site base page to navigate."""

    @property
    @abstractmethod
    def page_elements(self) -> dict:
        """Important page elements of the site to navigate."""

    @property
    @abstractmethod
    def page_urls(self) -> dict:
        """URLs of the pages to navigate."""

    
    # ABSTRACT METHODS
    @abstractmethod
    def get_available_jobs(self):
        """Get the available jobs listed on the site."""


    # LOGIN METHODS
    # METHOD: is_logged_in, check if the user is logged in by querying a "logged in" element
    def is_logged_in(self) -> bool: #check if the user is logged in by querying a "logged in" element
        
        self._navigator.wait_on_load()
        
        # after waiting for the page to load, try and find the logged in element
        try:
            self._navigator.driver.find_element(By.CSS_SELECTOR, self.page_elements["logged_in"])
            return True
        except NoSuchElementException:
            return False

    # METHOD: login, login to the tutoring platform
    def login(self): #login to the site
        # navigate to the login page
        self._navigator.open(self.page_urls["login"])
        
        # check already logged in
        if self.is_logged_in():
            print("Already logged in")
            return
        
        # attempt to login
        try: 
            print("Logging in...")
            result = self._navigator.wait_on(self.page_elements["username_field"], attempts=5)
            time.sleep(1)
            
            # get login elements
            username_field = self._navigator.driver.find_element(By.CSS_SELECTOR, self.page_elements["username_field"])
            password_field = self._navigator.driver.find_element(By.CSS_SELECTOR, self.page_elements["password_field"])
            login_button = self._navigator.driver.find_element(By.CSS_SELECTOR, self.page_elements["login_button"])

            # Use JavaScript to clear the fields
            self._navigator.driver.execute_script("arguments[0].value = '';", username_field)
            self._navigator.driver.execute_script("arguments[0].value = '';", password_field)

            #send the username and password to the fields
            username_field.send_keys(os.getenv("TUTORCRUNCHER_USERNAME"))
            password_field.send_keys(os.getenv("TUTORCRUNCHER_PASSWORD"))

            login_button.click()
            
        except Exception as e:
            print(f"Error logging in: {e}")


    # NAVIGATION METHODS
    # METHOD: open, open the site
    def open(self, url: str = ""):
        if url == "":
            url = self.url

        self._navigator.open(url)



#CONCRETE SITENAVIGATOR IMPLEMENTATIONS --------------

# CLASS: TutorCruncher
# Description: Navigator for TutorCruncher
class TutorCruncher(SiteNavigator):
    # PROPERTIES
    url = "https://secure.tutorcruncher.com/"
    cookie_file = "tutorcruncher_cookies.pk1"

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
        "jobs_page": "https://secure.tutorcruncher.com/cal/con/service/",
        "login": "https://secure.tutorcruncher.com/"
    }

    # CONSTRUCTOR
    def __init__(self, company: str, navigator: Navigator = Navigator()):
        super().__init__(navigator)

        self.set_company(company) #set the company

    # METHOD: set_company, set the agency to navigate on tutorcruncher
    def set_company(self, company: str):
        # check if the company is valid
        if company not in AGENCIES:
            raise Exception(f"Invalid company entered: {company}")
        
        # if the company is valid, update the attribute
        self.company = company #update attribute

        # get the company dropdown
        company_dropdown = self._navigator.wait_on(self.page_elements["agency_dropdown_open"], attempts=5)
        company_dropdown.click()


        # select the company from the dropdown
        company_dropdown_items = self._navigator.wait_on(self.page_elements["agency_dropdown_item"], attempts=5)

        if len(company_dropdown_items) == 0:
            raise Exception("Company dropdown items not found")

        for item in company_dropdown_items:
            item_text = item.text.strip().lower()
            if self.company.strip().lower() == item_text: #tutorcruncher company found
                item.click()
                return True
            
        
        #if the company is not found, return
        company_dropdown.click()
        print(f"Company {self.company} is already selected")


    # METHOD: get_available_jobs, get the available jobs listed on the site
    def get_available_jobs(self):
        # navigate to the available jobs page
        self._navigator.open(self.page_urls["jobs_page"])
        self._navigator.wait_on_load()

        # get the page source
        page_source = self._navigator.get_src()
        soup = BeautifulSoup(page_source, 'html.parser')

        #retrieve jobs via class
        job_elements = soup.find_all("div", class_=self.page_elements["job_element"][1:])
        print("number of jobs: ", len(job_elements))

    
        #iterate through each job and add them to the application provider
        available_jobs = []
        for job in job_elements:
            #job fields
            title = job.find("h3", class_="card-title")
            pay = job.find("div", class_="tcc-pay-rate")
            tags = job.find_all("div", class_="detail-long-item")[1]
            job_text = job.find_all("div", class_="detail-long-item")[0]
            elements = {
                "job_link": title.find("a").get("href"),
                "apply_link": self.url + job.find("a", class_="btn").get("href")[1:]
            }

            #create the job
            print("job elements: ", elements)
            new_job = Job(self.company, title.text, pay.text, job_text.text, tags.text, elements)
            new_job = self.get_detailed_job_text(new_job)
            available_jobs.append(new_job)

        return available_jobs


    # METHOD: get_detailed_job_text, get the detailed job text
    def get_detailed_job_text(self, job: Job) -> Job:
        """ Function takes in a job object and replaces the job text with the detailed job text
        """

        job_desc_link = job.elements["job_link"]

        #remove the first character if it is a "/"
        if job_desc_link[0] == "/":
            job_desc_link = job_desc_link[1:]

        desc_url = self.url + job_desc_link #long description url


        # try to find the detailed job text
        try:
            self._navigator.open(desc_url)
            self._navigator.wait_on_load()

            # get the page source
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            job_text = soup.find("div", class_="tcc-job-description")

            # replace the job text
            job.job_text = job_text.text
            return job

        # if no detailed job text found, return the job as is
        except:
            pass

        return job




# CLASS: Lanterna
# Description: Navigator for TutorCruncherChina
class Lanterna(SiteNavigator):
    def __init__(self):
        pass



# CLASS: NavController
# Description: Context class for managing navigators for different agencies
class NavController:
    def __init__(self, agency: str, navigator: Navigator = Navigator()):
        self.agency = agency
        self.set_site_navigator(agency, navigator)

    def set_site_navigator(self, agency: str, navigator: Navigator):
        if agency not in AGENCIES:
            raise Exception(f"Invalid agency entered: {agency}")
        
        self.agency = agency

        if agency == "Lanterna": #lanterna has a different navigator
            self.navigator = Lanterna(navigator)
        else:
            self.navigator = TutorCruncher(agency, navigator)
        





"""
    NAVIGATOR MODULE
"""
# File:            || Navigator.py ||
# Description:     || Module for handling the navigation of tutoring sites ||


# IMPORTS
import os, pickle, time
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

from bs4 import BeautifulSoup

from tasks.ClientApplications import ApplicationProvider
from tasks.JobsManager import Job, AvailabilityFilter, TypeFilter, SubjectFilter


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

    @abstractmethod
    def navigate_to(self, page: str, url: str = None):
        """Navigate to a specific page."""

    @abstractmethod
    def get_available_jobs(self, url: str = None):
        """Get available jobs from the site."""
    


    def __init__(self):
        
        # Check if the cookie folder exists, if not, create it
        self.cookie_folder = "cookies"
        if not os.path.exists("cookies"):
            os.makedirs("cookies")

        # set up the chrome driver
        def load_driver():
            c_options = Options()
            c_service = Service(ChromeDriverManager().install())

            if bool(os.getenv("USE_CHROME_PROFILE")):
                print("Using Chrome profile")
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
        
    
    def wait_then_click(self, element: str): #wait on something to happen then click it
        element = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, element))
        )
        element.click()


    def nav_to(self, url: str): #navigate to a specific url
        self.driver.get(url)


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
        #assumes that the user is on the login page
        
        if (self.is_logged_in()): #return if already logged in
            print("Already logged in")
            return

        try:
            print("Logging in...")
            self.wait_on(self.page_elements["username_field"])

            # get login elements
            username_field = self.driver.find_element(By.CSS_SELECTOR, self.page_elements["username_field"])
            password_field = self.driver.find_element(By.CSS_SELECTOR, self.page_elements["password_field"])
            login_button = self.driver.find_element(By.CSS_SELECTOR, self.page_elements["login_button"])

            #send the username and password to the fields
            username_field.send_keys(os.getenv("TUTORCRUNCHER_USERNAME"))
            password_field.send_keys(os.getenv("TUTORCRUNCHER_PASSWORD"))

            login_button.click()
            
        except Exception as e:
            print(f"Error logging in: {e}")
    

    #UTILITY METHODS
    def to_class(self, classname: str):
        #remove the dot if it exists
        if (classname[0] == "."):
            classname = classname[1:]

        return classname
    


#CONCRETE IMPLEMENTATIONS:
#Description: Concrete implementations of the SiteNavigator abstract class
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
        "jobs_page": "https://secure.tutorcruncher.com/cal/con/service/"
    }

    def __init__(self, company: str):
        super().__init__()
        self.company = company

        # Perform initial navigation actions on init
        self.open()
        self.login()
        self.set_company()


    def set_company(self):
        max_attempts = 5

        # try to select the agency
        for attempt in range(max_attempts):
            try:
                # get the dropdown element
                dropdown = self.wait_on(self.page_elements["agency_dropdown_open"]) 
                dropdown.click()

                #find the dropdown item
                dropdown_items = self.wait_on(self.page_elements["agency_dropdown_item"])
                print("dropdown items: ", dropdown_items)

                # check each item in the dropdown to find the company
                for item in dropdown_items:
                    item_text = item.text.strip().lower()
                    
                    if self.company.strip().lower() == item_text: #if the agency name is in the item text
                        item.click()
                        return True
                    
                # If the loop completes without finding a match
                print(f"No dropdown item found containing '{self.company}'")
                dropdown.click()
                return False
        

            # handle exceptions
            except StaleElementReferenceException:
                if attempt < max_attempts - 1:
                    print(f"Stale element encountered. Retrying... (Attempt {attempt + 1})")
                else:
                    print("Max retry attempts reached. Unable to select agency.")
                    return False
                
    def navigate_to(self, page: str, url: str = None):
        if url is not None:
            self.nav_to(url)
        else:
            try:
                # Wait for the menu items to be present
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, self.page_elements["menu_items"]))
                )
                
                # Find all menu items
                items = self.driver.find_elements(By.CSS_SELECTOR, self.page_elements["menu_items"])
                
                # Debug: Print all menu items
                print(f"Available menu items: {[item.text for item in items]}")
                
                for item in items:
                    if page.lower() in item.text.strip().lower():
                        print(f"Found matching menu item: {item.text}")
                        try:
                            item.click()
                            return
                        except TimeoutException:
                            print(f"Timeout waiting for {item.text} to be clickable")
                
                print(f"Page '{page}' not found")

                self.wait_on("page_load")
            
            except Exception as e:
                print(f"An error occurred while navigating: {str(e)}")


    # JOBS METHODS
    def get_available_jobs(self, url: str = None):
        # Navigate to the available jobs page
        self.navigate_to("Available Jobs")
        self.wait_on(self.page_urls["jobs_page"])

        # get the page source
        page_source = self.driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        #retrieve jobs via class
        job_elements= soup.find_all("div",class_=self.to_class(self.page_elements["job_element"]))
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
                "job_link": title.find("a"),
                "apply_link": job.find("a", class_="btn")
            }
            
            #create the job
            new_job = Job(title.text, pay.text, job_text.text, tags.text, elements)
            available_jobs.append(new_job)
            
        return available_jobs

    def get_detailed_job_text(self, job: Job) -> Job:
        """ Function takes in a job object and replaces the job text with the detailed job text
        """

        job_desc_link = job.elements["job_link"].get("href")

        #remove the first character if it is a "/"
        if job_desc_link[0] == "/":
            job_desc_link = job_desc_link[1:]

        desc_url = self.url + job_desc_link #long description url


        # try to find the detailed job text
        try:
            self.driver.get(desc_url)
            self.wait_on("page_load")

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

        # set the application provider
        self.applications = ApplicationProvider()
            

    def run(self):
        fetched_jobs = self._siteNavigator.get_available_jobs() #fetch available jobs from tutoring platform
        self.applications.add_jobs(fetched_jobs) #add fetched jobs to the applications provider
        self.applications.filter_jobs([SubjectFilter(), TypeFilter()]) #filter jobs to find jobs I can do

        # replace each job's job_text with the detailed job text
        for job in self.applications.jobs:
            job = self._siteNavigator.get_detailed_job_text(job)

        self.applications.filter_jobs([AvailabilityFilter()])

        self.applications.get_jobs()



        # Keep the browser open for 30 seconds
        time.sleep(10)
        

        
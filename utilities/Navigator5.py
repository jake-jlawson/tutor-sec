"""
Navigator Module

This module contains the Navigator class, which is used to navigate various tutoring sites.

The Navigator class provides methods for:
- Opening a browser and navigating to a specified URL.
- Navigating different tutoring platforms.
"""
from abc import ABC, abstractmethod
from dotenv import load_dotenv
import os
import pickle

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

load_dotenv() #load the environment variables



#SITENAVIGATOR: Abstract Base Class which defines standard site navigation operations
class SiteNavigator(ABC):
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.cookie_dir = os.path.join("cookies", self.cookie_file)

        if not os.path.exists("cookies"):
            os.makedirs("cookies")


    #ABSTRACT PROPERTIES
    @property
    @abstractmethod
    def url(self) -> str:
        pass

    @property
    @abstractmethod
    def page_elements(self) -> dict:
        pass

    @property
    @abstractmethod
    def cookie_file(self) -> str:
        pass


    #ABSTRACT METHODS
    @abstractmethod
    def is_logged_in(self) -> bool:
        pass


    #HANDLE COOKIES
    def save_cookies(self):
        cookies = self.driver.get_cookies()
        with open(self.cookie_dir, "wb") as f:
            pickle.dump(cookies, f)
        print("Cookies saved")

    def load_cookies(self):
        if os.path.exists(self.cookie_dir):
            with open(self.cookie_dir, "rb") as f:
                cookies = pickle.load(f)
            for cookie in cookies:
                self.driver.add_cookie(cookie)
            print("Cookies loaded")

            self.driver.refresh()
            return True
        return False

    def clear_cookies(self):
        if os.path.exists(self.cookie_dir):
            os.remove(self.cookie_dir)
        self.driver.delete_all_cookies()
        self.driver.refresh()
        print("Cookies cleared")


    #STANDARD NAVIGATION METHODS
    def open(self, with_cookies: bool = True):
        self.driver.get(self.url)
        
        if with_cookies:
            cookies_loaded = self.load_cookies()
            if cookies_loaded:
                print("Cookies loaded")
        else:
            self.clear_cookies()
        
        
    #NAVIGATION UTILITIES
    def wait_on(self, element: str, multiple: bool = False):
        
        if multiple:
            return WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, element))
            )
        else:
            return WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, element))
            )
        

#CONCRETE IMPLEMENTATION: TutorCruncher
class TutorCruncher(SiteNavigator):
    #PROPERTIES
    url = "https://secure.tutorcruncher.com/"
    cookie_file = "tutorcruncher_cookies.pk1"
    page_elements = {
        "logged_in_element": "#account-menu-dd",
        "username_field": "#id_username",
        "password_field": "#id_password",
        "login_button": "#email-signin",
        "agency_dropdown_open": "#branch-choice",
        "agency_dropdown": "#dropdown-menu",
        "agency_dropdown_item": ".dropdown-item",
        "menu_items": ".menu-item"
    }


    # CHECK IF LOGGED IN
    def is_logged_in(self):
        try:
            # Wait for a short time for an element that's only present when logged in
            # Adjust the selector based on TutorCruncher's actual logged-in page structure
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.page_elements["logged_in_element"]))
            )
            return True
        except TimeoutException:
            return False


    # Login to the site
    def login(self):
        logged_in = self.is_logged_in()
        print("logged_in: ", logged_in)
        
        if (logged_in):
            print("Already logged in")
            return
        
        try:
            self.wait_on(self.page_elements["username_field"]) #wait on login page load
            
            # get login elements
            username_field = self.driver.find_element(By.CSS_SELECTOR, self.page_elements["username_field"])
            password_field = self.driver.find_element(By.CSS_SELECTOR, self.page_elements["password_field"])
            login_button = self.driver.find_element(By.CSS_SELECTOR, self.page_elements["login_button"])

            #send the username and password to the fields
            username_field.send_keys(os.getenv("TUTORCRUNCHER_USERNAME"))
            password_field.send_keys(os.getenv("TUTORCRUNCHER_PASSWORD"))

            login_button.click()

            # Wait for login to complete (adjust the condition as needed)
            self.wait_on(self.page_elements["logged_in_element"])

            # Save cookies after successful login
            self.save_cookies()


        # handle exceptions
        except TimeoutException:
            print("Timeout waiting for login page elements or login to complete")
        except NoSuchElementException as e:
            print(f"Element not found: {str(e)}")
        except Exception as e:
            print(f"An error occurred during login: {str(e)}")

        
    # Get the agency from the dropdown
    def getAgency(self, agency_name: str):
        max_attempts = 5 
        
        # try to select the agency
        for attempt in range(max_attempts):
            try:
                # get the dropdown element
                dropdown = self.wait_on(self.page_elements["agency_dropdown_open"]) 
                dropdown.click()

                #find the dropdown item
                dropdown_items = self.wait_on(self.page_elements["agency_dropdown_item"], multiple=True)
                print("dropdown items: ", dropdown_items)

                # check each item in the dropdown
                for item in dropdown_items:
                    item_text = item.text.strip().lower()
                    
                    if agency_name.strip().lower() in item_text: #if the agency name is in the item text
                        item.click()
                        return True
                    
                # If the loop completes without finding a match
                print(f"No dropdown item found containing '{agency_name}'")
                return False
        

            # handle exceptions
            except StaleElementReferenceException:
                if attempt < max_attempts - 1:
                    print(f"Stale element encountered. Retrying... (Attempt {attempt + 1})")
                else:
                    print("Max retry attempts reached. Unable to select agency.")
                    return False
                

    # Navigate to different tutor cruncher pages (jobs, applications, etc.)
    def getPage(self, page: str):
        
        #get navigation
        navigation = self.wait_on(self.page_elements["menu_items"], multiple=True)

        print("navigation: ", navigation)
        
        
        





#NAVIGATOR: Class which uses a sitenavigator to navigate a site
class Navigator:
    def __init__(self, siteNavigator: SiteNavigator) -> None:
        self._siteNavigator = siteNavigator #set the site navigator

    def navigate(self):
        self._siteNavigator.open(with_cookies=False)
        self._siteNavigator.login()
        self._siteNavigator.getAgency("Oxbridge Applications")
        self._siteNavigator.getPage("jobs")

    @property
    def siteNavigator(self): #getter for the site navigator
        return self._siteNavigator

    @siteNavigator.setter
    def siteNavigator(self, siteNavigator: SiteNavigator): #setter for the site navigator
        self._siteNavigator = siteNavigator




navigator = Navigator(TutorCruncher())
navigator.navigate()




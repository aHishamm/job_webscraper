import requests
from bs4 import BeautifulSoup
import csv
import pandas as pd 
from tqdm import tqdm 
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time
from tqdm import tqdm
class Bayt_jobs:
    def __init__(self):
        self.base_url = "https://www.bayt.com"

    def fetch_jobs(self, query, page=1):
        try:
            formatted_query = query.replace(" ", "-").lower()  
            url = f"{self.base_url}/en/international/jobs/{formatted_query}-jobs/?page={page}"
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(url, headers=headers)

            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            job_listings = soup.find_all("li", attrs={"data-js-job": ""}) 

            jobs = []
            for job in job_listings:
                job_info = self.__extract_job_info(job, query)  
                if job_info:
                    jobs.append(job_info)

            return jobs
        except Exception as e:
            print("Error:", e)
            return None

    def __extract_job_info(self, job, search_query):
        """
        Extracts job details from a job listing.
        """
        try:
            job_general_information = job.find("h2")
            job_title = job_general_information.get_text(strip=True) if job_general_information else None

            job_url_tag = job_general_information.find("a") if job_general_information else None
            job_url = self.base_url + job_url_tag["href"] if job_url_tag else None

            company_tag = job.find("div", class_="t-nowrap p10l")
            company_name = company_tag.find("span").get_text(strip=True) if company_tag and company_tag.find("span") else None

            location_tag = job.find("div", class_="t-mute t-small")
            job_location = location_tag.get_text(strip=True) if location_tag else None

            return {
                "search_query": search_query,  
                "title": job_title,
                "company": company_name,
                "location": job_location,
                "url": job_url,
            }
        except Exception as e:
            print("Error extracting job info:", e)
            return None
class NaukrigulfJobs:
    def __init__(self):
        self.driver = uc.Chrome()
        self.driver.maximize_window()
        self.base_url = "https://www.naukrigulf.com"
    
    def fetch_jobs(self, query, orig, max_pages=10):
        jobs = []
        
        for page in range(1, max_pages + 1):
            url = f"{self.base_url}/{query}-jobs-{page}"
            print(f"Scraping: {url}")
            
            self.driver.get(url)
            time.sleep(3)
            
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "ng-box.srp-tuple"))
                )
            except:
                print(f"No jobs found for {query} on page {page}. Skipping...")
                continue
            
            job_listings = self.driver.find_elements(By.CLASS_NAME, "ng-box.srp-tuple")
            
            for job in job_listings:
                job_info = self.__extract_job_info(job, query,orig)
                if job_info:
                    jobs.append(job_info)
            
        return jobs
    
    def __extract_job_info(self, job, search_query,orig):
        """
        Extract job details from a Selenium WebElement.
        """
        try:
            job_title_elem = job.find_element(By.CLASS_NAME, "designation-title")
            job_title = job_title_elem.text.strip()
            job_url = job_title_elem.find_element(By.XPATH, "..").get_attribute("href")
            
            company_name_elem = job.find_element(By.CLASS_NAME, "info-org")
            company_name = company_name_elem.text.strip() if company_name_elem else "N/A"
            
            location_elem = job.find_element(By.CLASS_NAME, "info-loc")
            location = location_elem.text.strip() if location_elem else "N/A"
            
            experience_elem = job.find_element(By.CLASS_NAME, "info-exp")
            experience = experience_elem.text.strip() if experience_elem else "N/A"
            
            description_elem = job.find_element(By.CLASS_NAME, "description")
            description = description_elem.text.strip() if description_elem else "N/A"
            
            return {
                "search_query": orig,
                "title": job_title,
                "company": company_name,
                "location": location,
                "experience": experience,
                "description": description,
                "url": job_url
            }
        except Exception as e:
            print("Error extracting job info:", e)
            return None

    def close(self):
        self.driver.quit()

class LinkedinJobs: 
    pass

class IndeedJobs:
    pass
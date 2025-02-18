from typing import List, Dict, Optional, Any, Union
import requests
from bs4 import BeautifulSoup
import csv
import pandas as pd 
from tqdm import tqdm 
from jobspy import scrape_jobs
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
from webdriver_manager.chrome import ChromeDriverManager
import time

class Bayt_jobs:
    """
    A class to scrape job listings from Bayt.com.
    
    Attributes:
        base_url (str): The base URL for Bayt.com
    """
    
    def __init__(self) -> None:
        """Initialize Bayt_jobs with base URL."""
        self.base_url = "https://www.bayt.com"

    def fetch_jobs(self, query: str, page: int = 1) -> Optional[List[Dict[str, str]]]:
        """
        Fetch job listings from Bayt.com based on search query.

        Args:
            query (str): Search term for jobs
            page (int): Page number for pagination

        Returns:
            Optional[List[Dict[str, str]]]: List of job listings or None if error occurs
        """
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

    def __extract_job_info(self, job: BeautifulSoup, search_query: str) -> Optional[Dict[str, str]]:
        """
        Extracts job details from a job listing.

        Args:
            job (BeautifulSoup): BeautifulSoup object containing job listing
            search_query (str): Original search query

        Returns:
            Optional[Dict[str, str]]: Dictionary containing job details or None if error occurs
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
    """A class to scrape job listings from Naukrigulf.com"""

    def __init__(self) -> None:
        """Initialize NaukrigulfJobs with Chrome driver"""
        self.driver = uc.Chrome()
        self.driver.maximize_window()
        self.base_url = "https://www.naukrigulf.com"
    
    def fetch_jobs(self, query: str, orig: str, max_pages: int = 10) -> List[Dict[str, str]]:
        """
        Fetch job listings from Naukrigulf.com

        Args:
            query (str): Search query for jobs
            orig (str): Original search term
            max_pages (int): Maximum number of pages to scrape

        Returns:
            List[Dict[str, str]]: List of job listings
        """
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
                job_info = self.__extract_job_info(job, query, orig)
                if job_info:
                    jobs.append(job_info)
            
        return jobs

    def __extract_job_info(self, job: webdriver.remote.webelement.WebElement, search_query: str, orig: str) -> Optional[Dict[str, str]]:
        """
        Extract job details from a Selenium WebElement.

        Args:
            job (WebElement): Selenium WebElement containing job listing
            search_query (str): Search query used
            orig (str): Original search term

        Returns:
            Optional[Dict[str, str]]: Dictionary containing job details or None if error occurs
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

    def close(self) -> None:
        """Close the Chrome driver"""
        self.driver.quit()

class LinkedinJobs:
    """A class to scrape job listings from LinkedIn"""

    def __init__(self, job_title: str, location: str) -> None:
        """
        Initialize LinkedinJobs with job title and location.

        Args:
            job_title (str): Job title to search for
            location (str): Location to search in
        """
        self.title = [job_title]
        self.location = [location]
        self.platform = ["LinkedIn"]
        self.all_jobs = pd.DataFrame()

    def fetch_listing(self, results_wanted: int = 100) -> pd.DataFrame:
        """
        Fetch job listings from LinkedIn.

        Args:
            results_wanted (int): Number of results to fetch

        Returns:
            pd.DataFrame: DataFrame containing job listings
        """
        for job in self.title:
            for country in self.location:
                print(f"Scraping: {job} in {country}...")
                jobs = scrape_jobs(
                    site_name=self.platform,
                    search_term=job,
                    location=country,
                    results_wanted=results_wanted,
                )
                jobs["Job Title"] = job
                jobs["Country"] = self.location[0]
                jobs["Platform"] = self.platform[0]
                self.all_jobs = pd.concat([self.all_jobs, jobs], ignore_index=True)
        return self.all_jobs

class IndeedJobs:
    """A class to scrape job listings from Indeed"""

    def __init__(self, job_title: str, location: str) -> None:
        """
        Initialize IndeedJobs with job title and location.

        Args:
            job_title (str): Job title to search for
            location (str): Location to search in
        """
        self.title = [job_title]
        self.location = [location]
        self.platform = ["indeed"]
        self.all_jobs = pd.DataFrame()

    def fetch_listing(self, result_wanted: int = 100) -> pd.DataFrame:
        """
        Fetch job listings from Indeed.

        Args:
            result_wanted (int): Number of results to fetch

        Returns:
            pd.DataFrame: DataFrame containing job listings
        """
        for job in self.title:
            for country in self.location:
                print(f"Scraping: {job} in {country}...")
                jobs = scrape_jobs(
                    site_name=self.platform,
                    search_term=job,
                    location=country,
                    results_wanted=result_wanted,
                )
                jobs["Job Title"] = job
                jobs["Country"] = self.location[0]
                jobs["Platform"] = self.platform[0]
                self.all_jobs = pd.concat([self.all_jobs, jobs], ignore_index=True)
        return self.all_jobs
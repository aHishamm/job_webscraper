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

scraper = NaukrigulfJobs()
job_queries = [
    "AI Engineer",
    "Data Scientist",
    "DevOps Engineer",
    "UX/UI Designer",
    "Cybersecurity Specialist",
    "Digital Marketing Specialist",
    "Social Media Marketing Specialist",
    "E-commerce Manager",
    "HR Manager",
    "Healthcare Administrator"
]

df = pd.DataFrame(columns=["search_query", "title", "company", "location", "experience", "description", "url"])

total_pages = len(job_queries) * 5  
with tqdm(total=total_pages, desc="Scraping Naukrigulf Jobs", unit="page") as pbar:
    for job_query in job_queries:
        job_query_new = job_query.replace(" ", "-").lower() 
        jobs_data = scraper.fetch_jobs(job_query_new,job_query, max_pages=5)
        if jobs_data:
            df = pd.concat([df, pd.DataFrame(jobs_data)], ignore_index=True)
        pbar.update(10)  

df["Platform"] = "Naukrigulf"

df.to_excel("naukrigulf_jobs_selenium.xlsx", index=False)

print("Jobs successfully saved in naukrigulf_jobs_selenium.xlsx.")

scraper.close()
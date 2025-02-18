import requests
from bs4 import BeautifulSoup
import csv
import pandas as pd 
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


scraper = Bayt_jobs()

job_listings = [
    "AI Engineer",
    "Data scientist",
    "DevOps engineer",
    "UX/UI designer",
    "Cybersecurity specialist",
    "Digital marketing specialist",
    "Social media marketing specialist",
    "E-commerce manager",
    "HR manager",
    "Healthcare administrator"
]

df = pd.DataFrame(columns=["search_query", "title", "company", "location", "url"])

total_pages = len(job_listings) * 10 
with tqdm(total=total_pages, desc="Scraping Jobs", unit="page") as pbar:
    for job_query in job_listings:
        for page in range(1, 11): 
            jobs_data = scraper.fetch_jobs(job_query, page=page)
            if jobs_data:
                df = pd.concat([df, pd.DataFrame(jobs_data)], ignore_index=True)  
            pbar.update(1)  


df.dropna(subset=["title", "company", "location", "url"], inplace=True)
df["Platform"] = "Bayt"
df.to_excel("bayt_jobs.xlsx", index=False)
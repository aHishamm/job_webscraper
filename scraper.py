import pandas as pd 
from tqdm import tqdm 
from jobspy import scrape_jobs # For Indeed and Linkedin 
from utils import Bayt_jobs, NaukrigulfJobs, LinkedinJobs, IndeedJobs # importing classes from utils.py


search_query = "data scientist"
location = "United States"

"""Usage for Bayt Jobs"""
bayt = Bayt_jobs() 
df = pd.DataFrame(columns=["search_query", "title", "company", "location", "url"])
total_pages = len([search_query]) * 5
with tqdm(total=total_pages, desc="Scraping Jobs", unit="page") as pbar:
        for page in range(1, 11): 
            jobs_data = bayt.fetch_jobs(search_query, page=page)
            if jobs_data:
                df = pd.concat([df, pd.DataFrame(jobs_data)], ignore_index=True)  # Append results
            pbar.update(1)
df.dropna(subset=["title", "company", "location", "url"], inplace=True)
df["Platform"] = "Bayt"
print(df)
#Saving the scraped output to an excel file
#df.to_excel("bayt_jobs.xlsx", index=False)

"""Usage for Naukrigulf Jobs"""
naukri = NaukrigulfJobs() 
df = pd.DataFrame(columns=["search_query", "title", "company", "location", "url"])
total_pages = len([search_query]) * 5
with tqdm(total=total_pages, desc="Scraping Jobs", unit="page") as pbar:
        for page in range(1, 11): 
            jobs_data = bayt.fetch_jobs(search_query, page=page)
            if jobs_data:
                df = pd.concat([df, pd.DataFrame(jobs_data)], ignore_index=True)  # Append results
            pbar.update(1)
df.dropna(subset=["title", "company", "location", "url"], inplace=True)
df["Platform"] = "Naukrigulf"
print(df)
#Saving the scraped output to an excel file
#df.to_excel("naukrigulf_jobs.xlsx", index=False)

"""Usage for Linkedin Jobs"""
linkedin = LinkedinJobs(search_query, location)
df = linkedin.fetch_listing(100) 
print(df)
#Saving the scraped output to an excel file
#df.to_excel("linkedin_jobs.xlsx", index=False)

"""Usage for Indeed Jobs""" 
indeed = IndeedJobs(search_query, location)
df = indeed.fetch_listing(100) 
print(df)
#Saving the scraped output to an excel file
#df.to_excel("indeed_jobs.xlsx", index=False)
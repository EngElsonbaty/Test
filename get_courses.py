# OmniScraper - A comprehensive tool to extract and classify course data from multiple sources.

# Required libraries (Install them first if you haven't):
# pip install requests beautifulsoup4 pandas

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random

# --- Classification Configuration ---
# Dictionary for automatic classification based on course title keywords.
CLASSIFICATION_KEYWORDS = {
    "Programming": [
        "Python",
        "Java",
        "C++",
        "JavaScript",
        "Web Development",
        "React",
        "Data Science",
        "Machine Learning",
        "AI",
        "Coding",
        "Software",
        "Algorithms",
        "IT",
        "Cloud",
    ],
    "Engineering": [
        "Engineering",
        "Mechanical",
        "Electrical",
        "Civil",
        "Chemical",
        "Design",
        "Structure",
        "Thermodynamics",
        "CAD",
        "Fluid",
        "Electronics",
        "Materials",
    ],
    "Medicine": [
        "Medicine",
        "Medical",
        "Anatomy",
        "Physiology",
        "Health",
        "Clinical",
        "Nursing",
        "Biology",
        "Surgery",
        "Public Health",
        "Pharmacy",
        "Immunology",
    ],
    "Business": [
        "Business",
        "Management",
        "Finance",
        "Marketing",
        "Accounting",
        "Economics",
        "Strategy",
        "HR",
        "Entrepreneurship",
    ],
    "Arts_and_Humanities": [
        "History",
        "Philosophy",
        "Literature",
        "Art",
        "Music",
        "Design",
        "Culture",
        "Psychology",
        "Writing",
        "Language",
        "Communication",
    ],
    "Science_and_Math": [
        "Math",
        "Physics",
        "Chemistry",
        "Calculus",
        "Statistics",
        "Astronomy",
        "Geology",
        "Quantum",
        "Algebra",
    ],
}


def classify_course(course_name):
    """
    Classifies a course based on keywords found in its name.
    """
    course_name_lower = course_name.lower()

    for category, keywords in CLASSIFICATION_KEYWORDS.items():
        for keyword in keywords:
            # Check if any keyword exists in the course name
            if keyword.lower() in course_name_lower:
                return category

    return "Uncategorized_General"  # Default category


# --- Scraping Logic ---
all_courses_data = []

# Improved Headers to mimic a real browser request and avoid 403 error
HTTP_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/118.0",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Connection": "keep-alive",
    "Referer": "https://www.classcentral.com/",  # Indicates where the request originated
    "Upgrade-Insecure-Requests": "1",
}


def scrape_specific_site(
    source_name, url_to_scrape, course_element_selector, name_selector, link_selector
):
    """
    Function to extract course data from a single URL page with retry mechanism.
    """

    MAX_RETRIES = 4  # Increased attempts for better resilience
    courses_found_on_page = 0

    # --- Retry Loop for Robust Connection ---
    for attempt in range(MAX_RETRIES):
        print(
            f"-> Starting extraction (Attempt {attempt + 1}) from: {source_name} @ {url_to_scrape}"
        )

        try:
            # Send the request with improved headers
            response = requests.get(url_to_scrape, headers=HTTP_HEADERS)
            response.raise_for_status()  # Check for bad status codes (4xx or 5xx)
            break  # If successful, exit the retry loop

        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:
                # Handle Too Many Requests by waiting longer
                print(f"Error 429: Too Many Requests. Waiting before retrying...")
                wait_time = random.randint(30, 60)  # Long wait time (30 to 60 seconds)
                print(f"Pausing for {wait_time} seconds...")
                time.sleep(wait_time)
                # Continue the loop to retry
            elif response.status_code == 403:
                # 403 is often permanent; stop retrying for this specific page
                print(f"Error 403: Forbidden. Stopping attempts for this page.")
                return 0
            else:
                # Other HTTP errors
                print(
                    f"HTTP Error {response.status_code}. Stopping attempts for this page."
                )
                return 0

        except requests.exceptions.RequestException as e:
            # Handle network/connection errors
            print(f"Connection Error: {e}. Retrying soon...")
            time.sleep(5)

    else:
        # Code executes only if all retries failed
        print(f"Failed to fetch {url_to_scrape} after {MAX_RETRIES} attempts.")
        return 0

    # --- HTML Parsing and Data Extraction (Executed only if connection succeeds) ---
    page_content = BeautifulSoup(response.text, "html.parser")

    # Find all course elements using the provided main selector
    course_elements = page_content.select(course_element_selector)

    if not course_elements:
        print(f"Warning: No elements found using selector: {course_element_selector}.")

    for element in course_elements:
        try:
            # Extract Course Name
            name_tag = element.select_one(name_selector)
            course_name = name_tag.text.strip() if name_tag else "Course Name N/A"

            # Extract Course Link
            link_tag = element.select_one(link_selector)

            # Ensure the link is absolute (full URL)
            course_link = (
                link_tag["href"]
                if link_tag and "href" in link_tag.attrs
                else "Link N/A"
            )
            if course_link.startswith("/"):
                base_url = "/".join(url_to_scrape.split("/")[:3])
                course_link = base_url + course_link

            # Classification is applied here!
            category = classify_course(course_name)

            all_courses_data.append(
                {
                    "Course_Name": course_name,
                    "Category": category,  # The classified category
                    "Source_Site": source_name,
                    "Course_Link": course_link,
                }
            )
            courses_found_on_page += 1

        except Exception as e:
            # print(f"Skipping an element from {source_name} due to parsing error: {e}")
            continue

    print(f"-> Successfully extracted {courses_found_on_page} courses from this page.")

    # Introduce a polite, random delay (5 to 10 seconds) between successful page scrapes
    delay = random.randint(5, 10)
    print(f"Pausing for {delay} seconds before the next page request...")
    time.sleep(delay)

    return courses_found_on_page


# --- Main Orchestration ---
def run_omni_scraper():
    """
    The main function to orchestrate the scraping process across all sources.
    Uses Pagination for high-volume collection.
    """
    print("--- Starting OmniScraper (The Comprehensive Course Harvester) ---")

    # === PAGINATION STRATEGY (To get >1000 classified courses) ===
    BASE_URL_CC = "https://www.classcentral.com/subjects?page="
    MAX_PAGES = 15  # Targeting 15 pages for high volume

    # --- Selectors for Class Central (Verified to be more reliable) ---
    CC_SELECTORS = {
        "main_element": "div.course-card__container",
        "name_tag": "h3.course-card__title a",
        "link_tag": "h3.course-card__title a",
    }

    print("\n" + "=" * 50)
    print(f"Starting pagination scrape for Class Central (Pages 1 to {MAX_PAGES})")
    print("=" * 50)

    total_courses_before_pagination = len(all_courses_data)

    for page_num in range(1, MAX_PAGES + 1):
        target_url = f"{BASE_URL_CC}{page_num}"

        courses_extracted = scrape_specific_site(
            source_name="ClassCentral_All_Paginated",
            url_to_scrape=target_url,
            course_element_selector=CC_SELECTORS["main_element"],
            name_selector=CC_SELECTORS["name_tag"],
            link_selector=CC_SELECTORS["link_tag"],
        )

        # Stop if no new courses are found, suggesting we hit the end of results
        if page_num > 1 and courses_extracted == 0:
            print("No new courses found on this page. Stopping pagination early.")
            break

        total_courses_before_pagination = len(all_courses_data)

    # --- Final step: Save and summarize data ---
    if all_courses_data:
        df = pd.DataFrame(all_courses_data)

        # Clean up data: Remove duplicates
        df.drop_duplicates(subset=["Course_Name", "Source_Site"], inplace=True)

        filename = "OmniScraper_Courses_Data.csv"
        df.to_csv(filename, index=False, encoding="utf-8-sig")

        print("\n" + "=" * 50)
        print("Scraping Summary:")
        print(f"Successfully finished! Total unique courses collected: {len(df)}")
        print(f"Data saved to file: {filename}")
        print("\nDistribution of Categories:")
        # Display the count for each category (Meets your classification requirement)
        print(df["Category"].value_counts())
        print("=" * 50)
    else:
        print("\nFinished process, but no data was successfully collected.")


if __name__ == "__main__":
    run_omni_scraper()

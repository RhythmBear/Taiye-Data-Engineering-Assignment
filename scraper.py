import asyncio
import pprint
from bs4 import BeautifulSoup
from selenium import webdriver
from playwright.async_api import async_playwright
import time
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

def extract_tags(html_content, tags: list[str]):
    """
    This takes in HTML content and a list of tags, and returns a string
    containing the text content of all elements with those tags, along with their href attribute if the
    tag is an "a" tag.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    text_parts = []

    for tag in tags:
        elements = soup.find_all(tag)
        for element in elements:
            # If the tag is a link (a tag), append its href as well
            if tag == "a":
                href = element.get('href')
                if href:
                    text_parts.append(f"{element.get_text()} ({href})")
                else:
                    text_parts.append(element.get_text())
            else:
                text_parts.append(element.get_text())

    return ' '.join(text_parts)


def remove_unessesary_lines(content):
    # Split content into lines
    lines = content.split("\n")

    # Strip whitespace for each line
    stripped_lines = [line.strip() for line in lines]

    # Filter out empty lines
    non_empty_lines = [line for line in stripped_lines if line]

    # Remove duplicated lines (while preserving order)
    seen = set()
    deduped_lines = [line for line in non_empty_lines if not (
        line in seen or seen.add(line))]

    # Join the cleaned lines without any separators (remove newlines)
    cleaned_content = "".join(deduped_lines)

    return cleaned_content


def get_chrome_driver():
    #  Create a new instance of the Chrome driver
    # Setting the driver path and requesting a page
    options = Options()        
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    options.headless = True
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

    return driver


def scrape_article_links_from_enr(url) -> [str]: 
    url = 'https://www.enr.com/topics/212-california-construction-projects'
    #
    driver = get_chrome_driver()
    driver.get(url)

    # Get all url's for the articles containing construction news

    # Wait for the page to be fully loaded
    wait = WebDriverWait(driver, 5)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

    article_urls = driver.find_elements(By.XPATH, '//a[@class="url"]')
    
    article_hrefs = [url.get_attribute('href') for url in article_urls]

    return article_hrefs


def scrape_article_links_from_riversideca() -> [str]: 

    url = "https://riversideca.gov/utilities/projects"
    # Create a new instance of the Firefox driver
    # Setting the driver path and requesting a page
    options = Options()        
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

    # Go to the provided URL
    driver.get(url)

    # Get all url's for the articles containing construction news

    # Wait for the page to be fully loaded
    wait = WebDriverWait(driver, 5)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

    article_urls = driver.find_elements(By.XPATH, '//a[contains(text(), "See Project")]')
    
    article_hrefs = [url.get_attribute('href') for url in article_urls]

    return article_hrefs



def get_content_from_riversideca():   
    get_links = scrape_article_links_from_riversideca()
    result_dict = {}

    driver = get_chrome_driver()
    for link in get_links:
        driver.get(link)

        wait = WebDriverWait(driver, 5)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

        page_source = driver.page_source
        tags = ['h1', 'h2', 'h3', 'p']

        # Get the desired Tags from the page source 
        scraped_content = remove_unessesary_lines(extract_tags(page_source, tags))
        result_dict[link] = scraped_content

    return result_dict


# Testing
links = scrape_article_links_from_riversideca()
print(get_content_from_riversideca())


       
       



import logging
import json
import requests
from urllib.parse import urlparse, urljoin

from langdetect import detect
from bs4 import BeautifulSoup


logger = logging.getLogger(__name__)


class BeautifulSoupCrawler:
    def __init__(self, name, allowed_domains, start_urls,
                 max_pages=10, languages=['en'], out_file="crawl_res.json"):
        self.name = name
        self.allowed_domains = allowed_domains
        self.start_urls = start_urls
        self.languages = languages
        self.out_file = out_file
        self.max_pages = max_pages
        self.data = []
        self.counter = 0

    def is_valid_url(self, url):
        # Check if the URL belongs to the allowed domains
        parsed_url = urlparse(url)
        return any(parsed_url.netloc.endswith(domain) for domain in self.allowed_domains)

    def extract_links(self, url):
        # Send a GET request to the URL
        response = requests.get(url)
        # Create a BeautifulSoup object from the response content
        soup = BeautifulSoup(response.content, 'html.parser')
        # Extract all the links from the page
        links = [urljoin(url, link.get('href')) for link in soup.find_all('a', href=True)]
        # Filter the links to keep only the valid ones
        valid_links = [link for link in links if self.is_valid_url(link)]
        return valid_links

    def extract_text(self, url):
        # Send a GET request to the URL
        response = requests.get(url)
        # Create a BeautifulSoup object from the response content
        soup = BeautifulSoup(response.content, 'html.parser')

        try: 
            # Find the main content container
            main_content = soup.find("div", class_="main-content")  # Adjust the class name according to the website's structure

            # Extract the text content from the main content container
            text_content = main_content.get_text(strip=True)
        except Exception as ex:
            # Extract the text content of the page, excluding <style> and <script> tags
            text_content = ' '.join([element.get_text(strip=True) for element in soup.find_all(string=True) if element.parent.name not in ['style', 'script']])
        return text_content

    def crawl(self):
        visited_urls = set()
        queue = self.start_urls.copy()

        while queue:
            url = queue.pop(0)

            if self.counter >= self.max_pages:
                break

            if url in visited_urls:
                continue

            visited_urls.add(url)

            text_content = self.extract_text(url)

            if detect(text_content) not in self.languages:
                continue

            item = {
                'url': url,
                'text_content': text_content
            }

            logger.info(f"Parsed item from URL: {url}")

            self.data.append(item)

            links = self.extract_links(url)
            queue.extend(links)

            self.counter +=1

    def start(self):
        logger.info(f"Running competitor analysis for '{self.name}'.")

        self.crawl()

        # Save the extracted data to a JSON file
        with open(self.out_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)

        logger.info(f"Crawler '{self.name}' completed. Extracted {len(self.data)} items.")


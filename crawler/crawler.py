import concurrent.futures
import json
import os
import time
import urllib.request
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
from tqdm import tqdm

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class UrlScraper:
    # Constructor
    def __init__(self, url_template, max_images=50, max_workers=4):
        self.url_template = url_template  # Link crawl
        self.max_images = max_images  # Max images
        self.max_workers = max_workers  # Thread
        self.setup_environment()  # Call for set up environment

    # Set up environment for selenium
    def setup_environment(self):
        os.environ['PATH'] += ':/usr/lib/chromium-browser/'
        os.environ['PATH'] += ':/usr/lib/chromium-browser/chromedriver/'

    def get_url_images(self, term):
        """
        Crawl the urls of images by term

        Parameters:
        term (str): The name of animal, plant, scenery, furniture

        Returns:
        urls (list): List of urls of images
        """

        # Initialize Chrome driver
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(options=options)

        url = self.url_template.format(search_term=term)
        driver.get(url)

        # Start crawl urls of image like brute force - the same mechanism with this but add some feature
        urls = []
        more_content_available = True

        pbar = tqdm(total=self.max_images, desc=f"Fetching images for {term}")  # Set up for visualize progress

        while len(urls) < self.max_images and more_content_available:
            soup = BeautifulSoup(driver.page_source, "html.parser")
            img_tags = soup.find_all("img")

            for img in img_tags:
                if len(urls) >= self.max_images:
                    break
                if 'src' in img.attrs:
                    href = img.attrs['src']
                    img_path = urljoin(url, href)
                    img_path = img_path.replace("_m.jpg", "_b.jpg").replace("_n.jpg", "_b.jpg").replace("_w.jpg",
                                                                                                        "_b.jpg")
                    if img_path == "https://combo.staticflickr.com/ap/build/images/getty/IStock_corporate_logo.svg":
                        continue
                    urls.append(img_path)
                    pbar.update(1)

            try:
                load_more_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//button[@id="yui_3_16_0_1_1721642285931_28620"]'))
                )
                load_more_button.click()
                time.sleep(2)
            except:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)

                new_soup = BeautifulSoup(driver.page_source, "html.parser")
                new_img_tags = new_soup.find_all("img", loading_="lazy")
                if len(new_img_tags) == len(img_tags):
                    more_content_available = False
                img_tags = new_img_tags

        pbar.close()
        driver.quit()
        return urls

    def scrape_urls(self, categories):
        """
        Call get_url_images method to get all urls of any object in categories\

        Parameter:
        categories (dictionary): the dict of all object we need to collect image with format categories{"name_object": [value1, value2, ...]}

        Returns:
        all_urls (dictionary): Dictionary of urls of images
        """
        all_urls = {category: {} for category in categories}

        # Handle multi-threading for efficent installation
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_term = {executor.submit(self.get_url_images, term): (category, term)
                              for category, terms in categories.items() for term in terms}

            for future in tqdm(concurrent.futures.as_completed(future_to_term), total=len(future_to_term),
                               desc="Overall Progress"):
                category, term = future_to_term[future]
                try:
                    urls = future.result()
                    all_urls[category][term] = urls
                    print(f"\nNumber of images retrieved for {term}: {len(urls)}")
                except Exception as exc:
                    print(f"\n{term} generated an exception: {exc}")
        return all_urls

    def save_to_file(self, data, filename):
        """
        Save the data to a JSON file.

        Parameters:
        data (dict): The data to be saved.
        filename (str): The name of the JSON file.

        Returns:
        None
        """
        with open(filename, 'w') as file:
            json.dump(data, file, indent=4)
        print(f"Data saved to {filename}")


class ImageDownloader:
    def __init__(self, json_file, download_dir='data/raw', max_workers=4, delay=1):
        current_file_directory = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(current_file_directory, '..'))
        self.json_file = json_file
        self.download_dir = os.path.join(project_root, download_dir)
        self.max_workers = max_workers
        self.delay = delay
        self.filename = set()
        self.setup_directory()

    def setup_directory(self):
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)

    def read_json(self):
        """
        Read the JSON file and return the data.

        Returns:
        data (dict): The data read from the JSON file.
        """
        with open(self.json_file, 'r') as file:
            data = json.load(file)
        return data

    def is_valid_url(self, url):
        """
        Check if the URL is valid.

        Parameters:
        url (str): The URL to be checked.

        Returns:
        bool: True if the URL is valid, False otherwise.
        """
        try:
            with urllib.request.urlopen(url) as response:
                if response.status == 200 and 'image' in response.info().get_content_type():
                    return True
        except Exception:
            return False

    def download_image(self, url, category, term, pbar):
        """
        Download the image from the given URL.

        Parameters:
        url (str): The URL of the image to be downloaded.
        category (str): The category of the image.
        term (str): The term or keyword associated with the image.
        pbar (tqdm): The progress bar object.

        Returns:
        str: A message indicating the status of the download.
        """
        if not self.is_valid_url(url):
            pbar.update(1)
            return f"Invalid URL: {url}"

        category_dir = os.path.join(self.download_dir, category)
        if not os.path.exists(category_dir):
            os.makedirs(category_dir)

        term_dir = os.path.join(category_dir, term)
        if not os.path.exists(term_dir):
            os.makedirs(term_dir)

        filename = os.path.join(term_dir, os.path.basename(urlparse(url).path))

        self.filename.add(filename)  # Record the filename directory

        try:
            urllib.request.urlretrieve(url, filename)
            pbar.update(1)
            return f"Downloaded: {url}"
        except Exception as e:
            pbar.update(1)
            return f"Failed to download {url}: {str(e)}"

    def download_images(self):
        """
        Download images from the JSON file.

        Returns:
        None
        """
        data = self.read_json()
        download_tasks = []

        total_images = sum(len(urls) for terms in data.values() for urls in terms.values())
        with tqdm(total=total_images, desc="Downloading images") as pbar:
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                for category, terms in data.items():
                    for term, urls in terms.items():
                        for url in urls:
                            download_tasks.append(executor.submit(self.download_image, url, category, term, pbar))
                            time.sleep(self.delay)  # Polite delay

                for future in concurrent.futures.as_completed(download_tasks):
                    print(future.result())

        self.export_filename()

    def export_filename(self):
        """
        Export the filename directories to a text file.

        Returns:
        None
        """
        with open('filename.txt', 'w') as file:
            for filename in sorted(self.filename):
                file.write(f"{filename}\n")

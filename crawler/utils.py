import os
import json
import urllib.request
from urllib.parse import urlparse
import time
from tqdm import tqdm
import concurrent.futures


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
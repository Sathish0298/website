import csv
import requests
from bs4 import BeautifulSoup
import time
import re
from langchain_community.tools import DuckDuckGoSearchResults

# Initialize the DuckDuckGo API Wrapper
ddg_api = DuckDuckGoSearchResults()

# Function to search for a product link
def search_product_link(product_name, site):
    query = f"site:{site} {product_name} buy {site}"
    results = ddg_api.run(query, max_results=1)
    if results:
        print(f"Found link: {results[0]['link']}")
        return results[0]['link']
    else:
        print("No results found.")
        return None

# Amazon review scraping function
def amazon_review_scraper(url, page):
    reviews = []
    with requests.Session() as session:
        # Set a user agent to mimic a web browser
        session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0"
            }
        )
        url = f"{url}&pageNumber={page}"
        print(f"Accessing {url}")  # Debugging statement
        response = session.get(url)
        if response.url != url:
            print(f"Redirected to {response.url} instead of {url}")
        soup = BeautifulSoup(response.content, "lxml")

        for review in soup.find_all("div", {"class": "a-section review aok-relative"}):
            name_element = review.find("span", {"class": "a-profile-name"})
            rating_element = review.find("i", {"data-hook": "review-star-rating"})
            comments_element = review.find(
                "div", {"class": "a-row a-spacing-small review-data"}
            )

            if name_element and rating_element and comments_element:
                rating_text = rating_element.text.strip()
                rating = int(float(rating_text.split(" ")[0]))
                review_data = {
                    "Name": name_element.text.strip(),
                    "Rating": rating,
                    "Comments": comments_element.text.strip(),
                }
            reviews.append(review_data)

            time.sleep(1)

    return reviews


# Flipkart review scraping function
def flipkart_review_scraper(url, page):
    url = f"{url}{page}"

    reviews = []

    user_agent = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0"
    }

    response = requests.get(url=url, headers=user_agent)
    soup = BeautifulSoup(response.content, "html.parser")

    for review in soup.find_all(
        "div", {"class": "_27M-vq"}
    ):  # Updated class for review container
        name = review.find(
            "p", {"class": "_2sc7ZR _2V5EHH"}
        ).text  # Updated class for reviewer's name
        rating = review.find(
            "div", {"class": "_3LWZlK"}
        ).text  # Updated class for rating
        comments = review.find(
            "div", {"class": "t-ZTKy"}
        ).text  # Updated class for review comments
        comments = re.sub(
            r"\s*READ\s+MORE\s*", "", comments
        )  # Remove 'READ MORE' links if present

        data = {
            "Name": name,
            "Rating": rating,
            "Comments": comments.strip(),
        }

        reviews.append(data)

    return reviews


# Snapdeal review scraping function
def snapdeal_review_scraper(url, page):
    url = f"{url}{page}"
    reviews = []

    user_agent = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0"
    }

    response = requests.get(url=url, headers=user_agent)
    soup = BeautifulSoup(response.content, "html.parser")

    reviews_skipped = 0  # Counter to track the number of reviews skipped

    for review in soup.find_all("div", {"class": "user-review"}):
        if reviews_skipped < 2:
            reviews_skipped += 1
            continue  # Skip the first two reviews

        rating_elements = review.find_all("i", class_="sd-icon sd-icon-star active")
        rating = len(rating_elements)
        name = review.find("div", {"class": "_reviewUserName"}).get("title")
        comments = review.find("p").text

        data = {
            "Name": name,
            "Rating": rating,
            "Comments": comments,
        }

        reviews.append(data)

    return reviews


# Integration of the full process
def extract_and_save_reviews(product_name):
    sites = ['amazon.com', 'flipkart.com', 'snapdeal.com']
    scrape_functions = {
        'amazon.in': amazon_review_scraper,
        'flipkart.com': flipkart_review_scraper,
        'snapdeal.com': snapdeal_review_scraper
    }

    with open('product_reviews.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Product Name', 'Site', 'Name', 'Rating', 'Comments'])

        for site in sites:
            url = search_product_link(product_name, site)
            if url:
                print(f"Scraping reviews from {url}")
                reviews = scrape_functions[site](url, 1)
                for review in reviews:
                    writer.writerow([product_name, site, review['Name'], review['Rating'], review['Comments']])
            else:
                print(f"No results found for {product_name} on {site}")

# Example usage
product_name = "Samsung Galaxy S22"
extract_and_save_reviews(product_name)

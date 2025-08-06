from fastapi import FastAPI, Query
from bs4 import BeautifulSoup
from urllib.parse import quote
import requests

app = FastAPI()

def fetch_ebay_data(keyword: str, shoe_size: str, max_price: float):
    query = keyword + " size " + shoe_size
    url = f"https://www.ebay.com/sch/i.html?_nkw={quote(query)}&_sop=12"
    response = requests.get(url)

    if response.status_code != 200:
        return {"error": f"Failed to retrieve data: {response.status_code}"}

    soup = BeautifulSoup(response.text, "html.parser")
    items = []

    for item in soup.select(".s-item"):
        title_tag = item.select_one(".s-item__title")
        price_tag = item.select_one(".s-item__price")
        bid_tag = item.select_one(".s-item__bidCount")
        url_tag = item.select_one(".s-item__link")
        size_tag = item.find(string=lambda string: string and shoe_size in string)
        shipping_tag = item.select_one(".s-item__shipping, .s-item__freeXDays")
        image_tag = item.select_one("div.s-item__image-wrapper.image-treatment img")

        if title_tag and price_tag and url_tag and size_tag and image_tag:
            if "Shop on eBay" in title_tag.text or "Shop eBay" in title_tag.text:
                continue

            price_text = price_tag.text.replace("$", "").replace(",", "").strip()
            if " to " in price_text:
                price_text = price_text.split(" to ")[0]
            try:
                price = float(price_text)
            except ValueError:
                continue

            if price <= max_price:
                shipping_cost = 0.0
                if shipping_tag:
                    shipping_text = shipping_tag.text.strip().replace("$", "").replace(",", "")
                    if "Free" not in shipping_text:
                        try:
                            shipping_cost = float(shipping_text.split()[0])
                        except ValueError:
                            shipping_cost = 0.0

                image_url = image_tag.get("src", "")

                item_data = {
                    "Image": image_url,
                    "Shoe": title_tag.text,
                    "Price": price,
                    "Shipping": shipping_cost,
                    "Currency": "USD",
                    "Bids": bid_tag.text if bid_tag else "N/A",
                    "URL": url_tag["href"]
                }
                items.append(item_data)

    return {"results": items}

@app.get("/ebay")
def ebay_search(
    keyword: str = Query(..., description="Shoe name, e.g., 'air jordan'"),
    shoe_size: str = Query(..., description="Shoe size, e.g., '10'"),
    max_price: float = Query(200.0, description="Maximum price filter"),
):
    return fetch_ebay_data(keyword, shoe_size, max_price)



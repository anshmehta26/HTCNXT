from fastapi import FastAPI, Query
from bs4 import BeautifulSoup
from urllib.parse import quote
import requests

app = FastAPI()

def fetch_quotes_by_tag(tag: str):
    url = f"http://quotes.toscrape.com/tag/{quote(tag)}/"
    response = requests.get(url)

    if response.status_code != 200:
        return {"error": f"Failed to retrieve data: {response.status_code}"}

    soup = BeautifulSoup(response.text, "html.parser")
    quotes = []

    for quote_block in soup.select(".quote"):
        text_tag = quote_block.select_one(".text")
        author_tag = quote_block.select_one(".author")
        tag_elements = quote_block.select(".tags .tag")

        if text_tag and author_tag:
            quote_data = {
                "quote": text_tag.text.strip(),
                "author": author_tag.text.strip(),
                "tags": [tag.text for tag in tag_elements]
            }
            quotes.append(quote_data)

    return {"results": quotes}

@app.get("/quotes")
def get_quotes_by_tag(
    tag: str = Query(..., description="Quote tag, e.g., 'life', 'love', 'inspirational'")
):
    return fetch_quotes_by_tag(tag)

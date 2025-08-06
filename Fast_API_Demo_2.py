import pika
import json
import pandas as pd
from IPython.display import display
from IPython.display import HTML

def display_with_images(results):
    html = "<table><tr><th>Image</th><th>Shoe</th><th>Price</th><th>Shipping</th><th>Bids</th><th>Link</th></tr>"
    for it in results["results"]:
        html += f"""
        <tr>
            <td><img src="{it['Image']}" width="80"></td>
            <td>{it['Shoe']}</td>
            <td>${it['Price']}</td>
            <td>${it['Shipping']}</td>
            <td>{it['Bids']}</td>
            <td><a href="{it['URL']}" target="_blank">View</a></td>
        </tr>
        """
    html += "</table>"
    display(HTML(html))

RABBIT_URL = "amqps://hfjbhgci:G1r-bQkihyAKAyM9zZnMKkbbnBpGaoim@turkey.rmq.cloudamqp.com/hfjbhgci"
params = pika.URLParameters(RABBIT_URL)
connection = pika.BlockingConnection(params)
channel = connection.channel()
channel.queue_declare(queue="ebay_jobs")

# --- Producer Function (handles a list of jobs) ---
def producer(jobs):
    """
    jobs: list of dicts with keys: keyword, shoe_size, max_price
    Example:
        jobs = [
            {"keyword": "air jordan", "shoe_size": "10", "max_price": 200},
            {"keyword": "yeezy", "shoe_size": "9", "max_price": 250}
        ]
    """
    for job in jobs:
        msg = json.dumps(job)
        channel.basic_publish(exchange="", routing_key="ebay_jobs", body=msg)
        print(f"[x] Queued scrape job for {job['keyword']} size {job['shoe_size']}")


import requests
import pandas as pd
import json

def consumer():
    print("[*] Waiting for jobs...")

    try:
        while True:
            method_frame, header_frame, body = channel.basic_get(queue="ebay_jobs", auto_ack=True)

            if body:
                job = json.loads(body.decode())
                print(f"[>] Sending API request for job: {job}")

                # --- Make FastAPI call ---
                params = {
                    "keyword": job["keyword"],
                    "shoe_size": job["shoe_size"],
                    "max_price": job["max_price"]
                }
                try:
                    response = requests.get("http://localhost:8000/ebay", params=params)

                    if response.status_code == 200:
                        data = response.json()
                        results = data.get("results", [])
                        if results:
                            df = pd.DataFrame(results)
                            print("✅ Results:")
                            display(df)
                        else:
                            print("❌ No results returned.")
                    else:
                        print(f"❌ API error {response.status_code}: {response.text}")

                except Exception as e:
                    print(f"❌ Exception calling API: {e}")

            else:
                print("[*] Queue empty. Done consuming.")
                break

    except KeyboardInterrupt:
        print("❌ Consumer interrupted manually.")

jobs = [
    {"keyword": "air jordan 1", "shoe_size": "10", "max_price": 250},
    {"keyword": "nike dunk low", "shoe_size": "9", "max_price": 200},
    {"keyword": "yeezy boost 350", "shoe_size": "11", "max_price": 300}
]

producer(jobs)

consumer()
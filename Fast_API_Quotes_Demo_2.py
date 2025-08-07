import pika
import json
import pandas as pd
from IPython.display import display
from IPython.display import HTML


RABBIT_URL = "amqps://hfjbhgci:G1r-bQkihyAKAyM9zZnMKkbbnBpGaoim@turkey.rmq.cloudamqp.com/hfjbhgci"
params = pika.URLParameters(RABBIT_URL)
connection = pika.BlockingConnection(params)
channel = connection.channel()
channel.queue_declare(queue="quotes_jobs")

# --- Producer Function (queues tags to search for) ---
def producer(jobs):
    """
    jobs: list of dicts with key: tag
    Example:
        jobs = [{"tag": "life"}, {"tag": "humor"}]
    """
    for job in jobs:
        msg = json.dumps(job)
        channel.basic_publish(exchange="", routing_key="quotes_jobs", body=msg)
        print(f"[x] Queued quote job for tag: {job['tag']}")


# --- Consumer Function (calls FastAPI + displays results) ---
import requests

def consumer():
    print("[*] Waiting for jobs...")

    try:
        while True:
            method_frame, header_frame, body = channel.basic_get(queue="quotes_jobs", auto_ack=True)

            if body:
                job = json.loads(body.decode())
                tag = job["tag"]
                print(f"[>] Sending API request for tag: {tag}")

                try:
                    response = requests.get("http://localhost:8000/quotes", params={"tag": tag})

                    if response.status_code == 200:
                        data = response.json()
                        results = data.get("results", [])
                        if results:
                            df = pd.DataFrame(results)
                            print(f"✅ Quotes for tag: {tag}")
                            display(df)
                        else:
                            print(f"❌ No quotes returned for tag: {tag}")
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
    {"tag": "life"},
    {"tag": "humor"},
    {"tag": "inspirational"}
]

producer(jobs)
consumer()

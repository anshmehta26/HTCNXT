from fastapi import FastAPI, Query
import pika, json

app = FastAPI()

# Your CloudAMQP URL
AMQP_URL = "amqps://hfjbhgci:G1r-bQkihyAKAyM9zZnMKkbbnBpGaoim@turkey.rmq.cloudamqp.com/hfjbhgci"

@app.get("/send-task/")
def send_task(data: str = Query(..., description="Task message to queue")):
    connection = pika.BlockingConnection(pika.URLParameters(AMQP_URL))
    channel = connection.channel()
    channel.queue_declare(queue="demo_queue", durable=True)

    channel.basic_publish(
        exchange='',
        routing_key='demo_queue',
        body=data,
        properties=pika.BasicProperties(delivery_mode=2)
    )
    connection.close()
    return {"message": f"✅ Task '{data}' sent to queue"}
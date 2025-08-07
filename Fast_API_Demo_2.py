import pika, json

AMQP_URL = "amqps://hfjbhgci:G1r-bQkihyAKAyM9zZnMKkbbnBpGaoim@turkey.rmq.cloudamqp.com/hfjbhgci"


def callback(ch, method, properties, body):
    print(f"📥 Received task: {body.decode()}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(pika.URLParameters(AMQP_URL))
channel = connection.channel()
channel.queue_declare(queue="demo_queue", durable=True)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue="demo_queue", on_message_callback=callback)

print("[*] Waiting for tasks. To exit, press CTRL+C")
channel.start_consuming()

import pika
import os
from dotenv import load_dotenv

load_dotenv()
RABBITMQ_URL = os.getenv("RABBITMQ_URL")

def publish_transaction(transaction_id: str):
    connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
    channel = connection.channel()
    channel.queue_declare(queue="transactions", durable=True)
    channel.basic_publish(
        exchange="",
        routing_key="transactions",
        body=transaction_id.encode("utf-8"),
        properties=pika.BasicProperties(delivery_mode=2),
    )
    connection.close()

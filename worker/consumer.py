import pika
import asyncio
from datetime import datetime
from app.db import collection
import os
from dotenv import load_dotenv

load_dotenv()

RABBITMQ_URL = os.getenv("RABBITMQ_URL")

# Global event loop - created once and reused
event_loop = None

def setup_event_loop():
    """Initialize the event loop once"""
    global event_loop
    if event_loop is None or event_loop.is_closed():
        event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(event_loop)

def callback(ch, method, properties, body):
    """RabbitMQ callback with proper error handling"""
    transaction_id = body.decode("utf-8")
    print(f"Processing transaction: {transaction_id}")
    
    try:
        # Ensure we have a valid event loop
        setup_event_loop()
        
        # Run the async task
        event_loop.run_until_complete(process_transaction(transaction_id))
        
        # Acknowledge successful processing
        ch.basic_ack(delivery_tag=method.delivery_tag)
        print(f"Successfully processed: {transaction_id}")
        
    except Exception as e:
        print(f"Error processing transaction {transaction_id}: {e}")
        
        # Check redelivery count to prevent infinite loops
        redelivered = getattr(method, 'redelivered', False)
        if redelivered:
            print(f"Message {transaction_id} already redelivered once. Discarding to prevent loop.")
            # Acknowledge to remove from queue (prevent infinite loop)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        else:
            print(f"Requeuing {transaction_id} for retry")
            # Requeue for first retry
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

async def process_transaction(transaction_id: str):
    """Process transaction with proper error handling"""
    try:
        await asyncio.sleep(30)  # simulate external API delay
        await collection.update_one(
            {"_id": transaction_id},
            {"$set": {"status": "PROCESSED", "processed_at": datetime.utcnow()}}
        )
        print(f"Transaction {transaction_id} processed.")
    except Exception as e:
        print(f"Database error for {transaction_id}: {e}")
        raise  # Re-raise to trigger retry logic

def start_consumer():
    """Start the RabbitMQ consumer with proper setup"""
    # Setup event loop first
    setup_event_loop()
    
    connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
    channel = connection.channel()
    channel.queue_declare(queue="transactions", durable=True)
    
    # Process one message at a time to avoid concurrency issues
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue="transactions", on_message_callback=callback)
    
    print("Worker started, waiting for messages...")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("Stopping consumer...")
        channel.stop_consuming()
        connection.close()
        if event_loop and not event_loop.is_closed():
            event_loop.close()

if __name__ == "__main__":
    start_consumer()

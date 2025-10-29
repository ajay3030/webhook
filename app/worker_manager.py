import threading
import asyncio
import pika
from datetime import datetime
from app.db import collection
import os
from dotenv import load_dotenv

load_dotenv()

RABBITMQ_URL = os.getenv("RABBITMQ_URL")

class WorkerManager:
    def __init__(self):
        self.running = False
        self.thread = None
    
    def start_worker_thread(self):
        """Start worker in a separate thread"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run_worker, daemon=True)
            self.thread.start()
            print("✅ Background worker started in thread")
    
    def _run_worker(self):
        """Worker thread function"""
        try:
            # Setup event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Start RabbitMQ consumer
            connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
            channel = connection.channel()
            channel.queue_declare(queue="transactions", durable=True)
            channel.basic_qos(prefetch_count=1)
            
            def callback(ch, method, properties, body):
                transaction_id = body.decode("utf-8")
                print(f"🔄 Processing transaction: {transaction_id}")
                
                try:
                    # Run async processing
                    loop.run_until_complete(self.process_transaction(transaction_id))
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    print(f"✅ Transaction {transaction_id} processed successfully")
                    
                except Exception as e:
                    print(f"❌ Error processing {transaction_id}: {e}")
                    redelivered = getattr(method, 'redelivered', False)
                    if redelivered:
                        ch.basic_ack(delivery_tag=method.delivery_tag)  # Prevent infinite loop
                    else:
                        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            
            channel.basic_consume(queue="transactions", on_message_callback=callback)
            print("🎧 Worker listening for messages...")
            channel.start_consuming()
            
        except Exception as e:
            print(f"❌ Worker thread error: {e}")
            self.running = False
    
    async def process_transaction(self, transaction_id: str):
        """Process transaction (same logic as before)"""
        await asyncio.sleep(30)  # Simulate external API delay
        await collection.update_one(
            {"_id": transaction_id},
            {"$set": {"status": "PROCESSED", "processed_at": datetime.utcnow()}}
        )

# Global worker instance
worker_manager = WorkerManager()

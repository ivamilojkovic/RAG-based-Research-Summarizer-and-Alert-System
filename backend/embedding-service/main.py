import pika
import json
from chunker import process_document

def callback(ch, method, properties, body):
    job = json.loads(body)
    source = job["source"]
    source_id = job["source_id"]

    print(f"[x] Received job for {source}:{source_id}")
    process_document(source, source_id)

    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host='rabbitmq', 
        credentials=pika.PlainCredentials('user', 'password')
    )
)
channel = connection.channel()
channel.queue_declare(queue='embedding_jobs', durable=True)
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='embedding_jobs', on_message_callback=callback)

print('[*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()

import psycopg2
import os
import pika
import json
from app.db.schema import alerts_schema, papers_schema

def send_to_queue(source, source_id):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='rabbitmq', credentials=pika.PlainCredentials('user', 'password'))
    )
    channel = connection.channel()
    channel.queue_declare(queue='embedding_jobs', durable=True)

    message = json.dumps({"source": source, "source_id": source_id})
    channel.basic_publish(
        exchange='',
        routing_key='embedding_jobs',
        body=message,
        properties=pika.BasicProperties(delivery_mode=2)
    )
    # connection.close()


class PostgresDB:
    def __init__(self):
        print(f"Connecting to DB at {os.getenv('DB_HOST')}")
        self.conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", 5432),
            database=os.getenv("DB_NAME", "postgres"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "postgres"),
        )
        self.conn.autocommit = True

    def insert_document(self, table, data):
        with self.conn.cursor() as cursor:
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['%s'] * len(data))
            values = list(data.values())
            query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders}) ON CONFLICT (source_id, source) DO NOTHING;"
            cursor.execute(query, values)

            if cursor.rowcount == 1:  # Insert happened
                send_to_queue(data['source'], data['source_id'])
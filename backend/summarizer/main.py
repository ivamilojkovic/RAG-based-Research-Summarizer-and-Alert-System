import pika
import json
import os
# from openai import OpenAI
from groq import Groq
from prompts import SUMMARIZER_SYSTEM_PROMPT
from db import PostgresDB

# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def update_alert_summary(alert_id, summary_data):
    db = PostgresDB()
    with db.conn.cursor() as cursor:
        cursor.execute(
            """
            UPDATE alerts
            SET summary = %s, status = 'completed', updated_at = NOW()
            WHERE id = %s
            """,
            (json.dumps(summary_data), alert_id)
        )
        db.conn.commit()

def summarize_text(prompt: str, chunks: list[str]) -> str:
    context = "\n---\n".join(chunks)
    full_prompt = f"{prompt}\n\nContext:\n{context}"

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SUMMARIZER_SYSTEM_PROMPT},
            {"role": "user", "content": full_prompt}
        ],
        temperature=0,
        top_p=1
    )
    return response.choices[0].message.content

def callback(ch, method, properties, body):
    job = json.loads(body)
    prompt = job["prompt"]
    chunks = job.get("chunks", [])
    alert_id = job.get("alert_id")

    print(f"[x] Summarizing for alert ID {alert_id}...")
    summary = summarize_text(prompt, chunks)
    print("Summary:\n", summary)

    update_alert_summary(alert_id, summary)

    ch.basic_ack(delivery_tag=method.delivery_tag)


connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host='rabbitmq', 
        credentials=pika.PlainCredentials('user', 'password')
    )
)
channel = connection.channel()
channel.queue_declare(queue='summarization_jobs', durable=True)
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='summarization_jobs', on_message_callback=callback)

print('[*] Waiting for summarization jobs. To exit press CTRL+C')
channel.start_consuming()


import requests 
from confluent_kafka import Producer
import time
import json

API_KEY = '52443a47c5d534f85794099e1721c8fe'


KAFKA_TOPIC = "movie_recommendation"
kafka_config = {
    "bootstrap.servers": "localhost:9092",
    "batch.num.messages": 1000, 
    "delivery.report.only.error": True
}

producer = Producer(kafka_config)
counter = 3
while True:
    try:
        url = f"https://api.themoviedb.org/3/movie/{counter}?api_key={API_KEY}"
        headers = {
            "accept": "application/json"
        }
        response = requests.get(url, headers=headers)
        counter += 1
        if response.status_code == 200:
            data = json.dumps(response.json())
            producer.produce(KAFKA_TOPIC, key="movie", value=data)
            producer.flush()
            print(response.json())
        else:
            print(f"Failed to fetch data. Status Code: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")

    time.sleep(3)
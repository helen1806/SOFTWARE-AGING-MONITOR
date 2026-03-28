from flask import Flask
from prometheus_client import Counter, Gauge, generate_latest
import time
import threading

app = Flask(__name__)
data = []

memory_gauge = Gauge('app_memory_bytes', 'Simulated memory usage')
latency_gauge = Gauge('app_latency_seconds', 'Response latency')
thread_gauge = Gauge('app_thread_count', 'Active thread count')

@app.route("/")
def home():
    data.append("leak" * 10000)
    latency = len(data) * 0.01
    time.sleep(latency)

    t = threading.Thread(target=lambda: time.sleep(60))
    t.start()

    # Update metrics
    memory_gauge.set(len(data) * 10000)
    latency_gauge.set(latency)
    thread_gauge.set(threading.active_count())

    return "Running"

@app.route("/metrics")
def metrics():
    return generate_latest()
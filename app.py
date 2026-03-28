import threading

@app.route("/")
def home():
    data.append("leak" * 10000)
    time.sleep(len(data) * 0.01)
    t = threading.Thread(target=lambda: time.sleep(60))
    t.start()  
    return "Running"
from flask import Flask, jsonify
import os
import requests
from google.transit import gtfs_realtime_pb2
from datetime import datetime, timezone
import time

API_KEY = "afd1203e-3451-430b-b694-d2fa4b4c70b8"
STOP_ID = "18157"
URL = f"https://api.511.org/transit/TripUpdates?api_key={API_KEY}&agency=SF"

app = Flask(__name__)

def minutes_until(timestamp):
    dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
    now = datetime.now(timezone.utc)
    diff = (dt - now).total_seconds() / 60
    return int(diff)

def get_next_departures():
    feed = gtfs_realtime_pb2.FeedMessage()
    response = requests.get(URL, headers={"Accept": "application/x-google-protobuf"})
    feed.ParseFromString(response.content)

    upcoming = []
    for entity in feed.entity:
        if entity.trip_update:
            for stu in entity.trip_update.stop_time_update:
                if stu.stop_id == STOP_ID and stu.arrival.time > time.time():
                    upcoming.append(stu.arrival.time)

    upcoming.sort()
    return [minutes_until(ts) for ts in upcoming[:3]]

@app.route("/nextbus")
def nextbus():
    departures = get_next_departures()
    return jsonify({"next": departures})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)


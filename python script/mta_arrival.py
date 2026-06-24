import requests
from datetime import datetime
from zoneinfo import ZoneInfo
from google.transit import gtfs_realtime_pb2


FEED_URL = "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-bdfm"

# Replace this with the stop_id you want.
# Subway stop_ids usually end in N or S:
# N = northbound / uptown direction
# S = southbound / downtown direction
STOP_ID = "G20N"


def fetch_feed(url: str):
    response = requests.get(url, timeout=10)
    response.raise_for_status()

    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(response.content)
    return feed


def get_arrivals(feed, stop_id: str):
    now = datetime.now(ZoneInfo("America/New_York")).timestamp()
    arrivals = []

    for entity in feed.entity:
        if not entity.HasField("trip_update"):
            continue

        trip = entity.trip_update.trip

        for stu in entity.trip_update.stop_time_update:
            if stu.stop_id != stop_id:
                continue

            if stu.HasField("arrival"):
                arrival_time = stu.arrival.time
            elif stu.HasField("departure"):
                arrival_time = stu.departure.time
            else:
                continue

            minutes_away = round((arrival_time - now) / 60)

            if minutes_away >= 0:
                arrivals.append({
                    "route": trip.route_id,
                    "arrival_time": datetime.fromtimestamp(
                        arrival_time,
                        ZoneInfo("America/New_York")
                    ),
                    "minutes_away": minutes_away,
                })

    return sorted(arrivals, key=lambda x: x["arrival_time"])


if __name__ == "__main__":
    feed = fetch_feed(FEED_URL)
    arrivals = get_arrivals(feed, STOP_ID)

    if not arrivals:
        print("No arrivals found. Check your feed URL and stop_id.")
    else:
        for arrival in arrivals[:10]:
            print(
                f"{arrival['route']} train: "
                f"{arrival['minutes_away']} min "
                f"at {arrival['arrival_time'].strftime('%I:%M:%S %p')}"
            )
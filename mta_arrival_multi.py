#!/usr/bin/env python3
"""Print upcoming NYC subway arrivals for selected stations and routes."""

from __future__ import annotations

import argparse
import math
import time
from collections import defaultdict
from datetime import datetime
from typing import Iterable
from zoneinfo import ZoneInfo

import requests
from google.protobuf.message import DecodeError
from google.transit import gtfs_realtime_pb2


# MTA subway GTFS-Realtime feeds.
FEED_URLS = {
    "ACE": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-ace",
    "BDFM": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-bdfm",
    "G": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-g",
    "JZ": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-jz",
    "NQRW": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-nqrw",
    "1234567": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs",
    "L": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-l",
    "SI": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-si",
}

ROUTE_TO_FEED = {
    **dict.fromkeys("ACEH", "ACE"),
    **dict.fromkeys("BDFM", "BDFM"),
    "FS": "BDFM",
    "G": "G",
    **dict.fromkeys("JZ", "JZ"),
    **dict.fromkeys("NQRW", "NQRW"),
    **dict.fromkeys("1234567", "1234567"),
    "GS": "1234567",
    "L": "L",
    "SI": "SI",
}

# Edit what train routes you want
ROUTES_TO_SHOW = ("D", "N", "R")

# N = north/uptown; S = south/downtown
# Double check with statitons that might have same name
STOPS = {
    "36 St Uptown": "R36N",
    "36 St Downtown": "R36S",
    "145 St Uptown" : "D13N",
    "145 St Downtown": "D13S",
}

ARRIVALS_PER_STATION = 2
NEW_YORK = ZoneInfo("America/New_York")
REQUEST_TIMEOUT_SECONDS = 10


def fetch_feed(url: str) -> gtfs_realtime_pb2.FeedMessage:
    """Download and parse one GTFS-Realtime feed."""
    response = requests.get(url, timeout=REQUEST_TIMEOUT_SECONDS)
    response.raise_for_status()

    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(response.content)
    return feed


def required_feed_names(routes: Iterable[str]) -> list[str]:
    """Return the feed groups needed by the requested routes."""
    feed_names: list[str] = []
    unknown_routes: list[str] = []

    for route in routes:
        feed_name = ROUTE_TO_FEED.get(route)
        if feed_name is None:
            unknown_routes.append(route)
        elif feed_name not in feed_names:
            feed_names.append(feed_name)

    if unknown_routes:
        unknown = ", ".join(unknown_routes)
        raise ValueError(f"No feed mapping is configured for route(s): {unknown}")

    return feed_names


def event_timestamp(stop_time_update) -> int | None:
    """Get the best available arrival/departure Unix timestamp."""
    if (
        stop_time_update.HasField("arrival")
        and stop_time_update.arrival.HasField("time")
    ):
        return stop_time_update.arrival.time

    if (
        stop_time_update.HasField("departure")
        and stop_time_update.departure.HasField("time")
    ):
        return stop_time_update.departure.time

    return None


def collect_arrivals(
    feeds: Iterable[gtfs_realtime_pb2.FeedMessage],
    routes: Iterable[str],
    stop_ids: Iterable[str],
    now_timestamp: float,
) -> dict[str, dict[str, list[int]]]:
    """Collect future arrival timestamps by stop_id and route."""
    wanted_routes = set(routes)
    wanted_stops = set(stop_ids)
    arrivals: dict[str, dict[str, list[int]]] = defaultdict(
        lambda: defaultdict(list)
    )

    for feed in feeds:
        for entity in feed.entity:
            if not entity.HasField("trip_update"):
                continue

            trip_update = entity.trip_update
            route = trip_update.trip.route_id
            if route not in wanted_routes:
                continue

            for update in trip_update.stop_time_update:
                if update.stop_id not in wanted_stops:
                    continue

                timestamp = event_timestamp(update)
                if timestamp is not None and timestamp >= now_timestamp - 30:
                    arrivals[update.stop_id][route].append(timestamp)

    # Sorting a set also removes occasional duplicate trip updates.
    for stop_arrivals in arrivals.values():
        for route, timestamps in stop_arrivals.items():
            stop_arrivals[route] = sorted(set(timestamps))

    return arrivals


def format_wait(timestamp: int, now_timestamp: float) -> str:
    """Format an arrival as a rider-friendly wait time."""
    seconds = max(0, timestamp - now_timestamp)
    minutes = math.floor(seconds / 60)
    return "Due" if minutes == 0 else f"{minutes} min"


def format_board(
    arrivals: dict[str, dict[str, list[int]]],
    now: datetime,
) -> str:
    """Build the terminal output."""
    lines = [f"Updated {now.strftime('%-I:%M:%S %p %Z')}", ""]

    for station_label, stop_id in STOPS.items():
        lines.append(station_label)

        # Combine all selected routes, sort by arrival time, and show only
        # the next ARRIVALS_PER_STATION trains at this station-direction.
        upcoming = sorted(
            (timestamp, route)
            for route in ROUTES_TO_SHOW
            for timestamp in arrivals.get(stop_id, {}).get(route, [])
        )[:ARRIVALS_PER_STATION]

        if upcoming:
            for timestamp, route in upcoming:
                lines.append(
                    f"  {route} - {format_wait(timestamp, now.timestamp())}"
                )
        else:
            lines.append("  No upcoming selected trains found.")

        lines.append("")

    return "\n".join(lines).rstrip()


def get_board() -> str:
    """Fetch current data and return the formatted arrival board."""
    now = datetime.now(NEW_YORK)
    feeds = [
        fetch_feed(FEED_URLS[name])
        for name in required_feed_names(ROUTES_TO_SHOW)
    ]
    arrivals = collect_arrivals(
        feeds=feeds,
        routes=ROUTES_TO_SHOW,
        stop_ids=STOPS.values(),
        now_timestamp=now.timestamp(),
    )
    return format_board(arrivals, now)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Show live MTA subway arrival times."
    )
    parser.add_argument(
        "--refresh",
        type=int,
        metavar="SECONDS",
        help="Refresh continuously at this interval (30 or more recommended).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    while True:
        try:
            board = get_board()
        except (requests.RequestException, DecodeError, ValueError) as error:
            board = f"Could not load MTA arrivals: {error}"

        if args.refresh:
            print("\033[2J\033[H", end="")
        print(board, flush=True)

        if not args.refresh:
            return 0
        time.sleep(max(1, args.refresh))


if __name__ == "__main__":
    raise SystemExit(main())

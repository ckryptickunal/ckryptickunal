from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Tuple

import matplotlib.pyplot as plt
import numpy as np

WEEKDAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def _parse_date_hint(value: Optional[str], default: Optional[datetime]) -> Optional[datetime]:
	if value is None:
		return default
	value = value.strip()
	if not value:
		return default
	try:
		if value.endswith("d"):
			days = int(value[:-1])
			return datetime.now(timezone.utc) - timedelta(days=days)
		if value.endswith("h"):
			hours = int(value[:-1])
			return datetime.now(timezone.utc) - timedelta(hours=hours)
	except Exception:
		pass
	try:
		return datetime.strptime(value, "%Y-%m-%d").replace(tzinfo=timezone.utc)
	except Exception:
		return default


def _fetch_events(connection: sqlite3.Connection) -> List[Tuple[float, str]]:
	cursor = connection.execute("SELECT timestamp_utc, app_name FROM usage_events ORDER BY timestamp_utc ASC")
	return [(float(ts), str(app)) for ts, app in cursor.fetchall()]


def _accumulate_minutes_per_weekday_hour(events: List[Tuple[float, str]], until_dt: datetime) -> np.ndarray:
	# 7 weekdays x 24 hours
	grid = np.zeros((7, 24), dtype=float)
	if not events:
		return grid

	max_span_seconds = 10 * 60.0

	for idx, (ts, _app) in enumerate(events):
		start = datetime.fromtimestamp(ts, tz=timezone.utc)
		end = until_dt
		if idx + 1 < len(events):
			next_ts = events[idx + 1][0]
			end = min(end, datetime.fromtimestamp(next_ts, tz=timezone.utc))
		# Cap long spans
		if (end - start).total_seconds() > max_span_seconds:
			end = start + timedelta(seconds=max_span_seconds)
		if end <= start:
			continue
		current = start
		while current < end:
			next_hour_boundary = (current.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1))
			boundary = min(next_hour_boundary, end)
			minutes = (boundary - current).total_seconds() / 60.0
			weekday = current.weekday()  # 0..6
			hour = current.hour          # 0..23
			grid[weekday, hour] += minutes
			current = boundary
	return grid


def generate_heatmap(db_path: str, output_path: str, since: Optional[str] = None, until: Optional[str] = None) -> None:
	connection = sqlite3.connect(db_path)
	events = _fetch_events(connection)
	connection.close()

	if not events:
		print("No data found. Run the monitor first.")
		return

	# Filter by dates
	since_dt = _parse_date_hint(since, None)
	until_dt = _parse_date_hint(until, None) or datetime.now(timezone.utc)
	if since_dt is not None:
		events = [(ts, app) for ts, app in events if datetime.fromtimestamp(ts, tz=timezone.utc) >= since_dt]
	events = [(ts, app) for ts, app in events if datetime.fromtimestamp(ts, tz=timezone.utc) <= until_dt]

	if not events:
		print("No data in the selected range.")
		return

	grid = _accumulate_minutes_per_weekday_hour(events, until_dt)

	plt.figure(figsize=(14, 4))
	# imshow expects row-major; rows are weekdays, cols are hours
	im = plt.imshow(grid, aspect="auto", cmap="YlOrRd", interpolation="nearest")
	plt.colorbar(im, label="Minutes focused")
	plt.yticks(ticks=range(7), labels=WEEKDAY_NAMES)
	plt.xticks(ticks=range(24), labels=[str(h) for h in range(24)])
	plt.title("App usage focus heatmap (minutes per hour)")
	plt.xlabel("Hour of day")
	plt.ylabel("Weekday")
	plt.tight_layout()
	plt.savefig(output_path)
	print(f"Saved heatmap to {output_path}")
from __future__ import annotations

import os
import time
import psutil
from typing import Optional

from .db import get_connection, ensure_schema, insert_usage_event, UsageEvent

# We attempt to import X11 libs lazily to allow non-X11 environments to still import the module.
try:
	from Xlib import display
	from Xlib import X
	from Xlib.error import DisplayConnectionError
	from Xlib.X import AnyPropertyType
except Exception:  # pragma: no cover - import guard for non-X11 systems
	display = None  # type: ignore
	X = None  # type: ignore
	DisplayConnectionError = Exception  # type: ignore
	AnyPropertyType = 0  # type: ignore


def _get_active_window_info() -> Optional[tuple[str, str]]:
	if display is None:
		return None
	try:
		d = display.Display()
		root = d.screen().root
		NET_ACTIVE_WINDOW = d.intern_atom('_NET_ACTIVE_WINDOW')
		NET_WM_PID = d.intern_atom('_NET_WM_PID')
		NET_WM_NAME = d.intern_atom('_NET_WM_NAME')

		prop = root.get_full_property(NET_ACTIVE_WINDOW, AnyPropertyType)
		if prop is None or not prop.value:
			return None
		window_id = prop.value[0]
		window = d.create_resource_object('window', window_id)

		# Window title: try _NET_WM_NAME then fallback to WM_NAME
		window_title = None
		net_wm_name = window.get_full_property(NET_WM_NAME, 0)
		if net_wm_name and net_wm_name.value:
			try:
				window_title = net_wm_name.value.decode('utf-8', errors='ignore')
			except Exception:
				window_title = str(net_wm_name.value)
		if not window_title:
			try:
				window_title = window.get_wm_name()
			except Exception:
				window_title = None

		# Process name from PID
		pid = None
		pid_prop = window.get_full_property(NET_WM_PID, AnyPropertyType)
		if pid_prop and pid_prop.value:
			pid = int(pid_prop.value[0])
		app_name = None
		if pid:
			try:
				proc = psutil.Process(pid)
				app_name = proc.name()
			except Exception:
				app_name = None

		if app_name is None:
			# Fallback: use window class
			try:
				klass = window.get_wm_class()
				if klass:
					app_name = klass[-1]
			except Exception:
				app_name = None

		if app_name is None:
			app_name = "unknown"
		if window_title is None:
			window_title = ""

		return app_name, window_title
	finally:
		try:
			d.close()
		except Exception:
			pass


def run_monitor(db_path: str, poll_interval: float = 1.0) -> None:
	connection = get_connection(db_path)
	ensure_schema(connection)

	last_seen: Optional[tuple[str, str]] = None
	while True:
		info = _get_active_window_info()
		if info is not None and info != last_seen:
			app_name, window_title = info
			event = UsageEvent(timestamp_utc=time.time(), app_name=app_name, window_title=window_title)
			insert_usage_event(connection, event)
			last_seen = info
		time.sleep(poll_interval)
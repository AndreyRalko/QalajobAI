"""Probe local LMS MySQL (manual SSH tunnel must already be open).

Example:
  ssh -L 6080:localhost:6080 user@lms-host
  python scripts/probe_lms_mysql.py
"""
import os
import sys

import django

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.conf import settings

from apps.lms_sync.services.mysql_client import fetch_rows, lms_mysql_connection


def main():
    host = settings.LMS_MYSQL_HOST
    port = settings.LMS_MYSQL_PORT
    print(f"Connecting to {host}:{port} / db={settings.LMS_MYSQL_DB}")
    with lms_mysql_connection() as connection:
        rows = fetch_rows(connection, "SELECT DATABASE() AS db, NOW() AS now_ts")
        print(rows[0] if rows else "No rows")
        count_rows = fetch_rows(
            connection,
            "SELECT COUNT(*) AS students FROM students WHERE isStudent = 1",
        )
        print(count_rows[0] if count_rows else "students count unavailable")
    print("OK")


if __name__ == "__main__":
    main()

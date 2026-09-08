"""Gunicorn config for Linux production behind nginx."""

import multiprocessing
import os

bind = os.environ.get("GUNICORN_BIND", "127.0.0.1:8088")
workers = int(os.environ.get("GUNICORN_WORKERS", max(multiprocessing.cpu_count() * 2 + 1, 3)))
threads = int(os.environ.get("GUNICORN_THREADS", "2"))
timeout = int(os.environ.get("GUNICORN_TIMEOUT", "120"))
keepalive = 5
accesslog = "-"
errorlog = "-"
loglevel = os.environ.get("GUNICORN_LOG_LEVEL", "info")
capture_output = True
preload_app = True

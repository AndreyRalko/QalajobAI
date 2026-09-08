import logging
from contextlib import contextmanager

import pymysql
from django.conf import settings
from pymysql.cursors import DictCursor
from pymysql.err import OperationalError

logger = logging.getLogger(__name__)


def configure_mysql_session(connection):
    timeout = settings.LMS_MYSQL_READ_TIMEOUT
    with connection.cursor() as cursor:
        cursor.execute("SET SESSION wait_timeout = %s", (max(timeout * 2, 3600),))
        cursor.execute("SET SESSION net_read_timeout = %s", (timeout,))
        cursor.execute("SET SESSION net_write_timeout = %s", (timeout,))


@contextmanager
def lms_mysql_connection():
    """
    Connect to LMS MySQL on a local forwarded port.

    Open the SSH tunnel manually first, e.g.:
      ssh -L 6080:localhost:6080 user@lms-host
    Then run:
      python manage.py sync_lms_daily --students-only
    """
    host = settings.LMS_MYSQL_HOST
    port = settings.LMS_MYSQL_PORT

    if not settings.LMS_MYSQL_DB or not settings.LMS_MYSQL_USER:
        raise RuntimeError(
            "LMS MySQL is not configured. Set LMS_MYSQL_DB and LMS_MYSQL_USER in .env"
        )

    logger.info(
        "Connecting to LMS MySQL %s at %s:%s (manual tunnel must already be open)",
        settings.LMS_MYSQL_DB,
        host,
        port,
    )
    try:
        connection = pymysql.connect(
            host=host,
            port=port,
            user=settings.LMS_MYSQL_USER,
            password=settings.LMS_MYSQL_PASSWORD,
            database=settings.LMS_MYSQL_DB,
            charset="utf8mb4",
            cursorclass=DictCursor,
            connect_timeout=settings.LMS_MYSQL_CONNECT_TIMEOUT,
            read_timeout=settings.LMS_MYSQL_READ_TIMEOUT,
            write_timeout=settings.LMS_MYSQL_READ_TIMEOUT,
            autocommit=True,
        )
    except OperationalError as exc:
        raise RuntimeError(
            f"Cannot reach LMS MySQL at {host}:{port}. "
            f"Open the SSH tunnel manually first, for example: "
            f"ssh -L {port}:localhost:{port} user@lms-host "
            f"Then rerun the sync command. Original error: {exc}"
        ) from exc

    try:
        configure_mysql_session(connection)
        yield connection
    except OperationalError as exc:
        raise RuntimeError(
            f"LMS MySQL connection failed at {host}:{port}. "
            f"Check that the manual SSH tunnel is still open. Original error: {exc}"
        ) from exc
    finally:
        logger.info("Closing LMS MySQL connection")
        connection.close()


def fetch_rows(connection, sql, params=None, *, retry=True):
    params = params or ()
    attempts = 2 if retry else 1
    last_error = None

    for attempt in range(1, attempts + 1):
        try:
            connection.ping(reconnect=True)
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                return cursor.fetchall()
        except OperationalError as exc:
            last_error = exc
            logger.warning(
                "MySQL query failed (attempt %s/%s): %s",
                attempt,
                attempts,
                exc,
            )
            if attempt >= attempts:
                raise
            connection.ping(reconnect=True)

    raise last_error

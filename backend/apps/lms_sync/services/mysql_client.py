import logging
from contextlib import contextmanager

import pymysql
from django.conf import settings
from pymysql.cursors import DictCursor
from pymysql.err import OperationalError

from .ssh_tunnel import lms_ssh_tunnel

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
    Open SSH tunnel, connect to LMS MySQL, yield connection.
    Tunnel and connection are closed on exit.
    """
    with lms_ssh_tunnel() as local_port:
        logger.info(
            "Connecting to LMS MySQL %s via localhost:%s",
            settings.LMS_MYSQL_DB,
            local_port,
        )
        try:
            connection = pymysql.connect(
                host="127.0.0.1",
                port=local_port,
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
            remote = f"{settings.LMS_MYSQL_REMOTE_HOST}:{settings.LMS_MYSQL_REMOTE_PORT}"
            raise RuntimeError(
                f"Cannot reach LMS MySQL at {remote} through SSH tunnel. "
                f"On Platonus servers MySQL is often on localhost:6080 "
                f"(ssh -L 6080:localhost:6080 user@host). Original error: {exc}"
            ) from exc
        try:
            configure_mysql_session(connection)
            yield connection
        except OperationalError as exc:
            remote = f"{settings.LMS_MYSQL_REMOTE_HOST}:{settings.LMS_MYSQL_REMOTE_PORT}"
            raise RuntimeError(
                f"Cannot reach LMS MySQL at {remote} through SSH tunnel. "
                f"On Platonus servers MySQL is often on localhost:6080 "
                f"(ssh -L 6080:localhost:6080 user@host). Original error: {exc}"
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

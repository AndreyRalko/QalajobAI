import logging
from contextlib import contextmanager
from pathlib import Path

from django.conf import settings

logger = logging.getLogger(__name__)


@contextmanager
def lms_ssh_tunnel():
    """
    Open SSH tunnel to the LMS server and yield local bind port for MySQL.
    Tunnel is closed automatically when the context exits.
    """
    from apps.lms_sync.services.paramiko_compat import ensure_paramiko_dsskey_compat

    ensure_paramiko_dsskey_compat()
    from sshtunnel import SSHTunnelForwarder

    ssh_host = settings.LMS_SSH_HOST
    ssh_port = settings.LMS_SSH_PORT
    ssh_user = settings.LMS_SSH_USER
    ssh_password = settings.LMS_SSH_PASSWORD or None
    ssh_pkey_path = settings.LMS_SSH_PKEY_PATH or None

    if not ssh_host or not ssh_user:
        raise RuntimeError("LMS SSH is not configured (LMS_SSH_HOST, LMS_SSH_USER).")

    ssh_pkey = None
    if ssh_pkey_path:
        key_path = Path(ssh_pkey_path)
        if not key_path.is_file():
            raise RuntimeError(f"LMS SSH private key not found: {key_path}")
        ssh_pkey = str(key_path)

    if not ssh_password and not ssh_pkey:
        raise RuntimeError("Set LMS_SSH_PASSWORD or LMS_SSH_PKEY_PATH for SSH auth.")

    remote_mysql_host = settings.LMS_MYSQL_REMOTE_HOST
    remote_mysql_port = settings.LMS_MYSQL_REMOTE_PORT

    logger.info(
        "Opening SSH tunnel to %s@%s:%s -> %s:%s",
        ssh_user,
        ssh_host,
        ssh_port,
        remote_mysql_host,
        remote_mysql_port,
    )

    tunnel = SSHTunnelForwarder(
        (ssh_host, ssh_port),
        ssh_username=ssh_user,
        ssh_password=ssh_password,
        ssh_pkey=ssh_pkey,
        remote_bind_address=(remote_mysql_host, remote_mysql_port),
        local_bind_address=("127.0.0.1", 0),
        set_keepalive=30.0,
    )
    tunnel.start()

    try:
        local_port = tunnel.local_bind_port
        logger.info("SSH tunnel ready on 127.0.0.1:%s", local_port)
        yield local_port
    finally:
        logger.info("Closing SSH tunnel to %s", ssh_host)
        tunnel.stop()

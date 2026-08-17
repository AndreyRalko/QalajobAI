"""Probe remote server for MySQL port via SSH. Run: python scripts/probe_lms_mysql.py"""
import os
import sys

import django

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.conf import settings

from apps.lms_sync.services.paramiko_compat import ensure_paramiko_dsskey_compat

ensure_paramiko_dsskey_compat()
import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(
    settings.LMS_SSH_HOST,
    port=settings.LMS_SSH_PORT,
    username=settings.LMS_SSH_USER,
    password=settings.LMS_SSH_PASSWORD,
    timeout=15,
)

commands = [
    "hostname",
    "hostname -I 2>/dev/null || true",
    "ss -tln 2>/dev/null | grep 330 || true",
    "netstat -tln 2>/dev/null | grep 330 || true",
    "ps aux 2>/dev/null | grep -i mysql | grep -v grep || true",
    "sudo ss -tlnp 2>/dev/null | grep -E '3306|mysql' || ss -tlnp 2>/dev/null | grep -E '3306|mysql' || true",
    "ls -la /var/run/mysqld/ 2>/dev/null || ls -la /tmp/mysql.sock 2>/dev/null || true",
    "cat /proc/3656251/cgroup 2>/dev/null | head -5 || true",
    "tr '\\0' ' ' </proc/3656251/cmdline 2>/dev/null; echo",
    "readlink /proc/3656251/root 2>/dev/null || true",
    "podman ps -a 2>/dev/null | head -10 || true",
    "docker inspect dd5b5aafb408 2>/dev/null | grep -E 'IPAddress|3306' | head -20 || true",
    "docker port dd5b5aafb408 2>/dev/null || true",
    "for i in 2 3 4 5 6 7 8 9 10; do timeout 1 bash -c \"echo >/dev/tcp/172.17.0.$i/3306\" 2>/dev/null && echo OPEN 172.17.0.$i:3306; done",
    "for i in 2 3 4 5 6 7 8 9 10; do timeout 1 bash -c \"echo >/dev/tcp/128.10.0.$i/3306\" 2>/dev/null && echo OPEN 128.10.0.$i:3306; done",
    "timeout 1 bash -c \"echo >/dev/tcp/127.0.0.1/6080\" 2>/dev/null && echo OPEN 127.0.0.1:6080 || echo CLOSED 127.0.0.1:6080",
    "timeout 1 bash -c \"echo >/dev/tcp/127.0.0.1/3306\" 2>/dev/null && echo OPEN 127.0.0.1:3306 || echo CLOSED 127.0.0.1:3306",
]

for cmd in commands:
    print(f"\n$ {cmd}")
    _, stdout, stderr = client.exec_command(cmd, timeout=15)
    out = stdout.read().decode(errors="replace").strip()
    err = stderr.read().decode(errors="replace").strip()
    if out:
        print(out.encode("ascii", errors="replace").decode("ascii"))
    if err:
        print("stderr:", err)

client.close()

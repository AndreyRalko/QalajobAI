"""Compatibility helpers for sshtunnel + paramiko>=4."""


def ensure_paramiko_dsskey_compat():
    """
    sshtunnel 0.4.0 references paramiko.DSSKey at import time.
    Paramiko 4+ removed DSA support — provide a stub so password/RSA auth still works.
    """
    import paramiko

    if hasattr(paramiko, "DSSKey"):
        return

    class _DSSKeyRemoved(paramiko.PKey):
        def __init__(self, *args, **kwargs):
            raise paramiko.SSHException(
                "DSA keys are not supported by paramiko>=4"
            )

    paramiko.DSSKey = _DSSKeyRemoved

import pkg_resources

from .extension import FormExtension

try:  # pragma: no cover
    __version__ = pkg_resources.get_distribution("mdform").version
except Exception:  # pragma: no cover
    # we seem to have a local copy not installed without setuptools
    # so the reported version will be unknown
    __version__ = "unknown"

__all__ = (FormExtension, __version__)

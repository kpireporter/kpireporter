import warnings

from .datasource import MySQLDatasource

__all__ = ["MySQLDatasource"]

warnings.warn(
    "kpireport-mysql has been deprecated in favor of kpireport-sql",
    DeprecationWarning
)

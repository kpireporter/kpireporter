from abc import ABC, abstractmethod
from datetime import datetime

from authlib.jose import jwt
from authlib.jose.errors import BadSignatureError, ExpiredTokenError, JoseError
from jinja2 import Markup

from . import license_keys

URL_PRICING = "https://kpireporter.com/pricing/"
URL_DOCS = "https://kpi-reporter.readthedocs.io/en/latest/"


def link(fmt, url, text=None):
    label = text or url
    if fmt == "html":
        return f'<a href="{url}">{label}</a>'
    elif fmt == "md":
        return f"[{label}]({url})"
    elif fmt == "slack":
        return f"<{label}|{url}>"
    else:
        return label


def strong(fmt, text):
    if fmt == "html":
        return f"<strong>{text}</strong>"
    elif fmt == "md":
        return f"**{text}**"
    elif fmt == "slack":
        return f"*{text}*"
    else:
        return text


def join(fmt, lines):
    if fmt == "html":
        return "<br>".join(lines)
    else:
        return "\n\n".join(lines)


class LicenseState(ABC):
    @abstractmethod
    def render(self, fmt: str):
        pass


class OKState(LicenseState):
    def __init__(self, claims):
        self.claims = claims
        assert self.claims is not None

    def render(self, fmt):
        exp_date = datetime.utcfromtimestamp(self.claims["exp"])
        expires = datetime.strftime(exp_date, "%Y-%m-%d")
        return f"Licensed to {self.claims['name']} until {expires}."


class ExpiredState(LicenseState):
    def __init__(self, claims):
        self.claims = claims
        assert self.claims is not None

    def render(self, fmt):
        exp_date = datetime.utcfromtimestamp(self.claims["exp"])
        expires = datetime.strftime(exp_date, "%Y-%m-%d")
        return join(
            fmt,
            [
                self.strong(fmt, f"Your license expired on {expires}."),
                (
                    f"Please {link(fmt, URL_PRICING, 'renew your license')} to "
                    "continue using KPI Reporter."
                ),
            ],
        )


class InvalidState(LicenseState):
    def render(self, fmt):
        return join(
            fmt,
            [
                strong(
                    fmt, "Your license is invalid or malformed and cannot be verified."
                ),
                (
                    f"Please consult the {link(fmt, URL_DOCS, 'documentation')} for "
                    "possible fixes."
                ),
            ],
        )


class UnlicensedState(LicenseState):
    def render(self, fmt):
        return join(
            fmt,
            [
                strong(fmt, "This instance of KPI Reporter is unlicensed."),
                "KPI Reporter is free for personal and noncommercial use.",
                (
                    "Commercial users must "
                    f"{str(link(fmt, URL_PRICING, 'purchase a license'))}."
                ),
            ],
        )


class License:
    claims = None
    rendered = False

    def __init__(self, license_jwt):
        self.state = UnlicensedState()

        if license_jwt:
            for key in license_keys:
                try:
                    self.claims = jwt.decode(license_jwt, key)
                    self.claims.validate()
                    # Key is valid, signature is OK, and license not expired.
                    self.state = OKState(self.claims)
                    break
                except ExpiredTokenError:
                    # Key is valid and signature is OK, but license has expired.
                    self.state = ExpiredState(self.claims)
                    break
                except JoseError:
                    # Malformed token or key not valid for token.
                    self.state = InvalidState()

    def render(self, fmt=None):
        self.rendered = True
        return Markup(self.state.render(fmt))

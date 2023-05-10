import abc
from typing import Dict, Literal, Union

from pydantic import BaseModel


# ==== auth ====
class BaseManifestAuth(abc.ABC, BaseModel):
    type: str


class ManifestNoAuth(BaseManifestAuth):
    type = "none"


class ManifestServiceHttpAuth(BaseManifestAuth):
    type = "service_http"
    authorization_type: Literal["bearer", "basic"]
    verification_tokens: Dict[str, str]


class ManifestUserHttpAuth(BaseManifestAuth):
    type = "user_http"
    authorization_type: Literal["bearer", "basic"]


class ManifestOAuthAuth(BaseManifestAuth):
    type = "oauth"
    client_url: str
    scope: str
    authorization_url: str
    authorization_content_type: str
    verification_tokens: Dict[str, str]


# ==== openapi ====
class ApiSpec(BaseModel):
    type: str
    url: str
    is_user_authenticated: bool

    @classmethod
    def openapi(cls, url: str):
        return cls(type="openapi", url=url, is_user_authenticated=False)


# ==== manifest ====
class PluginManifest(BaseModel):
    schema_version: Literal["v1"]
    name_for_model: str
    name_for_human: str
    description_for_model: str
    description_for_human: str
    auth: Union[ManifestServiceHttpAuth, ManifestUserHttpAuth, ManifestOAuthAuth, ManifestNoAuth]
    api: ApiSpec
    logo_url: str
    contact_email: str
    legal_info_url: str

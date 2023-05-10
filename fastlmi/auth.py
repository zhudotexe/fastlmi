import abc
from typing import Annotated, Dict, List, Literal, Optional

from fastapi import HTTPException, Header
from starlette import status

from fastlmi import ai_plugin


class LMIAuth(abc.ABC):
    def ai_plugin(self) -> ai_plugin.BaseManifestAuth:
        """Returns the auth manifest for the AI Plugin interface"""
        raise NotImplementedError

    def __call__(self, authorization: Annotated[Optional[str], Header] = None):
        """
        The auth scheme can be used as a dependency and should check authentication before calling into the route
        function.

        You can require auth on all endpoints:

        >>> auth = LMIAuth(...)
        >>> app = FastLMI(auth=auth, dependencies=[Depends(auth)], ...)
        >>>
        >>> @app.post("/hello")
        ... def hello():
        ...     ...

        or on only certain endpoints:

        >>> auth = LMIAuth(...)
        >>> app = FastLMI(auth=auth, ...)
        >>>
        >>> @app.post("/hello", dependencies=[Depends(auth)])
        ... def hello():
        ...     ...
        """
        raise NotImplementedError


class LMINoAuth(LMIAuth):
    """
    No authentication; anyone is allowed to call these endpoints. This auth scheme exists so that other auth schemes
    can be used as a drop-in replacement in the future; if you do not intend to ever add auth, you can instead pass
    (or omit) ``auth=None`` to the ``FastLMI`` constructor.
    """

    def ai_plugin(self) -> ai_plugin.ManifestNoAuth:
        return ai_plugin.ManifestNoAuth()

    def __call__(self, authorization: Annotated[Optional[str], Header()] = None):
        return True


class LMIServiceAuth(LMIAuth):
    """
    Service-level auth: the AI agent or LMI driver will send an authorization token you decide as a header with each
    request.

    This auth scheme allows defining a set of allowed access tokens (if one wanted to, for example, have a different
    token for each plugin service).

    Example (auth on all endpoints):

    >>> auth = LMIServiceAuth(
    ...     access_tokens=["your_secret_token_here"],
    ...     verification_tokens={"openai": "verification_token_generated_in_the_ChatGPT_UI"}
    ... )
    >>> app = FastLMI(auth=auth, dependencies=[Depends(auth)], ...)
    >>>
    >>> @app.post("/hello")
    ... def hello():
    ...     ...

    Example (auth on only specific endpoints):

    >>> auth = LMIServiceAuth(
    ...     access_tokens=["your_secret_token_here"],
    ...     verification_tokens={"openai": "verification_token_generated_in_the_ChatGPT_UI"}
    ... )
    >>> app = FastLMI(auth=auth, ...)
    >>>
    >>> @app.post("/hello", dependencies=[Depends(auth)])
    ... def hello():
    ...     ...
    """

    def __init__(
        self,
        access_tokens: List[str],
        authorization_type: Literal["bearer", "basic"] = "bearer",
        verification_tokens: Dict[str, str] = None,
    ):
        if verification_tokens is None:
            verification_tokens = {}
        if authorization_type not in ("bearer", "basic"):
            raise ValueError(f"Expected authorization type to be 'bearer' or 'basic' but got {authorization_type!r}")
        self.access_tokens = set(access_tokens)
        self.authorization_type = authorization_type
        self.verification_tokens = verification_tokens

    def ai_plugin(self) -> ai_plugin.ManifestServiceHttpAuth:
        return ai_plugin.ManifestServiceHttpAuth(
            authorization_type=self.authorization_type, verification_tokens=self.verification_tokens
        )

    def __call__(self, authorization: Annotated[Optional[str], Header()] = None):
        if authorization is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Expected authorization token")
        if self.authorization_type == "bearer":
            if not authorization.startswith("Bearer "):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Malformed authorization token")
            if authorization.removeprefix("Bearer ") not in self.access_tokens:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid authorization token")
            return True
        elif self.authorization_type == "basic":
            if not authorization.startswith("Basic "):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Malformed authorization token")
            if authorization.removeprefix("Basic ") not in self.access_tokens:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid authorization token")
            return True
        raise ValueError(f"Expected authorization type to be 'bearer' or 'basic' but got {self.authorization_type!r}")

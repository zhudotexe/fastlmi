from typing import Optional

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from starlette.requests import Request
from starlette.responses import JSONResponse

from fastlmi import openai


class FastLMI(FastAPI):
    def __init__(
        self,
        *,
        title: str,
        description: str,
        contact_email: str,  # todo maybe make these optional and have option to enable openai?
        legal_url: str,
        openai_manifest_url: Optional[str] = "/.well-known/ai-plugin.json",
        name_for_model: Optional[str] = None,
        description_for_model: Optional[str] = None,
        logo_url: Optional[str] = None,  # todo could be fun to add a func to serve image
        **kwargs,
    ):
        """
        :param title: Human-readable name, such as the full company name
        :param description: Human-readable description of the application
        :param contact_email: Email contact for safety/moderation, support, and deactivation
        :param legal_url: Redirect URL for users to view the application's legal information (e.g. Terms of Service)
        :param openai_manifest_url: The path to expose the OpenAI plugin manifest at
        :param name_for_model: Name the model will use to target the plugin (no spaces allowed, only letters and
            numbers)
        :param description_for_model: Description better tailored to the model, such as token context length
            considerations or keyword usage for improved plugin prompting
        :param logo_url: URL the logo image is hosted at (can be relative to root or external URL)
        :param kwargs: Extra options to pass to FastAPI
        """
        self.openai_manifest_url = openai_manifest_url
        self.name_for_model = name_for_model or title
        self.description_for_model = description_for_model or description
        self.contact_email = contact_email
        self.legal_url = legal_url
        self.logo_url = logo_url
        # pass some reasonable defaults on to FastAPI
        kwargs.setdefault("terms_of_service", legal_url)
        kwargs.setdefault("contact", {"email": contact_email})
        super().__init__(title=title, description=description, **kwargs)

    def setup(self) -> None:
        super().setup()
        if self.openapi_url and self.openai_manifest_url:
            self.add_route(self.openai_manifest_url, self.openai_plugin_manifest, include_in_schema=False)

    def openai_plugin_manifest(self, req: Request) -> JSONResponse:
        # see https://platform.openai.com/docs/plugins/getting-started/plugin-manifest
        # <scheme>://<netloc>/<path>?<query>#<fragment>
        # rewrite path to root_path, then tack on the relative urls to point to the right endpoints
        components = req.url.components
        scheme = components.scheme
        netloc = components.netloc
        root_path = req.scope.get("root_path", "")
        root_url = f"{scheme}://{netloc}/{root_path}".rstrip("/")
        openapi_url = root_url + self.openapi_url
        if self.logo_url and self.logo_url.startswith("/"):
            logo_url = root_url + self.logo_url
        else:
            logo_url = self.logo_url or "https://public.mechanus.zhu.codes/fastlmi_logo.png"
        return JSONResponse(
            jsonable_encoder(
                openai.PluginManifest(
                    schema_version="v1",
                    name_for_human=self.title,
                    name_for_model=self.name_for_model,
                    description_for_human=self.description,
                    description_for_model=self.description_for_model,
                    auth=openai.ManifestNoAuth(),
                    api=openai.ApiSpec.openapi(openapi_url),
                    logo_url=logo_url,
                    contact_email=self.contact_email,
                    legal_info_url=self.legal_url,
                )
            )
        )

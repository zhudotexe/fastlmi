from starlette.middleware.cors import CORSMiddleware


def cors_allow_openai(app):
    """
    Add CORS middleware to an app to allow requests from chat.openai.com (for localhost plugins).
    This utility is provisional.
    """
    app.add_middleware(
        CORSMiddleware, allow_origins=["https://chat.openai.com"], allow_methods=["*"], allow_headers=["*"]
    )
    return app

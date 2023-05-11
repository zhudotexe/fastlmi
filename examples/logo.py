"""
By default, FastLMI will use the FastLMI logo for all apps that do not specify their own logo.

You have 2 options to specify a custom logo:

1. An externally hosted logo (e.g. on a CDN). To specify this, set `logo_url` to the url of the image.
2. An internally hosted logo (i.e. FastLMI will serve an image saved on disk).

Whichever you choose, FastLMI will expose the right absolute URL in generated LMI metadata.
"""
from fastlmi import FastLMI

# externally-hosted logo
app = FastLMI(
    title="External Logo Demo",
    description="Demonstrates how to define a FastLMI app with a custom logo.",
    logo_url="https://public.mechanus.zhu.codes/fastlmi_logo.png",
)

# internally-hosted logo
app2 = FastLMI(
    title="Internal Logo Demo",
    description="Demonstrates how to define a FastLMI app with a custom logo.",
)
app2.serve_local_logo(path="logo.png", url="/logo.png")

# define routes as usual...

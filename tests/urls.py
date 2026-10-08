from django.urls import path
from django.urls.resolvers import URLPattern, URLResolver

from tests.browser.preview import preview_css, preview_form

urlpatterns: list[URLPattern | URLResolver] = [
    path("__preview__/", preview_form, name="form_preview"),
    path("__preview__/daisy-forms.css", preview_css, name="form_preview_css"),
]

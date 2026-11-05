from django.urls import path
from django.urls.resolvers import URLPattern, URLResolver

from tests.browser.preview import (
    preview_css,
    preview_form,
    preview_formset,
    preview_formset_js,
)

urlpatterns: list[URLPattern | URLResolver] = [
    path("__preview__/", preview_form, name="form_preview"),
    path("__preview__/daisy-forms.css", preview_css, name="form_preview_css"),
    path("__preview__/formset/", preview_formset, name="formset_preview"),
    path("__preview__/formset.js", preview_formset_js, name="formset_preview_js"),
]

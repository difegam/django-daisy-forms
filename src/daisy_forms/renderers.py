"""Django form renderer configuration."""

from django.forms.renderers import TemplatesSetting

from .boundfield import DaisyBoundField


class DaisyFormRenderer(TemplatesSetting):
    form_template_name = "daisy_forms/form.html"
    formset_template_name = "daisy_forms/formset.html"
    field_template_name = "daisy_forms/field.html"
    bound_field_class = DaisyBoundField

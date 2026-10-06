from django.contrib.admin import AdminSite
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import AnonymousUser, User
from django.template import Context, Template
from django.test import override_settings
from django.test.client import RequestFactory


@override_settings(FORM_RENDERER="daisy_forms.renderers.DaisyFormRenderer")
def test_admin_model_form_renders_with_daisy_renderer() -> None:
    site = AdminSite(name="test")
    model_admin = UserAdmin(User, site)
    request = RequestFactory().get("/admin/auth/user/add/")
    request.user = AnonymousUser()
    form_class = model_admin.get_form(request)

    output = Template("{{ form }}").render(Context({"form": form_class()}))

    assert '<div class="fieldset">' in output
    assert 'class="input' in output

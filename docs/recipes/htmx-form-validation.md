# Whole-form validation with HTMX 2

Keep validation in Django. A regular POST renders the full page with bound-field errors. An HTMX POST replaces the form with the server-rendered form fragment when invalid (status `422`) or with a success fragment when valid. The package does not install or configure HTMX.

## View

The example assumes a ContactForm and contact URL, with successful submissions handled at the marked point.

```python
from django.shortcuts import render
from django.views.decorators.vary import vary_on_headers

from .forms import ContactForm


@vary_on_headers("HX-Request")
def contact(request):
    form = ContactForm(request.POST if request.method == "POST" else None)
    valid = False

    if request.method == "POST":
        valid = form.is_valid()
        if valid:
            # Save or otherwise process form.cleaned_data here.
            if request.headers.get("HX-Request") == "true":
                return render(request, "contact/_success.html")

        elif request.headers.get("HX-Request") == "true":
            return render(
                request,
                "contact/_form.html",
                {"form": form},
                status=422,
            )

    return render(
        request,
        "contact/page.html",
        {"form": form, "submitted": valid},
    )
```

`HX-Request` is only a response-format hint; it is not a security boundary.
`Vary: HX-Request` keeps caches from serving a fragment to a full-page request
or vice versa. For normal POSTs, the view renders the full page whether the
form is invalid or valid. Applications may redirect after successful normal
submissions if that better fits their flow.

## Templates

The page template includes the form fragment used for both normal and HTMX responses:

```django
{# contact/page.html #}
{% extends "base.html" %}
{% block content %}
  {% if submitted %}<p role="status">Your message was received.</p>{% endif %}
  {% include "contact/_form.html" %}
{% endblock %}
```

The fragment keeps a stable id so outerHTML can replace it. Configure HTMX to swap `422` responses:

```html
<meta name="htmx-config" content='{"responseHandling":[
  {"code":"204","swap":false},
  {"code":"[23]..","swap":true},
  {"code":"422","swap":true},
  {"code":"[45]..","swap":false,"error":true},
  {"code":"...","swap":false}
]}' />
```

```django
{# contact/_form.html #}
{% load daisy_forms %}
<form id="contact-form" method="post" action="{% url 'contact' %}"
      hx-post="{% url 'contact' %}" hx-target="#contact-form"
      hx-swap="outerHTML">
  {% csrf_token %}
  {% daisy_field form.name %}
  {% daisy_field form.email %}
  {% daisy_field form.message %}
  <button class="btn btn-primary" type="submit">Send message</button>
</form>
```

```html
<!-- contact/_success.html -->
<div id="contact-form" role="status" class="alert alert-success">
  Your message was received.
</div>
```

Django renders help text, field errors, aria-invalid and aria-describedby normally. The browser swaps the HTML; no client-side validation code or middleware is needed. See the [HTMX 2 response-handling documentation](https://htmx.org/docs/#response-handling) for more on status handling.

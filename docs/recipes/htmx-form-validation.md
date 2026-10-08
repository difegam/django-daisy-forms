# Whole-form validation with HTMX 2

This recipe keeps validation in Django. A regular POST renders the full page
with bound-field errors. An HTMX POST replaces the form with the same
server-rendered form fragment when invalid, using status `422`, or with a
success fragment when valid. The package does not install or configure HTMX.

## View

The example assumes a `ContactForm`, a `contact` URL, and that successful
submissions are handled by the application at the marked point.

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

The page template includes the same form fragment used for the invalid HTMX
response:

```django
{# contact/page.html #}
{% extends "base.html" %}
{% block content %}
  {% if submitted %}<p role="status">Your message was received.</p>{% endif %}
  {% include "contact/_form.html" %}
{% endblock %}
```

The fragment keeps a stable id so `outerHTML` can replace it with another form
fragment or the success fragment. The HTMX configuration preserves the other
HTMX 2 response defaults while making `422` responses swappable:

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

Django renders the invalid form's help text, field errors,
`aria-invalid` and `aria-describedby` in the usual way. The browser only swaps
that HTML; no client-side validation code or package middleware is needed.

See the [HTMX 2 response-handling documentation](https://htmx.org/docs/#response-handling)
for the status handling configuration described here.

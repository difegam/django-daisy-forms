# htmx validation

Django validation stays authoritative. htmx only swaps server-rendered HTML. The
package does not install or configure htmx.

## Allow 422 swaps (required)

htmx 2 does not swap `4xx` responses by default. Add this once to the base template.
It keeps the other defaults:

```html
<meta name="htmx-config" content='{"responseHandling":[
  {"code":"204","swap":false},
  {"code":"[23]..","swap":true},
  {"code":"422","swap":true},
  {"code":"[45]..","swap":false,"error":true},
  {"code":"...","swap":false}
]}' />
```

## Per-field validation (on blur)

A field group has several sibling elements (control, help text, errors), so wrap it in
an element with a stable id and swap that wrapper.

```django
{# products/_price_field.html #}
{% load daisy_forms %}
{% url "products:validate_price" as validate_price_url %}
<div id="price-field">
  {% daisy_field form.price prefix="$" suffix="USD" class+="input-sm" hx-post=validate_price_url hx-trigger="blur changed" hx-target="#price-field" hx-swap="outerHTML" %}
</div>
```

Include the partial inside the `<form>` that holds `{% csrf_token %}`
(`{% include "products/_price_field.html" %}`). For non-GET requests, htmx sends the
enclosing form's values, including the CSRF token.

Validate with the real form so the rules live in one place:

```python
from django.shortcuts import render
from django.views.decorators.http import require_POST

from .forms import ProductForm


@require_POST
def validate_price(request):
    form = ProductForm(request.POST)
    form.is_valid()
    status = 422 if "price" in form.errors else 200
    return render(request, "products/_price_field.html", {"form": form}, status=status)
```

Errors from other fields are ignored because only the `price` partial is rendered. A
`ModelForm` that edits an object needs the same instance as the edit view. Take the pk
from the URL (`path("<int:pk>/validate-price/", ...)`) and pass
`instance=get_object_or_404(Product, pk=pk)`, so uniqueness and model validation match.

## Whole-form submission

```python
from django.shortcuts import render
from django.views.decorators.vary import vary_on_headers


@vary_on_headers("HX-Request")
def contact(request):
    form = ContactForm(request.POST if request.method == "POST" else None)
    if request.method == "POST":
        if form.is_valid():
            # process form.cleaned_data
            if request.headers.get("HX-Request") == "true":
                return render(request, "contact/_success.html")
        elif request.headers.get("HX-Request") == "true":
            return render(request, "contact/_form.html", {"form": form}, status=422)
    return render(request, "contact/page.html", {"form": form})
```

```django
{# contact/_form.html, included by page.html #}
{% url "contact" as contact_url %}
<form id="contact-form" method="post" action="{{ contact_url }}"
      hx-post="{{ contact_url }}" hx-target="#contact-form" hx-swap="outerHTML">
  {% csrf_token %}
  {{ form }}
  <button class="btn btn-primary" type="submit">Send</button>
</form>
```

`_success.html` keeps `id="contact-form"` so later swaps still find their target.
`HX-Request` is a response-format hint, not a security boundary.

## Do not

- Return `200` or `400` for invalid input. Use `422` with the config above.
- Duplicate validation rules in a separate "validation" form or in JavaScript.
- Use `hx-on*`, `on*` or `x-on*` in `{% daisy_field %}`. They raise
  `TemplateSyntaxError`. Put behavior in `hx-*` attributes or a script.

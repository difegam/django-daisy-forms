# Validation & errors

django-daisy-forms keeps validation server-authoritative. Errors come from Django's validation, and the package renders them accessibly using the same `aria` attributes Django already generates.

## How errors are rendered

When a field fails validation, the package:

1. Adds `aria-invalid="true"` to the control
2. Renders an error list with `id="{auto_id}_error"`
3. Adds `aria-describedby="{auto_id}_helptext {auto_id}_error"` to link the control to both help text and errors
4. Applies the `-error` variant to the daisyUI component class

Example of an invalid email field:

```html
<div class="fieldset">
  <label class="fieldset-legend" for="id_email">Email</label>
  <p class="label" id="id_email_helptext">We never share it.</p>
  <ul class="text-error text-sm" id="id_email_error">
    <li>Enter a valid email address.</li>
  </ul>
  <input type="email" name="email" value="invalid"
         class="input input-error w-full"
         aria-invalid="true"
         aria-describedby="id_email_helptext id_email_error"
         id="id_email">
</div>
```

## Error IDs

The error list uses `id="{auto_id}_error"`, which matches Django's `aria_describedby` property. Django builds this attribute from:

- `{auto_id}_helptext` — when help text exists
- `{auto_id}_error` — when errors exist

The package renders both elements with the correct IDs, so `aria-describedby` works automatically.

## Help text

Help text is rendered with `id="{auto_id}_helptext"` and is always present when set, even if the field is valid:

```html
<p class="label" id="id_email_helptext">We never share it.</p>
```

Help text is escaped unless it is marked safe with `mark_safe()`. This is a deliberate divergence from Django's documented behavior (which says help text is not escaped).

## Client-side validation

The package does not add daisyUI's `validator` class by default. This class colors fields based on native constraint validation, which can conflict with server-side validation and duplicate error messages.

To opt in to client-side validation for a specific field, add `validator` through widget `attrs`:

```python
email = forms.EmailField(
    widget=forms.EmailInput(attrs={"class": "validator"}),
)
```

Or through the template tag:

```django
{% daisy_field form.email class+="validator" %}
```

## htmx integration

With htmx, return a `422` status with the re-rendered field group when validation fails. htmx 2 swaps `4xx` responses by default, so the error markup replaces the form fragment.

```python
from django.shortcuts import render
from django.views.decorators.vary import vary_on_headers

from .forms import ContactForm


@vary_on_headers("HX-Request")
def contact(request):
    form = ContactForm(request.POST if request.method == "POST" else None)

    if request.method == "POST":
        if form.is_valid():
            # Save or process form.cleaned_data
            if request.headers.get("HX-Request") == "true":
                return render(request, "contact/_success.html")
        elif request.headers.get("HX-Request") == "true":
            return render(
                request,
                "contact/_form.html",
                {"form": form},
                status=422,
            )

    return render(request, "contact/page.html", {"form": form})
```

The template uses `hx-post` and `hx-target` to swap the form fragment:

```django
<form id="contact-form" method="post" action="{% url 'contact' %}"
      hx-post="{% url 'contact' %}" hx-target="#contact-form"
      hx-swap="outerHTML">
  {% csrf_token %}
  {% daisy_field form.email %}
  <button class="btn btn-primary" type="submit">Send</button>
</form>
```

Configure htmx to swap `422` responses by adding a meta tag:

```html
<meta name="htmx-config" content='{"responseHandling":[
  {"code":"204","swap":false},
  {"code":"[23]..","swap":true},
  {"code":"422","swap":true},
  {"code":"[45]..","swap":false,"error":true},
  {"code":"...","swap":false}
]}' />
```

See the [HTMX form validation recipe](../recipes/htmx-form-validation.md) for a complete example.

## Non-field errors

Non-field errors (errors not associated with a specific field) render in an alert at the top of the form:

```html
<div role="alert" class="alert alert-error alert-soft">
  <ul>
    <li>The two password fields didn't match.</li>
  </ul>
</div>
```

Formset non-form errors render the same way.

## Required fields

Required fields get a red asterisk in the label:

```html
<label class="fieldset-legend" for="id_email">
  Email
  <span class="text-error" aria-hidden="true">*</span>
</label>
```

The `required` attribute on the input comes from Django's field definition.

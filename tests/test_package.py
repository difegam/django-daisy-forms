from django.apps import apps


def test_public_package_is_importable() -> None:
    import daisy_forms

    assert daisy_forms.__name__ == "daisy_forms"


def test_app_config_uses_public_package_name() -> None:
    config = apps.get_app_config("daisy_forms")

    assert config.name == "daisy_forms"

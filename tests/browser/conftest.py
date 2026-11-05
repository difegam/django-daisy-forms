from collections.abc import Iterator
from threading import Thread
from wsgiref.simple_server import make_server

import pytest
from django.core.wsgi import get_wsgi_application


@pytest.fixture
def preview_server() -> Iterator[str]:
    server = make_server("127.0.0.1", 0, get_wsgi_application())
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        thread.join()
        server.server_close()

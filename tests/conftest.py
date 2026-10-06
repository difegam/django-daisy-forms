import subprocess
from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def dist_path(tmp_path_factory: pytest.TempPathFactory) -> Path:
    output_path = tmp_path_factory.mktemp("dist")
    repository_root = Path(__file__).parent.parent

    subprocess.run(
        ["uv", "build", "--no-sources", "--out-dir", str(output_path)],
        check=True,
        cwd=repository_root,
    )

    return output_path

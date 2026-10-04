from importlib.metadata import version

import evalia


def test_runtime_version_matches_installed_metadata() -> None:
    """Keep the public package version aligned with its installed metadata."""
    assert evalia.__version__ == version("evalia")

import asyncio
from types import SimpleNamespace
from unittest.mock import patch

import pytest

import routeable_api.__main__ as entry


@pytest.mark.parametrize("platform", ["win32", "linux"])
def test_main_selects_compatible_event_loop(platform: str) -> None:
    with (
        patch.object(entry, "sys", SimpleNamespace(platform=platform)),
        patch.object(entry.uvicorn, "run") as run,
    ):
        entry.main()

    run.assert_called_once()
    loop_factory = run.call_args.kwargs["loop"]
    if platform == "win32":
        assert loop_factory is asyncio.SelectorEventLoop
    else:
        assert loop_factory == "auto"

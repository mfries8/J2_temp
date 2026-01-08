import shutil
from pathlib import Path

from typer.testing import CliRunner

from meteor_darkflight.cli_api.cli import app


def test_validate_command_with_templates(tmp_path):
    templates_dir = Path("docs/templates")
    target_dir = tmp_path / "BlacksvilleGA_2025"
    target_dir.mkdir()

    for name in [
        "event.json",
        "fragments.json",
        "atmos_profile.json",
        "radar_metadata.json",
    ]:
        shutil.copy(templates_dir / name, target_dir / name)

    runner = CliRunner()
    event_path = target_dir / "event.json"
    result = runner.invoke(
        app,
        ["validate", "--event", str(event_path)],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert "Validation passed" in result.stdout

from pathlib import Path

from cinesolo.storyboard import validate_storyboard_file

EXAMPLE = Path(__file__).parent.parent / "examples" / "storyboard_example.yaml"


def test_example_storyboard_is_valid():
    ok, message = validate_storyboard_file(EXAMPLE)
    assert ok, message
    assert "S001" not in message  # 只是确保message是摘要而不是抛异常


def test_missing_file_reports_failure(tmp_path):
    ok, message = validate_storyboard_file(tmp_path / "does_not_exist.yaml")
    assert not ok
    assert "校验失败" in message


def test_duplicate_shot_id_reports_failure(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text(
        """
project: "p"
episode: "E01"
shots:
  - id: "S001"
    scene: "a"
  - id: "S001"
    scene: "b"
""".strip(),
        encoding="utf-8",
    )
    ok, message = validate_storyboard_file(bad)
    assert not ok
    assert "重复" in message

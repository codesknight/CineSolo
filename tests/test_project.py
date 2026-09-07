from cinesolo.project import init_shots_from_storyboard
from cinesolo.storyboard import load_storyboard
from pathlib import Path


def test_init_shots_creates_expected_dirs(tmp_path, monkeypatch):
    monkeypatch.setenv("CINESOLO_DATA_ROOT", str(tmp_path))

    example = Path(__file__).parent.parent / "examples" / "storyboard_example.yaml"
    sb = load_storyboard(example)

    shot_dirs = init_shots_from_storyboard(sb)

    assert len(shot_dirs) == 2
    for shot_dir in shot_dirs:
        assert (shot_dir / "generated").is_dir()
        assert (shot_dir / "edit").is_dir()
    assert (tmp_path / "projects" / sb.project / sb.episode / "output").is_dir()

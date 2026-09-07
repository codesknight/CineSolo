from pathlib import Path
from unittest.mock import MagicMock

from cinesolo.render import build_workflow_for_shot, load_template, render_shot
from cinesolo.storyboard import Shot

TEMPLATE_PATH = Path(__file__).parent.parent / "workflows" / "txt2img_basic.json"


def test_load_template():
    template = load_template(TEMPLATE_PATH)
    assert template["4"]["class_type"] == "CheckpointLoaderSimple"


def test_build_workflow_overrides_prompt_and_seed():
    template = load_template(TEMPLATE_PATH)
    shot = Shot(
        id="S001",
        prompt="a cat",
        negative_prompt="blurry",
        workflow_params={"width": 768, "height": 512, "seed": 42},
    )

    wf = build_workflow_for_shot(template, shot)

    assert wf["6"]["inputs"]["text"] == "a cat"
    assert wf["7"]["inputs"]["text"] == "blurry"
    assert wf["5"]["inputs"]["width"] == 768
    assert wf["5"]["inputs"]["height"] == 512
    assert wf["3"]["inputs"]["seed"] == 42
    # 原模板不应被修改（深拷贝）
    assert template["6"]["inputs"]["text"] == "1girl"


def test_build_workflow_random_seed_when_not_specified():
    template = load_template(TEMPLATE_PATH)
    shot = Shot(id="S001", prompt="a cat")
    wf = build_workflow_for_shot(template, shot)
    assert isinstance(wf["3"]["inputs"]["seed"], int)


def test_render_shot_saves_images(tmp_path):
    template = load_template(TEMPLATE_PATH)
    shot = Shot(id="S001", prompt="a cat")

    client = MagicMock()
    client.submit_prompt.return_value = "prompt-123"
    client.wait_for_result.return_value = {"status": {"status_str": "success"}, "outputs": {}}
    client.extract_images.return_value = [{"filename": "cinesolo_S001_00001_.png", "subfolder": "", "type": "output"}]
    client.fetch_image.return_value = b"fake-png-bytes"

    out_dir = tmp_path / "generated"
    saved = render_shot(client, shot, out_dir, template=template)

    assert len(saved) == 1
    assert saved[0].exists()
    assert saved[0].read_bytes() == b"fake-png-bytes"
    client.submit_prompt.assert_called_once()

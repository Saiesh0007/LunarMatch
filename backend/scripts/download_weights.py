"""Download the pretrained SuperPoint / SuperGlue / LightGlue weights into backend/weights/.

The .pth files are git-ignored (45+ MB each), so a fresh clone needs this once:

    python scripts/download_weights.py

Sources: magicleap/SuperGluePretrainedNetwork (research-only licence) and
cvg/LightGlue (Apache-2.0). The pipeline degrades gracefully to RIFT2 / dense
matching when weights are absent, but the learned-matcher tests require them.
"""
import sys
import urllib.request
from pathlib import Path

WEIGHTS_DIR = Path(__file__).resolve().parents[1] / "weights"
FILES = {
    "superpoint_v1.pth": "https://github.com/magicleap/SuperGluePretrainedNetwork/raw/master/models/weights/superpoint_v1.pth",
    "superglue_outdoor.pth": "https://github.com/magicleap/SuperGluePretrainedNetwork/raw/master/models/weights/superglue_outdoor.pth",
    "superpoint_lightglue.pth": "https://github.com/cvg/LightGlue/releases/download/v0.1_arxiv/superpoint_lightglue.pth",
}


def main() -> int:
    WEIGHTS_DIR.mkdir(parents=True, exist_ok=True)
    for name, url in FILES.items():
        dest = WEIGHTS_DIR / name
        if dest.exists() and dest.stat().st_size > 1_000_000:
            print(f"ok       {name} ({dest.stat().st_size / 1e6:.1f} MB)")
            continue
        print(f"fetching {name} ...", flush=True)
        tmp = dest.with_suffix(".part")
        urllib.request.urlretrieve(url, tmp)
        tmp.replace(dest)
        print(f"saved    {name} ({dest.stat().st_size / 1e6:.1f} MB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

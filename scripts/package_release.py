# SPDX-License-Identifier: GPL-3.0-only
"""Prepare the module source archive, notes and checksums for a GitHub release."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tomllib
import zipfile


def _check_source_path(relative):
    """Keep generated files, local environments and downloaded assets out."""
    path = Path(relative)
    forbidden = {"assets", "outputs", "cache", "caches", ".cache", "venv", ".venv",
                 "dist", "build", "runs", "__pycache__", ".pytest_cache", "node_modules", ".tox"}
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"Source archive path escaped the repository: {relative}")
    if any(part.lower() in forbidden or part.lower().startswith(".venv-")
           for part in path.parts[:-1]):
        raise ValueError(f"Runtime assets, caches or build outputs cannot enter the source archive: {relative}")
    if path.suffix.lower() in {".pyc", ".pyo", ".whl", ".zip", ".onnx", ".stl", ".step", ".stp",
                              ".mp4", ".webm", ".avi", ".so", ".dll", ".dylib"} or path.name.endswith(".tar.gz"):
        raise ValueError(f"Binary assets or generated artifacts cannot enter the source archive: {relative}")


def prepare_release(package_root, output):
    package_root = Path(package_root).resolve()
    output = Path(output).resolve()
    config = tomllib.loads((package_root / "pyproject.toml").read_text())
    version = config["project"]["version"]
    if not re.fullmatch(r"\d+\.\d+\.\d+(?:(?:a|b|rc)\d+)?", version):
        raise ValueError("Release version must be an explicit semantic version")
    distribution = re.sub(r"[-_.]+", "_", config["project"]["name"]).lower()
    if not re.fullmatch(r"[a-z0-9_]+", distribution):
        raise ValueError("Invalid distribution name")
    notes_path = package_root / "docs/releases" / f"{version}.md"
    guide_path = package_root / "docs/USAGE.zh-CN.md"
    if not notes_path.is_file() or not guide_path.is_file():
        raise ValueError("Release requires version-specific notes and a usage guide")
    tag = "legged-robot-v" + version
    output.mkdir(parents=True, exist_ok=True)
    wheels = sorted(output.glob(f"{distribution}-{version}-*.whl"))
    sdist = output / f"{distribution}-{version}.tar.gz"
    if not wheels or not sdist.is_file():
        raise ValueError(f"Build the {version} wheel and sdist before preparing the release")
    paths = subprocess.check_output(
        ["git", "ls-files", "-z", "--", "."], cwd=package_root
    ).decode().split("\0")
    sources = []
    for relative in sorted(path for path in paths if path):
        _check_source_path(relative)
        source = (package_root / relative).resolve()
        if package_root not in source.parents:
            raise ValueError("Source archive path escaped the repository")
        _check_source_path(source.relative_to(package_root))
        if not source.is_file():
            raise ValueError(f"Tracked source is missing or is not a file: {relative}")
        sources.append((relative, source))
    if not sources:
        raise ValueError("Source archive requires tracked repository files")
    archive = output / f"legged-robot-{version}-source.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as bundle:
        for relative, source in sources:
            bundle.write(source, f"legged-robot-{version}/" + relative)
    for source in (guide_path, package_root / "requirements-sim.txt"):
        shutil.copyfile(source, output / source.name)
    artifacts = sorted([*wheels, sdist, archive,
                        output / guide_path.name, output / "requirements-sim.txt"])
    checksums = "".join(
        hashlib.sha256(path.read_bytes()).hexdigest() + "  " + path.name + "\n"
        for path in artifacts
    )
    (output / "SHA256SUMS.txt").write_text(checksums)
    source_commit = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=package_root, text=True
    ).strip()
    source_dirty = bool(subprocess.check_output(
        ["git", "status", "--porcelain", "--untracked-files=no"],
        cwd=package_root, text=True
    ).strip())
    source_label = "构建基准源码提交" if source_dirty else "对应源程序提交"
    notes = notes_path.read_text(encoding="utf-8").rstrip() + (
        f"\n\n{source_label}：[{source_commit}]"
        f"(https://github.com/maganrobotics-boop/OmindOS-Locomotion/commit/{source_commit})。\n"
    )
    if source_dirty:
        notes += "\n此本地构建包含未提交修改，不作为公开发布产物。\n"
    (output / "RELEASE_NOTES.md").write_text(notes)
    metadata = {"version": version, "tag": tag,
                "source_repository": "maganrobotics-boop/OmindOS-Locomotion",
                "source_commit": source_commit,
                "source_dirty": source_dirty,
                "release_repository": "maganrobotics-boop/OmindOS-Locomotion-Release",
                "prerelease": bool(re.search(r"(?:a|b|rc)\d+$", version)),
                "artifacts": [path.name for path in artifacts] + ["SHA256SUMS.txt"]}
    (output / "release-metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    return metadata


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("dist"))
    args = parser.parse_args()
    package_root = Path(__file__).resolve().parents[1]
    print(json.dumps(prepare_release(package_root, args.output)))


if __name__ == "__main__":
    main()

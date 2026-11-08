#!/usr/bin/env python3
"""Validate the Roku project and create its unsigned development sideload ZIP."""

from __future__ import annotations

import argparse
import re
import struct
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree


ROOT = Path(__file__).resolve().parent.parent
PACKAGE_PATH = ROOT / "dist" / "SplashZone.zip"
REQUIRED_MANIFEST_ENTRIES = {
    "screensaver_title",
    "screensaver_private",
    "major_version",
    "minor_version",
    "build_version",
    "ui_resolutions",
    "rsg_version",
    "splash_screen_hd",
}


def validate_manifest() -> None:
    manifest_path = ROOT / "manifest"
    if not manifest_path.is_file():
        raise ValueError("Missing Roku root manifest.")

    content = manifest_path.read_text(encoding="utf-8")
    if not content.endswith("\n"):
        raise ValueError("The manifest must end with a newline.")

    entries: dict[str, str] = {}
    for line_number, raw_line in enumerate(content.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise ValueError(f"Invalid manifest entry on line {line_number}.")
        key, value = (part.strip() for part in line.split("=", 1))
        if not key or not value:
            raise ValueError(f"Empty manifest key or value on line {line_number}.")
        if key in entries:
            raise ValueError(f"Duplicate manifest entry: {key}.")
        entries[key] = value

    missing = REQUIRED_MANIFEST_ENTRIES - entries.keys()
    if missing:
        raise ValueError(f"Missing required manifest entries: {', '.join(sorted(missing))}.")
    if "title" in entries:
        raise ValueError(
            "Standalone screensavers must not declare title; Roku's static analysis "
            "treats it as a channel attribute. Use screensaver_title only."
        )
    if entries["screensaver_title"] != "Splash Zone":
        raise ValueError("screensaver_title must be Splash Zone.")
    if entries["screensaver_private"] != "0":
        raise ValueError(
            "The standalone system screensaver must declare screensaver_private=0."
        )
    if entries["ui_resolutions"] != "fhd":
        raise ValueError("The SceneGraph project must declare its supported FHD UI resolution.")
    if entries["rsg_version"] != "1.3":
        raise ValueError("The manifest must declare rsg_version=1.3.")
    splash_uri = "pkg:/images/splash-screen_HD.jpg"
    if entries["splash_screen_hd"] != splash_uri:
        raise ValueError(f"splash_screen_hd must be declared as {splash_uri}.")
    splash_path = ROOT.joinpath(*splash_uri.removeprefix("pkg:/").split("/"))
    if not splash_path.is_file():
        raise ValueError(f"Missing HD splash screen: {splash_path.relative_to(ROOT)}.")
    if not splash_path.read_bytes().startswith(b"\xff\xd8"):
        raise ValueError("splash_screen_hd must point to a valid JPEG image.")

    required_icons = {
        "mm_icon_focus_fhd": ("pkg:/images/channel-icon_FHD.png", (540, 405)),
        "mm_icon_focus_hd": ("pkg:/images/channel-icon_HD.png", (290, 218)),
    }
    for manifest_key, (uri, dimensions) in required_icons.items():
        if entries.get(manifest_key) != uri:
            raise ValueError(f"{manifest_key} must be declared as {uri}.")
        icon_path = ROOT.joinpath(*uri.removeprefix("pkg:/").split("/"))
        if not icon_path.is_file():
            raise ValueError(f"Missing app icon: {icon_path.relative_to(ROOT)}.")
        icon_data = icon_path.read_bytes()
        if len(icon_data) < 24 or icon_data[:8] != b"\x89PNG\r\n\x1a\n":
            raise ValueError(f"{manifest_key} must point to a valid PNG image.")
        icon_dimensions = struct.unpack(">II", icon_data[16:24])
        if icon_dimensions != dimensions:
            raise ValueError(
                f"{manifest_key} must be {dimensions[0]}x{dimensions[1]} pixels, "
                f"got {icon_dimensions[0]}x{icon_dimensions[1]}."
            )

    for key in ("major_version", "minor_version", "build_version"):
        if not entries[key].isdigit():
            raise ValueError(f"Manifest {key} must be an integer.")


def validate_components() -> None:
    component_dir = ROOT / "components"
    xml_paths = sorted(component_dir.glob("*.xml"))
    if not xml_paths:
        raise ValueError("No SceneGraph component XML files found.")

    components: dict[str, ElementTree.Element] = {}
    for xml_path in xml_paths:
        try:
            component = ElementTree.parse(xml_path).getroot()
        except ElementTree.ParseError as error:
            raise ValueError(f"Invalid XML in {xml_path.relative_to(ROOT)}: {error}") from error
        if component.tag != "component" or not component.get("name"):
            raise ValueError(f"{xml_path.relative_to(ROOT)} must have a named component root.")
        name = component.attrib["name"]
        if name in components:
            raise ValueError(f"Duplicate SceneGraph component name: {name}.")
        components[name] = component

    for xml_path in xml_paths:
        component = ElementTree.parse(xml_path).getroot()
        component_name = component.attrib["name"]
        ids = [
            node.attrib["id"]
            for node in component.iter()
            if node.tag != "field" and node.get("id")
        ]
        if len(ids) != len(set(ids)):
            raise ValueError(f"Duplicate node IDs in {xml_path.relative_to(ROOT)}.")
        id_set = set(ids)

        for script in component.findall("./script"):
            uri = script.get("uri", "")
            if not uri.startswith("pkg:/"):
                raise ValueError(f"Invalid script URI in {xml_path.relative_to(ROOT)}: {uri}")
            script_path = ROOT.joinpath(*uri.removeprefix("pkg:/").split("/"))
            if not script_path.is_file():
                raise ValueError(f"Missing component script: {uri}")

        for node in component.iter():
            if node.tag in components and node.tag != component_name:
                continue
            if node.tag not in {
                "component",
                "interface",
                "children",
                "script",
                "field",
                "Animation",
                "Vector2DFieldInterpolator",
                "Timer",
                "Rectangle",
                "Group",
            } and node.tag not in components:
                raise ValueError(
                    f"Unknown component <{node.tag}> in {xml_path.relative_to(ROOT)}."
                )

        for node in component.iter("Vector2DFieldInterpolator"):
            target = node.get("fieldToInterp", "").split(".", 1)[0]
            if target not in id_set:
                raise ValueError(
                    f"Animation in {xml_path.relative_to(ROOT)} targets missing node ID {target!r}."
                )

    scene = components.get("AquariumScene")
    if scene is None:
        raise ValueError("Missing AquariumScene component.")
    scene_scripts = {
        script.get("uri")
        for script in scene.findall("./script")
    }
    if "pkg:/components/AquariumScene.brs" not in scene_scripts:
        raise ValueError(
            "AquariumScene must import pkg:/components/AquariumScene.brs to initialize motion."
        )
    if not any(node.get("id") == "MotionTimer" for node in scene.iter("Timer")):
        raise ValueError("AquariumScene must include the MotionTimer used by the scene script.")
    for node in scene.iter():
        if node.tag in {"StickFish", "Bubble"} and node.tag not in components:
            raise ValueError(f"Scene references missing component <{node.tag}>.")


def validate_screensaver_entrypoint() -> None:
    main_path = ROOT / "source" / "main.brs"
    if not main_path.is_file():
        raise ValueError("Missing source/main.brs.")
    source = main_path.read_text(encoding="utf-8")
    if not re.search(r"(?im)^\s*sub\s+RunScreenSaver\s*\(", source):
        raise ValueError("source/main.brs must define RunScreenSaver().")
    if re.search(r"(?im)^\s*(?:sub|function)\s+(?:Main|RunUserInterface)\s*\(", source):
        raise ValueError("Screensavers must not define Main() or RunUserInterface().")


def package_channel() -> None:
    package_files = [ROOT / "manifest"]
    for directory in ("source", "components", "images"):
        package_files.extend(
            path for path in (ROOT / directory).rglob("*") if path.is_file()
        )
    package_files.sort(key=lambda path: path.relative_to(ROOT).as_posix())

    PACKAGE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(PACKAGE_PATH, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in package_files:
            archive.write(path, path.relative_to(ROOT).as_posix())

    with zipfile.ZipFile(PACKAGE_PATH) as archive:
        entries = set(archive.namelist())
        required = {
            "manifest",
            "source/main.brs",
            "components/AquariumScene.xml",
            "images/channel-icon_FHD.png",
            "images/channel-icon_HD.png",
            "images/splash-screen_HD.jpg",
        }
        missing = required - entries
        if missing:
            raise ValueError(f"Built ZIP is missing required files: {', '.join(sorted(missing))}.")
        if any(name.startswith(("/", "\\")) or ".." in Path(name).parts for name in entries):
            raise ValueError("Built ZIP contains an unsafe archive path.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="validate the project without creating the ZIP package",
    )
    args = parser.parse_args()

    try:
        validate_manifest()
        validate_components()
        validate_screensaver_entrypoint()
        if args.check:
            print("Splash Zone project validation passed.")
        else:
            package_channel()
            print(f"Built Roku channel package: {PACKAGE_PATH.relative_to(ROOT)}")
    except (OSError, ValueError, zipfile.BadZipFile) as error:
        print(f"Build validation failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

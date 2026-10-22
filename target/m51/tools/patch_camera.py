#!/usr/bin/env python3
import sys

cam_path = "/home/arnav/M51_85_STABLE_REBASE/work/extracted/system/system/system/cameradata/camera-feature.xml"
with open(cam_path, "r", encoding="utf-8") as f:
    content = f.read()

target = '<local name="BACK_CAMCORDER_RESOLUTION_FEATURE_MAP_1920X1080" value="true" hdr="true" hdr10="false" preview-size="1920x1080" snapshot-support="true" snapshot-size="4624x2604" vdis="true" super-vdis="true" effect="true" object-tracking="false" external-storage-support="true"/>'
replacement = target + '\n    <local name="BACK_CAMCORDER_RESOLUTION_FEATURE_MAP_1920X1080_60FPS" value="true" hdr="false" hdr10="false" preview-size="1920x1080" snapshot-support="true" snapshot-size="4624x2604" vdis="false" super-vdis="false" effect="false" object-tracking="false" external-storage-support="true" seamless-zoom-support="false" uw-support="false"/>'

if target not in content:
    print("ERROR: Target line not found in camera-feature.xml!")
    sys.exit(1)

if "BACK_CAMCORDER_RESOLUTION_FEATURE_MAP_1920X1080_60FPS" in content:
    print("ALREADY PATCHED!")
    sys.exit(0)

new_content = content.replace(target, replacement, 1)
with open(cam_path, "w", encoding="utf-8") as f:
    f.write(new_content)

print("Successfully added BACK_CAMCORDER_RESOLUTION_FEATURE_MAP_1920X1080_60FPS to camera-feature.xml!")

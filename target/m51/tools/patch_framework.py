#!/usr/bin/env python3
import sys

FW_DIR = "/home/arnav/M51_85_STABLE_REBASE/work/patch-stage-v4/apktool_work/framework_out"

# 1. InputRune.smali
input_rune = f"{FW_DIR}/smali_classes6/com/samsung/android/rune/InputRune.smali"
with open(input_rune, "r", encoding="utf-8") as f:
    ir_content = f.read()

target_ir = "sput-boolean v1, Lcom/samsung/android/rune/InputRune;->PWM_SKIP_TOO_FAST_DOUBLE_PRESS:Z"
rep_ir = "sput-boolean v4, Lcom/samsung/android/rune/InputRune;->PWM_SKIP_TOO_FAST_DOUBLE_PRESS:Z"
if target_ir in ir_content:
    ir_content = ir_content.replace(target_ir, rep_ir, 1)
    with open(input_rune, "w", encoding="utf-8") as f:
        f.write(ir_content)
    print("Patched InputRune.smali successfully!")
elif rep_ir in ir_content:
    print("InputRune.smali already patched!")
else:
    print("WARNING: target line not found in InputRune.smali")

# 2. SemFingerprintManager$Characteristics.smali getSensorType
char_smali = f"{FW_DIR}/smali_classes6/com/samsung/android/bio/fingerprint/SemFingerprintManager$Characteristics.smali"
with open(char_smali, "r", encoding="utf-8") as f:
    lines = f.readlines()

in_getSensorType = False
patched_char = False
for idx, l in enumerate(lines):
    if ".method public whitelist getSensorType()I" in l or ".method public getSensorType()I" in l:
        in_getSensorType = True
    if in_getSensorType:
        if "const/4 p0, 0x2" in l:
            lines[idx] = l.replace("const/4 p0, 0x2", "const/4 p0, 0x1")
            patched_char = True
            print("Patched getSensorType() in SemFingerprintManager$Characteristics.smali from 0x2 to 0x1!")
        if ".end method" in l:
            in_getSensorType = False

if patched_char:
    with open(char_smali, "w", encoding="utf-8") as f:
        f.writelines(lines)
else:
    print("Note: getSensorType already 0x1 or pattern not found.")

# 3. String replacement: google_touch_display_optical,settings=3,aod_transition_animation -> google_touch_side,settings=3,navi=1
for target_file in [
    f"{FW_DIR}/smali_classes6/com/samsung/android/bio/fingerprint/SemFingerprintManager.smali",
    f"{FW_DIR}/smali_classes6/com/samsung/android/bio/fingerprint/SemFingerprintManager$Characteristics.smali"
]:
    with open(target_file, "r", encoding="utf-8") as f:
        c = f.read()
    if "google_touch_display_optical,settings=3,aod_transition_animation" in c:
        c = c.replace("google_touch_display_optical,settings=3,aod_transition_animation", "google_touch_side,settings=3,navi=1")
        with open(target_file, "w", encoding="utf-8") as f:
            f.write(c)
        print(f"Patched sensor config string in {target_file}")
    elif "google_touch_side,settings=3,navi=1" in c:
        print(f"Sensor config string already patched in {target_file}")
    else:
        print(f"Note: sensor config string not found in {target_file}")

print("Framework patching complete!")

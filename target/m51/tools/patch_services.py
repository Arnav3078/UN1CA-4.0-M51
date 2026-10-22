#!/usr/bin/env python3
import os
import re

SERV_DIR = "/home/arnav/M51_85_STABLE_REBASE/work/patch-stage-v4/apktool_work/services_out"

# 1. Patch LockSettingsService.smali
lock_path = f"{SERV_DIR}/smali/com/android/server/locksettings/LockSettingsService.smali"
with open(lock_path, "r", encoding="utf-8") as f:
    lock_content = f.read()

pattern_lock = r"\.method public static isEnablePrevCredential\(\)Z.*?\n\.end method"
replacement_lock = """.method public static isEnablePrevCredential()Z
    .locals 1

    const/4 v0, 0x0

    return v0
.end method"""

if re.search(pattern_lock, lock_content, re.DOTALL):
    lock_content = re.sub(pattern_lock, replacement_lock, lock_content, count=1, flags=re.DOTALL)
    with open(lock_path, "w", encoding="utf-8") as f:
        f.write(lock_content)
    print("Patched LockSettingsService.smali successfully!")
else:
    raise RuntimeError("isEnablePrevCredential pattern not found in LockSettingsService.smali")

# 2. Patch FingerprintService$1.smali position
fp_path = f"{SERV_DIR}/smali/com/android/server/biometrics/sensors/fingerprint/FingerprintService$1.smali"
with open(fp_path, "r", encoding="utf-8") as f:
    fp_content = f.read()

target_fp = """    new-instance p0, Ljava/io/File;

    const-string v0, "/sys/class/fingerprint/fingerprint/position"

    invoke-direct {p0, v0}, Ljava/io/File;-><init>(Ljava/lang/String;)V

    invoke-static {p0}, Lcom/android/server/biometrics/SemUtils;->readFile(Ljava/io/File;)[B

    move-result-object p0

    if-eqz p0, :cond_2

    :try_start_0
    new-instance v0, Ljava/lang/String;

    sget-object v1, Ljava/nio/charset/StandardCharsets;->UTF_8:Ljava/nio/charset/Charset;

    invoke-direct {v0, p0, v1}, Ljava/lang/String;-><init>([BLjava/nio/charset/Charset;)V

    invoke-virtual {v0}, Ljava/lang/String;->trim()Ljava/lang/String;

    move-result-object p0"""

replacement_fp = """    :try_start_0
    const-string p0, "53.45,13.25\""""

if target_fp in fp_content:
    fp_content = fp_content.replace(target_fp, replacement_fp, 1)
    with open(fp_path, "w", encoding="utf-8") as f:
        f.write(fp_content)
    print("Patched FingerprintService$1.smali position successfully!")
else:
    raise RuntimeError("target_fp position block not found in FingerprintService$1.smali")

# 3. Patch SemBiometricFeature.smali:
# Set FEATURE_JDM_HAL = true (activates Face HIDL 2.0 fallback natively in One UI 8.5)
# Set FP_FEATURE_SENSOR_IS_SIDE = true
# Set FP_FEATURE_SENSOR_IS_OPTICAL = false
# Set FP_FEATURE_SENSOR_IS_IN_DISPLAY_TYPE = false
# Set FP_FEATURE_SENSOR_IS_ULTRASONIC = false
bio_path = f"{SERV_DIR}/smali/com/android/server/biometrics/SemBiometricFeature.smali"
with open(bio_path, "r", encoding="utf-8") as f:
    bio_content = f.read()

# FEATURE_JDM_HAL
target_jdm = """    const-string/jumbo v1, "jdm"

    invoke-virtual {v0, v1}, Ljava/lang/String;->contains(Ljava/lang/CharSequence;)Z

    move-result v0

    sput-boolean v0, Lcom/android/server/biometrics/SemBiometricFeature;->FEATURE_JDM_HAL:Z"""

rep_jdm = """    const/4 v0, 0x1

    sput-boolean v0, Lcom/android/server/biometrics/SemBiometricFeature;->FEATURE_JDM_HAL:Z"""

if target_jdm in bio_content:
    bio_content = bio_content.replace(target_jdm, rep_jdm, 1)
    print("Patched FEATURE_JDM_HAL to true in SemBiometricFeature.smali!")
else:
    raise RuntimeError("target_jdm not found in SemBiometricFeature.smali")

with open(bio_path, "w", encoding="utf-8") as f:
    f.write(bio_content)

# 4. Patch SemFingerprintServiceExtImpl.smali
# Ensure mHasOpticalUdfps, mHasUltrasonicUdfps, mHasUdfps are forced to false (0x0)
ext_path = f"{SERV_DIR}/smali/com/android/server/biometrics/sensors/fingerprint/SemFingerprintServiceExtImpl.smali"
with open(ext_path, "r", encoding="utf-8") as f:
    ext_content = f.read()

target_ext = """    sget-boolean v0, Lcom/android/server/biometrics/SemBiometricFeature;->FP_FEATURE_SENSOR_IS_ULTRASONIC:Z

    iput-boolean v0, p0, Lcom/android/server/biometrics/sensors/fingerprint/SemFingerprintServiceExtImpl;->mHasUltrasonicUdfps:Z

    sget-boolean v0, Lcom/android/server/biometrics/SemBiometricFeature;->FP_FEATURE_SENSOR_IS_OPTICAL:Z

    iput-boolean v0, p0, Lcom/android/server/biometrics/sensors/fingerprint/SemFingerprintServiceExtImpl;->mHasOpticalUdfps:Z

    sget-boolean v0, Lcom/android/server/biometrics/SemBiometricFeature;->FP_FEATURE_SENSOR_IS_IN_DISPLAY_TYPE:Z

    iput-boolean v0, p0, Lcom/android/server/biometrics/sensors/fingerprint/SemFingerprintServiceExtImpl;->mHasUdfps:Z"""

rep_ext = """    const/4 v0, 0x0

    iput-boolean v0, p0, Lcom/android/server/biometrics/sensors/fingerprint/SemFingerprintServiceExtImpl;->mHasUltrasonicUdfps:Z

    iput-boolean v0, p0, Lcom/android/server/biometrics/sensors/fingerprint/SemFingerprintServiceExtImpl;->mHasOpticalUdfps:Z

    iput-boolean v0, p0, Lcom/android/server/biometrics/sensors/fingerprint/SemFingerprintServiceExtImpl;->mHasUdfps:Z"""

if target_ext in ext_content:
    ext_content = ext_content.replace(target_ext, rep_ext, 1)
    with open(ext_path, "w", encoding="utf-8") as f:
        f.write(ext_content)
    print("Patched SemFingerprintServiceExtImpl.smali UDFPS flags to false!")
else:
    raise RuntimeError("target_ext block not found in SemFingerprintServiceExtImpl.smali")

print("services.jar patching completed successfully!")

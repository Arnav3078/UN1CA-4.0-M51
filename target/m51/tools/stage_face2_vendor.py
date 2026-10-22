#!/usr/bin/env python3
import shutil
import os

VENDOR_DIR = "/home/arnav/M51_85_STABLE_REBASE/work/extracted/vendor"
A71_VENDOR = "/home/arnav/a71_clean_port/UN1CA/out/fw/SM-A715F_SEE/vendor"

# 1. Copy face@2.0-service binary
src_bin = f"{A71_VENDOR}/bin/hw/vendor.samsung.hardware.biometrics.face@2.0-service"
dst_bin = f"{VENDOR_DIR}/vendor/bin/hw/vendor.samsung.hardware.biometrics.face@2.0-service"
shutil.copy2(src_bin, dst_bin)
os.chmod(dst_bin, 0o755)
print(f"Copied face@2.0-service binary ({os.path.getsize(dst_bin)} bytes)")

# 2. Copy face@2.0-service.rc
src_rc = f"{A71_VENDOR}/etc/init/vendor.samsung.hardware.biometrics.face@2.0-service.rc"
dst_rc = f"{VENDOR_DIR}/vendor/etc/init/vendor.samsung.hardware.biometrics.face@2.0-service.rc"
shutil.copy2(src_rc, dst_rc)
os.chmod(dst_rc, 0o644)
print(f"Copied face@2.0-service.rc ({os.path.getsize(dst_rc)} bytes)")

# 3. Remove face@3.0-service.rc
old_rc = f"{VENDOR_DIR}/vendor/etc/init/vendor.samsung.hardware.biometrics.face@3.0-service.rc"
if os.path.exists(old_rc):
    os.remove(old_rc)
    print("Removed face@3.0-service.rc")

# 4. Update vendor_fs_config
fs_cfg_path = f"{VENDOR_DIR}/config/vendor_fs_config"
with open(fs_cfg_path, "r", encoding="utf-8") as f:
    fs_lines = f.readlines()

new_fs_lines = []
for line in fs_lines:
    if "face@3.0-service" in line:
        continue
    new_fs_lines.append(line)

new_fs_lines.append("vendor/bin/hw/vendor.samsung.hardware.biometrics.face@2.0-service 0 2000 0755\n")
new_fs_lines.append("vendor/etc/init/vendor.samsung.hardware.biometrics.face@2.0-service.rc 0 0 0644\n")

with open(fs_cfg_path, "w", encoding="utf-8") as f:
    f.writelines(sorted(set(new_fs_lines)))
print("Updated vendor_fs_config successfully!")

# 5. Update vendor_file_contexts
ctx_path = f"{VENDOR_DIR}/config/vendor_file_contexts"
with open(ctx_path, "r", encoding="utf-8") as f:
    ctx_lines = f.readlines()

new_ctx_lines = []
for line in ctx_lines:
    if "face@3.0-service" in line:
        continue
    new_ctx_lines.append(line)

new_ctx_lines.append("/vendor/bin/hw/vendor\\.samsung\\.hardware\\.biometrics\\.face@2\\.0-service u:object_r:hal_face_default_exec:s0\n")
new_ctx_lines.append("/vendor/etc/init/vendor\\.samsung\\.hardware\\.biometrics\\.face@2\\.0-service\\.rc u:object_r:vendor_configs_file:s0\n")

with open(ctx_path, "w", encoding="utf-8") as f:
    f.writelines(sorted(set(new_ctx_lines)))
print("Updated vendor_file_contexts successfully!")

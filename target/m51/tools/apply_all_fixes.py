#!/usr/bin/env python3
import sys, os, re, shutil, struct, capstone

cs = capstone.Cs(capstone.CS_ARCH_ARM64, capstone.CS_MODE_ARM)

def arm64_b(cur, target):
    diff = target - cur
    assert diff % 4 == 0
    imm26 = (diff >> 2) & 0x03ffffff
    return struct.pack('<I', 0x14000000 | imm26)

def arm64_bl(cur, target):
    diff = target - cur
    assert diff % 4 == 0
    imm26 = (diff >> 2) & 0x03ffffff
    return struct.pack('<I', 0x94000000 | imm26)

def arm64_cbnz(cur, target, reg):
    diff = target - cur
    assert diff % 4 == 0
    imm19 = (diff >> 2) & 0x0007ffff
    return struct.pack('<I', 0x35000000 | (imm19 << 5) | reg)

print('=== 1. Restoring & Patching libbauthtzcommon.so (64-bit) ===')
stock_tz64 = '/home/arnav/stock_vendor/lib64/libbauthtzcommon.so'
path_tz64 = '/home/arnav/M51_85_STABLE_REBASE/work/extracted/vendor/vendor/lib64/libbauthtzcommon.so'
shutil.copyfile(stock_tz64, path_tz64)

with open(path_tz64, 'rb') as f:
    b_tz = bytearray(f.read())

b_tz[0x4164:0x4168] = b'\xbf\x02\x00\xb9' # str wzr, [x21]
b_tz[0x4be0:0x4be4] = b'\xbf\x02\x00\xb9' # str wzr, [x21]
b_tz[0x4c3c:0x4c40] = b'\x0a\x00\x00\x14' # b #0x4c64

with open(path_tz64, 'wb') as f:
    f.write(b_tz)
print('libbauthtzcommon.so (64-bit) patched successfully!')

print('=== 2. Restoring & Patching libbauthserver.so (64-bit) ===')
stock_srv64 = '/home/arnav/stock_vendor/lib64/libbauthserver.so'
path_srv64 = '/home/arnav/M51_85_STABLE_REBASE/work/extracted/vendor/vendor/lib64/libbauthserver.so'
shutil.copyfile(stock_srv64, path_srv64)

with open(path_srv64, 'rb') as f:
    b_srv = bytearray(f.read())

# A. Jump table at 0x22da6:
# Index 0 -> Target 0 (0x4ea08)
# Index 1 -> Target 0 (0x4ea08)
print(f'Old table[0,1,2]: {b_srv[0x22da6:0x22dac].hex()}')
b_srv[0x22da6:0x22da8] = b'\x00\x00' # Index 0 -> Target 0 (0x4ea08)
b_srv[0x22da8:0x22daa] = b'\x00\x00' # Index 1 -> Target 0 (0x4ea08)
print(f'New table[0,1,2]: {b_srv[0x22da6:0x22dac].hex()}')

# B. Target 0 at 0x4ea0c:
# Stock has: cbnz w25, #0x515a8 (aborts enrollment immediately if function_status != 0)
# We patch it to: cbnz w25, #0x599c0 (routes to 50ms usleep delay loop in dead-code cave)
# When w25 == 0 (common_prepare): falls through to stock Target 0 (returns w0 = 1, cleanly exiting common_prepare)
# When w25 == 1 (Enroll_Do): branches to 0x599c0 (usleep 50ms, returns w0 = 0 to loop cleanly at 20 Hz without aborting)
b_srv[0x4ea0c:0x4ea10] = arm64_cbnz(0x4ea0c, 0x599c0, 25)
print('Patched 0x4ea0c to cbnz w25, #0x599c0')

# C. Dead-function cave at 0x599b8..0x599d0:
# 0x599b8: mov w0, wzr; ret (disables failing send_hat_hmackey)
b_srv[0x599b8:0x599c0] = bytes.fromhex('e0031f2ac0035fd6')
# 0x599c0: mov w0, #0xc350 (50,000 microseconds = 50 ms)
# 0x599c4: bl  #0x759b0   (usleep)
# 0x599c8: mov w23, wzr   (w23 = 0)
# 0x599cc: b   #0x515a8   (return w0 = 0 to BAuth_Enroll_Do)
cave_bytes = bytearray()
cave_bytes += bytes.fromhex('006a9852')          # mov w0, #0xc350
cave_bytes += arm64_bl(0x599c4, 0x759b0)         # bl #0x759b0 (usleep)
cave_bytes += bytes.fromhex('f7031f2a')          # mov w23, wzr
cave_bytes += arm64_b(0x599cc, 0x515a8)          # b #0x515a8
b_srv[0x599c0:0x599d0] = cave_bytes
print('Injected 50ms usleep delay-gated loop at 0x599c0..0x599d0')

# D. Ensure 0x57990 has b #0x579ec (skip error check in BAuth_Enroll_Init)
b_srv[0x57990:0x57994] = b'\x17\x00\x00\x14'

# E. SIGSEGV Guard in FPBAuthService::set_active_group at 0x5e378
# Replace ldr w8, [x21, #0xc] and following checks with branch to 0x5e38c
sig_bytes = bytearray()
sig_bytes += arm64_b(0x5e378, 0x5e38c) # b #0x5e38c
sig_bytes += b'\x1f\x20\x03\xd5' * 4  # 4x NOP
b_srv[0x5e378:0x5e38c] = sig_bytes
print('Injected SIGSEGV guard at 0x5e378 (b #0x5e38c + NOPs)')

# F. SIGSEGV Guard at 0x5e498:
# Ensure 0x5e49c: ldr w8, [x21, #0xc] is never executed
b_srv[0x5e498:0x5e49c] = arm64_b(0x5e498, 0x5e4b4) # b #0x5e4b4
print('Injected SIGSEGV guard at 0x5e498 (b #0x5e4b4)')

with open(path_srv64, 'wb') as f:
    f.write(b_srv)
print('libbauthserver.so (64-bit) patched successfully!')

print('\n=== Verifying disassembly of patched regions ===')
print('Disassembly of 0x4ea08..0x4ea18:')
for ins in cs.disasm(b_srv[0x4ea08:0x4ea18], 0x4ea08):
    print(f'  0x{ins.address:x}: {ins.mnemonic:8s} {ins.op_str}')

print('\nDisassembly of 0x599b8..0x599d4:')
for ins in cs.disasm(b_srv[0x599b8:0x599d4], 0x599b8):
    print(f'  0x{ins.address:x}: {ins.mnemonic:8s} {ins.op_str}')

print('\nDisassembly of 0x5e378..0x5e390:')
for ins in cs.disasm(b_srv[0x5e378:0x5e390], 0x5e378):
    print(f'  0x{ins.address:x}: {ins.mnemonic:8s} {ins.op_str}')

print('\nDisassembly of 0x5e498..0x5e4a4:')
for ins in cs.disasm(b_srv[0x5e498:0x5e4a4], 0x5e498):
    print(f'  0x{ins.address:x}: {ins.mnemonic:8s} {ins.op_str}')

print('\n=== 3. Adding build marker and version info ===')
VERSION_TAG = 'v10_fp_common_prepare_and_sigsegv_fix'
marker_dir = '/home/arnav/M51_85_STABLE_REBASE/work/extracted/vendor/vendor/etc'
with open(os.path.join(marker_dir, 'fp_patch_version.txt'), 'w') as f:
    f.write(f'{VERSION_TAG}\n')

# Update property in vendor/default.prop
prop_file = '/home/arnav/M51_85_STABLE_REBASE/work/extracted/vendor/vendor/default.prop'
if os.path.exists(prop_file):
    with open(prop_file, 'r') as f:
        props = f.read()
    if re.search(r'^ro\.vendor\.fp\.patch=.*$', props, re.M):
        props = re.sub(r'^ro\.vendor\.fp\.patch=.*$', f'ro.vendor.fp.patch={VERSION_TAG}', props, flags=re.M)
    else:
        props += f'\nro.vendor.fp.patch={VERSION_TAG}\n'
    with open(prop_file, 'w') as f:
        f.write(props)
    print(f'Updated ro.vendor.fp.patch={VERSION_TAG} in default.prop')

# Update property in vendor/build.prop
build_prop = '/home/arnav/M51_85_STABLE_REBASE/work/extracted/vendor/vendor/build.prop'
if os.path.exists(build_prop):
    with open(build_prop, 'r') as f:
        props = f.read()
    if re.search(r'^ro\.vendor\.fp\.patch=.*$', props, re.M):
        props = re.sub(r'^ro\.vendor\.fp\.patch=.*$', f'ro.vendor.fp.patch={VERSION_TAG}', props, flags=re.M)
    else:
        props += f'\nro.vendor.fp.patch={VERSION_TAG}\n'
    with open(build_prop, 'w') as f:
        f.write(props)
    print(f'Updated ro.vendor.fp.patch={VERSION_TAG} in build.prop')

print('\n=== 4. Verifying camera and floating features ===')
path3 = '/home/arnav/M51_85_STABLE_REBASE/work/extracted/system/system/system/etc/floating_feature.xml'
if os.path.exists(path3):
    with open(path3, 'r', encoding='utf-8') as f:
        c3 = f.read()
    c3 = re.sub(r'\s*<SEC_FLOATING_FEATURE_CAMERA_SUPPORT_60FPS>[^<]*</SEC_FLOATING_FEATURE_CAMERA_SUPPORT_60FPS>\n?', '\n', c3)
    c3 = re.sub(r'\s*<SEC_FLOATING_FEATURE_CAMERA_SUPPORT_FHD_60FPS>[^<]*</SEC_FLOATING_FEATURE_CAMERA_SUPPORT_FHD_60FPS>\n?', '\n', c3)
    with open(path3, 'w', encoding='utf-8') as f:
        f.write(c3)

path4 = '/home/arnav/M51_85_STABLE_REBASE/work/extracted/system/system/system/cameradata/camera-feature.xml'
if os.path.exists(path4):
    with open(path4, 'r', encoding='utf-8') as f:
        c4 = f.read()
    c4 = re.sub(r'\s*<local name="BACK_CAMCORDER_RESOLUTION_FEATURE_MAP_1920X1080_60FPS"[^>]*/>\n?', '\n', c4)
    c4 = c4.replace('<local name="BACK_WIDE_CAMERA_PREVIEW_FPS_MIN" value="30" />', '<local name="BACK_WIDE_CAMERA_PREVIEW_FPS_MIN" value="10" />')
    c4 = c4.replace('<local name="CAMERA_PREVIEW_FPS_MIN" value="30" />', '<local name="CAMERA_PREVIEW_FPS_MIN" value="15" />')
    with open(path4, 'w', encoding='utf-8') as f:
        f.write(c4)

print('\n=== ALL V10 FIXES APPLIED CLEANLY ===')

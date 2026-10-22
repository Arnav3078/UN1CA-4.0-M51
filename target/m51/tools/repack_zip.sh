#!/bin/bash
set -ex
ZIP_ROOT="/home/arnav/M51_85_STABLE_REBASE/work/final-package/zip-root"
UNSIGNED_ZIP="/home/arnav/M51_85_STABLE_REBASE/work/final-package/UN1CA_4.0.0_OneUI8.5_m51-unsigned.zip"
SIGNED_ZIP="/home/arnav/M51_85_STABLE_REBASE/work/final-package/UN1CA_4.0.0_OneUI8.5_m51-signed.zip"
SIGNAPK="/home/arnav/a71_clean_port/UN1CA/out/tools/bin/signapk"
KEY_X509="/home/arnav/a71_clean_port/UN1CA/external/signapk/external/platform_build/target/product/security/testkey.x509.pem"
KEY_PK8="/home/arnav/a71_clean_port/UN1CA/external/signapk/external/platform_build/target/product/security/testkey.pk8"

echo "=== Repacking unsigned zip ==="
cd "$ZIP_ROOT"
rm -f "$UNSIGNED_ZIP"
zip -q -r -0 "$UNSIGNED_ZIP" .
ls -lh "$UNSIGNED_ZIP"

echo "=== Signing package with testkey ==="
rm -f "$SIGNED_ZIP"
"$SIGNAPK" -w "$KEY_X509" "$KEY_PK8" "$UNSIGNED_ZIP" "$SIGNED_ZIP"
ls -lh "$SIGNED_ZIP"

echo "=== Verifying signed zip integrity ==="
unzip -t "$SIGNED_ZIP" | tail -n 5

echo "=== Copying to Windows Downloads ==="
cp -af "$SIGNED_ZIP" /mnt/c/Users/s/Downloads/
ls -lh /mnt/c/Users/s/Downloads/UN1CA_4.0.0_OneUI8.5_m51-signed.zip
echo "=== ALL DONE ==="

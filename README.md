<h1 align="center">
  <img loading="lazy" src="readme-res/banner.png"/>
</h1>
<p align="center">
  <a href="https://github.com/Arnav3078/UN1CA-4.0-M51/blob/oneui-8.5/LICENSE"><img loading="lazy" src="https://img.shields.io/github/license/Arnav3078/UN1CA-4.0-M51?style=for-the-badge&logo=github"/></a>
  <a href="https://github.com/Arnav3078/UN1CA-4.0-M51/commits/oneui-8.5"><img loading="lazy" src="https://img.shields.io/github/last-commit/Arnav3078/UN1CA-4.0-M51/oneui-8.5?style=for-the-badge"/></a>
  <a href="https://github.com/Arnav3078/UN1CA-4.0-M51/stargazers"><img loading="lazy" src="https://img.shields.io/github/stars/Arnav3078/UN1CA-4.0-M51?style=for-the-badge"/></a>
</p>
<p align="center"><b>UN1CA 4.0</b> — One UI 8.5 Custom Firmware for <b>Samsung Galaxy M51 (SM-M515F / m51)</b></p>

---

## 📱 About This Release
This repository provides the complete source tree, device target configuration, and porting patches for **UN1CA 4.0 (One UI 8.5)** tailored specifically for the **Samsung Galaxy M51** (Qualcomm Snapdragon 730G / `sm7150`).

- **ROM Version:** UN1CA 4.0.0-m51
- **One UI Version:** One UI 8.5 (Android 16 / SDK 36)
- **Source Firmware:** Samsung Galaxy S23 FE (`SM-S711U1` / `r11quew` / `BP4A.251205.006.S711U1UES8FZF2`)
- **Target Vendor:** Samsung Galaxy M51 (`SM-M515F` / `m51nsxx` / `M515FXXS6DXE4`)
- **Kernel:** LostPrime Kernel (`4.14.357-openela-LostPrime-g54d444ba7c65`) with KernelSU
- **Official Package:** `UN1CA_4.0.0_OneUI8.5_m51-signed.zip`
- **Official SHA256:** `be5fb6051ae9c94eef0054be59e00b87922b3bbbc439ad686298167660946a7b`
- **Status:** Verified 1:1 Stable Release

---

## ✨ Features & Device Adaptations

### 🛠️ Hardware & Port Fixes for Galaxy M51
- **Capacitive Side Fingerprint Sensor:** Full side-sensor configuration and position mapping (`google_touch_side,settings=3,navi=1`) with patched `libbauthtzcommon` / `libbauthserver` and framework integration.
- **Face Unlock:** Fully functional biometrics stack supporting both 2.0 and 3.0 HALs.
- **Audio & Sound:** Dolby Atmos in-game, SoundAlive custom equalizer, dual speaker / head-tracking audio profiles.
- **Display & Refresh Rate:** Extra Brightness support, MDNIE hardware tuning, and adaptive refresh rate enhancements.
- **Camera:** Preserved M51 stock multi-camera feature profiles (`camera-feature.xml` & `media_profiles_vendor.xml`).
- **Network & Connectivity:** Dual-SIM multisim support, VoLTE, VoWiFi, and high-performance Wi-Fi concurrency.
- **Kernel:** Pre-integrated with LostPrime Kernel supporting KernelSU for root and module management.
- **OTA Updates:** Integrated OTA updater configuration tracking [UN1CA-M51-Updates](https://github.com/Arnav3078/UN1CA-M51-Updates).

---

## 🌟 Upstream & Full Credits
This project stands on the shoulders of giants. Full credit and heartfelt appreciation go to:

### 👑 Project Leaders & Upstream Creators:
- **[Salvo Giangreco (@salvogiangri)](https://github.com/salvogiangri)**:
  - Original **Creator, Project Architect & Lead Developer of UN1CA**.
  - Architect of the UN1CA modular patch system, build system, and One UI porting ecosystem.
- **[Mehedi H Joy (@mehedihjoy0)](https://github.com/mehedihjoy0)**:
  - Maintainer of **[UN1CA-SM7150](https://github.com/mehedihjoy0/UN1CA-SM7150)** 
  - Initial Galaxy M51 (`target/m51`) bring-up, Snapdragon 7150 platform hardware adaptations, audio/camera blobs, and One UI 8.x/8.5 compatibility patches.

### 🤝 Additional Contributions:
- **[kurtnettle](https://github.com/kurtnettle)** for the excellent LostPrime Kernel for SM7150 with KernelSU support.
- **[ShaDisNX255](https://github.com/ShaDisNX255)** for NcX ROM and invaluable community guidance.
- **[Arnav (@Arnav3078)](https://github.com/Arnav3078)** for UN1CA 4.0 One UI 8.5 stable rebase, side-sensor/face unlock fixes, OTA maintenance, and device trees.
- The entire UN1CA and Samsung porting community!

---

## 🌿 Repository Branches

| Branch | Description |
| :--- | :--- |
| **`oneui-8.5`** | **Active branch** containing One UI 8.5 source code, M51 target configs, tools, and patches. |
| **`un1ca-4.0`** | Release branch for UN1CA 4.0.0 milestone. |
| **`sixteen`** | Base UN1CA upstream branch tracking SM7150. |

---

## 🚀 Building from Source

### 1. Prerequisites (Ubuntu / Debian / WSL2)
```bash
sudo apt update && sudo apt install -y \
    git curl wget python3 python3-pip zip unzip openjdk-17-jdk \
    build-essential libxml2-utils erofs-utils
```

### 2. Clone the Repository
```bash
git clone https://github.com/Arnav3078/UN1CA-4.0-M51.git -b oneui-8.5
cd UN1CA-4.0-M51
```

### 3. Initialize Build Environment for Galaxy M51
```bash
source buildenv.sh m51
```

### 4. Build Target Files & Flashable ZIP
```bash
./scripts/internal/create_target_files_zip.sh out/m51_target_files.zip
./scripts/build_flashable_zip.sh out/m51_target_files.zip
```
Your flashable ROM package will be produced in the `out/` directory.

---

## 📜 Licensing
This project is licensed under the **GNU General Public License v3.0 (GPL-3.0)** - see the [LICENSE](LICENSE) file for details.

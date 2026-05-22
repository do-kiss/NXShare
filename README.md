# NXShare

**A Nintendo Switch Homebrew app to transfer your screenshots and videos to any device via browser.**

![NXShare](icon.jpg)

---

## What it does

NXShare starts a small web server on your Switch. Open the displayed URL in any browser on a PC, phone or tablet (same WiFi required), and you get a clean gallery view of all your screenshots and videos - with thumbnails, filters and multi-select download.

- 🎬 Browse and view all screenshots and videos
- 🔍 Filter by screenshots/videos or by game
- ⬇️ Download individual files or select multiple at once



## Screenshots

![NXShare Gallery](screenshot.jpg)

---

## Compatibility

| | |
|---|---|
| **Atmosphère** | tested 1.9.3 and 1.11.1 |
| **Firmware** | tested 20.3.0 and 22.0.0 |
| **Storage** | SysMMC and emuMMC (auto-detected) |

---

## Installation

Download the latest `NXShare.nro` from the [Releases](../../releases) page and copy it to the `switch/` folder on your SD card


NXShare is also available in the Homebrew App Store

---

## Usage

1. Make sure your Switch is connected to WiFi
2. Launch NXShare from the Homebrew Launcher (Applet Mode)
3. The screen shows a URL / QR code. Open the URL in any browser on the same network, or scan the QR code
5. Browse, preview and download your media

---

## Building from source

See [BUILD.md](BUILD.md) for detailed instructions.

```bash
pacman -S switch-dev
git clone https://github.com/musebrot1/NXShare
cd NXShare
make all
```

---

## Credits

- **[libnx](https://github.com/switchbrew/libnx)** by switchbrew — Nintendo Switch homebrew library (ISC License)
- **[devkitPro](https://devkitpro.org)** — ARM toolchain and build system
- **[NXGallery](https://github.com/iUltimateLP/NXGallery)** by iUltimateLP — inspiration for capsa API usage

---

## License

MIT License — see [LICENSE](LICENSE) for details.

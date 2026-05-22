# NXShare – Build Guide (Windows)

## Requirements

**devkitPro** (free, official Nintendo Switch homebrew SDK)

---

## Step 1: Install devkitPro

1. Go to: https://github.com/devkitPro/installer/releases
2. Download the latest **`devkitProUpdater-X.X.X.exe`**
3. Run the installer as Administrator
4. When selecting components, check:
   - ✅ **Switch Development** (required)
   - ✅ **devkitARM** (sometimes needed)
5. Let everything install (~5-10 minutes, downloads ~500 MB)
6. Leave the default path as `C:\devkitPro`

---

## Step 2: Open the MSYS2 terminal

devkitPro automatically installs an MSYS2 environment.

1. Open the **Start Menu**
2. Search for **"MSYS2"** or **"devkitPro MSYS2"**
3. Launch it — a terminal window will open

---

## Step 3: Install required packages

In the MSYS2 terminal:

```bash
pacman -Syu
pacman -S switch-dev
```

Press `Y` and Enter when prompted.

---

## Step 4: Build the project

Navigate to the project folder in the MSYS2 terminal:

```bash

make all
```

If everything worked, you will see at the end:
```
Built: NXShare.nro
```

---

## Step 5: Copy the app to your Switch


Copy `NXShare.nro` to the `switch/` folder on your SD card:
   ```
   SD:/switch/NXShare.nro
   ```

---

## Step 6: Launch the app

1. Boot with **Atmosphère**
2. Open the **Homebrew Launcher** (in Applet Mode)
3. Launch **NXShare** 
4. The screen will show an IP address, e.g. `http://192.168.1.42:8080`
5. Open that URL in a browser on your phone or PC — done! 🎉

---

## Troubleshooting

| Problem | Solution |
|--------|--------|
| `make: command not found` | devkitPro not installed correctly, reinstall |
| `DEVKITPRO not set` | Use the devkitPro MSYS2 terminal, not regular CMD |
| No network connection | Switch WiFi connected? Same router as PC/phone? |
| No media found | Any screenshots/videos on the Switch? Correct emuMMC path? |
| Compilation errors | In MSYS2 terminal: `pacman -S switch-dev` and try again |

---

## Compatibility

- ✅ Atmosphère tested 1.9.3 - 1.11.1
- ✅ SysMMC and emuMMC (album path is detected automatically)
- ✅ JPG and PNG screenshots, MP4 videos
- ✅ All modern browsers (Chrome, Firefox, Safari, Edge)

---

## Web app features

- 📷 View and download all files from the Album in the browser
- ⬇️ Download individual files with one click
- ✅ Select and download multiple files at once
- 🔍 Filter by screenshots/videos or games


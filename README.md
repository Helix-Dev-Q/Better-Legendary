# Legendary Manifest Installer

A simple GUI for downloading specific Fortnite builds using manifest files, no Epic Games Launcher needed.

---

## How it works

You need two things before you can download anything:

**1. A manifest file**
Manifests tell the downloader exactly what files a specific build of Fortnite is made of. You can find manifests for different Fortnite versions here:
👉 https://github.com/polynite/fn-releases

*NOTE:* older versions like 12.41 for example wont work they'll have to be recent fortnite builds.

Download the `.manifest` file for whichever version you want.

**2. An Epic Games account**
The files are downloaded directly from Epic's servers, so you need to be signed in. You only have to do this once.

---

## Installation

**Step 1 — Build it yourself**

You'll need Python 3.9+ installed. Clone the repo, open a terminal in the folder, and run these commands:

```
python -m venv .venv
.venv\Scripts\pip install -e .
.venv\Scripts\pip install pyinstaller
.venv\Scripts\pyinstaller --onefile --windowed --icon=assets/windows_icon.ico --name better-legendary --add-data "legendary;legendary" better-legendary.py
```

The finished `better-legendary.exe` will be in the `dist/` folder.

---

## Signing in

1. Go to the **Auth** tab
2. Click **Open Login Page** — a browser window will open
3. You'll see a page with some JSON, find the `authorizationCode` value and copy it (just the code, no quotes)
4. Paste it into the Auth code box and hit Login
5. It'll show your Epic username when it works

You only need to do this once.

---

## Downloading a build

1. Go to the **Install** tab
2. Select your `.manifest` file
3. Pick a folder to download into
4. Leave the Base URL and App name as default unless you know what you're changing
5. Pick what you want to download — Core is required, everything else is optional
6. Hit **Start Download**

It shows live progress and an ETA while it runs. You can stop it at any time and it'll resume from where it left off next time.

---

## Troubleshooting

- **Login failed** — make sure you only copied the code value, not the whole JSON
- **Download keeps erroring** — just restart it, it resumes automatically
- **App won't open** — make sure you're on Windows 10/11 64-bit

# ==========================================================================
# Buildozer configuration - Medicine Assistant APK
# Build with:  buildozer -v android debug
# ==========================================================================
[app]

title = Medicine Assistant
package.name = medicineassistant
package.domain = org.medicineassistant.app

# Application code lives in this folder (main.py is the entry point).
source.dir = .
source.include_exts = py,png,jpg,kv,ttf,txt,md

version = 0.5

# Pure-python requirements only (sqlite3 is built into Android Python).
# pyjnius comes automatically with kivy (used for Android TTS + ML Kit OCR).
requirements = python3,kivy==2.3.1,charset_normalizer==3.3.2

# On-device OCR (Google ML Kit, FREE + offline inference - no cloud API,
# no key, no data leaves the phone). Latin script model.
android.gradle_dependencies = com.google.mlkit:text-recognition:16.0.1

# Bundle the OCR model in the APK at install time -> scanning works
# even on the very first run without internet.
android.meta_data = com.google.mlkit.vision.DEPENDENCIES=ocr

orientation = portrait
fullscreen = 0

# Branding: custom icon + splash (judges ka pehla impression!)
icon.filename = %(source.dir)s/assets/icon.png
presplash.filename = %(source.dir)s/assets/presplash.png

# Modern phones (64-bit). Building one arch is much faster.
android.archs = arm64-v8a
android.api = 33
# API 24+: CPython 3.14 (remote_debugging.c) needs preadv/pwritev,
# which the NDK only declares from API 24 upwards.
android.minapi = 24

# Only ONE runtime permission: RECORD_AUDIO, asked just-in-time when the
# user taps the mic button for voice search (SpeechRecognizer is on-device
# on most phones). Gallery photos use the system picker (no storage
# permission), ML Kit OCR and TTS run on-device. INTERNET is not requested.
android.permissions = RECORD_AUDIO

[buildozer]
log_level = 1
# Keep the Android SDK/NDK inside this folder (self-contained).
# buildozer.dir = ./.buildozer

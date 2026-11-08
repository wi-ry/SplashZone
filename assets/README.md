# Splash Zone listing artwork

- `store/SplashZone-Store-540x405.png` is the 540×405 Streaming Store image.
- `../images/channel-icon_FHD.png` is the same 540×405 art included in the channel ZIP and referenced by `mm_icon_focus_fhd` in the manifest.
- `../images/channel-icon_HD.png` is the 290×218 HD variant used by devices running the HD Roku UI.
- `../images/splash-screen_HD.jpg` is the 1280×720 launch splash image referenced by `splash_screen_hd`.
- `screenshots/SplashZone-Screenshot-01-1920x1080.png` through `03` are 1920×1080 representative preview renders at 0, 8, and 16 seconds of simulated fish and bubble motion.

The preview renders are generated from the scene layout; they were not captured from a running Roku device or emulator. Capture actual device/emulator screenshots before using them wherever Roku requires genuine app screenshots.

Regenerate these images with `python scripts/generate_store_assets.py` (requires Pillow).

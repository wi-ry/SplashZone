# Splash Zone project guidance

- This repository is a standalone Roku SceneGraph screensaver, not a streaming app.
- Preserve `RunScreenSaver()` as the entry point; do not add `Main()` or `RunUserInterface()`.
- Screensavers must not require user input or use audio/video playback.
- Keep the app identity as **Splash Zone** in the manifest and release package.
- Keep SceneGraph XML and BrightScript valid, and ensure component and script references resolve.
- The scene uses Roku's FHD `1920x1080` UI coordinate space; describe 4K TV support as scaled UI, not native UHD rendering.
- Run `npm run lint` and `npm run build` after code changes. The build validator writes `dist/SplashZone.zip`.
- A pre-commit hook bumps SemVer from staged added/deleted lines: up to 20 lines bumps patch, 21–100 bumps minor, and over 100 bumps major. It updates `package.json`, `package-lock.json`, and the Roku manifest together.
- Keep generated files, dependencies, and local secrets out of version control; see `.gitignore`.

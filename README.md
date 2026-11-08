# Splash Zone

A standalone Roku SceneGraph screensaver with animated stick-drawn fish, rising outlined bubbles, and a simple underwater backdrop. It uses no external images, video, audio, or interactive controls.

The scene motion is driven by a SceneGraph `Timer` that updates each fish and bubble position. On device, the BrightScript console prints `[Splash Zone] Motion timer started` and `[Splash Zone] Motion timer tick received` when its motion loop is running.

## Roku display resolution

The scene is authored in Roku's FHD (`1920x1080`) SceneGraph coordinate space and is suitable for 4K Roku TVs, which scale the app UI to the display. Roku's app manifest UI resolution setting does not provide a native 4K SceneGraph mode, so this project does not claim native UHD rendering.

## Development

Install Node.js and Python, then install the BrightScript lint dependencies:

```sh
npm ci
```

Run the BrightScript/SceneGraph linter and project checks:

```sh
npm run lint
```

Build and validate the installable channel package:

```sh
npm run build
```

The development/sideload ZIP is written to `dist/SplashZone.zip`. It contains the channel files with `manifest` at the archive root and HD/FHD channel icons declared in the manifest; it is **not** a signed Streaming Store submission package. Roku uses the appropriate icon variant for its UI resolution. Generated project artwork and screenshot previews are in [`assets/`](</W:/Development/SplashZone/assets>).

### Create a Streaming Store package

Roku requires a signed `.pkg` for Streaming Store submission. The `.pkg` cannot be produced by this CI build: Roku's packaging guide requires sideloading the app to a linked, internet-connected Roku development device and signing it with a key stored on that device.

1. Sideload `dist/SplashZone.zip` to your Roku development device using its Development Application Installer.
2. Generate or restore the correct developer key on the Roku. For a new app, Roku's guide uses the device's `genkey` utility; keep the developer ID and password private.
3. Open the device's Development Application page, select **Packager**, and create the signed package using the app name, version, and key password.
4. Download the resulting `.pkg` and upload that signed package to the Streaming Store beta submission. Do not upload `dist/SplashZone.zip` as the store package.

See Roku's [Packaging Roku apps guide](https://developer.roku.com/dev/docs/packaging-channels) for key generation, signing, and repackaging details. Keep signing passwords and keys out of this repository and CI.

GitHub Actions runs lint, version-policy tests, and build checks on pushes and pull requests. Every successful push to `main` automatically creates a GitHub Release tagged from `package.json` (for example, `v2.0.1`) and attaches the unsigned development ZIP with a versioned filename such as `SplashZone-v2.0.1-dev-sideload.zip`. No manual tag is needed. The release asset is not the signed `.pkg` required by the Streaming Store. If a release is retried for the same commit, its ZIP is replaced; an existing version attached to a different commit causes the release job to fail rather than overwrite it.

### Automatic SemVer

The Git pre-commit hook counts added and deleted lines in staged changes, excluding version metadata. It increments the patch for up to 20 changed lines, the minor version for 21–100 lines, and the major version for more than 100 lines. Minor bumps reset patch to zero; major bumps reset minor and patch to zero. `package.json`, `package-lock.json`, and the Roku manifest stay in sync, and the hook stages the version updates automatically.

Install dependencies with `npm ci` or run `npm run prepare` to enable the repository's `.githooks` hook path. The initial commit establishes the baseline and does not bump; later commits with no staged source changes do not bump. CI does not install local Git hooks.

## AI agent support

Repository-specific guidance is in `.github/copilot-instructions.md`. The `.github/skills/roku-screensaver-ci/SKILL.md` skill describes how to validate, build, and extend the Roku screensaver.

## License

Splash Zone is released under the MIT License. See [LICENSE](LICENSE).

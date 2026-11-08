---
name: roku-screensaver-ci
description: 'Lint, validate, build, and package the Splash Zone Roku SceneGraph screensaver. Use when changing BrightScript, SceneGraph XML, the Roku manifest, CI, or the installable ZIP.'
argument-hint: 'Describe the Roku screensaver change to validate or build'
---

# Splash Zone Roku screensaver workflow

## When to use

- Changing BrightScript or SceneGraph components.
- Updating the channel manifest or screensaver entry point.
- Running project checks or producing the sideloadable Roku package.

## Procedure

1. Install locked dependencies with `npm ci` if needed.
2. Run `npm run lint` to check BrightScript diagnostics, XML structure, component/script links, animation targets, and screensaver manifest requirements.
3. Run `npm run build` to validate the project and create `dist/SplashZone.zip`, an unsigned development/sideload ZIP.
4. Confirm the archive contains `manifest`, `source/`, and `components/` at its root. Do not present this ZIP as a signed Streaming Store package.
5. To submit to the Streaming Store, sideload the ZIP onto a linked, internet-connected Roku development device and generate the signed `.pkg` through Roku's Development Application Packager. Never put signing keys or passwords in source control or CI.
6. For runtime changes, install the development package on a Roku device and confirm the screensaver closes on remote input.
7. Do not describe the FHD SceneGraph UI as native 4K; Roku scales it on 4K TVs.

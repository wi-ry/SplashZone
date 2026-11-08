const { execFileSync } = require("node:child_process");
const fs = require("node:fs");
const path = require("node:path");

const root = path.resolve(__dirname, "..");
const excludedPaths = [
    ".",
    ":(exclude)package.json",
    ":(exclude)package-lock.json",
    ":(exclude)manifest",
];

function getNextVersion(version, changedLines) {
    const match = /^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$/.exec(version);
    if (!match) {
        throw new Error(`Expected a stable SemVer version, received "${version}".`);
    }

    if (!Number.isInteger(changedLines) || changedLines < 0) {
        throw new Error("Changed line count must be a non-negative integer.");
    }
    if (changedLines === 0) {
        return null;
    }

    let [, major, minor, patch] = match.map(Number);
    if (changedLines <= 20) {
        patch += 1;
    } else if (changedLines <= 100) {
        minor += 1;
        patch = 0;
    } else {
        major += 1;
        minor = 0;
        patch = 0;
    }

    return `${major}.${minor}.${patch}`;
}

function getStagedChangedLines() {
    const result = execFileSync(
        "git",
        ["diff", "--cached", "--numstat", "--", ...excludedPaths],
        { cwd: root, encoding: "utf8" },
    );

    return result.split(/\r?\n/).reduce((total, line) => {
        if (!line) {
            return total;
        }
        const [added, deleted] = line.split("\t");
        if (added === "-" || deleted === "-") {
            return total;
        }
        return total + Number(added) + Number(deleted);
    }, 0);
}

function updateManifest(manifest, version) {
    const [major, minor, patch] = version.split(".");
    const values = {
        major_version: major,
        minor_version: minor,
        build_version: patch.padStart(5, "0"),
    };

    for (const [key, value] of Object.entries(values)) {
        const expression = new RegExp(`^${key}=.*$`, "gm");
        const matches = manifest.match(expression) ?? [];
        if (matches.length !== 1) {
            throw new Error(`Expected exactly one ${key} entry in the manifest.`);
        }
        manifest = manifest.replace(expression, `${key}=${value}`);
    }

    return manifest;
}

function bumpVersion() {
    try {
        execFileSync("git", ["rev-parse", "--verify", "HEAD"], {
            cwd: root,
            stdio: "ignore",
        });
    } catch {
        console.log("Initial commit; keeping the baseline version.");
        return;
    }

    const changedLines = getStagedChangedLines();
    const packagePath = path.join(root, "package.json");
    const packageLockPath = path.join(root, "package-lock.json");
    const manifestPath = path.join(root, "manifest");
    const packageJson = JSON.parse(fs.readFileSync(packagePath, "utf8"));
    const nextVersion = getNextVersion(packageJson.version, changedLines);

    if (nextVersion === null) {
        console.log("No staged source changes; skipping automatic version bump.");
        return;
    }

    const packageLock = JSON.parse(fs.readFileSync(packageLockPath, "utf8"));
    if (
        packageLock.version !== packageJson.version ||
        packageLock.packages?.[""]?.version !== packageJson.version
    ) {
        throw new Error("package.json and package-lock.json versions do not match.");
    }

    const manifest = fs.readFileSync(manifestPath, "utf8");
    const nextManifest = updateManifest(manifest, nextVersion);
    packageJson.version = nextVersion;
    packageLock.version = nextVersion;
    packageLock.packages[""].version = nextVersion;

    fs.writeFileSync(packagePath, `${JSON.stringify(packageJson, null, 2)}\n`);
    fs.writeFileSync(packageLockPath, `${JSON.stringify(packageLock, null, 2)}\n`);
    fs.writeFileSync(manifestPath, nextManifest);

    execFileSync("git", ["add", "--", "package.json", "package-lock.json", "manifest"], {
        cwd: root,
        stdio: "inherit",
    });
    console.log(
        `Bumped Splash Zone to ${nextVersion} for ${changedLines} staged added/deleted lines.`,
    );
}

if (require.main === module) {
    try {
        bumpVersion();
    } catch (error) {
        console.error(`Automatic version bump failed: ${error.message}`);
        process.exitCode = 1;
    }
}

module.exports = { getNextVersion, updateManifest };

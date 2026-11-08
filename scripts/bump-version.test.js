const assert = require("node:assert/strict");
const { execFileSync } = require("node:child_process");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const test = require("node:test");

const { getNextVersion, updateManifest } = require("./bump-version");

test("bumps patch for changes up to 20 lines", () => {
    assert.equal(getNextVersion("1.2.3", 1), "1.2.4");
    assert.equal(getNextVersion("1.2.3", 20), "1.2.4");
});

test("bumps minor for changes between 21 and 100 lines", () => {
    assert.equal(getNextVersion("1.2.3", 21), "1.3.0");
    assert.equal(getNextVersion("1.2.3", 100), "1.3.0");
});

test("bumps major for changes over 100 lines", () => {
    assert.equal(getNextVersion("1.2.3", 101), "2.0.0");
});

test("does not bump when no source lines changed", () => {
    assert.equal(getNextVersion("1.2.3", 0), null);
});

test("rejects invalid versions and line counts", () => {
    assert.throws(() => getNextVersion("v1.2.3", 1), /stable SemVer/);
    assert.throws(() => getNextVersion("1.2.3", -1), /non-negative integer/);
});

test("synchronizes SemVer fields in the Roku manifest", () => {
    const manifest = [
        "screensaver_title=Splash Zone",
        "major_version=1",
        "minor_version=2",
        "build_version=00003",
        "ui_resolutions=fhd",
        "",
    ].join("\n");

    assert.equal(
        updateManifest(manifest, "4.5.6"),
        manifest
            .replace("major_version=1", "major_version=4")
            .replace("minor_version=2", "minor_version=5")
            .replace("build_version=00003", "build_version=00006"),
    );
});

test("updates and stages all version files for a commit", (t) => {
    const repository = fs.mkdtempSync(path.join(os.tmpdir(), "splash-zone-version-"));
    t.after(() => fs.rmSync(repository, { recursive: true, force: true }));

    const write = (relativePath, content) => {
        const filePath = path.join(repository, relativePath);
        fs.mkdirSync(path.dirname(filePath), { recursive: true });
        fs.writeFileSync(filePath, content);
    };
    const runGit = (...args) =>
        execFileSync("git", args, { cwd: repository, stdio: "ignore" });

    write("package.json", JSON.stringify({ version: "1.2.3" }));
    write(
        "package-lock.json",
        JSON.stringify({
            version: "1.2.3",
            packages: { "": { version: "1.2.3" } },
        }),
    );
    write(
        "manifest",
        "screensaver_title=Splash Zone\nmajor_version=1\nminor_version=2\nbuild_version=00003\n",
    );
    write("scripts/bump-version.js", fs.readFileSync(require.resolve("./bump-version.js")));
    write("src/change.brs", "baseline\n");

    runGit("init", "--quiet");
    runGit("config", "user.name", "Splash Zone test");
    runGit("config", "user.email", "test@example.invalid");
    runGit("add", ".");
    runGit("commit", "--quiet", "-m", "baseline");

    write("src/change.brs", `${"updated\n".repeat(10)}`);
    runGit("add", "src/change.brs");
    execFileSync(process.execPath, ["scripts/bump-version.js"], {
        cwd: repository,
        stdio: "ignore",
    });

    assert.equal(JSON.parse(fs.readFileSync(path.join(repository, "package.json"))).version, "1.2.4");
    assert.equal(
        JSON.parse(fs.readFileSync(path.join(repository, "package-lock.json"))).packages[""].version,
        "1.2.4",
    );
    assert.match(
        fs.readFileSync(path.join(repository, "manifest"), "utf8"),
        /build_version=00004/,
    );
    const stagedFiles = execFileSync("git", ["diff", "--cached", "--name-only"], {
        cwd: repository,
        encoding: "utf8",
    }).trim().split(/\r?\n/);
    assert.ok(stagedFiles.includes("package.json"));
    assert.ok(stagedFiles.includes("package-lock.json"));
    assert.ok(stagedFiles.includes("manifest"));
});

const { execFileSync } = require("node:child_process");
const path = require("node:path");

const root = path.resolve(__dirname, "..");

if (process.env.CI) {
    console.log("Skipping local Git hook setup in CI.");
    process.exit(0);
}

try {
    execFileSync("git", ["rev-parse", "--show-toplevel"], {
        cwd: root,
        stdio: "ignore",
    });
    execFileSync("git", ["config", "--local", "core.hooksPath", ".githooks"], {
        cwd: root,
        stdio: "inherit",
    });
    console.log("Configured Git to use .githooks.");
} catch (error) {
    console.error("Could not configure the Splash Zone Git hooks.", error.message);
    process.exit(1);
}

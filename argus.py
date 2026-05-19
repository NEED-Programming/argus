#!/usr/bin/env python3

import os
import shutil
import subprocess
import sys
from pathlib import Path

# ── ANSI Colors ───────────────────────────────────────────────────────────────
RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

def banner():
    print(f"""{CYAN}{BOLD}
  █████╗ ██████╗  ██████╗ ██╗   ██╗███████╗
 ██╔══██╗██╔══██╗██╔════╝ ██║   ██║██╔════╝
 ███████║██████╔╝██║  ███╗██║   ██║███████╗
 ██╔══██║██╔══██╗██║   ██║██║   ██║╚════██║
 ██║  ██║██║  ██║╚██████╔╝╚██████╔╝███████║
 ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝  ╚═════╝ ╚══════╝
  The Hundred-Eyed — Bug Bounty Recon Pipeline
  subfinder → httpx → gowitness
{RESET}""")

def info(msg):    print(f"{GREEN}[+]{RESET} {msg}")
def warn(msg):    print(f"{YELLOW}[!]{RESET} {msg}")
def error(msg):   print(f"{RED}[-]{RESET} {msg}")
def section(msg): print(f"\n{BOLD}{CYAN}━━ {msg} ━━{RESET}")


# ── Tool Definitions ──────────────────────────────────────────────────────────
TOOLS = {
    "subfinder": "go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest",
    "httpx":     "go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest",
    "gowitness": "go install github.com/sensepost/gowitness/v3@latest",
}

EXTRA_PATHS = [
    Path.home() / "go" / "bin",
    Path("/usr/local/bin"),
    Path("/usr/bin"),
]


def find_tool(name: str) -> str | None:
    # Check EXTRA_PATHS first so ~/go/bin takes priority over system PATH
    # (avoids picking up Python's httpx instead of the Go version)
    for p in EXTRA_PATHS:
        candidate = p / name
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate)
    return shutil.which(name)


def preflight() -> dict[str, str]:
    section("Preflight Tool Check")
    paths = {}

    for tool, install_cmd in TOOLS.items():
        path = find_tool(tool)
        if path:
            info(f"{tool:12s} found → {path}")
            paths[tool] = path
        else:
            warn(f"{tool:12s} not found")
            answer = input(f"  Install {BOLD}{tool}{RESET}? [y/N] ").strip().lower()
            if answer == "y":
                info(f"Running: {install_cmd}")
                result = subprocess.run(install_cmd, shell=True)
                if result.returncode == 0:
                    path = find_tool(tool)
                    if path:
                        info(f"{tool} installed → {path}")
                        paths[tool] = path
                    else:
                        error(f"{tool} installed but not found. Add ~/go/bin to your PATH.")
                        sys.exit(1)
                else:
                    error(f"Failed to install {tool}. Exiting.")
                    sys.exit(1)
            else:
                error(f"{tool} is required. Exiting.")
                sys.exit(1)

    info("All tools ready.\n")
    return paths


# ── Pipeline ──────────────────────────────────────────────────────────────────
def run(cmd: list[str], step: str) -> None:
    info(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        error(f"{step} failed. Exiting.")
        sys.exit(1)


def main():
    banner()

    if len(sys.argv) != 2:
        print(f"Usage: python3 argus.py <domain>")
        print(f"Example: python3 argus.py example.com")
        sys.exit(1)

    domain = sys.argv[1]
    tools  = preflight()

    section(f"Target: {domain}")

    # Step 1 — subfinder
    section("Step 1 — Subdomain Enumeration")
    run([tools["subfinder"], "-d", domain, "-silent", "-o", "subs.txt"], "subfinder")

    # Step 2 — httpx
    section("Step 2 — HTTP Probing")
    run([tools["httpx"], "-l", "subs.txt", "-o", "live.txt"], "httpx")

    # Step 3 — gowitness scan
    section("Step 3 — Screenshots")
    run([
        tools["gowitness"], "scan", "file",
        "-f", "live.txt",
        "--write-db",
        "--threads", "10",
        "--delay", "3",
    ], "gowitness scan")

    # Step 4 — gowitness report server
    section("Step 4 — Report Server")
    info("Open your browser → http://127.0.0.1:7171")
    try:
        subprocess.run([tools["gowitness"], "report", "server"])
    except KeyboardInterrupt:
        print(f"\n{YELLOW}[!]{RESET} Server stopped.")


if __name__ == "__main__":
    main()

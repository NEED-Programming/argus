# 👁️ Argus
> *In Greek mythology, Argus Panoptes was a hundred-eyed giant — an all-seeing watchman who never slept.*

Argus is a bug bounty recon pipeline that chains **subfinder**, **httpx**, and **gowitness** into a single command. Point it at a domain and it will enumerate subdomains, probe for live hosts, screenshot everything, and serve you a visual report.

---

## Pipeline

```
subfinder → httpx → gowitness scan → gowitness report server
```

| Step | Tool | What it does |
|------|------|-------------|
| 1 | subfinder | Enumerates subdomains silently |
| 2 | httpx | Probes subdomains for live HTTP/S hosts |
| 3 | gowitness | Screenshots every live host |
| 4 | gowitness | Serves a visual report UI at localhost:7171 |

---

## Requirements

- Python 3.10+
- Go (for installing the tools below)

### Tools
Argus will check for these at runtime and offer to install any that are missing:

| Tool | Source |
|------|--------|
| subfinder | github.com/projectdiscovery/subfinder |
| httpx (Go) | github.com/projectdiscovery/httpx |
| gowitness | github.com/sensepost/gowitness |

> **Note:** If you have Python's `httpx` installed on your system, Argus will correctly prefer the Go version from `~/go/bin`.

Make sure `~/go/bin` is in your PATH:
```bash
echo 'export PATH=$PATH:~/go/bin' >> ~/.bashrc
source ~/.bashrc
```

---

## Installation

```bash
git clone https://github.com/NEED-Programming/argus.git
cd argus
chmod +x argus.py
```

---

## Usage

```bash
python3 argus.py <domain>
```

### Example

```bash
python3 argus.py example.com
```

Argus will:
1. Run a preflight check on all required tools
2. Offer to auto-install any that are missing via `go install`
3. Run the full pipeline
4. Open a report server at `http://127.0.0.1:7171`

---

## Output

All results are written to the current working directory:

```
subs.txt          # All discovered subdomains
live.txt          # Live HTTP/S hosts
screenshots/      # PNG/JPEG screenshots of every live host
gowitness.sqlite3 # gowitness database (used by the report UI)
```

---

## Report UI

Once the pipeline completes, Argus launches the gowitness report server automatically:

```
http://127.0.0.1:7171
```

Browse screenshots, filter by status code, and triage targets visually. Press `Ctrl+C` to stop the server when done.

---

## Preflight Tool Check

On first run against a fresh system:

```
━━ Preflight Tool Check ━━
[!] subfinder     not found
  Install subfinder? [y/N] y
[+] Running: go install -v github.com/projectdiscovery/subfinder/...
[+] subfinder installed → /root/go/bin/subfinder
[+] httpx        found → /root/go/bin/httpx
[+] gowitness    found → /root/go/bin/gowitness
[+] All tools ready.
```

---

## Disclaimer

Argus is intended for **authorized security testing and bug bounty programs only**. Only run against targets you have explicit permission to test. Unauthorized use may violate computer access laws such as the CFAA.

---

## Credits

Built on top of:
- [subfinder](https://github.com/projectdiscovery/subfinder) by ProjectDiscovery
- [httpx](https://github.com/projectdiscovery/httpx) by ProjectDiscovery  
- [gowitness](https://github.com/sensepost/gowitness) by @leonjza

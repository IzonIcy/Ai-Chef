# Security Policy

## Supported versions

Ai-Chef is a small personal tool. Only the latest released version receives
fixes.

| Version | Supported |
| --- | --- |
| 1.0.x | yes |
| < 1.0 | no |

## Reporting a vulnerability

Please **don't** open a public issue for a security problem.

Use GitHub's private reporting: go to the Security tab on this repository and
choose "Report a vulnerability". Include:

- what the issue is and which file/feature it affects
- steps to reproduce, or the relevant prompt/model output if it's a parsing bug
- your OS, Python version, and Ai-Chef version

I'll aim to acknowledge within a week and to ship a fix or a mitigation plan
reasonably promptly.

## Scope

In scope:

- Anything involving `OPENAI_API_KEY` — leaking, logging, or transmitting it.
- Path traversal in the data directory or in grocery-list export paths.
- Parsing untrusted model output in a way that executes code or writes outside
  the intended directory.
- Corrupting or losing user state through `json_store`.

Out of scope:

- Vulnerabilities in third-party dependencies with no reachable path through
  this project's own code — please report those upstream instead.
- Malicious input used to make a bad recipe. The model will believe anything.

## Notes on the design

A few things are deliberate and worth knowing before you report them:

- **User data lives outside the repo**, in the platform data directory
  (`~/.local/share/ai-chef` on Linux, `~/Library/Application Support/ai-chef` on
  macOS). `data_dir.get_data_dir()` is the only thing that constructs a path.
- **Writes are atomic.** `json_store` writes to a temp file and renames, so an
  interrupted write can't corrupt state.
- **The API key is read from the environment or `.env`** and is never written to
  the data directory or included in exports.
- **This is a local single-user CLI.** It has no authentication, no network
  listener, and no multi-user support. Reports about missing auth on a local
  tool aren't vulnerabilities.

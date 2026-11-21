# Source and license

The replay tools, tests, and file and HTTP helpers originate from the [Thorustinfer source release](https://github.com/massif-01/Thorustinfer/tree/3962b5c19f9ebd766809b935f705f6eb34b7c184). Thorustinfer derives from [iMMIQ/orinfer](https://github.com/iMMIQ/orinfer/tree/b5ce33d5c04d244b292c5f7866d79b2e0cb1165d). The source files used here were under `tools/bench` and `python/thorustinfer_build/common/files.py`.

On 2026-11-21 the benchmark modules and their tests were extracted into this repository. Imports now resolve locally, the shared helpers are included here, and the AgentX runner uses the current user's cache directory by default. This repository is licensed under LGPL-3.0-or-later. See [LICENSE](LICENSE) and [COPYING](COPYING).

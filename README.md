# Thorustinfer benchmarks

Replay multi-turn inference workloads against a running [Thorustinfer](https://github.com/massif-01/Thorustinfer) server. The compact runner uses Chat Completions and records request counts, prompt tokens, cached tokens and generated tokens. The AgentX runner reproduces a separate, fixed Mini-Weka protocol.

[中文说明](README.zh-CN.md)

## Compact replay

From this checkout, install the tokenizer library, then generate four synthetic trajectories in a new directory. The generator also writes a manifest containing their hashes.

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python -m thorustinfer_benchmarks.mini_weka_synthetic --output results/dataset --trajectories 4
```

Start Thorustinfer with your model. Set the endpoint, served model name and path to the model directory containing its matching `tokenizer.json`. If your service uses an API key, export it as `THORUSTINFER_API_KEY`.

```sh
python -m thorustinfer_benchmarks.mini_weka_compact \
  --url http://127.0.0.1:8088/v1 --model local-model \
  --tokenizer /path/to/model --manifest results/dataset/manifest.json \
  --concurrency 2 --wall-limit 60 --output results/compact
```

Open `results/compact/summary.json` to inspect the run. The output directory must be new for each run. The time limit can stop a run before all trajectories finish.

## AgentX Mini

The fixed protocol uses an external AgentX harness, its sixteen original trace windows, the manifest and an idle Linux model service on the same host. Supply the service PID and matching tokenizer and model paths. This workload checks for a 262,144-token service context. The compact runner above accepts generated traces.

```sh
python -m thorustinfer_benchmarks.agentx_mini --help
python -m unittest discover -s tests
```

Source history and licensing are documented in [NOTICES.md](NOTICES.md).

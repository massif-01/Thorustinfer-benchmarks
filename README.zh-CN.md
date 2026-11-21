# Thorustinfer benchmarks

用多轮请求测量 [Thorustinfer](https://github.com/massif-01/Thorustinfer)。紧凑回放通过 Chat Completions 记录请求数、输入 token、缓存命中 token 和生成 token。AgentX 入口复现固定的 Mini-Weka 测试。

[English](README.md)

## 运行紧凑回放

在本仓库目录安装分词器库，然后生成四条合成轨迹。生成器会写入轨迹文件和包含哈希的清单。

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python -m thorustinfer_benchmarks.mini_weka_synthetic --output results/dataset --trajectories 4
```

启动已加载模型的 Thorustinfer。下面的命令需要服务地址、模型服务名和包含配套 `tokenizer.json` 的模型目录。如果服务启用了鉴权，请在客户端设置 `THORUSTINFER_API_KEY`。

```sh
python -m thorustinfer_benchmarks.mini_weka_compact \
  --url http://127.0.0.1:8088/v1 --model local-model \
  --tokenizer /path/to/model --manifest results/dataset/manifest.json \
  --concurrency 2 --wall-limit 60 --output results/compact
```

运行结束后查看 `results/compact/summary.json`。每轮使用新的输出目录。达到时间上限时，报告会记录已完成的请求和轨迹数。

## AgentX Mini

固定回放需要外部 AgentX harness、原始 16 个窗口和清单，并在 Linux 服务所在机器上读取进程数据。启动时提供服务 PID、分词器和模型路径。该基准要求空闲服务具备 262,144 token 上下文；上面的紧凑回放使用合成轨迹。

```sh
python -m thorustinfer_benchmarks.agentx_mini --help
python -m unittest discover -s tests
```

源码来源与许可见 [NOTICES.md](NOTICES.md)。

# FlagScale 智能监控功能使用说明

### 运行训练 (这里的路径和文件名是我自己的，根据对应的修改就行。)
```bash
python run.py --config-path ./examples/aquila/conf --config-name train train=3b_fixed experiment.runner.nproc_per_node=2 train.data.data_path=./data/pile_wikipedia_demo action=run

# 然后执行生成的脚本（监控会自动启动）
bash /path/to/outputs/logs/scripts/host_0_localhost_run.sh
```

### 查看监控结果
```bash
# 查看所有监控文件
ls -la outputs/logs/monitor/

# 查看智能诊断报告
cat outputs/logs/monitor/host_*_diagnostic_*.txt

# 查看收集的训练日志
ls -la outputs/logs/monitor/host_*_temp_*.log

# 查看状态跟踪
cat outputs/logs/monitor/status.log
```

## 📁 文件说明

| 文件 | 作用 |
|------|------|
| `host_*_diagnostic_*.txt` | **智能诊断报告** - 自动分析训练错误 |
| `host_*_temp_*.log` | **收集的训练日志** - 增量收集的日志内容 |
| `status.log` | **状态跟踪** - 记录训练状态变化 |

## 🔍 诊断报告示例

```
Diagnostic Report for localhost (node 0)
Generated at 2025-09-11 01:53:17
Analysis:
- OutOfMemoryError: The training process ran out of GPU memory.
- RendezvousConnectionError: Connection to rendezvous backend failed.
- CodeError: Python exception occurred during execution.
```
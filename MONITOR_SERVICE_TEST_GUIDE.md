# 测试指南


### 1. 基本测试（推荐先运行）
```bash
cd /path/to/FlagScale-log-feature
python test_monitor_service.py
```

### 2. 指定测试类型
```bash
# 基本功能
python test_monitor_service.py --test basic

# 集成功能  
python test_monitor_service.py --test integration

# 日志收集
python test_monitor_service.py --test logs
```

### 3. 自定义参数
```bash
# 设置监控间隔为5秒
python test_monitor_service.py --interval 5

# 自定义配置文件
python test_monitor_service.py --config your_config.yaml
```

## 改进内容

### 那个无限循环的问题：
移除 `runner_train.py` 中的 `while True` 无限循环

### 新增文件
- `flagscale/elastic/monitor_service.py` - 独立的监控服务
- `test_monitor_service.py` - 测试脚本

### 修改的文件
- `flagscale/runner/runner_train.py` - 集成监控服务，提供非阻塞接口


### 用法

#### 方式1：训练时启动监控
```python
runner = SSHTrainRunner(config)
monitor_service = runner.run(
    monitor=True,                    # 启动监控
    enable_log_collection=True,      # 启用日志收集
    enable_diagnostic=True           # 启用诊断报告
)
# 训练开始后，监控服务在后台运行，终端不会被阻塞

# 如果需要停止监控
if monitor_service:
    monitor_service.stop()
```

#### 方式2：独立启动监控服务
```python
runner = SSHTrainRunner(config)
runner.run()  # 只运行训练，不启动监控

# 稍后独立启动监控
monitor_service = runner.start_monitoring_service(
    interval=10,
    enable_log_collection=True,
    enable_diagnostic=True
)
```

#### 方式3：单次查询状态（推荐用于脚本）
```python
runner = SSHTrainRunner(config)
status = runner.query_once()  # 非阻塞，立即返回
print(f"当前状态: {status.name}")
```

## 🧪 实际环境测试

### 在服务器上测试真实训练任务

1. **准备你的训练配置文件**，例如 `train_config.yaml`

2. **修改你的训练启动脚本**：
```python
from flagscale.runner.runner_train import SSHTrainRunner
from omegaconf import OmegaConf

# 加载你的配置
config = OmegaConf.load("train_config.yaml")
runner = SSHTrainRunner(config)

# 启动训练和监控（非阻塞）
monitor_service = runner.run(
    monitor=True,
    interval=30,  # 每30秒监控一次
    enable_log_collection=True,
    enable_diagnostic=True
)

print("训练已启动，监控服务在后台运行")
print("你现在可以继续使用终端做其他事情")

# 如果需要手动检查状态
import time
time.sleep(60)  # 等待1分钟
status = runner.query_once()
print(f"训练状态: {status.name}")
```

3. **检查监控结果**：
```bash
# 查看监控日志
ls /path/to/your/logs/monitor/

# 查看状态日志
cat /path/to/your/logs/monitor/status.log

# 查看收集的训练日志
ls /path/to/your/logs/monitor/host_*_temp_*.log

# 查看诊断报告
ls /path/to/your/logs/monitor/host_*_diagnostic*.txt
```

## 🔍 测试验证点

### 1. 终端是否不再阻塞？
- 运行训练后，终端应该可以继续使用
- 不应该出现无限的状态查询循环

### 2. 监控服务是否正常运行？
- 检查 `/tmp/flagscale_test/logs/monitor/status.log` 是否有状态记录
- 确认每个监控间隔都有新的日志条目

### 3. 日志收集是否工作？
- 检查是否生成了临时日志文件 `host_*_temp_*.log`
- 确认日志内容是增量收集的

### 4. 诊断报告是否生成？
- 检查是否生成了诊断文件 `host_*_diagnostic*.txt`
- 确认诊断报告包含错误分析

## ⚠️ 常见问题和解决方案

### 问题1：ImportError: No module named 'flagscale.elastic.monitor_service'
**解决方案**：确保在FlagScale项目根目录下运行测试
```bash
cd /path/to/FlagScale-log-feature
python test_monitor_service.py
```

### 问题2：权限错误，无法创建日志目录
**解决方案**：确保对日志目录有写权限
```bash
sudo chmod 755 /tmp/flagscale_test
# 或者修改配置使用有权限的目录
```

### 问题3：监控服务启动失败
**解决方案**：检查配置文件格式和路径
```python
# 确保配置包含必要的字段
config.train.system.logging.log_dir
```

## 📈 性能考虑

1. **监控间隔**：建议设置为 10-30 秒，避免过于频繁的状态查询
2. **日志文件大小**：定期清理临时日志文件，避免占用过多磁盘空间
3. **网络开销**：多节点环境下，监控会产生SSH连接，注意网络开销

## 📞 支持和反馈

如果测试过程中遇到问题，请提供以下信息：

1. **错误信息**：完整的错误堆栈
2. **配置文件**：使用的配置内容（脱敏）
3. **环境信息**：Python版本、操作系统等
4. **日志文件**：相关的日志输出

## 🎉 验收标准

测试通过的标志：
- ✅ 运行 `python test_monitor_service.py` 无错误
- ✅ 终端不再被无限循环阻塞
- ✅ 可以在训练运行时继续使用终端
- ✅ 监控日志正常生成和更新
- ✅ 日志收集和诊断功能正常工作
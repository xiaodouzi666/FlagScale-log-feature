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
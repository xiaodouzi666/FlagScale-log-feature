#!/usr/bin/env python3
"""简化的监控服务测试"""

import os
import time
from omegaconf import OmegaConf
from flagscale.runner.runner_train import SSHTrainRunner
from flagscale.elastic.monitor_service import MonitorService

def test_simple_monitor():
    print("=== 简化监控服务测试 ===")
    
    # 创建基本配置
    config_dict = {
        "experiment": {
            "exp_dir": "/root/autodl-tmp/FlagScale-log-feature/outputs",
            "task": {
                "type": "train",
                "backend": "megatron",
                "entrypoint": "echo 'test'"
            },
            "runner": {
                "type": "ssh",
                "nnodes": 1,
                "nproc_per_node": 1,
                "hostfile": None,
                "ssh_port": 22,
                "no_shared_fs": False
            }
        },
        "train": {
            "system": {
                "checkpoint": {
                    "save": "/root/autodl-tmp/FlagScale-log-feature/outputs/checkpoints",
                    "load": "/root/autodl-tmp/FlagScale-log-feature/outputs/checkpoints"
                },
                "logging": {
                    "log_dir": "/root/autodl-tmp/FlagScale-log-feature/outputs/logs",
                    "scripts_dir": "/root/autodl-tmp/FlagScale-log-feature/outputs/logs/scripts",
                    "pids_dir": "/root/autodl-tmp/FlagScale-log-feature/outputs/logs/pids",
                    "details_dir": "/root/autodl-tmp/FlagScale-log-feature/outputs/logs/details",
                    "tensorboard_dir": "/root/autodl-tmp/FlagScale-log-feature/outputs/tensorboard",
                    "wandb_save_dir": "/root/autodl-tmp/FlagScale-log-feature/outputs/wandb"
                }
            },
            "model": {},
            "data": {}
        }
    }
    
    config = OmegaConf.create(config_dict)
    
    # 创建runner
    runner = SSHTrainRunner(config)
    
    # 手动测试状态查询
    print("1. 测试状态查询...")
    try:
        status = runner.query_once()
        print(f"   状态查询成功: {status.name}")
    except Exception as e:
        print(f"   状态查询失败: {e}")
    
    # 创建监控服务
    print("2. 创建监控服务...")
    monitor = MonitorService(config, runner, interval=2)
    
    # 检查monitor目录
    monitor_dir = "/root/autodl-tmp/FlagScale-log-feature/outputs/logs/monitor"
    print(f"   Monitor目录: {monitor_dir}")
    print(f"   目录存在: {os.path.exists(monitor_dir)}")
    
    # 手动测试日志收集
    print("3. 手动测试日志收集...")
    try:
        monitor._collect_logs()
        print("   日志收集调用成功")
        
        # 检查是否生成了文件
        if os.path.exists(monitor_dir):
            files = os.listdir(monitor_dir)
            print(f"   Monitor目录文件: {files}")
    except Exception as e:
        print(f"   日志收集失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 手动测试诊断功能
    print("4. 手动测试诊断功能...")
    try:
        monitor._generate_diagnostics()
        print("   诊断功能调用成功")
        
        # 再次检查文件
        if os.path.exists(monitor_dir):
            files = os.listdir(monitor_dir)
            print(f"   Monitor目录文件: {files}")
    except Exception as e:
        print(f"   诊断功能失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 测试启动监控服务
    print("5. 测试启动监控服务...")
    try:
        monitor.start_monitoring(enable_log_collection=True, enable_diagnostic=True)
        print("   监控服务启动成功")
        
        # 等待几秒
        print("   等待5秒观察...")
        time.sleep(5)
        
        # 检查状态
        status_summary = monitor.get_status_summary()
        print(f"   监控状态: {status_summary}")
        
        # 最终检查文件
        if os.path.exists(monitor_dir):
            files = os.listdir(monitor_dir)
            print(f"   最终Monitor目录文件: {files}")
            for file in files:
                file_path = os.path.join(monitor_dir, file)
                if os.path.isfile(file_path):
                    size = os.path.getsize(file_path)
                    print(f"     {file}: {size} bytes")
        
        # 停止服务
        monitor.stop()
        print("   监控服务已停止")
        
    except Exception as e:
        print(f"   监控服务测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple_monitor()
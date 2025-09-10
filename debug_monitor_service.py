#!/usr/bin/env python3
"""调试监控服务的问题"""

import os
import sys
import time
import subprocess

def check_monitor_setup():
    """检查监控相关的设置和文件"""
    print("=== 监控服务调试 ===")
    
    # 1. 检查必要目录
    dirs_to_check = [
        "/root/autodl-tmp/FlagScale-log-feature/outputs/logs",
        "/root/autodl-tmp/FlagScale-log-feature/outputs/logs/monitor", 
        "/root/autodl-tmp/FlagScale-log-feature/outputs/logs/scripts"
    ]
    
    print("1. 检查目录结构:")
    for dir_path in dirs_to_check:
        exists = os.path.exists(dir_path)
        writable = os.access(dir_path, os.W_OK) if exists else False
        print(f"   {dir_path}: 存在={exists}, 可写={writable}")
    
    # 2. 检查监控脚本是否存在
    monitor_script = "/root/autodl-tmp/FlagScale-log-feature/outputs/logs/scripts/monitor_0_localhost.py"
    print(f"\n2. 检查监控脚本:")
    print(f"   {monitor_script}: 存在={os.path.exists(monitor_script)}")
    
    if os.path.exists(monitor_script):
        print(f"   脚本大小: {os.path.getsize(monitor_script)} bytes")
        print("   脚本内容预览:")
        try:
            with open(monitor_script, 'r') as f:
                lines = f.readlines()[:10]  # 显示前10行
                for i, line in enumerate(lines):
                    print(f"     {i+1}: {line.rstrip()}")
        except Exception as e:
            print(f"     读取脚本失败: {e}")
    
    # 3. 检查主训练脚本
    main_script = "/root/autodl-tmp/FlagScale-log-feature/outputs/logs/scripts/host_0_localhost_run.sh"
    print(f"\n3. 检查主训练脚本:")
    print(f"   {main_script}: 存在={os.path.exists(main_script)}")
    
    if os.path.exists(main_script):
        print("   脚本中与监控相关的部分:")
        try:
            with open(main_script, 'r') as f:
                lines = f.readlines()
                for i, line in enumerate(lines):
                    if 'monitor' in line.lower():
                        print(f"     Line {i+1}: {line.rstrip()}")
        except Exception as e:
            print(f"     读取脚本失败: {e}")
    
    # 4. 检查监控日志
    monitor_log = "/tmp/monitor_output.log"
    print(f"\n4. 检查监控日志:")
    print(f"   {monitor_log}: 存在={os.path.exists(monitor_log)}")
    
    if os.path.exists(monitor_log):
        print(f"   日志大小: {os.path.getsize(monitor_log)} bytes")
        print("   日志内容:")
        try:
            with open(monitor_log, 'r') as f:
                content = f.read()
                print(f"     {content}")
        except Exception as e:
            print(f"     读取日志失败: {e}")
    
    # 5. 检查原始训练日志
    train_log = "/root/autodl-tmp/FlagScale-log-feature/outputs/logs/host_0_localhost.output"
    print(f"\n5. 检查原始训练日志:")
    print(f"   {train_log}: 存在={os.path.exists(train_log)}")
    
    if os.path.exists(train_log):
        size = os.path.getsize(train_log)
        print(f"   日志大小: {size} bytes")
        mtime = os.path.getmtime(train_log)
        print(f"   最后修改时间: {time.ctime(mtime)}")
    
    # 6. 检查进程
    print(f"\n6. 检查相关进程:")
    try:
        result = subprocess.run(["ps", "aux"], capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            for line in lines:
                if 'monitor' in line.lower() or 'python' in line.lower():
                    print(f"   {line}")
    except Exception as e:
        print(f"   检查进程失败: {e}")

def test_monitor_directly():
    """直接测试监控功能"""
    print("\n=== 直接测试监控功能 ===")
    
    try:
        sys.path.insert(0, "/root/autodl-tmp/FlagScale-log-feature")
        from omegaconf import OmegaConf
        from flagscale.elastic.monitor_service import MonitorService
        from flagscale.runner.runner_base import JobStatus
        
        print("✓ 成功导入必要模块")
        
        # 创建简化配置
        config = OmegaConf.create({
            "train": {
                "system": {
                    "logging": {
                        "log_dir": "/root/autodl-tmp/FlagScale-log-feature/outputs/logs"
                    }
                }
            },
            "experiment": {
                "runner": {
                    "no_shared_fs": False,
                    "ssh_port": 22
                }
            }
        })
        
        # 创建虚拟runner
        class TestRunner:
            def __init__(self):
                self.resources = None
                self.config = config
            
            def _query_status(self):
                return JobStatus.COMPLETED_OR_IDLE
        
        runner = TestRunner()
        print("✓ 创建虚拟runner成功")
        
        # 创建监控服务
        monitor = MonitorService(config, runner, interval=2)
        print("✓ 创建监控服务成功")
        
        # 测试日志收集
        print("\n测试日志收集功能...")
        try:
            monitor._collect_logs()
            print("✓ 日志收集调用成功")
        except Exception as e:
            print(f"✗ 日志收集失败: {e}")
            import traceback
            traceback.print_exc()
        
        # 测试诊断功能
        print("\n测试诊断功能...")
        try:
            monitor._generate_diagnostics()
            print("✓ 诊断功能调用成功")
        except Exception as e:
            print(f"✗ 诊断功能失败: {e}")
            import traceback
            traceback.print_exc()
        
        # 检查生成的文件
        monitor_dir = "/root/autodl-tmp/FlagScale-log-feature/outputs/logs/monitor"
        print(f"\n检查监控目录: {monitor_dir}")
        if os.path.exists(monitor_dir):
            files = os.listdir(monitor_dir)
            print(f"  文件列表: {files}")
            for file in files:
                file_path = os.path.join(monitor_dir, file)
                if os.path.isfile(file_path):
                    size = os.path.getsize(file_path)
                    print(f"    {file}: {size} bytes")
        
    except Exception as e:
        print(f"✗ 直接测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_monitor_setup()
    test_monitor_directly()
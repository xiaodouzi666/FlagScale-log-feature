#!/usr/bin/env python3
"""
FlagScale Monitor Service 测试脚本

使用方法:
1. 基本测试: python test_monitor_service.py
2. 自定义参数: python test_monitor_service.py --config your_config.yaml --interval 5
"""

import os
import sys
import time
import argparse
import tempfile
from pathlib import Path

# 添加FlagScale到Python路径
flagscale_root = Path(__file__).parent
sys.path.insert(0, str(flagscale_root))

from omegaconf import DictConfig, OmegaConf
from flagscale.runner.runner_train import SSHTrainRunner
from flagscale.elastic.monitor_service import MonitorService
from flagscale.logger import logger


def create_test_config():
    """创建测试用的配置"""
    config_dict = {
        "experiment": {
            "exp_dir": "/tmp/flagscale_test",
            "task": {
                "type": "train",
                "backend": "megatron",
                "entrypoint": "echo 'test training job'"
            },
            "runner": {
                "type": "ssh",
                "nnodes": 1,
                "nproc_per_node": 1,
                "hostfile": None,
                "ssh_port": 22,
                "no_shared_fs": False
            },
            "envs": {
                "CUDA_VISIBLE_DEVICES": "0"
            }
        },
        "train": {
            "system": {
                "checkpoint": {
                    "save": "/tmp/flagscale_test/checkpoints",
                    "load": "/tmp/flagscale_test/checkpoints"
                },
                "logging": {
                    "log_dir": "/tmp/flagscale_test/logs",
                    "scripts_dir": "/tmp/flagscale_test/logs/scripts",
                    "pids_dir": "/tmp/flagscale_test/logs/pids",
                    "details_dir": "/tmp/flagscale_test/logs/details",
                    "tensorboard_dir": "/tmp/flagscale_test/tensorboard",
                    "wandb_save_dir": "/tmp/flagscale_test/wandb"
                }
            },
            "model": {
                "num_layers": 12,
                "hidden_size": 768,
                "num_attention_heads": 12
            },
            "data": {
                "seq_length": 1024,
                "train_iters": 100
            }
        }
    }
    
    return OmegaConf.create(config_dict)


def test_basic_functionality():
    """测试基本功能"""
    print("=== FlagScale Monitor Service 基本功能测试 ===")
    
    # 创建测试配置
    config = create_test_config()
    
    # 创建runner实例
    runner = SSHTrainRunner(config)
    
    # 创建监控服务
    monitor = MonitorService(config, runner, interval=2)
    
    print("✓ 配置和实例创建成功")
    
    # 测试状态查询
    try:
        status = runner.query_once()
        print(f"✓ 状态查询成功: {status.name}")
    except Exception as e:
        print(f"⚠ 状态查询失败（正常，因为没有实际任务）: {e}")
    
    # 测试监控服务启动
    print("\n--- 测试监控服务启动 ---")
    monitor.start_monitoring(enable_log_collection=True, enable_diagnostic=True)
    print("✓ 监控服务启动成功（后台运行）")
    
    # 等待几秒观察
    print("等待 5 秒观察监控服务运行...")
    time.sleep(5)
    
    # 获取监控状态
    status_summary = monitor.get_status_summary()
    print(f"✓ 监控服务状态: {status_summary}")
    
    # 停止监控服务
    monitor.stop()
    print("✓ 监控服务停止成功")
    
    print("\n=== 基本功能测试完成 ===")


def test_integration_with_runner():
    """测试与runner的集成"""
    print("\n=== 测试 Runner 集成 ===")
    
    config = create_test_config()
    runner = SSHTrainRunner(config)
    
    # 测试通过run方法启动监控
    print("测试通过 run() 方法启动监控（非阻塞）...")
    
    try:
        # 启动训练和监控（不会实际运行训练，因为是测试环境）
        monitor_service = runner.run(
            monitor=True, 
            interval=2,
            enable_log_collection=True,
            enable_diagnostic=True,
            dryrun=True  # 使用dryrun模式避免实际执行
        )
        
        if monitor_service:
            print("✓ 通过 runner.run() 启动监控服务成功")
            
            # 等待观察
            time.sleep(3)
            
            # 停止服务
            monitor_service.stop()
            print("✓ 监控服务停止成功")
        else:
            print("ℹ 未启动监控服务（monitor=False）")
            
    except Exception as e:
        print(f"⚠ 集成测试出现异常: {e}")
    
    # 测试独立启动监控服务
    print("\n测试独立启动监控服务...")
    try:
        monitor_service = runner.start_monitoring_service(
            interval=2,
            enable_log_collection=True,
            enable_diagnostic=True
        )
        print("✓ 独立启动监控服务成功")
        
        time.sleep(3)
        monitor_service.stop()
        print("✓ 监控服务停止成功")
        
    except Exception as e:
        print(f"⚠ 独立启动测试出现异常: {e}")
    
    print("=== Runner 集成测试完成 ===")


def test_log_collection():
    """测试日志收集功能"""
    print("\n=== 测试日志收集功能 ===")
    
    # 创建临时日志文件模拟训练日志
    temp_dir = "/tmp/flagscale_test_logs"
    os.makedirs(temp_dir, exist_ok=True)
    
    # 创建模拟的训练输出日志
    mock_log_file = os.path.join(temp_dir, "host.output")
    with open(mock_log_file, "w") as f:
        f.write("Training started...\n")
        f.write("Epoch 1/10\n")
        f.write("completed\n")  # 这会被诊断功能识别
    
    print(f"✓ 创建模拟日志文件: {mock_log_file}")
    
    # 测试日志收集
    config = create_test_config()
    config.train.system.logging.log_dir = temp_dir
    
    # 导入日志收集模块直接测试
    from flagscale.elastic.log_collector import collect_logs
    from flagscale.elastic.diagnostic import generate_diagnostic_report
    
    try:
        # 测试日志收集
        collected_log = collect_logs(config, "localhost", 0, temp_dir, dryrun=False)
        if collected_log and os.path.exists(collected_log):
            print(f"✓ 日志收集成功: {collected_log}")
            
            # 测试诊断报告生成
            diagnostic_report = generate_diagnostic_report(
                config, "localhost", 0, collected_log, return_content=False
            )
            if diagnostic_report and os.path.exists(diagnostic_report):
                print(f"✓ 诊断报告生成成功: {diagnostic_report}")
            else:
                print("⚠ 诊断报告生成失败")
        else:
            print("⚠ 日志收集失败")
            
    except Exception as e:
        print(f"⚠ 日志收集测试出现异常: {e}")
    
    print("=== 日志收集功能测试完成 ===")


def main():
    parser = argparse.ArgumentParser(description="FlagScale Monitor Service 测试脚本")
    parser.add_argument("--config", type=str, help="配置文件路径（可选，不提供则使用测试配置）")
    parser.add_argument("--interval", type=int, default=2, help="监控间隔时间（秒）")
    parser.add_argument("--test", choices=["basic", "integration", "logs", "all"], 
                       default="all", help="要运行的测试类型")
    
    args = parser.parse_args()
    
    print("FlagScale Monitor Service 测试工具")
    print("=" * 50)
    
    if args.config:
        print(f"使用配置文件: {args.config}")
        # 如果提供了配置文件，这里可以加载
        # config = OmegaConf.load(args.config)
    else:
        print("使用内置测试配置")
    
    try:
        if args.test in ["basic", "all"]:
            test_basic_functionality()
        
        if args.test in ["integration", "all"]:
            test_integration_with_runner()
        
        if args.test in ["logs", "all"]:
            test_log_collection()
        
        print(f"\n🎉 测试完成！监控间隔: {args.interval}秒")
        print("\n📝 测试说明:")
        print("- 基本功能测试：验证监控服务的创建、启动、停止")
        print("- 集成测试：验证与 runner_train.py 的集成")
        print("- 日志收集测试：验证日志收集和诊断报告功能")
        
    except KeyboardInterrupt:
        print("\n用户中断测试")
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
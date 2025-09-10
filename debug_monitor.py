#!/usr/bin/env python3
"""调试监控服务的脚本"""

from flagscale.elastic.log_collector import collect_logs
from flagscale.elastic.diagnostic import generate_diagnostic_report
from omegaconf import OmegaConf
import os

# 创建基本配置
config = OmegaConf.create({
    'train': {
        'system': {
            'logging': {
                'log_dir': '/root/autodl-tmp/FlagScale-log-feature/outputs/logs'
            }
        }
    },
    'experiment': {
        'runner': {
            'no_shared_fs': False,
            'ssh_port': 22
        }
    }
})

print('=== 测试日志收集 ===')
try:
    log_file = collect_logs(config, 'localhost', 0, '/root/autodl-tmp/FlagScale-log-feature/outputs/logs/monitor')
    print(f'日志收集结果: {log_file}')
    if log_file and os.path.exists(log_file):
        print(f'文件大小: {os.path.getsize(log_file)} bytes')
        # 查看文件内容前几行
        with open(log_file, 'r') as f:
            content = f.read()[:500]
            print(f'文件内容预览: {content[:200]}...')
except Exception as e:
    print(f'日志收集失败: {e}')
    import traceback
    traceback.print_exc()

print('\n=== 测试诊断功能 ===')
try:
    original_log = '/root/autodl-tmp/FlagScale-log-feature/outputs/logs/host_0_localhost.output'
    if os.path.exists(original_log):
        print(f'原始日志文件存在，大小: {os.path.getsize(original_log)} bytes')
        diagnostic = generate_diagnostic_report(config, 'localhost', 0, original_log, return_content=True)
        print(f'诊断报告内容:\n{diagnostic}')
        
        # 也测试写入文件的版本
        diagnostic_file = generate_diagnostic_report(config, 'localhost', 0, original_log, return_content=False)
        print(f'诊断报告文件: {diagnostic_file}')
    else:
        print('原始日志文件不存在')
except Exception as e:
    print(f'诊断功能失败: {e}')
    import traceback
    traceback.print_exc()

print('\n=== 检查文件系统 ===')
print(f'monitor目录内容: {os.listdir("/root/autodl-tmp/FlagScale-log-feature/outputs/logs/monitor/")}')
print(f'原始日志最后修改时间: {os.path.getmtime("/root/autodl-tmp/FlagScale-log-feature/outputs/logs/host_0_localhost.output")}')
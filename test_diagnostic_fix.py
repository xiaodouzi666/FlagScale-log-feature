#!/usr/bin/env python3
"""测试修复后的诊断功能"""

from flagscale.elastic.diagnostic import generate_diagnostic_report
from omegaconf import OmegaConf

# 创建基本配置
config = OmegaConf.create({})

# 测试诊断功能是否能识别实际的错误
log_file = '/root/autodl-tmp/FlagScale-log-feature/outputs/logs/host_0_localhost.output'

print("=== 测试修复后的诊断功能 ===")
print(f"分析日志文件: {log_file}")

# 生成诊断报告
diagnostic_content = generate_diagnostic_report(
    config, 
    'localhost', 
    0, 
    log_file, 
    return_content=True
)

print("诊断报告:")
print(diagnostic_content)

# 也查看日志文件的一部分内容，用于对比
print("\n=== 日志文件内容样本 ===")
try:
    with open(log_file, 'r') as f:
        content = f.read()
        # 显示包含错误的部分
        lines = content.split('\n')
        for i, line in enumerate(lines[-50:]):  # 显示最后50行
            if any(keyword in line.lower() for keyword in ['error', 'exception', 'traceback', 'rendezvous']):
                print(f"Line {len(lines)-50+i}: {line}")
except Exception as e:
    print(f"读取日志文件失败: {e}")

print("\n=== 错误关键词匹配测试 ===")
from flagscale.elastic.diagnostic import error_types

# 手动测试一些关键词是否在日志中
try:
    with open(log_file, 'r') as f:
        log_content = f.read().lower()
        
    found_keywords = []
    for keyword, description in error_types.items():
        if keyword in log_content:
            found_keywords.append((keyword, description))
            
    if found_keywords:
        print("找到的错误关键词:")
        for keyword, desc in found_keywords:
            print(f"  {keyword} -> {desc}")
    else:
        print("没有找到任何匹配的错误关键词")
        
    # 显示日志中的一些关键信息
    print(f"\n日志文件大小: {len(log_content)} 字符")
    if 'rendezvous' in log_content:
        print("✓ 包含 'rendezvous'")
    if 'error' in log_content:
        print("✓ 包含 'error'")
    if 'traceback' in log_content:
        print("✓ 包含 'traceback'")
        
except Exception as e:
    print(f"关键词匹配测试失败: {e}")
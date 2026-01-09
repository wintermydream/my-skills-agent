import sys
import os
import time

# 确保可以导入当前目录下的 agent.py
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from agent import SkillsAgent

def test_cache():
    print("🚀 开始缓存功能测试...")
    # 显式开启缓存
    agent = SkillsAgent(enable_cache=True)
    
    test_query = "请提取关键信息：2024年1月，腾讯公司宣布投资10亿元人民币支持AI创业团队。" 
    
    # 第一次调用：应该触发 API 请求
    print("\n--- 第一次调用 (预期触发 API) ---")
    start_time = time.time()
    result1 = agent.process(test_query)
    duration1 = time.time() - start_time
    print(f"耗时: {duration1:.2f}s")
    print(f"输出: {result1[:50]}...")

    # 第二次调用：应该使用缓存
    print("\n--- 第二次调用 (预期使用缓存) ---")
    start_time = time.time()
    result2 = agent.process(test_query)
    duration2 = time.time() - start_time
    print(f"耗时: {duration2:.2f}s")
    print(f"输出: {result2[:50]}...")
    
    # 检查耗时或输出中的提示
    if duration2 < 0.1:
        print("\n✅ 缓存功能验证通过！")
    else:
        print("\n❌ 缓存功能验证失败。")

def test_cache_toggle():
    print("\n🚀 开始缓存开关测试...")
    # 显式关闭缓存
    agent = SkillsAgent(enable_cache=False)
    
    test_query = "请提取关键信息：2024年1月，腾讯公司宣布投资10亿元人民币支持AI创业团队。" 
    
    print("\n--- 第一次调用 (缓存关闭) ---")
    start_time = time.time()
    agent.process(test_query)
    duration1 = time.time() - start_time
    print(f"耗时: {duration1:.2f}s")

    print("\n--- 第二次调用 (缓存关闭，预期仍触发 API) ---")
    start_time = time.time()
    agent.process(test_query)
    duration2 = time.time() - start_time
    print(f"耗时: {duration2:.2f}s")
    
    if duration2 > 0.5:
        print("\n✅ 缓存开关功能验证通过 (关闭状态有效)！")
    else:
        print("\n❌ 缓存开关功能验证失败。")

if __name__ == "__main__":
    test_cache()
    test_cache_toggle()

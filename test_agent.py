import sys
import os

# 确保可以导入当前目录下的 agent.py
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from agent import SkillsAgent

def main():
    # 初始化 Agent
    agent = SkillsAgent()
    
    test_query = "请提取关键信息：2024年1月，腾讯公司宣布投资10亿元人民币支持AI创业团队，CEO马化腾出席发布会。" 

    result = agent.process(test_query) 
    print("📤 最终输出：") 
    print(result) 

if __name__ == "__main__":
    main()
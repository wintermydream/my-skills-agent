
import os
import sys

# 将当前目录加入路径以便导入 agent
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

from agent import Skill, SkillLibrary

def test_skill_loading():
    print("--- 开始测试技能加载 ---")
    library = SkillLibrary()
    
    # 验证是否加载了技能
    skill_names = [s.metadata.get('name') for s in library.skills]
    print(f"已加载技能列表: {skill_names}")
    
    # 验证 translator 技能
    translator = next((s for s in library.skills if s.metadata.get('name') == 'professional_translator'), None)
    if translator:
        print("✅ 成功加载 professional_translator")
    else:
        print("❌ 未能加载 professional_translator")

    # 验证 text-processing 技能及其引用
    tp_skill = next((s for s in library.skills if s.metadata.get('name') == 'text-processing'), None)
    if tp_skill:
        print("✅ 成功加载 text-processing")
        # 检查是否注入了引用的内容
        if "--- 引用文件开始: FORMS.md ---" in tp_skill.instructions:
            print("✅ 成功注入 FORMS.md 内容")
        if "--- 引用文件开始: REFERENCE.md ---" in tp_skill.instructions:
            print("✅ 成功注入 REFERENCE.md 内容")
        if "--- 引用文件开始: EXAMPLES.md ---" in tp_skill.instructions:
            print("✅ 成功注入 EXAMPLES.md 内容")
        
        # 打印部分解析后的指令以便查看效果
        print("\n解析后的 text-processing 指令预览:")
        print(tp_skill.instructions[:300] + "...")
    else:
        print("❌ 未能加载 text-processing")

if __name__ == "__main__":
    test_skill_loading()

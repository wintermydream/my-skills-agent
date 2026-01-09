"""
国产大模型Skills Agent - 完整实现
支持智谱GLM和通义千问的动态切换
"""

import os
import yaml
import re
import hashlib
import json
from typing import Dict, List, Optional
from zhipuai import ZhipuAI
from dashscope import Generation
from openai import OpenAI

# 获取项目根目录（agent.py 所在目录）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ==================== 配置加载模块 ====================
class Config:
    """加载和管理配置文件"""
    def __init__(self, config_path=None):
        if config_path is None:
            config_path = os.path.join(BASE_DIR, 'config.yaml')
        with open(config_path, 'r', encoding='utf-8') as f:
            self.data = yaml.safe_load(f)
    
    def get_api_key(self, provider: str) -> str:
        """获取指定厂商的API密钥"""
        return self.data['api_keys'].get(provider, '')
    
    def get_model_config(self, model_name: str) -> Dict:
        """获取模型配置信息"""
        return self.data['models'].get(model_name, {})
    
    @property
    def default_model(self) -> str:
        return self.data.get('default_model', 'glm-4')
    
    @property
    def enable_cache(self) -> bool:
        return self.data.get('enable_cache', True)

# ==================== Skill管理模块 ====================
class Skill:
    """单个Skill的数据结构，支持外部文件引用"""
    MAX_REF_DEPTH = 3  # 最大递归深度，防止死循环

    def __init__(self, filepath: str, depth: int = 0, loaded_paths: set = None):
        self.filepath = os.path.abspath(filepath)
        self.depth = depth
        self.loaded_paths = loaded_paths or {self.filepath}
        self.metadata = {}
        self.instructions = ""
        self._parse_file()
        
        # 只有在非递归或未达到深度限制时解析引用
        if self.depth < self.MAX_REF_DEPTH:
            self._resolve_references()
    
    def _parse_file(self):
        """解析.md文件，分离元数据和指令"""
        if not os.path.exists(self.filepath):
            self.instructions = f"\n⚠️ [错误：文件不存在 {self.filepath}]\n"
            return

        with open(self.filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 只有主文件（depth=0）才强制要求 YAML 头
        match = re.search(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if match:
            yaml_str = match.group(1)
            try:
                self.metadata = yaml.safe_load(yaml_str) or {}
            except Exception as e:
                print(f"⚠️ YAML解析失败 {self.filepath}: {e}")
            self.instructions = content[match.end():].strip()
        else:
            if self.depth == 0:
                raise ValueError(f"主技能文件格式错误（缺失YAML头）：{self.filepath}")
            else:
                # 被引用的子文件可以没有YAML头
                self.instructions = content.strip()
    
    def _resolve_references(self):
        """解析指令中的 [xxx](yyy.md) 链接并注入内容"""
        base_dir = os.path.dirname(self.filepath)
        # 匹配 Markdown 链接：[描述](文件名.md)
        ref_pattern = r'\[.*?\]\((.*?\.md)\)'
        
        def replace_with_content(match):
            ref_filename = match.group(1)
            ref_path = os.path.abspath(os.path.join(base_dir, ref_filename))
            
            # 避免重复加载和死循环
            if ref_path in self.loaded_paths:
                return f"\n⚠️ [循环引用或重复加载: {ref_filename}]\n"
            
            if not os.path.exists(ref_path):
                return f"\n⚠️ [引用文件未找到: {ref_filename}]\n"

            # 递归加载子文件
            self.loaded_paths.add(ref_path)
            sub_skill = Skill(ref_path, depth=self.depth + 1, loaded_paths=self.loaded_paths)
            
            return f"\n--- 引用文件开始: {ref_filename} ---\n{sub_skill.instructions}\n--- 引用文件结束: {ref_filename} ---\n"

        self.instructions = re.sub(ref_pattern, replace_with_content, self.instructions)
    
    def matches_query(self, query: str) -> bool:
        """判断用户查询是否匹配该Skill的触发词"""
        triggers = self.metadata.get('triggers', [])
        # 如果没有触发词，可能是一个纯辅助文件
        if not triggers:
            return False
        query_lower = query.lower()
        return any(trigger.lower() in query_lower for trigger in triggers)

class SkillLibrary:
    """管理所有Skills的库"""
    def __init__(self, skills_dir=None):
        if skills_dir is None:
            skills_dir = os.path.join(BASE_DIR, 'skills')
        self.skills: List[Skill] = []
        self._load_all_skills(skills_dir)
    
    def _load_all_skills(self, skills_dir: str):
        """扫描并加载所有技能文件夹中的 SKILL.md 文件"""
        if not os.path.exists(skills_dir):
            print(f"⚠️ Skills目录不存在：{skills_dir}")
            return
            
        # 遍历 skills 目录下的所有子目录
        for item in os.listdir(skills_dir):
            item_path = os.path.join(skills_dir, item)
            
            # 如果是目录，则查找目录下的 SKILL.md
            if os.path.isdir(item_path):
                skill_file = os.path.join(item_path, 'SKILL.md')
                if os.path.exists(skill_file):
                    try:
                        skill = Skill(skill_file)
                        self.skills.append(skill)
                        print(f"✅ 已从文件夹加载技能：{skill.metadata.get('name', item)}")
                    except Exception as e:
                        print(f"❌ 加载文件夹技能失败 {item}: {e}")
                else:
                    print(f"ℹ️ 文件夹 {item} 中未找到 SKILL.md，跳过")
            
            # 保留对根目录下 .md 文件的向后兼容支持（可选，但根据用户要求，我们将迁移到文件夹模式）
            elif item.endswith('.md') and item != 'SKILL.md':
                try:
                    skill = Skill(item_path)
                    self.skills.append(skill)
                    print(f"✅ 已从根目录加载技能：{skill.metadata.get('name', item)}")
                except Exception as e:
                    print(f"❌ 加载根目录技能失败 {item}: {e}")
    
    def find_skill(self, query: str) -> Optional[Skill]:
        """根据用户查询找到匹配的Skill"""
        for skill in self.skills:
            if skill.matches_query(query):
                return skill
        return None

# ==================== 模型调用模块 ====================
class ModelCaller:
    """统一的模型调用接口，支持多厂商"""
    def __init__(self, config: Config):
        self.config = config
        self.cache = {}
        self.zhipu_client = ZhipuAI(api_key=config.get_api_key('zhipu'))
        self.openrouter_client = OpenAI(
            api_key=config.get_api_key('openrouter'),
            base_url="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": "https://github.com/gepa-research/GEPA", # 可选，OpenRouter 用于排行
                "X-Title": "GEPA Skills Agent", # 可选，在 OpenRouter 仪表盘显示
            }
        )
    
    def call(self, model_name: str, messages: List[Dict],
             temperature: float = 0.7, max_tokens: int = 2000) -> str:
        """
        统一调用接口（增加缓存支持）
        :param model_name: 模型名称（如'glm-4'或'qwen-max'）
        :param messages: 对话消息列表
        :return: 模型返回的文本
        """
        enable_cache = self.config.enable_cache
        cache_key = None

        if enable_cache:
            # System Prompt和User Query完全一致，使用缓存
            # 生成缓存键
            cache_key = hashlib.md5(
                json.dumps(messages, sort_keys=True).encode()
            ).hexdigest()
            
            if cache_key in self.cache:
                print(f"⚡ 使用缓存结果 (模型: {model_name})")
                return self.cache[cache_key]

        model_config = self.config.get_model_config(model_name)
        provider = model_config.get('provider')
        print(f"🤖 调用模型：{model_name} (提供商：{provider})")
        if provider == 'zhipu':
            result = self._call_zhipu(model_config['model_name'], messages, temperature, max_tokens)
        elif provider == 'qwen':
            result = self._call_qwen(model_config['model_name'], messages, temperature, max_tokens)
        elif provider == 'openrouter':
            result = self._call_openrouter(model_config['model_name'], messages, temperature, max_tokens)
        else:
            raise ValueError(f"不支持的提供商：{provider}")
        
        # 存入缓存
        if enable_cache and cache_key:
            self.cache[cache_key] = result
        return result

    def _call_openrouter(self, model: str, messages: List[Dict],
                         temp: float, max_tok: int) -> str:
        """调用OpenRouter API"""
        response = self.openrouter_client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temp,
            max_tokens=max_tok
        )
        return response.choices[0].message.content
    
    def _call_zhipu(self, model: str, messages: List[Dict],
                    temp: float, max_tok: int) -> str:
        """调用智谱API"""
        response = self.zhipu_client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temp,
            max_tokens=max_tok
        )
        return response.choices[0].message.content
    
    def _call_qwen(self, model: str, messages: List[Dict],
                   temp: float, max_tok: int) -> str:
        """调用通义千问API"""
        os.environ['DASHSCOPE_API_KEY'] = self.config.get_api_key('qwen')
        response = Generation.call(
            model=model,
            messages=messages,
            result_format='message',
            temperature=temp,
            max_tokens=max_tok
        )
        return response.output.choices[0].message.content

# ==================== 主Agent逻辑 ====================
class SkillsAgent:
    """Skills Agent主控制器"""
    def __init__(self, config_path=None, enable_cache=None):
        self.config = Config(config_path)
        # 如果初始化时显式指定了 enable_cache，则覆盖配置文件中的设置
        if enable_cache is not None:
            self.config.data['enable_cache'] = enable_cache
            
        self.library = SkillLibrary()
        self.caller = ModelCaller(self.config)
    
    def process(self, user_query: str) -> str:
        """
        处理用户请求的完整流程：
        1. 查找匹配的Skill
        2. 构建提示词
        3. 调用模型
        4. 返回结果
        """
        print(f"\n{'='*50}")
        print(f"📝 用户输入：{user_query}")
        print(f"{'='*50}\n")
        
        # 步骤1：技能匹配
        skill = self.library.find_skill(user_query)
        if not skill:
            return self._default_chat(user_query)
        print(f"🎯 匹配到技能：{skill.metadata['name']}")
        
        # 步骤2：选择模型
        model_name = skill.metadata.get('model_preference', self.config.default_model)
        
        # 步骤3：构建完整提示词
        messages = [
            {"role": "system", "content": "你是一个严格按照指令执行任务的AI助手。"},
            {"role": "user", "content": f"{skill.instructions}\n---\n用户请求：{user_query}"}
        ]
        
        # 步骤4：调用模型
        try:
            result = self.caller.call(
                model_name=model_name,
                messages=messages,
                temperature=self.config.data.get('temperature', 0.7),
                max_tokens=self.config.data.get('max_tokens', 2000)
            )
            print(f"\n✅ 执行完成\n")
            return result
        except Exception as e:
            return f"❌ 执行出错：{str(e)}"
    
    def _default_chat(self, query: str) -> str:
        """默认对话模式（未匹配到特定Skill时）"""
        print("💬 使用默认对话模式")
        messages = [{"role": "user", "content": query}]
        return self.caller.call(model_name=self.config.default_model, messages=messages)

# ==================== 程序入口 ====================
if __name__ == "__main__":
    agent = SkillsAgent()
    test_query = "请帮我翻译：人工智能正在改变世界"
    result = agent.process(test_query)
    print("="*50)
    print("📤 最终输出：")
    print(result)
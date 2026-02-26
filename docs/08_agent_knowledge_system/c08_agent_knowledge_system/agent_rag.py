import re
import json
import requests
from dashscope import Generation
from structured_memory import MemoryMetadataDB, VectorMemoryDB
from knowledge_manager import KnowledgeManager
from config import *

class RAGEnabledAgent:
    def __init__(self, user_id="default_user"):
        self.user_id = user_id
        self.dashscope_api_key = DASHSCOPE_API_KEY
        
        # 初始化结构化记忆
        self.metadata_db = MemoryMetadataDB(SQLITE_DB_PATH)
        self.vector_db = VectorMemoryDB(VECTOR_DB_PATH, EMBEDDING_MODEL)
        
        # 初始化知识库
        self.knowledge_manager = KnowledgeManager()
        
        # 工具映射表
        self.tool_map = {
            "计算": self.calculate,
            "天气查询": self.get_weather,
            "联网搜索": self.web_search
        }

    # ---------------- LLM调用 ----------------
    def call_llm(self, prompt):
        """调用通义千问API"""
        try:
            response = Generation.call(
                model="qwen-turbo",
                api_key=self.dashscope_api_key,
                messages=[{"role": "user", "content": prompt}],
                result_format="text",
                temperature=0.1
            )
            if response.status_code == 200:
                return response.output.text.strip()
            else:
                return f"LLM调用失败：{response.message}"
        except Exception as e:
            return f"LLM调用异常：{str(e)}"

    # ---------------- 工具函数 ----------------
    def calculate(self, expr):
        """计算工具"""
        try:
            # 安全字符校验
            safe_expr = re.sub(r'[^0-9+\-*/().]', '', expr)
            if not safe_expr:
                return "计算失败：输入包含非法字符"
            result = eval(safe_expr, {"__builtins__": None}, {})
            return f"计算结果：{safe_expr} = {result}"
        except Exception as e:
            return f"计算失败：{str(e)}"

    def get_weather(self, city):
        """天气查询工具"""
        try:
            city_encoded = requests.utils.quote(city)
            url = f"http://wttr.in/{city_encoded}?format=3"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return f"天气查询结果：{response.text.strip()}"
            else:
                return f"天气查询失败：状态码{response.status_code}"
        except Exception as e:
            return f"天气查询异常：{str(e)}"

    def web_search(self, query):
        """联网搜索工具"""
        try:
            url = "https://searx.be/search"
            params = {
                "q": query,
                "format": "json",
                "language": "zh-CN",
                "safesearch": "0"
            }
            response = requests.get(url, params=params, timeout=15)
            if response.status_code == 200:
                results = response.json()
                summaries = []
                for idx, res in enumerate(results.get("results", [])[:3]):
                    summaries.append(f"{idx+1}. {res.get('title')}：{res.get('content')[:100]}...")
                if summaries:
                    return f"联网搜索结果：\n{chr(10).join(summaries)}"
                else:
                    return "联网搜索失败：无结果"
            else:
                return f"联网搜索失败：状态码{response.status_code}"
        except Exception as e:
            return f"联网搜索异常：{str(e)}"

    # ---------------- 工具解析与执行 ----------------
    def parse_tool_command(self, llm_response):
        """解析工具调用指令"""
        pattern = r"TOOL: (\w+)\((.*?)\)"
        match = re.search(pattern, llm_response)
        if match:
            tool_name = match.group(1)
            tool_params = match.group(2).strip()
            return tool_name, tool_params
        return None, None

    def execute_task_plan(self, plan):
        """执行任务规划"""
        try:
            step_pattern = r"STEP(\d+): (.*?)(?=STEP|FINISH|$)"
            steps = re.findall(step_pattern, plan, re.DOTALL)
            finish_pattern = r"FINISH: (.*?)$"
            finish_match = re.search(finish_pattern, plan)
            
            step_results = []
            for idx, step in steps:
                step = step.strip()
                if "TOOL:" in step:
                    tool_name, tool_params = self.parse_tool_command(step)
                    if tool_name in self.tool_map:
                        step_res = self.tool_map[tool_name](tool_params)
                    else:
                        step_res = f"步骤{idx}失败：未知工具{tool_name}"
                else:
                    step_res = self.call_llm(f"请回答：{step}")
                step_results.append(f"步骤{idx}：{step_res}")
            
            final_result = finish_match.group(1).strip() if finish_match else ""
            return f"任务执行结果：\n{chr(10).join(step_results)}\n最终结论：{final_result}"
        except Exception as e:
            return f"任务规划执行失败：{str(e)}"

    # ---------------- 结构化记忆 ----------------
    def extract_memory_info(self, user_input, agent_response):
        """提取记忆信息"""
        extract_prompt = f"""
        请从以下对话中提取需要长期记忆的核心信息，仅输出JSON：
        用户输入：{user_input}
        智能体回复：{agent_response}
        
        输出格式：
        {{
            "content": "核心内容（≤100字）",
            "type": "USER_PREFERENCE/TASK_RECORD/TOOL_RESULT/CONTEXT_INFO"
        }}
        
        无有效记忆时content为空，type为CONTEXT_INFO。
        """
        try:
            llm_result = self.call_llm(extract_prompt)
            llm_result = re.search(r"\{.*\}", llm_result, re.DOTALL).group()
            memory_info = json.loads(llm_result)
            if memory_info.get("content") and memory_info.get("type") in [
                "USER_PREFERENCE", "TASK_RECORD", "TOOL_RESULT", "CONTEXT_INFO"
            ]:
                return memory_info
            else:
                return {"content": "", "type": "CONTEXT_INFO"}
        except Exception as e:
            print(f"提取记忆失败：{e}")
            return {"content": "", "type": "CONTEXT_INFO"}

    def add_structured_memory(self, user_input, agent_response):
        """添加结构化记忆"""
        memory_info = self.extract_memory_info(user_input, agent_response)
        if memory_info["content"]:
            self.vector_db.add_memory(
                content=memory_info["content"],
                metadata_db=self.metadata_db,
                user_id=self.user_id,
                memory_type=memory_info["type"]
            )

    def retrieve_structured_memory(self, user_input):
        """检索结构化记忆"""
        retrieved_memories = self.vector_db.retrieve_memory(
            query=user_input,
            metadata_db=self.metadata_db,
            user_id=self.user_id,
            days=30,
            top_k=TOP_K_MEMORY
        )
        
        if retrieved_memories:
            memory_text = "【历史记忆】\n"
            for mem in retrieved_memories:
                memory_text += f"- {mem['content']}（相似度：{mem['similarity']}）\n"
            return memory_text
        else:
            return ""

    # ---------------- RAG核心逻辑 ----------------
    def retrieve_all_context(self, user_input):
        """获取所有上下文（记忆+知识库）"""
        # 1. 结构化记忆
        memory_context = self.retrieve_structured_memory(user_input)
        # 2. 外部知识库
        knowledge_context = self.knowledge_manager.search_knowledge(user_input)
        # 合并
        full_context = ""
        if memory_context:
            full_context += memory_context + "\n"
        if knowledge_context:
            full_context += knowledge_context + "\n"
        return full_context

    def run_with_rag(self, user_input):
        """带RAG增强的主流程"""
        # 1. 检索上下文
        context = self.retrieve_all_context(user_input)
        
        # 2. 构建Prompt
        system_prompt = """
        你是具备结构化长期记忆+外部私有知识库的智能体，回答规则：
        1. 优先使用【历史记忆】和【外部知识库参考】的信息；
        2. 引用知识库内容时必须标注来源（文档名+页码）；
        3. 无相关知识时回答“暂无相关知识”；
        4. 工具调用格式：TOOL: 工具名(参数)；
        5. 任务规划格式：TASK: 名称\nSTEP1: 步骤1\nFINISH: 结论。
        """
        full_prompt = f"{system_prompt}\n{context}\n用户问题：{user_input}"
        
        # 3. LLM推理
        llm_response = self.call_llm(full_prompt)
        
        # 4. 执行工具/规划
        if "TOOL:" in llm_response:
            tool_name, tool_params = self.parse_tool_command(llm_response)
            if tool_name in self.tool_map:
                tool_result = self.tool_map[tool_name](tool_params)
                final_response = tool_result
            else:
                final_response = f"未知工具：{tool_name}"
        elif "TASK:" in llm_response:
            final_response = self.execute_task_plan(llm_response)
        else:
            final_response = llm_response
        
        # 5. 保存记忆
        self.add_structured_memory(user_input, final_response)
        
        return final_response
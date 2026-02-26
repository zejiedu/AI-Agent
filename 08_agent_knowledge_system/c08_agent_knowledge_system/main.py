from agent_rag import RAGEnabledAgent
from knowledge_manager import KnowledgeManager
import os

def init_demo_docs():
    """初始化测试文档目录"""
    demo_dir = "./demo_docs"
    if not os.path.exists(demo_dir):
        os.makedirs(demo_dir)
        # 创建测试MD文件
        with open(f"{demo_dir}/readme.md", "w", encoding="utf-8") as f:
            f.write("""# 智能体测试文档
## 功能说明
智能体支持PDF/MD/TXT格式的外部知识库接入，结合结构化记忆提供精准回答。

### 关键参数
- 向量库：ChromaDB
- 嵌入模型：all-MiniLM-L6-v2
- 支持文档：PDF、MD、TXT
""")
        # 创建测试TXT文件
        with open(f"{demo_dir}/notes.txt", "w", encoding="utf-8") as f:
            f.write("智能体工程笔记：\n1. 结构化记忆使用向量库存储\n2. 外部知识库支持多格式文档\n3. RAG增强提升回答准确性\n")
    return demo_dir

if __name__ == "__main__":
    # 1. 初始化测试文档
    demo_dir = init_demo_docs()
    
    # 2. 初始化智能体和知识库
    agent = RAGEnabledAgent(user_id="test_rag_001")
    km = agent.knowledge_manager
    
    # 3. 欢迎信息
    print("===== 智能体工程（结构化记忆+外部知识库） =====")
    print("指令说明：")
    print("  - exit      退出程序")
    print("  - list      查看知识库文档")
    print("  - add       批量添加demo_docs目录文档")
    print("  - add [文件]  添加单个文档（如：add ./demo_docs/readme.md）")
    print("  - del [文件]  删除文档（如：del ./demo_docs/readme.md）")
    print("===============================================")
    
    # 4. 交互循环
    while True:
        user_input = input("\n请输入指令/问题：").strip()
        if not user_input:
            continue
        
        # 退出
        if user_input.lower() == "exit":
            print("程序退出！")
            break
        
        # 查看文档列表
        elif user_input.lower() == "list":
            km.list_documents()
        
        # 批量添加demo文档
        elif user_input.lower() == "add":
            km.add_batch_documents(demo_dir)
        
        # 添加单个文档
        elif user_input.lower().startswith("add "):
            file_path = user_input[4:].strip()
            km.add_document(file_path)
        
        # 删除文档
        elif user_input.lower().startswith("del "):
            file_path = user_input[4:].strip()
            if km.delete_document(file_path):
                print(f"成功删除：{file_path}")
        
        # 智能体问答
        else:
            response = agent.run_with_rag(user_input)
            print(f"\n智能体回复：\n{response}")







            
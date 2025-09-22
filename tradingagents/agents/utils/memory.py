import chromadb
from chromadb.config import Settings
from openai import OpenAI


class FinancialSituationMemory:
    """金融情境记忆类，用于存储和检索金融情境及其对应的建议"""
    
    def __init__(self, name, config):
        """初始化金融情境记忆"""
        # 根据后端URL设置嵌入模型
        if config["backend_url"] == "http://localhost:11434/v1":
            self.embedding = "nomic-embed-text"
        else:
            self.embedding = "text-embedding-3-small"
        # 初始化OpenAI客户端
        self.client = OpenAI(base_url=config["backend_url"])
        # 初始化ChromaDB客户端
        self.chroma_client = chromadb.Client(Settings(allow_reset=True))
        # 创建情境集合
        self.situation_collection = self.chroma_client.create_collection(name=name)

    def get_embedding(self, text):
        """获取文本的OpenAI嵌入向量"""
        
        response = self.client.embeddings.create(
            model=self.embedding, input=text
        )
        return response.data[0].embedding

    def add_situations(self, situations_and_advice):
        """添加金融情境及其对应的建议。参数是包含情境和建议元组的列表"""
        
        # 初始化存储列表
        situations = []
        advice = []
        ids = []
        embeddings = []

        # 计算偏移量用于ID生成
        offset = self.situation_collection.count()

        # 处理每个情境和建议对
        for i, (situation, recommendation) in enumerate(situations_and_advice):
            situations.append(situation)
            advice.append(recommendation)
            ids.append(str(offset + i))
            embeddings.append(self.get_embedding(situation))

        # 将数据添加到集合中
        self.situation_collection.add(
            documents=situations,
            metadatas=[{"recommendation": rec} for rec in advice],
            embeddings=embeddings,
            ids=ids,
        )

    def get_memories(self, current_situation, n_matches=1):
        """使用OpenAI嵌入向量查找匹配的建议"""
        # 获取当前情境的嵌入向量
        query_embedding = self.get_embedding(current_situation)

        # 查询匹配的结果
        results = self.situation_collection.query(
            query_embeddings=[query_embedding],
            n_results=n_matches,
            include=["metadatas", "documents", "distances"],
        )

        # 处理匹配结果
        matched_results = []
        for i in range(len(results["documents"][0])):
            matched_results.append(
                {
                    "matched_situation": results["documents"][0][i],
                    "recommendation": results["metadatas"][0][i]["recommendation"],
                    "similarity_score": 1 - results["distances"][0][i],
                }
            )

        return matched_results


if __name__ == "__main__":
    # 示例用法
    # 注意：这只是一个示例，实际使用时需要提供正确的配置
    config = {
        "backend_url": "https://api.openai.com/v1"
    }
    matcher = FinancialSituationMemory("financial_situations", config)

    # 示例数据
    example_data = [
        (
            "高通胀率伴随利率上升和消费者支出下降",
            "考虑防御性行业如消费必需品和公用事业。审查固定收益投资组合的久期。",
        ),
        (
            "科技板块显示高波动性，机构抛售压力增加",
            "减少对高增长科技股的敞口。寻找具有强劲现金流的成熟科技公司的价值机会。",
        ),
        (
            "强势美元影响新兴市场，外汇波动性增加",
            "对冲国际头寸的货币敞口。考虑减少对新兴市场债务的配置。",
        ),
        (
            "市场显示板块轮动迹象，收益率上升",
            "重新平衡投资组合以维持目标配置。考虑增加受益于较高利率的板块的敞口。",
        ),
    ]

    # 添加示例情境和建议
    matcher.add_situations(example_data)

    # 示例查询
    current_situation = """
    市场显示科技板块波动性增加，机构投资者减少头寸，
    利率上升影响成长股估值
    """

    try:
        recommendations = matcher.get_memories(current_situation, n_matches=2)

        for i, rec in enumerate(recommendations, 1):
            print(f"\n匹配 {i}:")
            print(f"相似度得分: {rec['similarity_score']:.2f}")
            print(f"匹配的情境: {rec['matched_situation']}")
            print(f"建议: {rec['recommendation']}")

    except Exception as e:
        print(f"推荐过程中出错: {str(e)}")
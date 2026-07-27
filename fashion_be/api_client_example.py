"""
API 客户端使用示例
展示如何通过 Python 调用 Fashion Evaluation API
"""
import requests
from typing import List, Dict, Optional
import json


class FashionEvaluationClient:
    """Fashion Evaluation API 客户端"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """初始化客户端"""
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
    
    def health_check(self) -> Dict:
        """健康检查"""
        response = self.session.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def sync_data(self) -> Dict:
        """手动触发数据同步"""
        response = self.session.post(f"{self.base_url}/api/sync")
        response.raise_for_status()
        return response.json()
    
    def get_all_evaluations(self, skip: int = 0, limit: int = 100) -> List[Dict]:
        """获取所有评估记录"""
        params = {"skip": skip, "limit": limit}
        response = self.session.get(f"{self.base_url}/api/evaluations", params=params)
        response.raise_for_status()
        return response.json()
    
    def get_evaluation(self, look_name: str) -> Dict:
        """获取单个评估记录"""
        response = self.session.get(f"{self.base_url}/api/evaluations/{look_name}")
        response.raise_for_status()
        return response.json()
    
    def delete_evaluation(self, look_name: str) -> Dict:
        """删除评估记录"""
        response = self.session.delete(f"{self.base_url}/api/evaluations/{look_name}")
        response.raise_for_status()
        return response.json()
    
    def get_evaluations_by_score_range(
        self, 
        criteria: str, 
        min_score: float = 0, 
        max_score: float = 10
    ) -> List[Dict]:
        """
        根据评分范围筛选评估记录
        
        Args:
            criteria: 评估标准 (theme_relevance, brand_dna, innovation, aesthetics, structural_logic, functionality)
            min_score: 最低分
            max_score: 最高分
        """
        all_evaluations = self.get_all_evaluations(limit=1000)
        
        score_field = f"{criteria}_score"
        filtered = [
            eval for eval in all_evaluations
            if min_score <= eval.get(score_field, 0) <= max_score
        ]
        
        return filtered
    
    def get_top_evaluations(self, criteria: str, top_n: int = 5) -> List[Dict]:
        """
        获取某个标准评分最高的N个评估
        
        Args:
            criteria: 评估标准
            top_n: 返回的数量
        """
        all_evaluations = self.get_all_evaluations(limit=1000)
        
        score_field = f"{criteria}_score"
        sorted_evaluations = sorted(
            all_evaluations,
            key=lambda x: x.get(score_field, 0),
            reverse=True
        )
        
        return sorted_evaluations[:top_n]
    
    def get_average_scores(self) -> Dict[str, float]:
        """计算所有评估的平均分"""
        all_evaluations = self.get_all_evaluations(limit=1000)
        
        if not all_evaluations:
            return {}
        
        criteria = [
            'theme_relevance',
            'brand_dna',
            'innovation',
            'aesthetics',
            'structural_logic',
            'functionality'
        ]
        
        averages = {}
        for criterion in criteria:
            score_field = f"{criterion}_score"
            scores = [eval.get(score_field, 0) for eval in all_evaluations]
            averages[criterion] = sum(scores) / len(scores) if scores else 0
        
        # 计算总平均分
        averages['overall'] = sum(averages.values()) / len(averages) if averages else 0
        
        return averages


def example_usage():
    """使用示例"""
    print("=" * 60)
    print("Fashion Evaluation API 客户端使用示例")
    print("=" * 60)
    print()
    
    # 创建客户端
    client = FashionEvaluationClient("http://localhost:8000")
    
    try:
        # 1. 健康检查
        print("1. 健康检查:")
        health = client.health_check()
        print(f"   状态: {health['status']}")
        print()
        
        # 2. 手动同步数据
        print("2. 手动同步数据:")
        sync_result = client.sync_data()
        print(f"   {sync_result['message']}")
        print(f"   新增: {sync_result['new_records']}")
        print(f"   更新: {sync_result['updated_records']}")
        print(f"   总计: {sync_result['total_records']}")
        print()
        
        # 3. 获取所有评估记录（前5条）
        print("3. 获取所有评估记录（前5条）:")
        evaluations = client.get_all_evaluations(skip=0, limit=5)
        for eval in evaluations:
            print(f"   - {eval['look_name']}: {eval['brand']} - {eval['theme']}")
        print()
        
        # 4. 获取单个评估记录
        print("4. 获取单个评估记录 (look_1):")
        look_1 = client.get_evaluation("look_1")
        print(f"   Look: {look_1['look_name']}")
        print(f"   Brand: {look_1['brand']}")
        print(f"   Theme: {look_1['theme']}")
        print(f"   Theme Relevance Score: {look_1['theme_relevance_score']}")
        print(f"   Brand DNA Score: {look_1['brand_dna_score']}")
        print(f"   Innovation Score: {look_1['innovation_score']}")
        print()
        
        # 5. 根据评分范围筛选
        print("5. 筛选创新分 >= 7 的评估:")
        high_innovation = client.get_evaluations_by_score_range(
            criteria="innovation",
            min_score=7,
            max_score=10
        )
        print(f"   找到 {len(high_innovation)} 个结果:")
        for eval in high_innovation[:5]:
            print(f"   - {eval['look_name']}: 创新分 {eval['innovation_score']}")
        print()
        
        # 6. 获取评分最高的5个评估
        print("6. 美学评分最高的5个评估:")
        top_aesthetics = client.get_top_evaluations("aesthetics", top_n=5)
        for i, eval in enumerate(top_aesthetics, 1):
            print(f"   {i}. {eval['look_name']}: {eval['aesthetics_score']}")
        print()
        
        # 7. 计算平均分
        print("7. 各项评估标准的平均分:")
        averages = client.get_average_scores()
        for criterion, score in averages.items():
            print(f"   {criterion}: {score:.2f}")
        print()
        
        print("=" * 60)
        print("示例完成！")
        
    except requests.exceptions.ConnectionError:
        print("错误: 无法连接到 API 服务器")
        print("请确保服务器正在运行: python main.py")
    except requests.exceptions.HTTPError as e:
        print(f"HTTP 错误: {e}")
    except Exception as e:
        print(f"错误: {e}")


if __name__ == "__main__":
    example_usage()

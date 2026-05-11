"""
测试修复后的解析器
"""
from parser import EvaluationParser
import json

# 初始化解析器
parser = EvaluationParser(config_path="../fashion_config.yaml")

# 测试解析 look_3
print("=" * 80)
print("测试多个文件 - 按关键词匹配（忽略符号）")
print("=" * 80)

test_files = [
    r"E:\fashion_agents_project\fashion_research_dir\workflow_0\group_01\look_1_evaluation.txt",
    r"E:\fashion_agents_project\fashion_research_dir\workflow_0\group_01\look_6_evaluation.txt",
    r"E:\fashion_agents_project\fashion_research_dir\workflow_0\group_01\look_13_evaluation.txt",
    r"E:\fashion_agents_project\fashion_research_dir\workflow_0\group_01\look_14_evaluation.txt"
]

for file_path in test_files:
    result = parser.parse_evaluation_file(file_path)
    
    if result:
        print(f"\n{'='*70}")
        print(f"[{result['look_name']}]")
        print(f"{'='*70}")
        
        print(f"\nStrengths ({len(result.get('strengths', ''))} chars):")
        if result.get('strengths'):
            print(f"  {result['strengths'][:80]}...")
        else:
            print("  [EMPTY]")
        
        print(f"\nWeaknesses ({len(result.get('weaknesses', ''))} chars):")
        if result.get('weaknesses'):
            print(f"  {result['weaknesses'][:80]}...")
        else:
            print("  [EMPTY]")
        
        print(f"\nImprovement Suggestions ({len(result.get('improvement_suggestions', ''))} chars):")
        if result.get('improvement_suggestions'):
            print(f"  {result['improvement_suggestions'][:80]}...")
        else:
            print("  [EMPTY]")
    else:
        print(f"[FAIL] 解析失败: {file_path}")

print("\n" + "=" * 80)
print("测试完成")
print("=" * 80)

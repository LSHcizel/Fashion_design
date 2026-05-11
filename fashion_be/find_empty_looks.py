"""
查找数据库中有空字段的 look
"""
import sqlite3
from pathlib import Path

db_path = Path("fashion_evaluation.db")

if not db_path.exists():
    print("[ERROR] 数据库文件不存在")
    exit(1)

conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# 查询有空字段的 look
cursor.execute("""
    SELECT 
        look_name,
        CASE WHEN strengths IS NULL OR strengths = '' THEN 0 ELSE 1 END as has_strengths,
        CASE WHEN weaknesses IS NULL OR weaknesses = '' THEN 0 ELSE 1 END as has_weaknesses,
        CASE WHEN improvement_suggestions IS NULL OR improvement_suggestions = '' THEN 0 ELSE 1 END as has_improvements
    FROM look_evaluations
    WHERE 
        (strengths IS NULL OR strengths = '') OR
        (weaknesses IS NULL OR weaknesses = '') OR
        (improvement_suggestions IS NULL OR improvement_suggestions = '')
    ORDER BY look_name
""")

rows = cursor.fetchall()

print("=" * 80)
print("有空字段的 Look 列表")
print("=" * 80)

for row in rows:
    look_name, has_strengths, has_weaknesses, has_improvements = row
    
    missing = []
    if not has_strengths:
        missing.append("Strengths")
    if not has_weaknesses:
        missing.append("Weaknesses")
    if not has_improvements:
        missing.append("Improvements")
    
    print(f"{look_name}: 缺失 {', '.join(missing)}")

print(f"\n总计: {len(rows)} 个 look 有空字段")

conn.close()

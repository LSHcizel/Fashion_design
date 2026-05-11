"""
检查数据库中的空字段
"""
import sqlite3
from pathlib import Path

db_path = Path("fashion_evaluation.db")

if not db_path.exists():
    print("[ERROR] 数据库文件不存在")
    exit(1)

conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# 查询所有 look 评估
cursor.execute("""
    SELECT 
        look_name,
        brand,
        theme,
        strengths,
        weaknesses,
        improvement_suggestions
    FROM look_evaluations
    ORDER BY id
    LIMIT 5
""")

rows = cursor.fetchall()

print("=" * 80)
print("数据库字段检查 (前5条)")
print("=" * 80)

for row in rows:
    look_name, brand, theme, strengths, weaknesses, improvements = row
    
    print(f"\n[{look_name}]")
    print(f"  Brand: {brand}")
    print(f"  Theme: {theme}")
    
    # 检查字段长度
    print(f"  Strengths: {len(strengths) if strengths else 0} chars")
    if strengths:
        print(f"    Preview: {strengths[:100]}...")
    else:
        print(f"    [EMPTY]")
    
    print(f"  Weaknesses: {len(weaknesses) if weaknesses else 0} chars")
    if weaknesses:
        print(f"    Preview: {weaknesses[:100]}...")
    else:
        print(f"    [EMPTY]")
    
    print(f"  Improvements: {len(improvements) if improvements else 0} chars")
    if improvements:
        print(f"    Preview: {improvements[:100]}...")
    else:
        print(f"    [EMPTY]")

# 统计空字段
cursor.execute("""
    SELECT 
        COUNT(*) as total,
        SUM(CASE WHEN strengths IS NULL OR strengths = '' THEN 1 ELSE 0 END) as empty_strengths,
        SUM(CASE WHEN weaknesses IS NULL OR weaknesses = '' THEN 1 ELSE 0 END) as empty_weaknesses,
        SUM(CASE WHEN improvement_suggestions IS NULL OR improvement_suggestions = '' THEN 1 ELSE 0 END) as empty_improvements
    FROM look_evaluations
""")

stats = cursor.fetchone()
total, empty_strengths, empty_weaknesses, empty_improvements = stats

print("\n" + "=" * 80)
print("统计信息")
print("=" * 80)
print(f"总记录数: {total}")
print(f"空的 Strengths: {empty_strengths}")
print(f"空的 Weaknesses: {empty_weaknesses}")
print(f"空的 Improvement Suggestions: {empty_improvements}")

conn.close()

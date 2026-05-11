"""
检查 strengths 字段是否都有内容
"""
import sqlite3
from pathlib import Path

db_path = Path("fashion_evaluation.db")
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# 统计 strengths 字段
cursor.execute("""
    SELECT 
        COUNT(*) as total,
        SUM(CASE WHEN strengths IS NULL OR strengths = '' THEN 1 ELSE 0 END) as empty_strengths,
        MIN(LENGTH(strengths)) as min_length,
        MAX(LENGTH(strengths)) as max_length,
        AVG(LENGTH(strengths)) as avg_length
    FROM look_evaluations
""")

stats = cursor.fetchone()
total, empty_strengths, min_len, max_len, avg_len = stats

print("=" * 80)
print("Strengths 字段统计")
print("=" * 80)
print(f"总记录数: {total}")
print(f"空字段数: {empty_strengths}")
print(f"最小长度: {min_len} 字符")
print(f"最大长度: {max_len} 字符")
print(f"平均长度: {int(avg_len)} 字符")

if empty_strengths == 0:
    print("\n[OK] 所有 look 的 Overall Assessment 都已成功导入！")
else:
    # 显示哪些是空的
    cursor.execute("""
        SELECT look_name
        FROM look_evaluations
        WHERE strengths IS NULL OR strengths = ''
    """)
    empty_looks = [row[0] for row in cursor.fetchall()]
    print(f"\n[WARNING] 以下 look 的 strengths 字段为空:")
    for look in empty_looks:
        print(f"  - {look}")

# 显示几个样本
print("\n" + "=" * 80)
print("样本数据 (前3条)")
print("=" * 80)

cursor.execute("""
    SELECT look_name, LENGTH(strengths) as len, SUBSTR(strengths, 1, 150) as preview
    FROM look_evaluations
    ORDER BY id
    LIMIT 3
""")

for row in cursor.fetchall():
    look_name, length, preview = row
    print(f"\n[{look_name}] ({length} chars)")
    print(f"{preview}...")

conn.close()

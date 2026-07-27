"""
触发数据库重新同步
"""
import requests
import time

print("=" * 80)
print("触发数据重新同步")
print("=" * 80)

try:
    # 检查后端是否运行
    health_response = requests.get("http://localhost:8000/health", timeout=5)
    if health_response.status_code != 200:
        print("[ERROR] 后端服务未运行或健康检查失败")
        exit(1)
    
    print("[OK] 后端服务正常运行")
    print("\n开始同步...")
    
    # 触发同步
    sync_response = requests.post("http://localhost:8000/api/sync", timeout=60)
    
    if sync_response.status_code == 200:
        result = sync_response.json()
        print("\n[OK] 同步成功！")
        print(f"\n{result.get('message', '')}")
        
        print(f"\nLook 评估:")
        look_info = result.get('look', {})
        print(f"  新增: {look_info.get('new_records', 0)}")
        print(f"  更新: {look_info.get('updated_records', 0)}")
        print(f"  总计: {look_info.get('total_records', 0)}")
        
        print(f"\nCollection 评估:")
        collection_info = result.get('collection', {})
        print(f"  新增: {collection_info.get('new_records', 0)}")
        print(f"  更新: {collection_info.get('updated_records', 0)}")
        print(f"  总计: {collection_info.get('total_records', 0)}")
    else:
        print(f"[ERROR] 同步失败，状态码: {sync_response.status_code}")
        print(sync_response.text)

except requests.exceptions.ConnectionError:
    print("[ERROR] 无法连接到后端服务，请确保后端正在运行")
    print("运行: python main.py")
except requests.exceptions.Timeout:
    print("[ERROR] 请求超时")
except Exception as e:
    print(f"[ERROR] 发生错误: {e}")

print("\n" + "=" * 80)

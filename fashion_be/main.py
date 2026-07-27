"""
FastAPI 主应用程序
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
from typing import List
import uvicorn
import os
import re
from datetime import datetime

import models
import schemas
import crud
from database import engine, get_db
from parser import EvaluationParser
from pathlib import Path


# 评估文件目录路径
EVALUATION_DIR = r"E:\fashion_agents_project\fashion_research_dir\workflow_0"
CONFIG_FILE = r"E:\fashion_agents_project\fashion_config.yaml"
# 图片根目录
IMAGES_ROOT = r"E:\fashion_agents_project\fashion_research_dir"
WORKFLOW_0_ROOT = os.path.join(IMAGES_ROOT, "workflow_0")


def is_date_dirname(name: str) -> bool:
    """
    判断目录名是否为“日期运行目录”：
    - YYYY-MM-DD
    - YYYY-MM-DD_02 / YYYY-MM-DD_03 ...
    """
    if not name:
        return False
    return re.fullmatch(r"\d{4}-\d{2}-\d{2}(?:_\d{2})?", name) is not None


def list_non_date_categories(workflow_root: str) -> List[str]:
    """列出 workflow_0 下所有非日期目录（用于前端下拉栏分类）"""
    p = Path(workflow_root)
    if not p.exists() or not p.is_dir():
        return []
    dirs = []
    for child in p.iterdir():
        if child.is_dir() and (not is_date_dirname(child.name)):
            dirs.append(child.name)
    return sorted(dirs)

def load_workflow0_non_date_evaluation_data(parser: EvaluationParser) -> tuple:
    """
    从 workflow_0 下所有“非日期目录”加载评估数据，并做命名去冲突处理。
    返回 (look_data, collection_data) 两个列表。
    说明：
    - 不递归日期目录（YYYY-MM-DD / YYYY-MM-DD_02...）
    - 为避免不同分类下 look_1 / look_2 重名导致数据库 unique 冲突，写库时会把 look_name 加上分类前缀：
      BA/look_1, DCV/look_1 ...
    - collection_name 同样加前缀以保持一致：BA/Qwen_collection_evaluation ...
    """
    all_look_data = []
    all_collection_data = []

    categories = list_non_date_categories(WORKFLOW_0_ROOT)
    for category in categories:
        category_dir = Path(WORKFLOW_0_ROOT) / category
        try:
            look_data, collection_data = parser.parse_directory_with_collections(str(category_dir))
        except Exception as e:
            print(f"警告: 解析目录失败，将跳过 {category_dir}: {e}")
            continue

        # 统一补齐字段 + 命名去冲突
        for rec in look_data:
            rec = normalize_look_record(rec)
            base_look_name = rec.get("look_name", "")
            rec["look_name"] = f"{category}/{base_look_name}" if base_look_name else f"{category}/"
            all_look_data.append(rec)

        for rec in collection_data:
            rec = normalize_collection_record(rec)
            base_collection_name = rec.get("collection_name", "")
            rec["collection_name"] = f"{category}/{base_collection_name}" if base_collection_name else f"{category}/"
            all_collection_data.append(rec)

    return all_look_data, all_collection_data


def normalize_look_record(record: dict) -> dict:
    """补齐 look 评估字段，避免某些解析缺失导致接口返回失败"""
    required_float = [
        "theme_relevance_score",
        "brand_dna_score",
        "innovation_score",
        "aesthetics_score",
        "structural_logic_score",
        "functionality_score",
    ]
    required_str = [
        "theme_relevance_justification",
        "brand_dna_justification",
        "innovation_justification",
        "aesthetics_justification",
        "structural_logic_justification",
        "functionality_justification",
        "strengths",
        "weaknesses",
        "improvement_suggestions",
        "image_path",
        "look_name",
        "brand",
        "theme",
    ]
    for k in required_float:
        if k not in record or record[k] is None:
            record[k] = 0.0
    for k in required_str:
        if k not in record or record[k] is None:
            record[k] = ""
    return record


def normalize_collection_record(record: dict) -> dict:
    required_float = [
        "narrative_cohesion_score",
        "visual_unity_score",
        "range_balance_score",
        "rhythm_flow_score",
    ]
    required_str = [
        "narrative_cohesion_justification",
        "visual_unity_justification",
        "range_balance_justification",
        "rhythm_flow_justification",
        "overall_assessment",
        "strengths",
        "weaknesses",
        "overall_quality",
        "collection_name",
        "brand",
        "theme",
    ]
    for k in required_float:
        if k not in record or record[k] is None:
            record[k] = 0.0
    for k in required_str:
        if k not in record or record[k] is None:
            record[k] = ""
    return record


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用启动和关闭时的生命周期管理"""
    # 启动时执行
    print("=" * 60)
    print("FastAPI 应用启动中...")
    
    # 创建数据库表
    print("创建数据库表...")
    models.Base.metadata.create_all(bind=engine)
    
    # 增量同步数据
    print("开始增量同步评估数据...")
    sync_result = sync_evaluations_on_startup()
    print(f"Look 评估同步完成: 新增 {sync_result['look_new']} 条, "
          f"更新 {sync_result['look_updated']} 条, "
          f"总计 {sync_result['look_total']} 条记录")
    print(f"Collection 评估同步完成: 新增 {sync_result['collection_new']} 条, "
          f"更新 {sync_result['collection_updated']} 条, "
          f"总计 {sync_result['collection_total']} 条记录")
    
    print("=" * 60)
    
    yield
    
    # 关闭时执行
    print("FastAPI 应用关闭")


app = FastAPI(
    title="Fashion Evaluation API",
    description="时尚设计评估数据管理系统",
    version="1.0.0",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "*"],  # 支持不同端口的前端
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件目录（图片）
if os.path.exists(IMAGES_ROOT):
    app.mount("/images", StaticFiles(directory=IMAGES_ROOT), name="images")
    print(f"静态文件目录已挂载: /images -> {IMAGES_ROOT}")
else:
    print(f"警告: 图片目录不存在: {IMAGES_ROOT}")


def convert_image_path_to_url(file_path: str) -> str:
    """
    将本地文件路径转换为 API 可访问的 URL
    
    Args:
        file_path: 本地文件路径，如 E:\\fashion_agents_project\\fashion_research_dir\\workflow_0\\group_01\\look_1.png
        
    Returns:
        API URL，如 /images/workflow_0/group_01/look_1.png
    """
    if not file_path:
        return ""
    
    # 规范化路径
    file_path = os.path.normpath(file_path)
    images_root = os.path.normpath(IMAGES_ROOT)
    
    # 如果路径在图片根目录下，转换为相对路径
    if file_path.startswith(images_root):
        relative_path = os.path.relpath(file_path, images_root)
        # 转换为 URL 格式（使用正斜杠）
        url_path = relative_path.replace(os.sep, '/')
        return f"/images/{url_path}"
    
    return file_path


def sync_evaluations_on_startup() -> dict:
    """
    启动时同步评估数据到数据库（包括 look 和 collection）
    
    Returns:
        包含同步统计信息的字典
    """
    try:
        # 创建解析器
        parser = EvaluationParser(config_path=CONFIG_FILE)
        
        # 解析 workflow_0 下所有非日期目录（如 BA/DCV/GPT/Qwen...）
        look_data, collection_data = load_workflow0_non_date_evaluation_data(parser)
        
        if not look_data and not collection_data:
            print(f"警告: 在目录 {WORKFLOW_0_ROOT} 的非日期子目录中未找到评估文件")
            return {
                "look_new": 0, "look_updated": 0, "look_total": 0,
                "collection_new": 0, "collection_updated": 0, "collection_total": 0
            }
        
        # 同步到数据库
        db = next(get_db())
        try:
            # 同步 look 评估
            look_new, look_updated, look_total = crud.sync_evaluations_from_data(db, look_data)
            
            # 同步 collection 评估
            collection_new, collection_updated, collection_total = crud.sync_collection_evaluations_from_data(db, collection_data)
            
            return {
                "look_new": look_new,
                "look_updated": look_updated,
                "look_total": look_total,
                "collection_new": collection_new,
                "collection_updated": collection_updated,
                "collection_total": collection_total
            }
        finally:
            db.close()
            
    except Exception as e:
        print(f"同步数据时出错: {e}")
        return {
            "look_new": 0, "look_updated": 0, "look_total": 0,
            "collection_new": 0, "collection_updated": 0, "collection_total": 0
        }


@app.get("/", tags=["Root"])
async def root():
    """根路径"""
    return {
        "message": "Fashion Evaluation API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


@app.post("/api/sync", tags=["Sync"])
async def manual_sync(db: Session = Depends(get_db)):
    """
    手动触发数据同步（包括 look 和 collection）
    
    从评估文件目录重新解析并同步数据到数据库
    """
    try:
        parser = EvaluationParser(config_path=CONFIG_FILE)
        look_data, collection_data = load_workflow0_non_date_evaluation_data(parser)
        
        if not look_data and not collection_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"在目录 {WORKFLOW_0_ROOT} 的非日期子目录中未找到评估文件"
            )
        
        # 同步 look 评估
        look_new, look_updated, look_total = crud.sync_evaluations_from_data(db, look_data)
        
        # 同步 collection 评估
        collection_new, collection_updated, collection_total = crud.sync_collection_evaluations_from_data(db, collection_data)
        
        return {
            "message": "数据同步成功",
            "look": {
                "new_records": look_new,
                "updated_records": look_updated,
                "total_records": look_total
            },
            "collection": {
                "new_records": collection_new,
                "updated_records": collection_updated,
                "total_records": collection_total
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"同步数据时出错: {str(e)}"
        )


@app.get("/api/evaluations", response_model=List[schemas.LookEvaluationResponse], tags=["Evaluations"])
async def get_evaluations(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """
    获取所有评估记录
    
    - **skip**: 跳过的记录数（用于分页）
    - **limit**: 返回的最大记录数
    """
    evaluations = crud.get_all_look_evaluations(db, skip=skip, limit=limit)
    
    # 转换图片路径为 URL
    for evaluation in evaluations:
        evaluation.image_path = convert_image_path_to_url(evaluation.image_path)
    
    return evaluations


@app.get("/api/evaluations/{look_name}", response_model=schemas.LookEvaluationResponse, tags=["Evaluations"])
async def get_evaluation(look_name: str, db: Session = Depends(get_db)):
    """
    根据 look_name 获取单个评估记录
    
    - **look_name**: Look 名称，例如 "look_1"
    """
    evaluation = crud.get_look_evaluation_by_name(db, look_name)
    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"未找到名为 '{look_name}' 的评估记录"
        )
    
    # 转换图片路径为 URL
    evaluation.image_path = convert_image_path_to_url(evaluation.image_path)
    
    return evaluation


@app.delete("/api/evaluations/{look_name}", tags=["Evaluations"])
async def delete_evaluation(look_name: str, db: Session = Depends(get_db)):
    """
    删除指定的评估记录
    
    - **look_name**: Look 名称
    """
    success = crud.delete_look_evaluation(db, look_name)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"未找到名为 '{look_name}' 的评估记录"
        )
    return {"message": f"成功删除评估记录: {look_name}"}


# ==================== Collection Evaluation Endpoints ====================

@app.get("/api/collections", response_model=List[schemas.CollectionEvaluationResponse], tags=["Collections"])
async def get_collections(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """
    获取所有 collection 总评记录
    
    - **skip**: 跳过的记录数（用于分页）
    - **limit**: 返回的最大记录数
    """
    collections = crud.get_all_collection_evaluations(db, skip=skip, limit=limit)
    return collections


# ==================== Workflow_0 Filesystem Endpoints ====================

@app.get("/api/workflow0/categories", response_model=List[str], tags=["Workflow0"])
async def get_workflow0_categories():
    """
    获取 workflow_0 下所有“非日期目录”的分类列表（如 BA / DCV / GPT / Qwen ...）
    """
    categories = list_non_date_categories(WORKFLOW_0_ROOT)
    return categories


@app.get("/api/workflow0/evaluations", response_model=List[schemas.LookEvaluationResponse], tags=["Workflow0"])
async def get_workflow0_look_evaluations(category: str):
    """
    直接从文件系统读取某个分类目录下的 look 评估（不依赖数据库）
    """
    category_dir = Path(WORKFLOW_0_ROOT) / category
    if not category_dir.exists() or not category_dir.is_dir():
        raise HTTPException(status_code=404, detail=f"分类目录不存在: {category_dir}")

    parser = EvaluationParser(config_path=CONFIG_FILE)
    look_data, _ = parser.parse_directory_with_collections(str(category_dir))

    now = datetime.now()
    results: List[schemas.LookEvaluationResponse] = []
    for i, rec in enumerate(look_data, start=1):
        rec = normalize_look_record(rec)
        # 图片路径转为可访问 URL
        rec["image_path"] = convert_image_path_to_url(rec.get("image_path", ""))
        results.append(
            schemas.LookEvaluationResponse(
                id=i,
                created_at=now,
                updated_at=now,
                **rec,
            )
        )
    return results


@app.get("/api/workflow0/collections", response_model=List[schemas.CollectionEvaluationResponse], tags=["Workflow0"])
async def get_workflow0_collection_evaluations(category: str):
    """
    直接从文件系统读取某个分类目录下的 collection 总评（不依赖数据库）
    """
    category_dir = Path(WORKFLOW_0_ROOT) / category
    if not category_dir.exists() or not category_dir.is_dir():
        raise HTTPException(status_code=404, detail=f"分类目录不存在: {category_dir}")

    parser = EvaluationParser(config_path=CONFIG_FILE)
    _, collection_data = parser.parse_directory_with_collections(str(category_dir))

    now = datetime.now()
    results: List[schemas.CollectionEvaluationResponse] = []
    for i, rec in enumerate(collection_data, start=1):
        rec = normalize_collection_record(rec)
        results.append(
            schemas.CollectionEvaluationResponse(
                id=i,
                created_at=now,
                updated_at=now,
                **rec,
            )
        )
    return results


@app.get("/api/collections/{collection_name}", response_model=schemas.CollectionEvaluationResponse, tags=["Collections"])
async def get_collection(collection_name: str, db: Session = Depends(get_db)):
    """
    根据 collection_name 获取单个总评记录
    
    - **collection_name**: Collection 名称，例如 "group_01_collection"
    """
    collection = crud.get_collection_evaluation_by_name(db, collection_name)
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"未找到名为 '{collection_name}' 的总评记录"
        )
    return collection


@app.delete("/api/collections/{collection_name}", tags=["Collections"])
async def delete_collection(collection_name: str, db: Session = Depends(get_db)):
    """
    删除指定的 collection 总评记录
    
    - **collection_name**: Collection 名称
    """
    success = crud.delete_collection_evaluation(db, collection_name)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"未找到名为 '{collection_name}' 的总评记录"
        )
    return {"message": f"成功删除总评记录: {collection_name}"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

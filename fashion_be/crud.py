"""
数据库CRUD操作
"""
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Optional
import models
import schemas


def get_look_evaluation_by_name(db: Session, look_name: str) -> Optional[models.LookEvaluation]:
    """根据look_name查询评估记录"""
    return db.query(models.LookEvaluation).filter(models.LookEvaluation.look_name == look_name).first()


def get_all_look_evaluations(db: Session, skip: int = 0, limit: int = 100) -> List[models.LookEvaluation]:
    """获取所有评估记录"""
    return db.query(models.LookEvaluation).offset(skip).limit(limit).all()


def create_look_evaluation(db: Session, evaluation_data: dict) -> models.LookEvaluation:
    """创建新的评估记录"""
    db_evaluation = models.LookEvaluation(**evaluation_data)
    db.add(db_evaluation)
    db.commit()
    db.refresh(db_evaluation)
    return db_evaluation


def update_look_evaluation(db: Session, look_name: str, evaluation_data: dict) -> Optional[models.LookEvaluation]:
    """更新现有评估记录"""
    db_evaluation = get_look_evaluation_by_name(db, look_name)
    if db_evaluation:
        for key, value in evaluation_data.items():
            if hasattr(db_evaluation, key):
                setattr(db_evaluation, key, value)
        db.commit()
        db.refresh(db_evaluation)
        return db_evaluation
    return None


def sync_evaluations_from_data(db: Session, evaluations_data: List[dict]) -> tuple:
    """
    从解析的数据批量同步到数据库
    
    Returns:
        (新增记录数, 更新记录数, 总记录数)
    """
    new_count = 0
    updated_count = 0
    
    for eval_data in evaluations_data:
        look_name = eval_data['look_name']
        existing = get_look_evaluation_by_name(db, look_name)
        
        if existing:
            # 更新现有记录
            update_look_evaluation(db, look_name, eval_data)
            updated_count += 1
        else:
            # 创建新记录
            create_look_evaluation(db, eval_data)
            new_count += 1
    
    total_count = db.query(models.LookEvaluation).count()
    
    return new_count, updated_count, total_count


def delete_look_evaluation(db: Session, look_name: str) -> bool:
    """删除评估记录"""
    db_evaluation = get_look_evaluation_by_name(db, look_name)
    if db_evaluation:
        db.delete(db_evaluation)
        db.commit()
        return True
    return False


# ==================== Collection Evaluation CRUD ====================

def get_collection_evaluation_by_name(db: Session, collection_name: str) -> Optional[models.CollectionEvaluation]:
    """根据collection_name查询总评记录"""
    return db.query(models.CollectionEvaluation).filter(
        models.CollectionEvaluation.collection_name == collection_name
    ).first()


def get_all_collection_evaluations(db: Session, skip: int = 0, limit: int = 100) -> List[models.CollectionEvaluation]:
    """获取所有总评记录"""
    return db.query(models.CollectionEvaluation).offset(skip).limit(limit).all()


def create_collection_evaluation(db: Session, evaluation_data: dict) -> models.CollectionEvaluation:
    """创建新的总评记录"""
    db_evaluation = models.CollectionEvaluation(**evaluation_data)
    db.add(db_evaluation)
    db.commit()
    db.refresh(db_evaluation)
    return db_evaluation


def update_collection_evaluation(db: Session, collection_name: str, evaluation_data: dict) -> Optional[models.CollectionEvaluation]:
    """更新现有总评记录"""
    db_evaluation = get_collection_evaluation_by_name(db, collection_name)
    if db_evaluation:
        for key, value in evaluation_data.items():
            if hasattr(db_evaluation, key):
                setattr(db_evaluation, key, value)
        db.commit()
        db.refresh(db_evaluation)
        return db_evaluation
    return None


def sync_collection_evaluations_from_data(db: Session, evaluations_data: List[dict]) -> tuple:
    """
    从解析的数据批量同步 collection 评估到数据库
    
    Returns:
        (新增记录数, 更新记录数, 总记录数)
    """
    new_count = 0
    updated_count = 0
    
    for eval_data in evaluations_data:
        collection_name = eval_data['collection_name']
        existing = get_collection_evaluation_by_name(db, collection_name)
        
        if existing:
            # 更新现有记录
            update_collection_evaluation(db, collection_name, eval_data)
            updated_count += 1
        else:
            # 创建新记录
            create_collection_evaluation(db, eval_data)
            new_count += 1
    
    total_count = db.query(models.CollectionEvaluation).count()
    
    return new_count, updated_count, total_count


def delete_collection_evaluation(db: Session, collection_name: str) -> bool:
    """删除总评记录"""
    db_evaluation = get_collection_evaluation_by_name(db, collection_name)
    if db_evaluation:
        db.delete(db_evaluation)
        db.commit()
        return True
    return False

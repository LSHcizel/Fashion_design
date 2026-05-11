"""
Pydantic 模型定义（用于API请求和响应）
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class CriteriaItem(BaseModel):
    """单个评估标准项"""
    score: float = Field(..., ge=0, le=10, description="评分(0-10)")
    justification: str = Field(..., description="评分理由")


class LookEvaluationBase(BaseModel):
    """Look评估基础模型"""
    look_name: str = Field(..., description="Look名称")
    brand: str = Field(..., description="品牌名称")
    theme: str = Field(..., description="主题名称")
    
    # Criteria 评分
    theme_relevance_score: float = Field(..., ge=0, le=10)
    theme_relevance_justification: str
    
    brand_dna_score: float = Field(..., ge=0, le=10)
    brand_dna_justification: str
    
    innovation_score: float = Field(..., ge=0, le=10)
    innovation_justification: str
    
    aesthetics_score: float = Field(..., ge=0, le=10)
    aesthetics_justification: str
    
    structural_logic_score: float = Field(..., ge=0, le=10)
    structural_logic_justification: str
    
    functionality_score: float = Field(..., ge=0, le=10)
    functionality_justification: str
    
    # Overall Assessment
    strengths: str
    weaknesses: str
    improvement_suggestions: str
    
    # 图片路径
    image_path: str


class LookEvaluationCreate(LookEvaluationBase):
    """创建Look评估时使用的模型"""
    pass


class LookEvaluationResponse(LookEvaluationBase):
    """响应模型，包含数据库字段"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SyncResponse(BaseModel):
    """同步操作响应"""
    message: str
    new_records: int
    updated_records: int
    total_records: int


# ==================== Collection Evaluation Schemas ====================

class CollectionEvaluationBase(BaseModel):
    """Collection评估基础模型"""
    collection_name: str = Field(..., description="Collection名称")
    brand: str = Field(..., description="品牌名称")
    theme: str = Field(..., description="主题名称")
    
    # Cohesion 评分
    narrative_cohesion_score: float = Field(..., ge=0, le=10)
    narrative_cohesion_justification: str
    
    visual_unity_score: float = Field(..., ge=0, le=10)
    visual_unity_justification: str
    
    # Composition 评分
    range_balance_score: float = Field(..., ge=0, le=10)
    range_balance_justification: str
    
    rhythm_flow_score: float = Field(..., ge=0, le=10)
    rhythm_flow_justification: str
    
    # Overall Assessment
    overall_assessment: str
    strengths: str
    weaknesses: str
    overall_quality: str


class CollectionEvaluationCreate(CollectionEvaluationBase):
    """创建Collection评估时使用的模型"""
    pass


class CollectionEvaluationResponse(CollectionEvaluationBase):
    """响应模型，包含数据库字段"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

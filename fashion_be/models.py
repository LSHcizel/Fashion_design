"""
数据库模型定义
"""
from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from sqlalchemy.sql import func
from database import Base


class LookEvaluation(Base):
    """Look 评估数据表"""
    __tablename__ = "look_evaluations"

    id = Column(Integer, primary_key=True, index=True)
    look_name = Column(String, unique=True, index=True, nullable=False, comment="Look 名称，如 look_1")
    brand = Column(String, nullable=False, comment="品牌名称")
    theme = Column(String, nullable=False, comment="主题名称")
    
    # Criteria 评分项（6个标准评估维度）
    theme_relevance_score = Column(Float, comment="主题相关性评分")
    theme_relevance_justification = Column(Text, comment="主题相关性理由")
    
    brand_dna_score = Column(Float, comment="品牌DNA契合度评分")
    brand_dna_justification = Column(Text, comment="品牌DNA契合度理由")
    
    innovation_score = Column(Float, comment="创新与原创性评分")
    innovation_justification = Column(Text, comment="创新与原创性理由")
    
    aesthetics_score = Column(Float, comment="美学与视觉冲击力评分")
    aesthetics_justification = Column(Text, comment="美学与视觉冲击力理由")
    
    structural_logic_score = Column(Float, comment="结构逻辑与材料表达评分")
    structural_logic_justification = Column(Text, comment="结构逻辑与材料表达理由")
    
    functionality_score = Column(Float, comment="预期功能性评分")
    functionality_justification = Column(Text, comment="预期功能性理由")
    
    # Overall Assessment 部分
    strengths = Column(Text, comment="优点描述")
    weaknesses = Column(Text, comment="弱点描述")
    improvement_suggestions = Column(Text, comment="改进建议")
    
    # 图片路径
    image_path = Column(String, nullable=False, comment="对应PNG图片的文件路径")
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")

    def __repr__(self):
        return f"<LookEvaluation(look_name='{self.look_name}', brand='{self.brand}', theme='{self.theme}')>"


class CollectionEvaluation(Base):
    """Collection 总评数据表"""
    __tablename__ = "collection_evaluations"

    id = Column(Integer, primary_key=True, index=True)
    collection_name = Column(String, unique=True, index=True, nullable=False, comment="Collection 名称，如 group_01_collection")
    brand = Column(String, nullable=False, comment="品牌名称")
    theme = Column(String, nullable=False, comment="主题名称")
    
    # Cohesion 类别评分项（2个）
    narrative_cohesion_score = Column(Float, comment="叙事连贯性评分")
    narrative_cohesion_justification = Column(Text, comment="叙事连贯性理由")
    
    visual_unity_score = Column(Float, comment="视觉统一性评分")
    visual_unity_justification = Column(Text, comment="视觉统一性理由")
    
    # Composition 类别评分项（2个）
    range_balance_score = Column(Float, comment="范围平衡性评分")
    range_balance_justification = Column(Text, comment="范围平衡性理由")
    
    rhythm_flow_score = Column(Float, comment="节奏与流动性评分")
    rhythm_flow_justification = Column(Text, comment="节奏与流动性理由")
    
    # Overall Collection Assessment 部分
    overall_assessment = Column(Text, comment="整体评估描述")
    strengths = Column(Text, comment="优点描述")
    weaknesses = Column(Text, comment="弱点描述")
    overall_quality = Column(Text, comment="整体质量评价")
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")

    def __repr__(self):
        return f"<CollectionEvaluation(collection_name='{self.collection_name}', brand='{self.brand}', theme='{self.theme}')>"

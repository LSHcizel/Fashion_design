/**
 * API 服务层 - 连接后端 FastAPI
 */

const API_BASE_URL = 'http://localhost:8000';

// ==================== Types ====================

export interface LookEvaluation {
  id?: number;
  look_name: string;
  brand: string;
  theme: string;
  
  // Criteria scores
  theme_relevance_score: number;
  theme_relevance_justification: string;
  brand_dna_score: number;
  brand_dna_justification: string;
  innovation_score: number;
  innovation_justification: string;
  aesthetics_score: number;
  aesthetics_justification: string;
  structural_logic_score: number;
  structural_logic_justification: string;
  functionality_score: number;
  functionality_justification: string;
  
  // Overall assessment
  strengths: string;
  weaknesses: string;
  improvement_suggestions: string;
  
  // Image path
  image_path: string;
  
  // Timestamps
  created_at?: string;
  updated_at?: string;
}

export interface CollectionEvaluation {
  id?: number;
  collection_name: string;
  brand: string;
  theme: string;
  
  // Cohesion criteria
  narrative_cohesion_score: number;
  narrative_cohesion_justification: string;
  visual_unity_score: number;
  visual_unity_justification: string;
  
  // Composition criteria
  range_balance_score: number;
  range_balance_justification: string;
  rhythm_flow_score: number;
  rhythm_flow_justification: string;
  
  // Overall assessment
  overall_assessment: string;
  strengths: string;
  weaknesses: string;
  overall_quality: string;
  
  // Timestamps
  created_at?: string;
  updated_at?: string;
}

// ==================== API Functions ====================

/**
 * 获取 workflow_0 下的分类列表（非日期目录）
 */
export async function fetchWorkflow0Categories(): Promise<string[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/workflow0/categories`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching workflow0 categories:', error);
    return [];
  }
}

/**
 * 获取所有 Look 评估
 */
export async function fetchLookEvaluations(category?: string): Promise<LookEvaluation[]> {
  try {
    const url = category
      ? `${API_BASE_URL}/api/workflow0/evaluations?category=${encodeURIComponent(category)}`
      : `${API_BASE_URL}/api/evaluations`;
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching look evaluations:', error);
    return [];
  }
}

/**
 * 获取单个 Look 评估
 */
export async function fetchLookEvaluation(lookName: string): Promise<LookEvaluation | null> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/evaluations/${lookName}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error(`Error fetching look evaluation ${lookName}:`, error);
    return null;
  }
}

/**
 * 获取所有 Collection 评估
 */
export async function fetchCollectionEvaluations(): Promise<CollectionEvaluation[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/collections`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching collection evaluations:', error);
    return [];
  }
}

/**
 * 获取某个分类目录下的 Collection 评估（来自 workflow_0 文件系统）
 */
export async function fetchWorkflow0CollectionEvaluations(category: string): Promise<CollectionEvaluation[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/workflow0/collections?category=${encodeURIComponent(category)}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching workflow0 collection evaluations:', error);
    return [];
  }
}

/**
 * 获取单个 Collection 评估
 */
export async function fetchCollectionEvaluation(collectionName: string): Promise<CollectionEvaluation | null> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/collections/${collectionName}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error(`Error fetching collection evaluation ${collectionName}:`, error);
    return null;
  }
}

/**
 * 手动触发数据同步
 */
export async function syncData(): Promise<any> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/sync`, {
      method: 'POST',
    });
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error syncing data:', error);
    throw error;
  }
}

/**
 * 检查后端健康状态
 */
export async function checkHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    return response.ok;
  } catch (error) {
    console.error('Error checking health:', error);
    return false;
  }
}

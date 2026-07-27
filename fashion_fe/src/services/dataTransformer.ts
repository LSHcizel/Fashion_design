/**
 * 数据转换层 - 将后端数据转换为前端组件格式
 */

import { LookEvaluation, CollectionEvaluation } from './api';
import { DesignCase, ThemeAnalysis, ThemeAnalysisCriteria } from '../data/mockData';

const API_BASE_URL = 'http://localhost:8000';

/**
 * 将后端 LookEvaluation 转换为前端 DesignCase 格式
 */
export function transformLookToDesignCase(look: LookEvaluation): DesignCase {
  // 计算总分
  const totalScore = 
    look.theme_relevance_score +
    look.brand_dna_score +
    look.innovation_score +
    look.aesthetics_score +
    look.structural_logic_score +
    look.functionality_score;

  // 解析优点列表（从文本解析为数组）
  const strengths = parseListItems(look.strengths);
  
  // 解析弱点列表
  const weaknesses = parseListItems(look.weaknesses);
  
  // 解析改进建议
  const improvements = parseListItems(look.improvement_suggestions);
  
  // 转换图片路径
  const imagePath = convertImagePath(look.image_path);

  return {
    id: look.look_name,
    name: formatLookName(look.look_name),
    imagePath: imagePath,
    totalScore,
    scores: [
      {
        criteria: 'Theme Relevance',
        score: look.theme_relevance_score,
        justification: look.theme_relevance_justification
      },
      {
        criteria: 'Brand DNA Alignment',
        score: look.brand_dna_score,
        justification: look.brand_dna_justification
      },
      {
        criteria: 'Innovation & Originality',
        score: look.innovation_score,
        justification: look.innovation_justification
      },
      {
        criteria: 'Aesthetics & Visual Impact',
        score: look.aesthetics_score,
        justification: look.aesthetics_justification
      },
      {
        criteria: 'Structural Logic & Material Expression',
        score: look.structural_logic_score,
        justification: look.structural_logic_justification
      },
      {
        criteria: 'Anticipated Functionality',
        score: look.functionality_score,
        justification: look.functionality_justification
      }
    ],
    strengths,
    weaknesses,
    improvements
  };
}

/**
 * 将后端 CollectionEvaluation 转换为前端 ThemeAnalysis 格式
 */
export function transformCollectionToThemeAnalysis(collection: CollectionEvaluation): ThemeAnalysis {
  // 解析优点列表
  const strengths = parseListItems(collection.strengths);
  
  // 解析弱点列表
  const weaknesses = parseListItems(collection.weaknesses);

  const analysisCriteria: ThemeAnalysisCriteria[] = [
    {
      category: 'Cohesion',
      criteria: 'Narrative Cohesion',
      score: collection.narrative_cohesion_score,
      justification: collection.narrative_cohesion_justification
    },
    {
      category: 'Cohesion',
      criteria: 'Visual Unity',
      score: collection.visual_unity_score,
      justification: collection.visual_unity_justification
    },
    {
      category: 'Composition',
      criteria: 'Range Balance',
      score: collection.range_balance_score,
      justification: collection.range_balance_justification
    },
    {
      category: 'Composition',
      criteria: 'Rhythm & Flow',
      score: collection.rhythm_flow_score,
      justification: collection.rhythm_flow_justification
    }
  ];

  return {
    collectionName: collection.collection_name,
    themeTitle: collection.theme,
    brand: collection.brand,
    analysisCriteria,
    overallAssessment: {
      description: collection.overall_assessment,
      strengths,
      weaknesses,
      overallQuality: collection.overall_quality
    }
  };
}

/**
 * 解析列表项（从 Markdown 格式的文本中提取列表项）
 * 输入示例: "- Item 1\n- Item 2\n- Item 3"
 * 输出: ["Item 1", "Item 2", "Item 3"]
 */
function parseListItems(text: string): string[] {
  if (!text) return [];
  
  // 分割行，移除空行
  const lines = text.split('\n').filter(line => line.trim());
  
  // 提取以 - 或 * 开头的项（兼容 Markdown 列表）
  const items = lines
    .map(line => line.trim())
    .filter(line => /^[-*•]\s+/.test(line))
    .map(line => line.replace(/^[-*•]\s+/, '').trim())
    .map(line => line.replace(/\*\*/g, '').trim())
    // 去除纯标题行（例如 "Strengths:" / "Weaknesses"）
    .filter(line => !/^(Strengths|Weaknesses|Improvement\s+Suggestion(?:s)?)\s*:?\s*$/i.test(line));
  
  // 如果没有列表项，则把整段作为单条展示（避免界面空白）
  if (items.length === 0) {
    return [text.trim()];
  }
  return items;
}

/**
 * 格式化 look 名称
 * 输入: "look_1" 
 * 输出: "Look 1"
 */
function formatLookName(lookName: string): string {
  // 将 look_1 转换为 Look 1
  const parts = lookName.split('_');
  if (parts.length >= 2) {
    return `${parts[0].charAt(0).toUpperCase() + parts[0].slice(1)} ${parts[1]}`;
  }
  return lookName;
}

/**
 * 转换图片路径为完整的 URL
 * 如果是相对路径（如 /images/...），转换为完整 URL
 * 如果是完整路径，保持不变
 */
function convertImagePath(path: string): string {
  if (!path) return '';
  
  // 如果是相对路径（以 /images 开头），转换为完整 URL
  if (path.startsWith('/images')) {
    return `${API_BASE_URL}${path}`;
  }
  
  // 如果已经是完整 URL，直接返回
  if (path.startsWith('http://') || path.startsWith('https://')) {
    return path;
  }
  
  // 其他情况（如本地文件路径），返回空字符串（将显示占位符）
  return '';
}

/**
 * 批量转换 Look 评估列表
 */
export function transformLooksToDesignCases(looks: LookEvaluation[]): DesignCase[] {
  return looks.map(transformLookToDesignCase);
}

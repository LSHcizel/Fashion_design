import React, { useState, useEffect } from 'react';
import { DesignCase, criteriaNames, ThemeAnalysis } from '../data/mockData';
import { fetchLookEvaluations, fetchWorkflow0Categories, fetchWorkflow0CollectionEvaluations } from '../services/api';
import { transformLooksToDesignCases, transformCollectionToThemeAnalysis } from '../services/dataTransformer';
import { BarChart3, TrendingUp, TrendingDown, RefreshCw, Download } from 'lucide-react';
import { motion } from 'framer-motion';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { 
  fadeInUp, 
  staggerContainer, 
  listItem,
  cardHover
} from '../utils/animations';
import * as XLSX from 'xlsx';

// 数字动画组件
function AnimatedNumber({ value, decimals = 0, delay = 0 }: { value: number; decimals?: number; delay?: number }) {
  const [displayValue, setDisplayValue] = useState(0);

  useEffect(() => {
    const duration = 1000;
    const steps = 60;
    const stepValue = value / steps;
    let current = 0;
    
    const timer = setTimeout(() => {
      const interval = setInterval(() => {
        current += stepValue;
        if (current >= value) {
          setDisplayValue(value);
          clearInterval(interval);
        } else {
          setDisplayValue(current);
        }
      }, duration / steps);
      
      return () => clearInterval(interval);
    }, delay);
    
    return () => clearTimeout(timer);
  }, [value, delay]);

  return <span>{decimals > 0 ? displayValue.toFixed(decimals) : Math.floor(displayValue)}</span>;
}

export function ScoreStatisticsPage() {
  const [designCases, setDesignCases] = useState<DesignCase[]>([]);
  const [themeAnalysis, setThemeAnalysis] = useState<ThemeAnalysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [categories, setCategories] = useState<string[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>('');

  const renderCategoryLabel = (c: string) => {
    return (
      <span className="block max-w-[320px] truncate" title={c}>
        {c}
      </span>
    );
  };
  
  // 初始化分类
  useEffect(() => {
    initCategories();
  }, []);

  // 分类变更时加载数据
  useEffect(() => {
    if (selectedCategory) {
      loadData(selectedCategory);
    }
  }, [selectedCategory]);

  const initCategories = async () => {
    try {
      const cats = await fetchWorkflow0Categories();
      setCategories(cats);
      const saved = localStorage.getItem('workflow0Category') || '';
      const initial = (saved && cats.includes(saved)) ? saved : (cats[0] || '');
      if (initial) {
        setSelectedCategory(initial);
        localStorage.setItem('workflow0Category', initial);
      } else {
        setError('No categories found under workflow_0 (non-date folders).');
        setLoading(false);
      }
    } catch (err) {
      setError('Failed to load categories. Please make sure the backend server is running.');
      setLoading(false);
    }
  };
  
  const loadData = async (category: string) => {
    try {
      setLoading(true);
      setError(null);
      
      // Load look evaluations
      const looks = await fetchLookEvaluations(category);
      const transformedLooks = transformLooksToDesignCases(looks);
      setDesignCases(transformedLooks);
      
      // Load collection evaluation
      const collections = await fetchWorkflow0CollectionEvaluations(category);
      if (collections.length > 0) {
        const transformedCollection = transformCollectionToThemeAnalysis(collections[0]);
        setThemeAnalysis(transformedCollection);
      } else {
        setThemeAnalysis(null);
      }
    } catch (err) {
      setError('Failed to load data. Please make sure the backend server is running.');
      console.error('Error loading data:', err);
    } finally {
      setLoading(false);
    }
  };
  
  // 导出Excel功能
  const exportToExcel = () => {
    // 计算平均分
    const averages = criteriaNames.map((criteriaName) => {
      const sum = designCases.reduce((acc, designCase) => {
        const score = designCase.scores.find((s) => s.criteria === criteriaName);
        return acc + (score?.score || 0);
      }, 0);
      return sum / designCases.length;
    });
    
    const totalAverage = designCases.reduce((acc, curr) => acc + curr.totalScore, 0) / designCases.length;
    
    // 准备表格数据
    const tableData = designCases.map((designCase) => {
      const row: any = {
        '设计案例': designCase.name,
        'ID': designCase.id,
      };
      
      // 添加各项评分
      criteriaNames.forEach((criteriaName) => {
        const score = designCase.scores.find((s) => s.criteria === criteriaName);
        row[criteriaName] = score?.score || 0;
      });
      
      row['总分'] = designCase.totalScore;
      
      return row;
    });
    
    // 添加平均分行
    const averageRow: any = {
      '设计案例': '平均分',
      'ID': '',
    };
    
    criteriaNames.forEach((criteriaName, index) => {
      averageRow[criteriaName] = parseFloat(averages[index].toFixed(1));
    });
    
    averageRow['总分'] = parseFloat(totalAverage.toFixed(1));
    
    tableData.push(averageRow);
    
    // 创建工作簿
    const wb = XLSX.utils.book_new();
    
    // 创建得分表工作表
    const ws = XLSX.utils.json_to_sheet(tableData);
    
    // 设置列宽
    const colWidths = [
      { wch: 20 }, // 设计案例
      { wch: 15 }, // ID
      ...criteriaNames.map(() => ({ wch: 18 })), // 各项评分
      { wch: 12 }, // 总分
    ];
    ws['!cols'] = colWidths;
    
    XLSX.utils.book_append_sheet(wb, ws, '得分统计');
    
    // 如果有主题分析数据，添加到第二个工作表
    if (themeAnalysis) {
      const themeData: any[] = [
        { '品牌': themeAnalysis.brand, '主题': themeAnalysis.themeTitle },
        {},
        { '类别': '评分标准', '评分': '得分', '得分值': '分数', '说明': '理由' },
      ];
      
      themeAnalysis.analysisCriteria.forEach((item) => {
        themeData.push({
          '类别': item.category,
          '评分': item.criteria,
          '得分值': item.score,
          '说明': item.justification,
        });
      });
      
      themeData.push({});
      themeData.push({ '类别': '整体评估', '评分': '', '得分值': '', '说明': '' });
      themeData.push({ '类别': '描述', '评分': '', '得分值': '', '说明': themeAnalysis.overallAssessment.description });
      
      themeData.push({});
      themeData.push({ '类别': '优势', '评分': '', '得分值': '', '说明': '' });
      themeAnalysis.overallAssessment.strengths.forEach((strength, index) => {
        themeData.push({ '类别': `${index + 1}`, '评分': '', '得分值': '', '说明': strength });
      });
      
      themeData.push({});
      themeData.push({ '类别': '劣势', '评分': '', '得分值': '', '说明': '' });
      themeAnalysis.overallAssessment.weaknesses.forEach((weakness, index) => {
        themeData.push({ '类别': `${index + 1}`, '评分': '', '得分值': '', '说明': weakness });
      });
      
      themeData.push({});
      themeData.push({ '类别': '整体质量', '评分': '', '得分值': '', '说明': themeAnalysis.overallAssessment.overallQuality });
      
      const ws2 = XLSX.utils.json_to_sheet(themeData);
      ws2['!cols'] = [{ wch: 15 }, { wch: 25 }, { wch: 10 }, { wch: 60 }];
      
      XLSX.utils.book_append_sheet(wb, ws2, '主题分析');
    }
    
    // 生成文件名（使用collection名称）
    let filename = '时尚评分数据.xlsx';
    
    if (themeAnalysis?.collectionName) {
      // 使用collection_name，如 "group_01_collection" -> "group_01"
      const collectionName = themeAnalysis.collectionName;
      // 移除 "_collection" 后缀
      const groupName = collectionName.replace(/_collection$/, '');
      filename = `${groupName}_评分数据.xlsx`;
    } else if (themeAnalysis?.themeTitle) {
      // 如果没有collectionName，使用主题名称
      const groupName = themeAnalysis.themeTitle.replace(/\s+/g, '_');
      filename = `${groupName}_评分数据.xlsx`;
    } else {
      // 如果都没有，使用时间戳
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
      filename = `时尚评分数据_${timestamp}.xlsx`;
    }
    
    // 导出文件
    XLSX.writeFile(wb, filename);
  };
  
  // Loading state
  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 text-center">
        <div className="flex items-center justify-center gap-2">
          <RefreshCw className="w-6 h-6 animate-spin text-gray-600" />
          <span className="text-gray-600">Loading statistics...</span>
        </div>
      </div>
    );
  }
  
  // Error state
  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
          <p className="text-red-800 mb-4">{error}</p>
          <button
            onClick={loadData}
            className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }
  
  // No data state
  if (designCases.length === 0) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 text-center">
        <p className="text-gray-600">No evaluations found. Please sync data from backend.</p>
      </div>
    );
  }
  
  // Calculate averages for each criterion
  const averages = criteriaNames.map((criteriaName) => {
    const sum = designCases.reduce((acc, designCase) => {
      const score = designCase.scores.find((s) => s.criteria === criteriaName);
      return acc + (score?.score || 0);
    }, 0);
    return sum / designCases.length;
  });

  const totalAverage = designCases.reduce((acc, curr) => acc + curr.totalScore, 0) / designCases.length;

  // Get color based on score
  const getScoreColor = (score: number) => {
    if (score >= 8) return 'text-green-700 bg-green-50';
    if (score >= 6) return 'text-blue-700 bg-blue-50';
    if (score >= 4) return 'text-yellow-700 bg-yellow-50';
    return 'text-red-700 bg-red-50';
  };

  const getAverageColor = (average: number) => {
    if (average >= 8) return 'text-green-700 bg-green-100 font-semibold';
    if (average >= 6) return 'text-blue-700 bg-blue-100 font-semibold';
    if (average >= 4) return 'text-yellow-700 bg-yellow-100 font-semibold';
    return 'text-red-700 bg-red-100 font-semibold';
  };

  return (
    <motion.div 
      initial="initial"
      animate="animate"
      variants={staggerContainer}
      className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8"
    >
      {/* Header */}
      <motion.div variants={fadeInUp} className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <motion.div
              initial={{ rotate: 0 }}
              animate={{ rotate: 360 }}
              transition={{ duration: 0.6, ease: "easeInOut" }}
            >
              <BarChart3 className="w-6 h-6 text-gray-900" />
            </motion.div>
            <h2 className="text-gray-900">Score Statistics</h2>
          </div>
          
          {/* 分类下拉栏 */}
          <div className="flex items-center gap-3">
            <div className="w-[260px]">
              <Select
                value={selectedCategory}
                onValueChange={(v) => {
                  setSelectedCategory(v);
                  localStorage.setItem('workflow0Category', v);
                }}
              >
                <SelectTrigger>
                  <SelectValue placeholder="选择分类（如 BA / DCV）" />
                </SelectTrigger>
                <SelectContent>
                  {categories.map((c) => (
                    <SelectItem key={c} value={c}>
                      {renderCategoryLabel(c)}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

          {/* 导出Excel按钮 */}
          <button
            onClick={exportToExcel}
            style={{
              padding: '12px 24px',
              backgroundColor: '#16a34a',
              color: 'white',
              borderRadius: '8px',
              border: 'none',
              fontSize: '16px',
              fontWeight: 'bold',
              cursor: 'pointer',
              boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}
            onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#15803d'}
            onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#16a34a'}
          >
            📥 导出Excel
          </button>
          </div>
        </div>
        <motion.p 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="text-gray-600"
        >
          Comprehensive evaluation scores for all design cases ({designCases.length} total)
        </motion.p>
      </motion.div>

      {/* Statistics Table */}
      <motion.div 
        variants={fadeInUp}
        whileHover={{ boxShadow: "0 10px 30px rgba(0, 0, 0, 0.1)" }}
        transition={{ duration: 0.3 }}
        className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden"
      >
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-200">
                <motion.th 
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="px-6 py-4 text-left text-sm font-semibold text-gray-900 sticky left-0 bg-gray-50 z-10"
                >
                  Design Case
                </motion.th>
                {criteriaNames.map((criteria, index) => (
                  <motion.th 
                    key={index}
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.05 }}
                    className="px-6 py-4 text-center text-sm font-semibold text-gray-900 min-w-[140px]"
                  >
                    {criteria}
                  </motion.th>
                ))}
                <motion.th 
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.3 }}
                  className="px-6 py-4 text-center text-sm font-semibold text-gray-900 bg-gray-100 min-w-[120px]"
                >
                  Total Score
                </motion.th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {designCases.map((designCase, rowIndex) => (
                <motion.tr 
                  key={designCase.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.1 + rowIndex * 0.05 }}
                  whileHover={{ 
                    backgroundColor: "rgb(249 250 251)",
                    scale: 1.005,
                    transition: { duration: 0.2 }
                  }}
                  className="transition-colors"
                >
                  <td className="px-6 py-4 text-sm font-medium text-gray-900 sticky left-0 bg-white z-10">
                    <div>
                      <div>{designCase.name}</div>
                      <div className="text-xs text-gray-500 mt-1">ID: {designCase.id}</div>
                    </div>
                  </td>
                  {criteriaNames.map((criteriaName, colIndex) => {
                    const score = designCase.scores.find((s) => s.criteria === criteriaName);
                    return (
                      <td key={colIndex} className="px-6 py-4 text-center">
                        <motion.span 
                          initial={{ scale: 0, opacity: 0 }}
                          animate={{ scale: 1, opacity: 1 }}
                          transition={{ 
                            delay: 0.2 + rowIndex * 0.05 + colIndex * 0.02,
                            type: "spring",
                            stiffness: 500,
                            damping: 25
                          }}
                          whileHover={{ scale: 1.15, rotate: 5 }}
                          className={`inline-flex items-center justify-center w-12 h-12 rounded-lg text-sm font-medium ${getScoreColor(score?.score || 0)}`}
                        >
                          {score?.score ?? '-'}
                        </motion.span>
                      </td>
                    );
                  })}
                  <td className="px-6 py-4 text-center bg-gray-50">
                    <motion.span 
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={{ 
                        delay: 0.3 + rowIndex * 0.05,
                        type: "spring",
                        stiffness: 500,
                        damping: 25
                      }}
                      className="inline-flex flex-col items-center justify-center px-4 py-2 rounded-lg font-semibold bg-gray-900 text-white"
                    >
                      <span className="text-lg">{designCase.totalScore}</span>
                      <span className="text-xs opacity-70 mt-1">/ 60</span>
                    </motion.span>
                  </td>
                </motion.tr>
              ))}
              
              {/* Average Row */}
              <motion.tr 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 + designCases.length * 0.05 }}
                className="bg-gray-100 border-t-2 border-gray-300"
              >
                <td className="px-6 py-4 text-sm font-semibold text-gray-900 sticky left-0 bg-gray-100 z-10">
                  Average Score
                </td>
                {averages.map((average, index) => (
                  <td key={index} className="px-6 py-4 text-center">
                    <motion.span 
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={{ 
                        delay: 0.6 + index * 0.05,
                        type: "spring",
                        stiffness: 500,
                        damping: 25
                      }}
                      whileHover={{ scale: 1.2, rotate: 10 }}
                      className={`inline-flex items-center justify-center w-12 h-12 rounded-lg text-sm ${getAverageColor(average)}`}
                    >
                      <AnimatedNumber value={average} decimals={1} delay={600 + index * 50} />
                    </motion.span>
                  </td>
                ))}
                <td className="px-6 py-4 text-center bg-gray-200">
                  <motion.span 
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ 
                      delay: 0.8,
                      type: "spring",
                      stiffness: 500,
                      damping: 25
                    }}
                    className="inline-flex flex-col items-center justify-center px-4 py-2 rounded-lg font-semibold bg-gray-900 text-white"
                  >
                    <span className="text-2xl">
                      <AnimatedNumber value={totalAverage} decimals={1} delay={800} />
                    </span>
                    <span className="text-xs opacity-70 mt-1">/ 60</span>
                  </motion.span>
                </td>
              </motion.tr>
            </tbody>
          </table>
        </div>
      </motion.div>

      {/* Summary Cards */}
      <motion.div 
        variants={staggerContainer}
        className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8"
      >
        <motion.div 
          variants={fadeInUp}
          whileHover={{ 
            scale: 1.05,
            boxShadow: "0 20px 40px rgba(34, 197, 94, 0.2)",
            transition: { duration: 0.2 }
          }}
          className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 relative overflow-hidden"
        >
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.5, type: "spring" }}
            className="absolute top-4 right-4"
          >
            <TrendingUp className="w-6 h-6 text-green-600 opacity-20" />
          </motion.div>
          <div className="text-sm text-gray-600 mb-1">Highest Scoring Criterion</div>
          <motion.div 
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.6 }}
            className="font-semibold text-gray-900"
          >
            {criteriaNames[averages.indexOf(Math.max(...averages))]}
          </motion.div>
          <motion.div 
            initial={{ opacity: 0, scale: 0 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.7, type: "spring", stiffness: 300 }}
            className="text-2xl font-semibold text-green-600 mt-2"
          >
            <AnimatedNumber value={Math.max(...averages)} decimals={1} delay={700} />
          </motion.div>
        </motion.div>

        <motion.div 
          variants={fadeInUp}
          whileHover={{ 
            scale: 1.05,
            boxShadow: "0 20px 40px rgba(239, 68, 68, 0.2)",
            transition: { duration: 0.2 }
          }}
          className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 relative overflow-hidden"
        >
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.6, type: "spring" }}
            className="absolute top-4 right-4"
          >
            <TrendingDown className="w-6 h-6 text-red-600 opacity-20" />
          </motion.div>
          <div className="text-sm text-gray-600 mb-1">Lowest Scoring Criterion</div>
          <motion.div 
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.7 }}
            className="font-semibold text-gray-900"
          >
            {criteriaNames[averages.indexOf(Math.min(...averages))]}
          </motion.div>
          <motion.div 
            initial={{ opacity: 0, scale: 0 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.8, type: "spring", stiffness: 300 }}
            className="text-2xl font-semibold text-red-600 mt-2"
          >
            <AnimatedNumber value={Math.min(...averages)} decimals={1} delay={800} />
          </motion.div>
        </motion.div>

        <motion.div 
          variants={fadeInUp}
          whileHover={{ 
            scale: 1.05,
            boxShadow: "0 20px 40px rgba(59, 130, 246, 0.2)",
            transition: { duration: 0.2 }
          }}
          className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 relative overflow-hidden"
        >
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.7, type: "spring" }}
            className="absolute top-4 right-4"
          >
            <BarChart3 className="w-6 h-6 text-blue-600 opacity-20" />
          </motion.div>
          <div className="text-sm text-gray-600 mb-1">Overall Average</div>
          <motion.div 
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.8 }}
            className="font-semibold text-gray-900"
          >
            All Cases
          </motion.div>
          <motion.div 
            initial={{ opacity: 0, scale: 0 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.9, type: "spring", stiffness: 300 }}
            className="text-2xl font-semibold text-blue-600 mt-2"
          >
            <AnimatedNumber value={totalAverage} decimals={1} delay={900} /> / 60
          </motion.div>
        </motion.div>
      </motion.div>

      {/* Theme Overall Analysis Section */}
      {themeAnalysis && (
        <motion.div 
          variants={fadeInUp}
          className="mt-12"
        >
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.0 }}
            className="mb-6"
          >
            <h2 className="text-gray-900">Theme Overall Analysis</h2>
            <motion.div 
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 1.1 }}
              className="mt-2 text-gray-600"
            >
              <span className="font-medium">{themeAnalysis.brand}</span> - "{themeAnalysis.themeTitle}" Collection
            </motion.div>
          </motion.div>

        {/* Analysis Criteria Table */}
        <motion.div 
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.2 }}
          whileHover={{ boxShadow: "0 10px 30px rgba(0, 0, 0, 0.1)" }}
          className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden mb-6"
        >
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="bg-gray-50 border-b border-gray-200">
                  <motion.th 
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 1.3 }}
                    className="px-6 py-4 text-left text-sm font-semibold text-gray-900 w-32"
                  >
                    Category
                  </motion.th>
                  <motion.th 
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 1.35 }}
                    className="px-6 py-4 text-left text-sm font-semibold text-gray-900 w-48"
                  >
                    Criteria
                  </motion.th>
                  <motion.th 
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 1.4 }}
                    className="px-6 py-4 text-center text-sm font-semibold text-gray-900 w-32"
                  >
                    Score (1-10)
                  </motion.th>
                  <motion.th 
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 1.45 }}
                    className="px-6 py-4 text-left text-sm font-semibold text-gray-900"
                  >
                    Justification
                  </motion.th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {themeAnalysis.analysisCriteria.map((item, index) => (
                  <motion.tr 
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 1.5 + index * 0.1 }}
                    whileHover={{ 
                      backgroundColor: "rgb(249 250 251)",
                      scale: 1.005 
                    }}
                    className="transition-colors"
                  >
                    <td className="px-6 py-4 text-sm font-semibold text-gray-900">
                      {item.category}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-700">
                      {item.criteria}
                    </td>
                    <td className="px-6 py-4 text-center">
                      <motion.span 
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        transition={{ 
                          delay: 1.6 + index * 0.1,
                          type: "spring",
                          stiffness: 500,
                          damping: 25
                        }}
                        whileHover={{ scale: 1.15, rotate: 5 }}
                        className={`inline-flex items-center justify-center w-12 h-12 rounded-lg text-sm font-medium ${getScoreColor(item.score)}`}
                      >
                        {item.score}
                      </motion.span>
                    </td>
                    <motion.td 
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ delay: 1.7 + index * 0.1 }}
                      className="px-6 py-4 text-sm text-gray-600 leading-relaxed"
                    >
                      {item.justification}
                    </motion.td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </div>
        </motion.div>

        {/* Overall Collection Assessment */}
        <motion.div 
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.8 }}
          whileHover={cardHover}
          className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden"
        >
          <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
            <h3 className="font-semibold text-gray-900">Overall Collection Assessment</h3>
          </div>
          <div className="p-6 space-y-6">
            {/* Description */}
            <motion.p 
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 1.9 }}
              className="text-sm text-gray-600 leading-relaxed"
            >
              {themeAnalysis.overallAssessment.description}
            </motion.p>

            {/* Strengths */}
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 2.0 }}
            >
              <h4 className="font-semibold text-gray-900 mb-3">Strengths:</h4>
              <motion.ul 
                variants={staggerContainer}
                initial="initial"
                animate="animate"
                className="space-y-2"
              >
                {themeAnalysis.overallAssessment.strengths.map((strength, index) => (
                  <motion.li 
                    key={index}
                    variants={listItem}
                    whileHover={{ x: 4 }}
                    className="flex items-start gap-2"
                  >
                    <motion.span 
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={{ delay: 2.1 + index * 0.05 }}
                      className="text-green-600 mt-1"
                    >
                      •
                    </motion.span>
                    <span className="text-sm text-gray-600 leading-relaxed flex-1">{strength}</span>
                  </motion.li>
                ))}
              </motion.ul>
            </motion.div>

            {/* Weaknesses */}
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 2.2 }}
            >
              <h4 className="font-semibold text-gray-900 mb-3">Weaknesses:</h4>
              <motion.ul 
                variants={staggerContainer}
                initial="initial"
                animate="animate"
                className="space-y-2"
              >
                {themeAnalysis.overallAssessment.weaknesses.map((weakness, index) => (
                  <motion.li 
                    key={index}
                    variants={listItem}
                    whileHover={{ x: 4 }}
                    className="flex items-start gap-2"
                  >
                    <motion.span 
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={{ delay: 2.3 + index * 0.05 }}
                      className="text-amber-600 mt-1"
                    >
                      •
                    </motion.span>
                    <span className="text-sm text-gray-600 leading-relaxed flex-1">{weakness}</span>
                  </motion.li>
                ))}
              </motion.ul>
            </motion.div>

            {/* Overall Quality */}
            <motion.div 
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 2.4 }}
              className="pt-4 border-t border-gray-200"
            >
              <h4 className="font-semibold text-gray-900 mb-3">Overall Quality:</h4>
              <p className="text-sm text-gray-600 leading-relaxed">
                {themeAnalysis.overallAssessment.overallQuality}
              </p>
            </motion.div>
          </div>
        </motion.div>
        </motion.div>
      )}
    </motion.div>
  );
}
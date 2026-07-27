import { useState, useEffect } from 'react';
import { ChevronLeft, ChevronRight, RefreshCw } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { DesignCase } from '../data/mockData';
import { fetchLookEvaluations, fetchWorkflow0Categories } from '../services/api';
import { transformLooksToDesignCases } from '../services/dataTransformer';
import { ImageWithFallback } from './figma/ImageWithFallback';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { 
  fadeInUp, 
  slideInRight, 
  slideInLeft, 
  staggerContainer, 
  listItem,
  numberAnimation,
  cardHover,
  buttonTap
} from '../utils/animations';

// 数字动画组件
function AnimatedNumber({ value, delay = 0 }: { value: number; delay?: number }) {
  const [displayValue, setDisplayValue] = useState(0);

  useEffect(() => {
    const duration = 1000; // 1秒
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
          setDisplayValue(Math.floor(current));
        }
      }, duration / steps);
      
      return () => clearInterval(interval);
    }, delay);
    
    return () => clearTimeout(timer);
  }, [value, delay]);

  return <span>{displayValue}</span>;
}

export function ImageDetailPage() {
  const [designCases, setDesignCases] = useState<DesignCase[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [direction, setDirection] = useState(0);
  const [categories, setCategories] = useState<string[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>('');

  const renderCategoryLabel = (c: string) => {
    // 长目录名在下拉列表里做省略，避免撑爆宽度；完整名称用 title 悬停查看
    return (
      <span className="block max-w-[320px] truncate" title={c}>
        {c}
      </span>
    );
  };
  
  // 初始化分类列表
  useEffect(() => {
    initCategories();
  }, []);

  // 分类变更时重新加载数据
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
      const looks = await fetchLookEvaluations(category);
      const transformed = transformLooksToDesignCases(looks);
      setDesignCases(transformed);
      setCurrentIndex(0);
    } catch (err) {
      setError('Failed to load data. Please make sure the backend server is running.');
      console.error('Error loading data:', err);
    } finally {
      setLoading(false);
    }
  };
  
  const currentCase = designCases[currentIndex];

  const goToPrevious = () => {
    setDirection(-1);
    setCurrentIndex((prev) => (prev > 0 ? prev - 1 : designCases.length - 1));
  };

  const goToNext = () => {
    setDirection(1);
    setCurrentIndex((prev) => (prev < designCases.length - 1 ? prev + 1 : 0));
  };

  const slideVariants = {
    enter: (direction: number) => ({
      x: direction > 0 ? 1000 : -1000,
      opacity: 0
    }),
    center: {
      x: 0,
      opacity: 1
    },
    exit: (direction: number) => ({
      x: direction < 0 ? 1000 : -1000,
      opacity: 0
    })
  };

  // Loading state
  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 text-center">
        <div className="flex items-center justify-center gap-2">
          <RefreshCw className="w-6 h-6 animate-spin text-gray-600" />
          <span className="text-gray-600">Loading evaluations...</span>
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
  
  return (
    <motion.div 
      initial="initial"
      animate="animate"
      className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8"
    >
      {/* Header with Navigation */}
      <motion.div 
        variants={fadeInUp}
        className="flex items-center justify-between mb-6"
      >
        <AnimatePresence mode="wait">
          <motion.div
            key={currentIndex}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
          >
            <h2 className="text-gray-900">{currentCase.name}</h2>
            <p className="text-sm text-gray-500 mt-1">
              Case {currentIndex + 1} of {designCases.length}
            </p>
          </motion.div>
        </AnimatePresence>
        <div className="flex items-center gap-3">
          {/* 分类下拉栏 */}
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

          <motion.button
            onClick={goToPrevious}
            whileHover={{ scale: 1.1, backgroundColor: "rgb(249 250 251)" }}
            whileTap={{ scale: 0.9 }}
            className="p-2 rounded-lg border border-gray-300 transition-colors"
            aria-label="Previous case"
          >
            <ChevronLeft className="w-5 h-5 text-gray-600" />
          </motion.button>
          <motion.button
            onClick={goToNext}
            whileHover={{ scale: 1.1, backgroundColor: "rgb(249 250 251)" }}
            whileTap={{ scale: 0.9 }}
            className="p-2 rounded-lg border border-gray-300 transition-colors"
            aria-label="Next case"
          >
            <ChevronRight className="w-5 h-5 text-gray-600" />
          </motion.button>
        </div>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Image Section */}
        <AnimatePresence mode="wait" custom={direction}>
          <motion.div
            key={currentIndex}
            custom={direction}
            variants={slideVariants}
            initial="enter"
            animate="center"
            exit="exit"
            transition={{
              x: { type: "spring", stiffness: 300, damping: 30 },
              opacity: { duration: 0.2 }
            }}
            className="bg-white rounded-lg shadow-sm border border-gray-200 p-6"
          >
            <motion.div 
              whileHover={{ scale: 1.02 }}
              transition={{ type: "spring", stiffness: 300, damping: 20 }}
              className="aspect-[3/4] bg-gray-100 rounded-lg overflow-hidden"
            >
              <ImageWithFallback
                src={currentCase.imagePath}
                alt={currentCase.name}
                className="w-full h-full object-cover"
              />
            </motion.div>
          </motion.div>
        </AnimatePresence>

        {/* Details Section */}
        <motion.div 
          variants={staggerContainer}
          initial="initial"
          animate="animate"
          className="space-y-6"
        >
          {/* Total Score */}
          <AnimatePresence mode="wait">
            <motion.div
              key={`score-${currentIndex}`}
              variants={fadeInUp}
              initial="initial"
              animate="animate"
              exit="exit"
              whileHover={cardHover}
              className="bg-white rounded-lg shadow-sm border border-gray-200 p-6"
            >
              <div className="flex items-baseline gap-2">
                <span className="text-gray-700">Total Score:</span>
                <motion.span 
                  key={currentCase.totalScore}
                  variants={numberAnimation}
                  initial="initial"
                  animate="animate"
                  className="text-3xl font-semibold text-gray-900"
                >
                  <AnimatedNumber value={currentCase.totalScore} />
                </motion.span>
                <span className="text-gray-500">/ 60</span>
              </div>
            </motion.div>
          </AnimatePresence>

          {/* Criteria Table */}
          <AnimatePresence mode="wait">
            <motion.div
              key={`criteria-${currentIndex}`}
              variants={fadeInUp}
              initial="initial"
              animate="animate"
              exit="exit"
              transition={{ delay: 0.1 }}
              whileHover={cardHover}
              className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden"
            >
              <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
                <h3 className="font-semibold text-gray-900">Criteria</h3>
              </div>
              <motion.div 
                variants={staggerContainer}
                className="divide-y divide-gray-200"
              >
                {currentCase.scores.map((item, index) => (
                  <motion.div 
                    key={index}
                    variants={listItem}
                    transition={{ delay: index * 0.05 }}
                    whileHover={{ backgroundColor: "rgb(249 250 251)", x: 4 }}
                    className="p-6 transition-colors"
                  >
                    <div className="flex items-start justify-between mb-3">
                      <h4 className="font-medium text-gray-900">{item.criteria}</h4>
                      <div className="flex items-center gap-2 ml-4">
                        <motion.span 
                          initial={{ scale: 0 }}
                          animate={{ scale: 1 }}
                          transition={{ 
                            delay: 0.2 + index * 0.05,
                            type: "spring",
                            stiffness: 500,
                            damping: 25
                          }}
                          className="px-3 py-1 bg-gray-900 text-white rounded-full text-sm font-medium"
                        >
                          {item.score}
                        </motion.span>
                        <span className="text-sm text-gray-500">/ 10</span>
                      </div>
                    </div>
                    <motion.p 
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ delay: 0.3 + index * 0.05 }}
                      className="text-sm text-gray-600 leading-relaxed"
                    >
                      {item.justification}
                    </motion.p>
                  </motion.div>
                ))}
              </motion.div>
            </motion.div>
          </AnimatePresence>

          {/* Overall Assessment */}
          <AnimatePresence mode="wait">
            <motion.div
              key={`assessment-${currentIndex}`}
              variants={fadeInUp}
              initial="initial"
              animate="animate"
              exit="exit"
              transition={{ delay: 0.2 }}
              whileHover={cardHover}
              className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden"
            >
              <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
                <h3 className="font-semibold text-gray-900">Overall Assessment</h3>
              </div>
              <div className="p-6 space-y-6">
                {/* Strengths */}
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3 }}
                >
                  <h4 className="font-medium text-gray-900 mb-3">Strengths:</h4>
                  <motion.ul 
                    variants={staggerContainer}
                    initial="initial"
                    animate="animate"
                    className="space-y-2"
                  >
                    {currentCase.strengths.map((strength, index) => (
                      <motion.li 
                        key={index}
                        variants={listItem}
                        whileHover={{ x: 4 }}
                        className="flex items-start gap-2"
                      >
                        <motion.span 
                          initial={{ scale: 0 }}
                          animate={{ scale: 1 }}
                          transition={{ delay: 0.4 + index * 0.05 }}
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
                  transition={{ delay: 0.4 }}
                >
                  <h4 className="font-medium text-gray-900 mb-3">Weaknesses:</h4>
                  <motion.ul 
                    variants={staggerContainer}
                    initial="initial"
                    animate="animate"
                    className="space-y-2"
                  >
                    {currentCase.weaknesses.map((weakness, index) => (
                      <motion.li 
                        key={index}
                        variants={listItem}
                        whileHover={{ x: 4 }}
                        className="flex items-start gap-2"
                      >
                        <motion.span 
                          initial={{ scale: 0 }}
                          animate={{ scale: 1 }}
                          transition={{ delay: 0.5 + index * 0.05 }}
                          className="text-red-600 mt-1"
                        >
                          •
                        </motion.span>
                        <span className="text-sm text-gray-600 leading-relaxed flex-1">{weakness}</span>
                      </motion.li>
                    ))}
                  </motion.ul>
                </motion.div>

                {/* Improvement Suggestions */}
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.5 }}
                >
                  <h4 className="font-medium text-gray-900 mb-3">Improvement Suggestions:</h4>
                  <motion.ul 
                    variants={staggerContainer}
                    initial="initial"
                    animate="animate"
                    className="space-y-2"
                  >
                    {currentCase.improvements.map((improvement, index) => (
                      <motion.li 
                        key={index}
                        variants={listItem}
                        whileHover={{ x: 4 }}
                        className="flex items-start gap-2"
                      >
                        <motion.span 
                          initial={{ scale: 0 }}
                          animate={{ scale: 1 }}
                          transition={{ delay: 0.6 + index * 0.05 }}
                          className="text-blue-600 mt-1"
                        >
                          •
                        </motion.span>
                        <span className="text-sm text-gray-600 leading-relaxed flex-1">{improvement}</span>
                      </motion.li>
                    ))}
                  </motion.ul>
                </motion.div>
              </div>
            </motion.div>
          </AnimatePresence>
        </motion.div>
      </div>
    </motion.div>
  );
}

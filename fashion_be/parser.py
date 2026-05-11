"""
评估文档解析器
解析 evaluation txt 文件并提取结构化数据
"""
import re
from pathlib import Path
from typing import Dict, Optional, List


def natural_sort_key(path):
    """
    自然排序键函数，用于按数字顺序排序文件名
    例如: look_1, look_2, ..., look_10, look_11
    """
    import re
    parts = re.split(r'(\d+)', str(path.stem))
    return [int(part) if part.isdigit() else part for part in parts]


class EvaluationParser:
    """评估文档解析器"""
    
    def __init__(self, config_path: str = "../fashion_config.yaml"):
        """初始化解析器"""
        self.brand = None
        self.theme = None
        self._load_config(config_path)
    
    def _load_config(self, config_path: str):
        """从配置文件加载 brand 和 theme"""
        import yaml
        
        config_file = Path(config_path)
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                self.brand = config.get('brand', 'Unknown')
                self.theme = config.get('theme', 'Unknown')
        else:
            print(f"警告: 配置文件 {config_path} 不存在，使用默认值")
            self.brand = "Unknown"
            self.theme = "Unknown"
    
    def parse_evaluation_file(self, file_path: str) -> Optional[Dict]:
        """
        解析单个评估文件
        
        Args:
            file_path: 评估文件路径
            
        Returns:
            包含所有字段的字典，如果解析失败返回None
        """
        file_path = Path(file_path)
        if not file_path.exists():
            print(f"文件不存在: {file_path}")
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取 look 名称（从文件名）
            look_name = file_path.stem.replace('_evaluation', '')
            
            # 优先从文件内容中提取 Brand 和 Theme
            brand, theme = self._extract_brand_theme(content)
            
            # 如果文件中没有，则使用配置文件的值
            if not brand:
                brand = self.brand
            if not theme:
                theme = self.theme
            
            # 解析 Criteria 表格
            criteria = self._parse_criteria_table(content)
            
            # 解析 Overall Assessment
            assessment = self._parse_overall_assessment(content)
            
            # 构建图片路径
            image_path = self._find_look_image_path(file_path.parent, look_name)
            
            # 检查图片是否存在
            if not image_path or not Path(image_path).exists():
                print(f"警告: 图片文件不存在: {file_path.parent} / {look_name}.[png|jpg|jpeg]")
            
            # 组合所有数据
            result = {
                'look_name': look_name,
                'brand': brand,
                'theme': theme,
                'image_path': image_path or str(file_path.parent / f"{look_name}.png"),
                **criteria,
                **assessment
            }
            
            return result
            
        except Exception as e:
            print(f"解析文件 {file_path} 时出错: {e}")
            return None

    @staticmethod
    def _find_look_image_path(parent_dir: Path, look_name: str) -> Optional[str]:
        """
        为 look_x 寻找对应图片文件，按优先级匹配：
        - .png
        - .jpg
        - .jpeg
        """
        for ext in [".png", ".jpg", ".jpeg"]:
            candidate = parent_dir / f"{look_name}{ext}"
            if candidate.exists():
                return str(candidate)
        return None
    
    def _extract_brand_theme(self, content: str) -> tuple:
        """
        从文件内容中提取 Brand 和 Theme 信息
        
        Args:
            content: 文件内容
            
        Returns:
            (brand, theme) 元组，如果未找到则返回 (None, None)
        """
        brand = None
        theme = None
        
        # 匹配 **Brand:** 格式
        brand_match = re.search(r'\*\*Brand:\*\*\s*(.+)', content, re.IGNORECASE)
        if brand_match:
            brand = brand_match.group(1).strip()
        
        # 匹配 **Theme:** 格式
        theme_match = re.search(r'\*\*Theme:\*\*\s*(.+)', content, re.IGNORECASE)
        if theme_match:
            theme = theme_match.group(1).strip()
        
        return brand, theme
    
    def _parse_criteria_table(self, content: str) -> Dict:
        """解析 Criteria 评分表格（兼容加粗/不加粗、多种 Markdown 表格格式）"""
        criteria_map = {
            'Theme Relevance': ('theme_relevance', 'theme_relevance_score', 'theme_relevance_justification'),
            'Brand DNA Alignment': ('brand_dna', 'brand_dna_score', 'brand_dna_justification'),
            'Innovation & Originality': ('innovation', 'innovation_score', 'innovation_justification'),
            'Aesthetics & Visual Impact': ('aesthetics', 'aesthetics_score', 'aesthetics_justification'),
            'Structural Logic & Material Expression': ('structural_logic', 'structural_logic_score', 'structural_logic_justification'),
            'Anticipated Functionality': ('functionality', 'functionality_score', 'functionality_justification'),
        }
        
        result = {}

        # 优先用“按行拆表格”的方式解析，兼容：
        # | Criteria | Score (1-10) | Justification |
        # | :--- | :---: | :--- |
        # | Theme Relevance | 6 | ... |
        for line in content.splitlines():
            line = line.strip()
            if not line.startswith("|"):
                continue
            if ":---" in line:
                continue
            # 去掉首尾 |
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) < 3:
                continue

            raw_criteria = cells[0].replace("**", "").strip()
            raw_score = cells[1].replace("**", "").strip()
            justification = cells[2].strip()

            # 跳过表头
            if raw_criteria.lower() in ["criteria", "category"]:
                continue
            if raw_criteria not in criteria_map:
                continue
            try:
                score = float(raw_score)
            except Exception:
                continue

            _, score_key, justification_key = criteria_map[raw_criteria]
            result[score_key] = score
            result[justification_key] = justification

        # 兜底：兼容旧格式（加粗的 criteria）
        if not result:
            pattern = r'\|\s*\*\*([^*]+)\*\*\s*\|\s*(\d+(?:\.\d+)?)\s*\|\s*(.+?)\s*\|'
            matches = re.finditer(pattern, content, re.MULTILINE)
            for match in matches:
                criteria_name = match.group(1).strip()
                score = float(match.group(2))
                justification = match.group(3).strip()
                if criteria_name in criteria_map:
                    _, score_key, justification_key = criteria_map[criteria_name]
                    result[score_key] = score
                    result[justification_key] = justification

        return result
    
    def _parse_overall_assessment(self, content: str) -> Dict:
        """解析 Overall Assessment 部分 - 按文字关键词匹配，忽略符号"""
        result = {
            'strengths': '',
            'weaknesses': '',
            'improvement_suggestions': ''
        }
        
        # 查找 Overall Assessment 部分（不限格式）
        # 兼容：
        # - ### Overall Assessment
        # - **Overall Assessment**
        # - **Overall Assessment:**
        assessment_match = re.search(
            r'(?is)(?:^|\n)\s*(?:###\s*)?\*{0,2}\s*Overall\s+Assessment\s*\*{0,2}\s*:?\s*\n(.*)$',
            content,
        )
        
        if not assessment_match:
            return result
        
        assessment_content = assessment_match.group(1)

        # 用“标题定位 + 切片”的方式解析，兼容：
        # - **Strengths:** / **Strengths**
        # - *   **Strengths**（前面可能有 bullet）
        # - Improvement Suggestion(s)
        # 兼容标题中的冒号在加粗内部/外部：
        # - **Strengths:** / **Strengths**:
        # - * **Strengths:**（带 bullet）
        heading_pattern = re.compile(
            r'(?im)^\s*[*\-]?\s*\*{0,2}\s*(Strengths|Weaknesses|Improvement\s+Suggestion(?:s)?)\s*:?\s*\*{0,2}\s*:?\s*$'
        )
        matches = list(heading_pattern.finditer(assessment_content))
        if not matches:
            # 没有结构化标题就把整体当 strengths（保底）
            result['strengths'] = assessment_content.strip()
            return result

        sections = []
        for m in matches:
            key = m.group(1).strip().lower()
            sections.append((key, m.start(), m.end()))
        sections.sort(key=lambda x: x[1])

        def slice_section(i: int) -> str:
            start = sections[i][2]
            end = sections[i + 1][1] if i + 1 < len(sections) else len(assessment_content)
            return assessment_content[start:end].strip()

        for i, (key, _s, _e) in enumerate(sections):
            body = slice_section(i)
            if key.startswith("strength"):
                result["strengths"] = body
            elif key.startswith("weak"):
                result["weaknesses"] = body
            elif key.startswith("improvement"):
                result["improvement_suggestions"] = body
        
        return result
    
    def parse_directory(self, directory_path: str) -> List[Dict]:
        """
        解析目录下所有的评估文件
        
        Args:
            directory_path: 目录路径
            
        Returns:
            包含所有解析结果的列表
        """
        directory = Path(directory_path)
        if not directory.exists() or not directory.is_dir():
            print(f"目录不存在: {directory_path}")
            return []
        
        results = []
        
        # 查找所有 _evaluation.txt 文件，使用自然排序（按数字大小）
        evaluation_files = sorted(directory.glob('*_evaluation.txt'), key=natural_sort_key)
        
        for file_path in evaluation_files:
            parsed_data = self.parse_evaluation_file(str(file_path))
            if parsed_data:
                results.append(parsed_data)
        
        print(f"成功解析 {len(results)} 个评估文件")
        return results
    
    def parse_collection_evaluation_file(self, file_path: str) -> Optional[Dict]:
        """
        解析 collection 总评文件
        
        Args:
            file_path: 评估文件路径
            
        Returns:
            包含所有字段的字典，如果解析失败返回None
        """
        file_path = Path(file_path)
        if not file_path.exists():
            print(f"文件不存在: {file_path}")
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取 collection 名称（从文件名）
            collection_name = file_path.stem.replace('_evaluation', '')
            
            # 优先从文件内容中提取 Brand 和 Theme
            brand, theme = self._extract_brand_theme(content)
            
            # 如果文件中没有，则使用配置文件的值
            if not brand:
                brand = self.brand
            if not theme:
                theme = self.theme
            
            # 解析 Collection Criteria 表格
            criteria = self._parse_collection_criteria_table(content)
            
            # 解析 Overall Collection Assessment
            assessment = self._parse_collection_overall_assessment(content)
            
            # 组合所有数据
            result = {
                'collection_name': collection_name,
                'brand': brand,
                'theme': theme,
                **criteria,
                **assessment
            }
            
            return result
            
        except Exception as e:
            print(f"解析文件 {file_path} 时出错: {e}")
            return None
    
    def _parse_collection_criteria_table(self, content: str) -> Dict:
        """解析 Collection Criteria 评分表格（兼容多种 Markdown 表格格式）"""
        criteria_map = {
            'Narrative Cohesion': ('narrative_cohesion', 'narrative_cohesion_score', 'narrative_cohesion_justification'),
            'Visual Unity': ('visual_unity', 'visual_unity_score', 'visual_unity_justification'),
            'Range Balance': ('range_balance', 'range_balance_score', 'range_balance_justification'),
            'Rhythm & Flow': ('rhythm_flow', 'rhythm_flow_score', 'rhythm_flow_justification'),
        }
        
        result = {}

        # 兼容：
        # | Category | Criteria | Score (1-10) | Justification |
        # | Cohesion | Narrative Cohesion | 8 | ... |
        for line in content.splitlines():
            line = line.strip()
            if not line.startswith("|"):
                continue
            if ":---" in line:
                continue
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) < 4:
                continue
            criteria_name = cells[1].replace("**", "").strip()
            raw_score = cells[2].replace("**", "").strip()
            justification = cells[3].strip()

            # 跳过表头
            if criteria_name.lower() in ["criteria", "score (1-10)", "justification", "category"]:
                continue
            if criteria_name not in criteria_map:
                continue
            try:
                score = float(raw_score)
            except Exception:
                continue

            _, score_key, justification_key = criteria_map[criteria_name]
            result[score_key] = score
            result[justification_key] = justification

        # 兜底：旧的正则格式
        if not result:
            pattern = r'\|\s*\*\*[^*]+\*\*\s*\|\s*([^|]+?)\s*\|\s*(\d+(?:\.\d+)?)\s*\|\s*(.+?)\s*\|'
            matches = re.finditer(pattern, content, re.MULTILINE)
            for match in matches:
                criteria_name = match.group(1).strip()
                score = float(match.group(2))
                justification = match.group(3).strip()
                if criteria_name in criteria_map:
                    _, score_key, justification_key = criteria_map[criteria_name]
                    result[score_key] = score
                    result[justification_key] = justification

        return result
    
    def _parse_collection_overall_assessment(self, content: str) -> Dict:
        """解析 Collection Overall Assessment 部分"""
        result = {
            'overall_assessment': '',
            'strengths': '',
            'weaknesses': '',
            'overall_quality': ''
        }
        
        # 查找 Overall Collection Assessment 部分
        assessment_match = re.search(r'###\s*Overall Collection Assessment\s*\n(.*?)(?=\*\*Strengths:\*\*|\*\*Weaknesses:\*\*|\*\*Overall Quality:\*\*|$)', content, re.DOTALL)
        if assessment_match:
            result['overall_assessment'] = assessment_match.group(1).strip()
        
        # 提取 Strengths - 支持段落文本或列表格式
        strengths_match = re.search(r'\*\*Strengths:\*\*\s*\n(.*?)(?=\n\*\*|\Z)', content, re.DOTALL)
        if strengths_match:
            result['strengths'] = strengths_match.group(1).strip()
        
        # 提取 Weaknesses - 支持段落文本或列表格式
        weaknesses_match = re.search(r'\*\*Weaknesses:\*\*\s*\n(.*?)(?=\n\*\*|\Z)', content, re.DOTALL)
        if weaknesses_match:
            result['weaknesses'] = weaknesses_match.group(1).strip()
        
        # 提取 Overall Quality - 支持段落文本
        quality_match = re.search(r'\*\*Overall Quality:\*\*\s*\n(.+?)(?=\n\n|\n###|\Z)', content, re.DOTALL)
        if quality_match:
            result['overall_quality'] = quality_match.group(1).strip()
        
        return result
    
    def parse_directory_with_collections(self, directory_path: str) -> tuple:
        """
        解析目录下所有的评估文件，区分 look 和 collection
        
        Args:
            directory_path: 目录路径
            
        Returns:
            (look_results, collection_results) 元组
        """
        directory = Path(directory_path)
        if not directory.exists() or not directory.is_dir():
            print(f"目录不存在: {directory_path}")
            return [], []
        
        look_results = []
        collection_results = []
        
        # 查找所有 _evaluation.txt 文件，使用自然排序（按数字大小）
        evaluation_files = sorted(directory.glob('*_evaluation.txt'), key=natural_sort_key)
        
        for file_path in evaluation_files:
            file_name = file_path.stem
            
            # 区分 collection 和 look 评估
            if 'collection' in file_name.lower():
                # 解析 collection 评估
                parsed_data = self.parse_collection_evaluation_file(str(file_path))
                if parsed_data:
                    collection_results.append(parsed_data)
            else:
                # 解析 look 评估
                parsed_data = self.parse_evaluation_file(str(file_path))
                if parsed_data:
                    look_results.append(parsed_data)
        
        print(f"成功解析 {len(look_results)} 个 Look 评估文件")
        print(f"成功解析 {len(collection_results)} 个 Collection 评估文件")
        
        return look_results, collection_results

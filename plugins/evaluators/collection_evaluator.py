"""
时尚系列评估 Agent
用于评估整个系列（collection）的作品，根据连贯性和组成维度进行评分
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from utils import *
from inference import *
from fashion import BaseAgent
import base64
import mimetypes
import os
import re
import time
import openai
import httpx
from PIL import Image
import fitz  # PyMuPDF


class CollectionEvaluationAgent(BaseAgent):
    """
    系列评估 Agent: 负责评估整个 collection 的作品
    任务：根据评估准则对给定的时尚系列进行多维度评估
    输入：group PDF 文件（包含系列中所有 look）
    输出：评估结果表格（包含4个维度的评分）
    """
    def __init__(self, model="gpt-4o-mini", notes=None, max_steps=100, openai_api_key=None):
        super().__init__(model, notes, max_steps, openai_api_key)
        self.phases = ["collection evaluation"]
        self.brand = str()
        self.theme = str()
        self.number_of_looks = 0
        self.pdf_path = str()
        self.evaluation_result = str()
        # 控制输入体积，避免一次性发送超大多图导致网关/代理断连
        self.max_pages = 25
        self.render_dpi = 150
        self.max_image_edge = 1024

    def context(self, phase):
        """
        构建上下文信息
        """
        if phase == "collection evaluation":
            context_parts = []

            # [Input information] - PDF with collection
            context_parts.append(
                f"[ Input information ] The pdf contains a series of {self.number_of_looks if self.number_of_looks > 0 else '<number_of_look>'} "
                f"fashion design works created for the {self.brand if self.brand else '<brand>'} brand "
                f"under the theme of {self.theme if self.theme else '<theme>'}. "
                "Figure 1 is the evaluation criteria to score a fashion collection work.\n\n"
            )

            # Evaluation criteria
            context_parts.append("**Figure 1: Collection Evaluation Criteria**\n")
            context_parts.append(self._get_evaluation_criteria_table())

            return "".join(context_parts)
        return ""

    def _get_evaluation_criteria_table(self):
        """
        返回系列评估准则表格
        """
        return (
            "Collection-Level Evaluation\n\n"
            "|  |  | 1-3 | 4-6 | 7-8 | 9-10 |\n"
            "|----------|----------|-----|-----|-----|------|\n"
            "| **Cohesion** | Narrative Cohesion | No clear theme | Vague theme | Clear story | Compelling universe |\n"
            "|  | Visual Unity | Chaotic | Inconsistent | Harmonious | Seamless Unity |\n"
            "| **Composition** | Range Balance | One-note | Imbalanced | Good variety | Perfect architecture |\n"
            "|  | Rhythm & Flow | Monotonous | Static | Dynamic flow | Masterful pacing |\n\n"
            "**Detailed Criteria Explanations:**\n\n"
            "1. **Cohesion - Narrative Cohesion** - 叙事连贯性\n"
            "   - Evaluate how well the collection tells a coherent story or conveys a unified concept\n"
            "   - Look for: thematic consistency, conceptual thread, narrative arc across looks\n"
            "   - Visual cues: recurring motifs, evolving theme interpretation, story progression\n"
            "   - 1-3: No discernible theme connecting the looks, collection feels random\n"
            "   - 4-6: Theme exists but weakly expressed, unclear narrative direction\n"
            "   - 7-8: Clear storyline with logical progression, theme is evident\n"
            "   - 9-10: Compelling narrative universe that captivates, masterful storytelling\n\n"
            "2. **Cohesion - Visual Unity** - 视觉统一性\n"
            "   - Assess the visual consistency and harmony across all looks in the collection\n"
            "   - Look for: color palette coherence, silhouette family, material consistency, design language\n"
            "   - Visual cues: repeated design elements, consistent aesthetic, unified mood\n"
            "   - 1-3: Visually chaotic, looks seem from different collections entirely\n"
            "   - 4-6: Some connection but inconsistent, lacks strong visual thread\n"
            "   - 7-8: Harmonious visual relationships, clearly from same collection\n"
            "   - 9-10: Seamlessly unified, every look feels essential to the whole\n\n"
            "3. **Composition - Range Balance** - 范围平衡\n"
            "   - Evaluate the diversity and balance of design offerings within the collection\n"
            "   - Look for: variety in silhouettes, occasion diversity, styling range, garment types\n"
            "   - Visual cues: mix of statement/basic pieces, day/evening options, proportional variety\n"
            "   - 1-3: One-note, extremely repetitive, lacks diversity\n"
            "   - 4-6: Imbalanced, too focused on one type or missing key pieces\n"
            "   - 7-8: Good variety with balanced offerings, well-rounded collection\n"
            "   - 9-10: Perfect architectural balance, every piece has its place and purpose\n\n"
            "4. **Composition - Rhythm & Flow** - 节奏与流动\n"
            "   - Assess the pacing and sequencing dynamics of the collection\n"
            "   - Look for: visual crescendos, transitions between looks, energy progression\n"
            "   - Visual cues: build-up of impact, strategic placement of key looks, overall flow\n"
            "   - 1-3: Monotonous, flat energy throughout, no dynamic progression\n"
            "   - 4-6: Static, lacks engaging pacing or interesting sequence\n"
            "   - 7-8: Dynamic flow with clear rhythm, engaging progression\n"
            "   - 9-10: Masterful pacing like a symphony, perfectly orchestrated journey\n\n"
        )

    def phase_prompt(self, phase):
        """
        定义阶段提示
        """
        if phase not in self.phases:
            raise Exception(f"Invalid phase: {phase}")
        
        if phase == "collection evaluation":
            phase_str = (
                "[ Role Definition ] Now, assume you are a top fashion designer.\n\n"
                "[ Task Information ] Please evaluate the given fashion collection in accordance with the given evaluation criteria.\n\n"
                "[ Evaluation Guidelines ]\n"
                "- Evaluate the ENTIRE collection as a whole, not individual looks\n"
                "- Consider how all looks work together to create a cohesive collection\n"
                "- Use the Collection-Level Evaluation rubric for scoring\n"
                "- Each score range (1-3, 4-6, 7-8, 9-10) has specific qualitative descriptors\n"
                "- Evaluate each criterion independently based on the rubric descriptors\n"
                "- Provide specific, concrete justifications that reference the rubric descriptors\n\n"
                "[ Output information ] You need to present the scoring results of the pdf in the form of a table.\n"
            )
        return phase_str

    def role_description(self):
        return "a top fashion designer."

    def command_descriptions(self, phase):
        """
        定义可用命令
        """
        if phase not in self.phases:
            raise Exception(f"Invalid phase: {phase}")
        
        if phase == "collection evaluation":
            return (
                "**Available Commands:**\n\n"
                "1. ```DIALOGUE\n[your thoughts or analysis here]\n```\n\n"
                "2. ```COLLECTION_EVALUATION_RESULT\n[evaluation table and assessment]\n```\n\n"
                "**Output Format Requirements:**\n"
                "- Create a table with columns: Category | Criteria | Score (1-10) | Justification\n"
                "- Include all 4 evaluation criteria (2 under Cohesion, 2 under Composition)\n"
                "- Reference the rubric level in each justification\n"
                "- Add an 'Overall Collection Assessment' section summarizing the collection's strengths, weaknesses, and overall quality\n\n"
                "**Scoring Guidelines:**\n"
                "- Evaluate the collection as a WHOLE, not individual looks\n"
                "- Match collection to rubric descriptors, then score within the corresponding range\n"
                "- Use full scoring range (1-10) based on actual collection quality\n"
                "- Explicitly reference rubric level in justification\n\n"
                "Use ONE command per turn. Include ``` markers: ```COMMAND\ncontent\n```\n"
            )
        return ""

    def example_command(self, phase):
        if phase not in self.phases:
            raise Exception(f"Invalid phase: {phase}")
        return (
            "**Example Format:**\n\n"
            "```COLLECTION_EVALUATION_RESULT\n"
            "**Collection Evaluation Results**\n\n"
            "| Category | Criteria | Score (1-10) | Justification |\n"
            "|----------|----------|-------------|----------------|\n"
            "| Cohesion | Narrative Cohesion | [score] | [Rubric level] - [Specific reasoning about story/theme] |\n"
            "| Cohesion | Visual Unity | [score] | [Rubric level] - [Specific reasoning about visual consistency] |\n"
            "| Composition | Range Balance | [score] | [Rubric level] - [Specific reasoning about variety] |\n"
            "| Composition | Rhythm & Flow | [score] | [Rubric level] - [Specific reasoning about pacing] |\n\n"
            "**Overall Collection Assessment:**\n"
            "Strengths: [Reference rubric levels achieved]\n"
            "Weaknesses: [Reference rubric gaps]\n"
            "Collection Quality: [Overall summary and how collection could improve]\n"
            "```\n"
        )

    def _pdf_to_images(self, pdf_path):
        """
        将 PDF 转换为图片列表
        
        Args:
            pdf_path: PDF 文件路径
        
        Returns:
            images: PIL Image 对象列表
        """
        images = []
        try:
            doc = fitz.open(pdf_path)
            page_count = len(doc)
            page_limit = min(page_count, self.max_pages) if self.max_pages and self.max_pages > 0 else page_count
            for page_num in range(page_limit):
                page = doc[page_num]
                # 将页面转换为图片（降低 DPI，减少请求体）
                scale = (self.render_dpi / 72) if self.render_dpi else (150 / 72)
                pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
                # 转换为 PIL Image
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                # 下采样到 max_image_edge，进一步减少体积
                max_edge = self.max_image_edge or 1024
                if max(img.size) > max_edge:
                    ratio = max_edge / float(max(img.size))
                    new_size = (max(1, int(img.size[0] * ratio)), max(1, int(img.size[1] * ratio)))
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                images.append(img)
            doc.close()
            return images
        except Exception as e:
            print(f"错误：无法读取 PDF 文件 {pdf_path}: {e}")
            return []

    def _images_to_data_urls(self, images):
        """
        将 PIL Image 列表转换为 data URL 列表
        
        Args:
            images: PIL Image 对象列表
        
        Returns:
            data_urls: data URL 字符串列表
        """
        data_urls = []
        for idx, img in enumerate(images):
            try:
                import io
                buffer = io.BytesIO()
                # 用 JPEG 压缩，避免 PNG 体积过大导致断连
                img.save(buffer, format="JPEG", quality=80, optimize=True, progressive=True)
                img_bytes = buffer.getvalue()
                img_b64 = base64.b64encode(img_bytes).decode('utf-8')
                data_url = f"data:image/jpeg;base64,{img_b64}"
                data_urls.append(data_url)
            except Exception as e:
                print(f"警告：无法转换图片 #{idx+1}: {e}")
        return data_urls

    def _inference_with_pdf(self, research_topic, phase, step, pdf_path, feedback="", temp=None):
        """
        使用 PDF 进行推理
        """
        sys_prompt = (
            f"You are {self.role_description()} \n"
            f"Task instructions: {self.phase_prompt(phase)}\n"
            f"{self.command_descriptions(phase)}"
        )
        context = self.context(phase)
        history_str = "\n".join([_[1] for _ in self.history])
        phase_notes = [_note for _note in self.notes if phase in _note["phases"]]
        notes_str = f"Notes for the task objective: {phase_notes}\n" if len(phase_notes) > 0 else ""
        complete_str = ""
        if step / (self.max_steps - 1) > 0.7:
            complete_str = "You must finish this task and submit as soon as possible!"
        prompt_text = (
            f"""{context}\n{'~' * 10}\nHistory: {history_str}\n{'~' * 10}\n"""
            f"Current Step #{step}, Phase: {phase}\n{complete_str}\n"
            f"[Objective] Your goal is to perform research on the following topic: {research_topic}\n"
            f"Feedback: {feedback}\nNotes: {notes_str}\n"
            f"Your previous command was: {self.prev_comm}. Make sure your new output is very different.\n"
            f"Please produce a single command below:\n"
        )

        # 将 PDF 转换为图片
        images = self._pdf_to_images(pdf_path)
        if not images:
            raise Exception(f"无法从 PDF 提取图片: {pdf_path}")
        
        # 更新 look 数量
        self.number_of_looks = len(images)
        
        # 转换为 data URLs
        data_urls = self._images_to_data_urls(images)

        api_key = self.openai_api_key or os.getenv("OHMYGPT_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise Exception("No API key provided for collection evaluation.")
        
        # 增大超时并启用 SDK 级重试（网络波动/代理断连时更稳）
        client = OpenAI(
            base_url=OPENAI_COMPAT_BASE_URL,
            api_key=api_key,
            timeout=120.0,
            max_retries=3,
        )
        
        # 构建消息内容，包含所有图片
        content_list = []
        for idx, data_url in enumerate(data_urls):
            content_list.append({"type": "image_url", "image_url": {"url": data_url}})
        
        messages = [
            {"role": "system", "content": sys_prompt + "\n\n" + prompt_text},
            {"role": "user", "content": content_list},
        ]
        
        # 额外做一次应用层重试（避免偶发的 RemoteProtocolError 直接中断批处理）
        last_err = None
        for attempt in range(1, 4):
            try:
                completion = client.chat.completions.create(
                    model=self.model, messages=messages, temperature=temp
                )
                last_err = None
                break
            except (openai.APIConnectionError, httpx.RemoteProtocolError, httpx.ConnectError, httpx.ReadTimeout) as e:
                last_err = e
                wait_s = min(10, 2 ** (attempt - 1))
                print(f"网络错误（第 {attempt}/3 次重试）：{e}；{wait_s}s 后重试")
                time.sleep(wait_s)
        if last_err is not None:
            raise last_err
        model_resp = completion.choices[0].message.content
        print("^" * 50, phase, "^" * 50)
        model_resp = self.clean_text(model_resp)
        self.prev_comm = model_resp
        self.history.append((None, f"Step #{step}, Phase: {phase}, Feedback: {feedback}, Your response: {model_resp}"))
        if len(self.history) >= self.max_hist_len:
            self.history.pop(0)
        return model_resp

    def evaluate_collection(self, pdf_path, brand, theme):
        """
        评估整个系列（从 PDF 输入）
        
        Args:
            pdf_path: group PDF 文件路径
            brand: 品牌名称
            theme: 主题
        
        Returns:
            evaluation_result: 评估结果文本
        """
        self.pdf_path = pdf_path
        self.brand = brand
        self.theme = theme
        
        max_tries = self.max_steps
        research_topic = f"Evaluate the fashion collection for {brand} under theme: {theme}"
        
        for _i in range(max_tries):
            resp = self._inference_with_pdf(
                research_topic=research_topic,
                phase="collection evaluation",
                feedback="",
                step=_i,
                pdf_path=pdf_path
            )
            
            if "```COLLECTION_EVALUATION_RESULT" in resp:
                evaluation_result = extract_prompt(resp, "COLLECTION_EVALUATION_RESULT")
                self.evaluation_result = evaluation_result
                self.reset()
                return evaluation_result
        
        # 如果达到最大尝试次数仍未获得结果
        return None

    def evaluate_collection_from_file(self, pdf_file_path, brand, theme):
        """
        从文件读取 collection PDF 并评估
        
        Args:
            pdf_file_path: collection PDF 文件路径
            brand: 品牌名称
            theme: 主题
        
        Returns:
            evaluation_result: 评估结果文本
        """
        return self.evaluate_collection(
            pdf_path=pdf_file_path,
            brand=brand,
            theme=theme
        )

def is_date_dirname(name: str) -> bool:
    """
    判断目录名是否为“日期运行目录”：
    - YYYY-MM-DD
    - YYYY-MM-DD_02 / YYYY-MM-DD_03 ...
    """
    if not name:
        return False
    return re.fullmatch(r"\d{4}-\d{2}-\d{2}(?:_\d{2})?", name) is not None


def find_pdfs_in_non_date_dirs(root_dir: str):
    """
    遍历 root_dir 下所有 PDF，但跳过任何“日期目录”以及其子树。
    返回：pdf 文件路径列表（绝对/相对取决于传入 root_dir 的形式）
    """
    pdf_files = []
    for current_root, dirs, files in os.walk(root_dir):
        # 剪枝：跳过日期目录
        dirs[:] = [d for d in dirs if not is_date_dirname(d)]

        for filename in files:
            if filename.lower().endswith(".pdf"):
                pdf_files.append(os.path.join(current_root, filename))
    return pdf_files


if __name__ == "__main__":
    # 示例用法
    import yaml
    
    # 从配置文件读取信息
    config_file = "fashion_config.yaml"
    brand = "Givenchy"
    theme = "I Am Your Mirror"
    model_name = "gpt-4o-mini"
    max_steps = 20
    config_api_key = None
    
    if os.path.exists(config_file):
        with open(config_file, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
            brand = config.get("brand", brand)
            theme = config.get("theme", theme)
            model_name = config.get("llm-backend", model_name)
            max_steps = config.get("max-steps", max_steps)
            config_api_key = config.get("api-key", None) or config.get("openai-api-key", None)
    
    # 初始化评估 agent
    api_key = config_api_key or os.getenv('OHMYGPT_API_KEY') or os.getenv('OPENAI_API_KEY')
    evaluator = CollectionEvaluationAgent(
        model=model_name,
        openai_api_key=api_key,
        max_steps=max_steps
    )
    
    # 扫描 fashion_research_dir 下所有“非日期目录”内的 PDF 文件
    research_dir = "fashion_research_dir"
    pdf_files = find_pdfs_in_non_date_dirs(research_dir)
    
    if not pdf_files:
        print(f"在 {research_dir} 目录下未找到任何（非日期目录下的）PDF 文件")
    else:
        print(f"找到 {len(pdf_files)} 个（非日期目录下的）PDF 文件，开始增量评估...\n")
        
        # 统计信息
        total_files = len(pdf_files)
        skipped_count = 0
        evaluated_count = 0
        failed_count = 0
        
        for idx, pdf_file in enumerate(sorted(pdf_files), 1):
            # 检查评估结果文件是否已存在
            result_file = pdf_file.replace(".pdf", "_collection_evaluation.txt")
            
            if os.path.exists(result_file):
                print(f"[{idx}/{total_files}] ⊘ 跳过（已评估）: {pdf_file}")
                skipped_count += 1
                continue
            
            print(f"\n{'='*80}")
            print(f"[{idx}/{total_files}] 正在评估系列: {pdf_file}")
            print('='*80)
            
            # 执行评估（单个文件失败不影响后续批处理）
            try:
                result = evaluator.evaluate_collection_from_file(
                    pdf_file_path=pdf_file,
                    brand=brand,
                    theme=theme
                )
            except Exception as e:
                print(f"\n✗ 评估失败（异常中断）：{e}")
                failed_count += 1
                continue
            
            if result:
                # 保存评估结果到文件
                with open(result_file, "w", encoding="utf-8") as f:
                    f.write(result)
                
                print(f"\n✓ 评估完成，结果已保存到: {result_file}")
                print("\n" + "-"*80)
                print("评估结果预览:")
                print("-"*80)
                print(result)
                evaluated_count += 1
            else:
                print(f"\n✗ 评估失败：未能生成评估结果")
                failed_count += 1
        
        print(f"\n{'='*80}")
        print(f"系列评估完成！")
        print(f"  总文件数: {total_files}")
        print(f"  已跳过（之前已评估）: {skipped_count}")
        print(f"  本次新评估: {evaluated_count}")
        print(f"  评估失败: {failed_count}")
        print('='*80)

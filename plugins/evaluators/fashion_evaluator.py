"""
时尚设计评估 Agent
用于评估生成的 look 描述，根据多个维度进行评分
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
from PIL import Image


class LookEvaluationAgent(BaseAgent):
    """
    评估 Agent: 负责评估生成的 look 描述
    任务：根据评估准则对给定的时尚设计进行多维度评估
    输入：Look 描述、品牌、主题、设计目标等
    输出：评估结果表格（包含6个维度的评分）
    """
    def __init__(self, model="gpt-4o-mini", notes=None, max_steps=100, openai_api_key=None):
        super().__init__(model, notes, max_steps, openai_api_key)
        self.phases = ["look evaluation"]
        self.brand = str()
        self.theme = str()
        self.design_target_prompt = str()
        self.image_path = str()
        self.evaluation_result = str()

    def context(self, phase):
        """
        构建上下文信息
        """
        if phase == "look evaluation":
            context_parts = []

            # [Input information] - image only
            context_parts.append(
                "[ Input information ] You will receive a fashion design work image to evaluate. "
                "Below are the evaluation criteria to score this fashion design work.\n\n"
            )

            # Evaluation criteria
            context_parts.append("**Evaluation Criteria**\n")
            context_parts.append(self._get_evaluation_criteria_table())

            # Minimal metadata (brand/theme/design target) to support scoring dimensions
            if self.brand or self.theme or self.design_target_prompt:
                context_parts.append("\n**Metadata**\n")
                if self.brand:
                    context_parts.append(f"Brand: {self.brand}\n")
                if self.theme:
                    context_parts.append(f"Theme: {self.theme}\n")
                if self.design_target_prompt:
                    context_parts.append(f"Design Target Prompt: {self.design_target_prompt}\n")

            return "".join(context_parts)
        return ""

    def _get_evaluation_criteria_table(self):
        """
        返回评估准则表格
        """
        return (
            "Single-look Evaluation\n\n"
            "|  | 1-3 | 4-6 | 7-8 | 9-10 |\n"
            "|----------|-----|-----|-----|------|\n"
            "| Theme Relevance | Irrelevant / Off-topic | Superficial / Literal | Accurate | Sublime / Profound |\n"
            "| Brand DNA Alignment | Identity Crisis | Generic / Ambiguous | Authentic /Orthodox | Evolutionary |\n"
            "| Innovation & Originality | Cliché/Derivative | Conservative | Fresh | Avant-Garde / Disruptive |\n"
            "| Aesthetics & Visual impact | Aesthetic Disaster | Mediocre | Pleasing | Stunning |\n"
            "| Structural Logic & Material Expression | Logical Collapse | Vague | Clear & Logical | Precise / Photorealistic |\n"
            "| Anticipated Functionality | Anti-Ergonomic | Restricted | Comfortable | Human-Centric |\n\n"
            "**Detailed Criteria Explanations:**\n\n"
            "1. **Theme Relevance** - 主题相关性与深度\n"
            "   - Evaluate how the design interprets and embodies the given theme\n"
            "   - Look for: symbolic elements, conceptual coherence, narrative strength\n"
            "   - Visual cues: color symbolism, silhouette metaphors, detail motifs that reference theme\n"
            "   - 1-3: No connection to theme or completely misinterprets it\n"
            "   - 4-6: Obvious/literal theme references without depth (e.g., using ocean prints for 'ocean' theme)\n"
            "   - 7-8: Thoughtful interpretation showing understanding of theme's essence\n"
            "   - 9-10: Transcendent expression that adds new meaning to the theme\n\n"
            "2. **Brand DNA Alignment** - 品牌基因契合度\n"
            "   - Assess consistency with brand's signature aesthetics, values, and heritage\n"
            "   - Look for: recognizable brand codes, design language, craftsmanship level\n"
            "   - Visual cues: silhouette vocabulary, material choices, construction details, proportions\n"
            "   - 1-3: Contradicts brand identity or unrecognizable as the brand\n"
            "   - 4-6: Generic fashion that could be any brand, lacks distinctive character\n"
            "   - 7-8: Clear brand signatures while remaining relevant and contemporary\n"
            "   - 9-10: Pushes brand forward while honoring its DNA, creates new brand vocabulary\n\n"
            "3. **Innovation & Originality** - 创新性与原创性\n"
            "   - Evaluate novelty in design approach, construction, or concept\n"
            "   - Look for: unexpected combinations, new techniques, fresh perspectives\n"
            "   - Visual cues: unconventional silhouettes, novel material uses, surprising details\n"
            "   - 1-3: Direct copies or overused clichés without any original thought\n"
            "   - 4-6: Safe, predictable choices that follow trends without taking risks\n"
            "   - 7-8: Fresh take on familiar ideas or interesting new combinations\n"
            "   - 9-10: Groundbreaking concepts that challenge conventions, potential trendsetter\n\n"
            "4. **Aesthetics & Visual Impact** - 美学与视觉冲击力\n"
            "   - Judge overall visual appeal, composition, color harmony, and memorability\n"
            "   - Look for: proportion balance, color coordination, visual hierarchy, emotional response\n"
            "   - Visual cues: silhouette clarity, color relationships, texture interplay, focal points\n"
            "   - 1-3: Visually chaotic, clashing elements, poor proportions, painful to look at\n"
            "   - 4-6: Acceptable but forgettable, lacks visual distinction or emotional impact\n"
            "   - 7-8: Harmonious and appealing, well-composed with clear aesthetic vision\n"
            "   - 9-10: Breathtaking visual impact, creates strong emotional response, unforgettable\n\n"
            "5. **Structural Logic & Material Expression** - 结构逻辑与材料表现\n"
            "   - Evaluate technical feasibility, construction clarity, and material appropriateness\n"
            "   - Look for: structural coherence, material behavior, construction details, pattern logic\n"
            "   - Visual cues: how fabric drapes/folds, seam placements, support structures, closures\n"
            "   - 1-3: Physically impossible or structurally nonsensical, materials behave incorrectly\n"
            "   - 4-6: Vague or inconsistent construction logic, unclear material properties\n"
            "   - 7-8: Logical construction with appropriate materials, technically sound and coherent\n"
            "   - 9-10: Precise technical execution, materials perfectly express design intent, photorealistic quality\n\n"
            "6. **Anticipated Functionality** - 预期功能性与穿着合理性\n"
            "   - Assess wearability, comfort, practical usability in real-world context\n"
            "   - Look for: movement allowance, ergonomic fit, practical details, ease of wear\n"
            "   - Visual cues: armhole placement, proportion to body, closure accessibility, weight distribution\n"
            "   - 1-3: Unwearable or would cause discomfort/injury, ignores human body needs\n"
            "   - 4-6: Limited functionality, restrictive movement, or compromised comfort\n"
            "   - 7-8: Well-balanced aesthetics and comfort, practical for intended use\n"
            "   - 9-10: Enhances wearer's comfort and movement, thoughtfully designed for human experience\n\n"
        )

    def phase_prompt(self, phase):
        """
        定义阶段提示
        """
        if phase not in self.phases:
            raise Exception(f"Invalid phase: {phase}")
        
        if phase == "look evaluation":
            phase_str = (
                "[ Role Definition ] Now, assume you are a top fashion designer and critical evaluator at a prestigious fashion house.\n\n"
                "[ Task Information ] Please evaluate the given fashion design in strict accordance with the given evaluation criteria.\n\n"
                "[ Evaluation Guidelines ]\n"
                "- STRICTLY follow the Single-look Evaluation rubric for scoring\n"
                "- Each score range (1-3, 4-6, 7-8, 9-10) has specific qualitative descriptors - use them precisely\n"
                "- Evaluate each criterion independently based on the rubric descriptors\n"
                "- Use the full scoring range to differentiate between designs\n"
                "- Be critical and discerning - identify both strengths AND weaknesses\n"
                "- Provide specific, concrete justifications that reference the rubric descriptors\n\n"
                "[ Output information ] You need to present the scoring results in the following format:\n"
                "1. Evaluation table with all 6 criteria, scores, and justifications\n"
                "2. Overall Assessment section with:\n"
                "   - Strengths (2-3 bullet points)\n"
                "   - Weaknesses (2-3 bullet points)\n"
                "   - Improvement Suggestions (2-3 bullet points)\n"
            )
        return phase_str

    def role_description(self):
        return "a top fashion designer and design evaluation expert at a prestigious fashion house."

    def command_descriptions(self, phase):
        """
        定义可用命令
        """
        if phase not in self.phases:
            raise Exception(f"Invalid phase: {phase}")
        
        if phase == "look evaluation":
            return (
                "**Available Commands:**\n\n"
                "1. ```DIALOGUE\n[your thoughts or analysis here]\n```\n\n"
                "2. ```EVALUATION_RESULT\n[evaluation table and assessment]\n```\n\n"
                "**Output Format Requirements:**\n"
                "- Create a table with columns: Criteria | Score (1-10) | Justification\n"
                "- Include all 6 evaluation criteria\n"
                "- Reference the rubric level in each justification\n"
                "- MUST include 'Overall Assessment' section with three parts:\n"
                "  1. Strengths: List 2-3 key strengths (bullet points)\n"
                "  2. Weaknesses: List 2-3 key weaknesses (bullet points)\n"
                "  3. Improvement Suggestions: List 2-3 specific suggestions (bullet points)\n\n"
                "**Scoring Guidelines:**\n"
                "- Match design to rubric descriptors, then score within the corresponding range\n"
                "- Use full scoring range (1-10) based on actual design quality\n"
                "- Explicitly reference rubric level in justification\n\n"
                "**IMPORTANT:** Every evaluation MUST include a complete Overall Assessment section with:\n"
                "- Strengths (2-3 bullet points)\n"
                "- Weaknesses (2-3 bullet points)\n"
                "- Improvement Suggestions (2-3 bullet points)\n\n"
                "Use ONE command per turn. Include ``` markers: ```COMMAND\ncontent\n```\n"
            )
        return ""

    def example_command(self, phase):
        if phase not in self.phases:
            raise Exception(f"Invalid phase: {phase}")
        return (
            "**Example Format:**\n\n"
            "```EVALUATION_RESULT\n"
            "**Evaluation Results**\n\n"
            "| Criteria | Score (1-10) | Justification |\n"
            "|----------|-------------|----------------|\n"
            "| Theme Relevance | [score] | [Rubric level] - [Specific reasoning] |\n"
            "| Brand DNA Alignment | [score] | [Rubric level] - [Specific reasoning] |\n"
            "| Innovation & Originality | [score] | [Rubric level] - [Specific reasoning] |\n"
            "| Aesthetics & Visual impact | [score] | [Rubric level] - [Specific reasoning] |\n"
            "| Structural Logic & Material Expression | [score] | [Rubric level] - [Specific reasoning] |\n"
            "| Anticipated Functionality | [score] | [Rubric level] - [Specific reasoning] |\n\n"
            "**Overall Assessment:**\n\n"
            "**Strengths:**\n"
            "- [First key strength with rubric level reference]\n"
            "- [Second key strength with rubric level reference]\n"
            "- [Third key strength with rubric level reference]\n\n"
            "**Weaknesses:**\n"
            "- [First key weakness with rubric gap reference]\n"
            "- [Second key weakness with rubric gap reference]\n"
            "- [Third key weakness with rubric gap reference]\n\n"
            "**Improvement Suggestions:**\n"
            "- [First specific improvement suggestion]\n"
            "- [Second specific improvement suggestion]\n"
            "- [Third specific improvement suggestion]\n"
            "```\n"
        )

    def _image_to_data_url(self, image_path):
        mime_type, _ = mimetypes.guess_type(image_path)
        if not mime_type:
            mime_type = "image/png"
        with open(image_path, "rb") as f:
            image_b64 = base64.b64encode(f.read()).decode("utf-8")
        return f"data:{mime_type};base64,{image_b64}"

    def _inference_with_image(self, research_topic, phase, step, image_path, feedback="", temp=None):
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

        data_url = self._image_to_data_url(image_path)

        api_key = self.openai_api_key or os.getenv("OHMYGPT_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise Exception("No API key provided for image evaluation.")
        client = OpenAI(base_url=OPENAI_COMPAT_BASE_URL, api_key=api_key)
        messages = [
            {"role": "system", "content": sys_prompt + "\n\n" + prompt_text},
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": data_url}}
                ],
            },
        ]
        completion = client.chat.completions.create(
            model=self.model, messages=messages, temperature=temp
        )
        model_resp = completion.choices[0].message.content
        print("^" * 50, phase, "^" * 50)
        model_resp = self.clean_text(model_resp)
        self.prev_comm = model_resp
        self.history.append((None, f"Step #{step}, Phase: {phase}, Feedback: {feedback}, Your response: {model_resp}"))
        if len(self.history) >= self.max_hist_len:
            self.history.pop(0)
        return model_resp

    def evaluate_look(self, image_path, brand, theme, design_target_prompt):
        """
        评估单个 look（图片输入）
        
        Args:
            image_path: Look 图片路径
            brand: 品牌名称
            theme: 主题
            design_target_prompt: 设计目标提示
        
        Returns:
            evaluation_result: 评估结果文本
        """
        # 清空历史记录，确保每个图片的评估独立进行，不受之前评估的影响
        self.reset()
        
        self.image_path = image_path
        self.brand = brand
        self.theme = theme
        self.design_target_prompt = design_target_prompt
        
        max_tries = self.max_steps
        brand_info = f" for {brand}" if brand else ""
        research_topic = f"Evaluate the fashion design work{brand_info} under theme: {theme}"
        
        for _i in range(max_tries):
            resp = self._inference_with_image(
                research_topic=research_topic,
                phase="look evaluation",
                feedback="",
                step=_i,
                image_path=image_path
            )
            
            if "```EVALUATION_RESULT" in resp:
                evaluation_result = extract_prompt(resp, "EVALUATION_RESULT")
                self.evaluation_result = evaluation_result
                self.reset()
                return evaluation_result
        
        # 如果达到最大尝试次数仍未获得结果
        return None

    def evaluate_look_from_file(self, image_file_path, brand, theme, design_target_prompt):
        """
        从文件读取 look 图片并评估
        
        Args:
            image_file_path: Look 图片文件路径
            brand: 品牌名称
            theme: 主题
            design_target_prompt: 设计目标提示
        
        Returns:
            evaluation_result: 评估结果文本
        """
        return self.evaluate_look(
            image_path=image_file_path,
            brand=brand,
            theme=theme,
            design_target_prompt=design_target_prompt
        )

    @staticmethod
    def create_group_pdf(collection_dir, output_pdf_path=None):
        """
        将指定目录下的所有图片文件纵向拼接成一个 PDF 文件
        支持格式：.png, .jpg, .jpeg
        
        Args:
            collection_dir: collection 目录路径（如 group_01, Gemini 等）
            output_pdf_path: 输出 PDF 文件路径，如果为 None 则自动根据目录名生成
        
        Returns:
            pdf_path: 生成的 PDF 文件路径，如果没有图片则返回 None
        """
        import glob
        
        # 获取目录下所有以 look_ 开头的图片文件（png, jpg, jpeg）
        image_files = []
        for ext in ['*.png', '*.jpg', '*.jpeg']:
            pattern = os.path.join(collection_dir, f"look_{ext}")
            image_files.extend(glob.glob(pattern))
        
        # 去重（Windows文件系统不区分大小写）
        image_files = list(set(image_files))
        
        # 使用自然排序（按数字大小排序）
        def natural_sort_key(path):
            """提取文件名中的数字进行排序"""
            import re
            basename = os.path.basename(path)
            # 提取 look_ 后面的数字
            match = re.search(r'look_(\d+)', basename)
            if match:
                return int(match.group(1))
            return 0
        
        png_files = sorted(image_files, key=natural_sort_key)
        
        if not png_files:
            return None
        
        # 打印找到的文件列表（用于调试）
        print(f"\n找到 {len(png_files)} 个 look 图片文件：")
        for idx, file in enumerate(png_files[:5], 1):  # 只显示前5个
            print(f"  {idx}. {os.path.basename(file)}")
        if len(png_files) > 5:
            print(f"  ...")
            print(f"  {len(png_files)}. {os.path.basename(png_files[-1])}")
        
        # 如果未指定输出路径，根据目录名自动生成
        if output_pdf_path is None:
            collection_name = os.path.basename(collection_dir)
            output_pdf_path = os.path.join(collection_dir, f"{collection_name}.pdf")
        
        # 打开所有图片
        images = []
        for png_file in png_files:
            try:
                img = Image.open(png_file)
                # 转换为 RGB 模式（PDF 需要）
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                images.append(img)
            except Exception as e:
                print(f"警告：无法打开图片 {png_file}: {e}")
                continue
        
        if not images:
            return None
        
        # 保存为 PDF（第一张作为主图，其余作为附加页）
        try:
            images[0].save(
                output_pdf_path,
                save_all=True,
                append_images=images[1:] if len(images) > 1 else [],
                resolution=100.0
            )
            print(f"✓ 已生成 PDF: {output_pdf_path} (包含 {len(images)} 张图片)")
            return output_pdf_path
        except Exception as e:
            print(f"✗ 生成 PDF 失败: {e}")
            return None


if __name__ == "__main__":
    # 示例用法
    import glob
    import yaml
    
    # 从配置文件读取信息
    config_file = "fashion_config.yaml"
    brand = "Givenchy"
    theme = "I Am Your Mirror"
    design_target = "can you analyze the theme of givenchy as a new fashion collection for I'm Your Mirror"
    model_name = "gpt-4o-mini"
    max_steps = 20
    config_api_key = None
    
    if os.path.exists(config_file):
        with open(config_file, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
            brand = config.get("brand", brand)
            theme = config.get("theme", theme)
            design_target = config.get("design-target-prompt", design_target)
            model_name = config.get("llm-backend", model_name)
            max_steps = config.get("max-steps", max_steps)
            config_api_key = config.get("api-key", None) or config.get("openai-api-key", None)
    
    # 初始化评估 agent
    api_key = config_api_key or os.getenv('OHMYGPT_API_KEY') or os.getenv('OPENAI_API_KEY')
    evaluator = LookEvaluationAgent(
        model=model_name,
        openai_api_key=api_key,
        max_steps=max_steps
    )
    
    # 扫描 fashion_research_dir 下所有包含图片的目录（不限定命名格式）
    research_dir = "fashion_research_dir"
    
    # 先找到所有包含 look_*.* 的图片目录（支持 png, jpg, jpeg）
    all_look_files = []
    for ext in ['png', 'jpg', 'jpeg']:
        all_look_files.extend(glob.glob(f"{research_dir}/**/look_*.{ext}", recursive=True))
    
    # 去重（Windows文件系统不区分大小写）
    all_look_files = list(set(all_look_files))
    
    collection_dirs = set()
    for look_file in all_look_files:
        collection_dir = os.path.dirname(look_file)
        collection_dirs.add(collection_dir)
    
    collection_dirs = sorted(list(collection_dirs))
    
    if not collection_dirs:
        print(f"在 {research_dir} 目录下未找到任何包含 look 图片的目录")
    else:
        print(f"找到 {len(collection_dirs)} 个包含 look 图片的目录\n")
        
        # 第一步：为每个 collection 目录生成 PDF
        print("="*80)
        print("第一步：为每个 collection 目录生成 PDF 文件")
        print("="*80)
        
        pdf_generated_count = 0
        pdf_skipped_count = 0
        
        for collection_dir in collection_dirs:
            collection_name = os.path.basename(collection_dir)
            pdf_path = os.path.join(collection_dir, f"{collection_name}.pdf")
            
            # 检查 PDF 是否已存在
            if os.path.exists(pdf_path):
                print(f"⊘ 跳过（PDF 已存在）: {pdf_path}")
                pdf_skipped_count += 1
                continue
            
            # 生成 PDF
            result_pdf = LookEvaluationAgent.create_group_pdf(collection_dir, pdf_path)
            if result_pdf:
                pdf_generated_count += 1
        
        print(f"\nPDF 生成完成：新生成 {pdf_generated_count} 个，跳过 {pdf_skipped_count} 个\n")
        
        # 第二步：扫描并评估所有 look 图片
        print("="*80)
        print("第二步：评估所有 look 图片")
        print("="*80)
        
        # 扫描所有 look 图片（支持 png, jpg, jpeg）
        look_files = []
        for ext in ['png', 'jpg', 'jpeg']:
            look_files.extend(glob.glob(f"{research_dir}/**/look_*.{ext}", recursive=True))
        
        # 去重并排序（Windows文件系统不区分大小写）
        look_files = sorted(list(set(look_files)))
        
        if not look_files:
            print(f"在 {research_dir} 目录下未找到任何 look 图片文件（.png, .jpg, .jpeg）")
        else:
            print(f"找到 {len(look_files)} 个 look 图片，开始增量评估...\n")
            
            # 统计信息
            total_files = len(look_files)
            skipped_count = 0
            evaluated_count = 0
            failed_count = 0
            
            for idx, look_file in enumerate(look_files, 1):
                # 检查评估结果文件是否已存在
                # 支持多种图片格式：.png, .jpg, .jpeg
                base_name = os.path.splitext(look_file)[0]
                result_file = f"{base_name}_evaluation.txt"
                
                if os.path.exists(result_file):
                    print(f"[{idx}/{total_files}] ⊘ 跳过（已评估）: {look_file}")
                    skipped_count += 1
                    continue
                
                print(f"\n{'='*80}")
                print(f"[{idx}/{total_files}] 正在评估: {look_file}")
                print('='*80)
                
                # 执行评估
                result = evaluator.evaluate_look_from_file(
                    image_file_path=look_file,
                    brand=brand,
                    theme=theme,
                    design_target_prompt=design_target
                )
                
                if result:
                    # 在评估结果前添加 Brand 和 Theme 信息
                    formatted_result = f"**Brand:** {brand}\n**Theme:** {theme}\n\n{result}"
                    
                    # 保存评估结果到文件
                    with open(result_file, "w", encoding="utf-8") as f:
                        f.write(formatted_result)
                    
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
            print(f"增量评估完成！")
            print(f"  总文件数: {total_files}")
            print(f"  已跳过（之前已评估）: {skipped_count}")
            print(f"  本次新评估: {evaluated_count}")
            print(f"  评估失败: {failed_count}")
            print('='*80)


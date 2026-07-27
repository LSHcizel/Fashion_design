from utils import *
from inference import *
import random, string
import os
import re
import base64
import mimetypes
import httpx
import openai


class BaseAgent:
    def __init__(self, model="gpt-4o-mini", notes=None, max_steps=100, openai_api_key=None):
        if notes is None: 
            self.notes = []
        else: 
            self.notes = notes
        self.max_steps = max_steps
        self.model = model
        self.phases = []
        self.history = list()
        self.prev_comm = str()
        self.openai_api_key = openai_api_key

        self.second_round = False
        self.max_hist_len = 15

    def set_model_backbone(self, model):
        self.model = model

    @staticmethod
    def clean_text(text):
        """
        Fix minor corrections
        :return: (str) corrected text
        """
        text = text.replace("```\n", "```")
        return text

    def override_inference(self, query, temp=0.0):
        sys_prompt = f"""You are {self.role_description()}"""
        model_resp = query_model(model_str=self.model, system_prompt=sys_prompt, prompt=query, temp=temp, openai_api_key=self.openai_api_key)
        return model_resp

    def inference(self, research_topic, phase, step, feedback="", temp=None):
        sys_prompt = f"""You are {self.role_description()} \nTask instructions: {self.phase_prompt(phase)}\n{self.command_descriptions(phase)}"""
        context = self.context(phase)
        history_str = "\n".join([_[1] for _ in self.history])
        phase_notes = [_note for _note in self.notes if phase in _note["phases"]]
        notes_str = f"Notes for the task objective: {phase_notes}\n" if len(phase_notes) > 0 else ""
        complete_str = str()
        if step/(self.max_steps-1) > 0.7: 
            complete_str = "You must finish this task and submit as soon as possible!"
        prompt = (
            f"""{context}\n{'~' * 10}\nHistory: {history_str}\n{'~' * 10}\n"""
            f"Current Step #{step}, Phase: {phase}\n{complete_str}\n"
            f"[Objective] Your goal is to perform research on the following topic: {research_topic}\n"
            f"Feedback: {feedback}\nNotes: {notes_str}\nYour previous command was: {self.prev_comm}. Make sure your new output is very different.\nPlease produce a single command below:\n")
        model_resp = query_model(model_str=self.model, system_prompt=sys_prompt, prompt=prompt, temp=temp, openai_api_key=self.openai_api_key)
        print("^"*50, phase, "^"*50)
        model_resp = self.clean_text(model_resp)
        self.prev_comm = model_resp
        steps_exp = None
        if feedback is not None and "```EXPIRATION" in feedback:
            steps_exp = int(feedback.split("\n")[0].replace("```EXPIRATION ", ""))
            feedback = extract_prompt(feedback, "EXPIRATION")
        self.history.append((steps_exp, f"Step #{step}, Phase: {phase}, Feedback: {feedback}, Your response: {model_resp}"))
        # remove histories that have expiration dates
        for _i in reversed(range(len(self.history))):
            if self.history[_i][0] is not None:
                self.history[_i] = (self.history[_i][0] - 1, self.history[_i][1])
                if self.history[_i][0] < 0:
                    self.history.pop(_i)
        if len(self.history) >= self.max_hist_len:
            self.history.pop(0)
        return model_resp

    def reset(self):
        self.history.clear()  # Clear the deque
        self.prev_comm = ""

    def context(self, phase):
        raise NotImplementedError("Subclasses should implement this method.")

    def phase_prompt(self, phase):
        raise NotImplementedError("Subclasses should implement this method.")

    def role_description(self):
        raise NotImplementedError("Subclasses should implement this method.")

    def command_descriptions(self, phase):
        raise NotImplementedError("Subclasses should implement this method.")

    def example_command(self, phase):
        raise NotImplementedError("Subclasses should implement this method.")


class ThemeAnalysisAgent(BaseAgent):
    """
    Agent 1: 负责分析时尚主题
    任务：分析给定主题（如 Chanel Cruise「Sous le Salon la Plage」）
    输入：Design target prompt、Theme、可选 Description（须先提炼关键要素再写入最终分析）
    输出：Theme analysis（全英文；含 Theme, Inspiration, Key aspects）
    """
    def __init__(self, model="gpt-4o-mini", notes=None, max_steps=100, openai_api_key=None):
        super().__init__(model, notes, max_steps, openai_api_key)
        self.phases = ["theme analysis"]
        self.design_target_prompt = str()
        self.theme = str()
        self.description = str()
        self.description_key_elements = str()
        self.num_chapters = 4
        self.theme_analysis = str()
        self.sub_themes = []

    def context(self, phase):
        """
        构建上下文信息
        输入包括：Design target prompt 和 Theme
        """
        sr_str = ""
        if self.second_round:
            sr_str = (
                f"The following are results from previous analysis:\n"
                f"Previous Theme Analysis: {self.theme_analysis}\n"
                f"Previous Sub-themes: {self.sub_themes}\n\n"
            )
        
        if phase == "theme analysis":
            desc_block = ""
            workflow_block = ""
            if (self.description or "").strip():
                desc_block = f"Description (supplementary notes about the theme):\n{self.description.strip()}\n\n"
                workflow_block = (
                    "Required workflow when Description is present:\n"
                    "1) First submit ```DESCRIPTION_KEY_ELEMENTS``` (English only) to extract design-relevant key elements from Description.\n"
                    "2) Then submit ```THEME_ANALYSIS``` (English only) that explicitly fuses those elements into Theme, Inspiration, and Key aspects.\n"
                    "Do not skip step 1.\n\n"
                )
            return (
                f"{sr_str}"
                f"Design target prompt: {self.design_target_prompt}\n\n"
                f"Theme: {self.theme}\n\n"
                f"Num chapters (sub-themes to produce): {self.num_chapters}\n\n"
                f"{desc_block}"
                f"{workflow_block}"
                f"You need to analyze the theme based on the above Design target prompt and Theme"
                f"{', using Description as primary source material' if desc_block else ''}."
                f" Write all analysis output in English."
            )
        return ""

    def phase_prompt(self, phase):
        """
        定义阶段提示
        """
        if phase not in self.phases:
            raise Exception(f"Invalid phase: {phase}")
        
        if phase == "theme analysis":
            phase_str = (
                "You are a fashion theme analyst and cultural researcher.\n"
                "Analyze the given theme and break it down into meaningful key aspects that can guide the design process.\n"
                "Write all submitted analysis in English.\n"
                "Key aspects are a holistic analytical layer—not a 1:1 chapter list. "
                "Chapter sub-themes (exactly Num chapters) must synthesize across ALL key aspects and inspiration, "
                "each offering a distinct narrative angle for one design chapter.\n"
                "When Description is provided: first distill design-relevant key elements from it "
                "(heritage facts, location/show context, silhouettes, materials, codes, accessories, mood, cultural signals—"
                "only what helps refine the collection theme). Submit these via DESCRIPTION_KEY_ELEMENTS before the final analysis.\n"
                "Then fuse those extracted elements into Theme, Inspiration, Key aspects, and Sub-themes; do not ignore Description facts, "
                "but do not paste Description verbatim—synthesize for downstream design use.\n"
            )
        return phase_str

    def role_description(self):
        return "a fashion theme analyst and cultural researcher at a prestigious fashion house."

    def command_descriptions(self, phase):
        """
        定义可用命令
        输出格式参考 Theme analysis 部分构建
        """
        if phase not in self.phases:
            raise Exception(f"Invalid phase: {phase}")
        
        if phase == "theme analysis":
            return (
                "You can produce dialogue using the following command: ```DIALOGUE\ndialogue here\n```\n"
                "where 'dialogue here' is the actual dialogue you will send and DIALOGUE is just the word DIALOGUE.\n"
                "When Description is provided, you MUST first submit key-element extraction using:\n"
                "```DESCRIPTION_KEY_ELEMENTS\n"
                "key elements here\n"
                "```\n"
                "DESCRIPTION_KEY_ELEMENTS structure (English only):\n"
                "- Heritage & provenance: [bullets]\n"
                "- Show / location context: [bullets]\n"
                "- Creative director intent: [bullets]\n"
                "- Silhouette & garment vocabulary: [bullets]\n"
                "- Materials, craft & surface: [bullets]\n"
                "- Color, stripe & graphic codes: [bullets]\n"
                "- Accessories & finishing: [bullets]\n"
                "- Mood, liberation & wearer fantasy: [bullets]\n"
                "Include only elements that materially help refine the collection theme.\n\n"
                "After DESCRIPTION_KEY_ELEMENTS, submit the final analysis using: ```THEME_ANALYSIS\ntheme analysis here\n```\n"
                "THEME_ANALYSIS structure (English only):\n\n"
                "**Theme:**\n"
                "[Collection title and overview; must reflect fused Description-derived elements.]\n\n"
                "**Inspiration:**\n"
                "[Designer, historical sources, show context; weave in extracted key elements in paragraph form.]\n\n"
                "**Key aspects of the theme:**\n"
                "[4–8 analytical aspects (holistic theme decomposition). Each: bold heading **Aspect Name:** then a paragraph. "
                "These are NOT chapter titles and must NOT be copied 1:1 as sub-themes.]\n\n"
                f"**Sub-themes for chapter development:**\n"
                f"[Exactly {self.num_chapters} chapter-ready sub-themes. Each: bold heading **Sub-theme title:** then 2–3 sentences "
                "stating a distinct chapter narrative that draws holistically from Theme, Inspiration, and multiple Key aspects—not one aspect per sub-theme.]\n\n"
                "If Description is absent, you may submit THEME_ANALYSIS directly without DESCRIPTION_KEY_ELEMENTS.\n"
                "You can only use a SINGLE command per inference turn. Do not use more than one command per inference.\n"
                "When performing a command, make sure to include the three ticks (```) at the top and bottom ```COMMAND\ntext\n``` "
                "where COMMAND is the specific command you want to run (e.g. DESCRIPTION_KEY_ELEMENTS, THEME_ANALYSIS, DIALOGUE).\n"
            )
        return ""

    def example_command(self, phase):
        if phase not in self.phases:
            raise Exception(f"Invalid phase: {phase}")
        return (
            "Example command for theme analysis (for reference only, adjust the corresponding text according to actual generation requirements):\n"
            "```THEME_ANALYSIS\n"
            "**Theme:**\n"
            "Theme: \"I Am Your Mirror\" — Androgyny and the Glamorous Nomad. The central theme of the womenswear show was the exploration of duality between the masculine and the feminine.\n\n"
            "**Inspiration:**\n"
            "Clare Waight Keller was heavily inspired by Annemarie Schwarzenbach. Annemarie Schwarzenbach was a Swiss author, journalist, and photographer active in the 1930s. She lived an adventurous, nomadic life and was famous for her striking, androgynous appearance, often dressing in men's clothing. Waight Keller used Schwarzenbach as a muse to create a collection that challenged traditional gender codes.\n\n"
            "**Key aspects of the theme:**\n"
            "**Gender Fluidity:**\n"
            "The show title \"I Am Your Mirror\" referred to the idea of a woman seeing her masculine side in the reflection, and vice-versa. This translated into clothes that borrowed heavily from menswear tailoring but were adapted for a female form.\n\n"
            "**Utility and Function:**\n"
            "The collection featured a strong \"glamorous utility\" vibe. There were high-fashion takes on cargo pants, multi-pocket jackets, and boiler suits, suggesting a woman on the move or traveling.\n\n"
            "**Sharp vs. Soft:**\n"
            "The silhouette was characterized by very sharp, strong shoulders on blazers and coats. This was contrasted with softer elements like flowing, pleated Grecian-style gowns in the eveningwear.\n\n"
            "**Sub-themes for chapter development:**\n"
            "**The Mirror in Motion:**\n"
            "A chapter synthesizing gender fluidity and nomadic utility into travel-ready tailoring with reflective surfaces and androgynous layering.\n\n"
            "**Sharp Departure:**\n"
            "A chapter balancing structured shoulders and soft evening drape, using contrast between masculine discipline and feminine release.\n"
            "```\n"
        )


class ConceptBrainstormingAgent(BaseAgent):
    """
    Agent 2: 负责设计概念头脑风暴
    任务：基于主题分析，为“单个子主题”生成“单个章节”的完整概念方案
    约束：每个子主题对应一个章节（1:1）
    """
    def __init__(self, model="gpt-4o-mini", notes=None, max_steps=100, openai_api_key=None):
        super().__init__(model, notes, max_steps, openai_api_key)
        self.phases = ["concept brainstorming"]
        self.theme = str()
        self.theme_analysis = str()
        # 当前要展开的子主题（=章节主题）
        self.sub_theme = str()

    def context(self, phase):
        """
        构建上下文信息
        """
        sr_str = ""
        if self.second_round:
            sr_str = (
                f"The following are results from previous brainstorming:\n"
                f"Previous Sub-theme: {self.sub_theme}\n\n"
            )
        
        if phase == "concept brainstorming":
            return (
                f"{sr_str}"
                f"Main Theme: {self.theme}\n"
                f"Current Theme Analysis: {self.theme_analysis}\n"
                f"Current Sub-theme (this chapter): {self.sub_theme}\n"
            )
        return ""

    def phase_prompt(self, phase):
        """
        定义阶段提示
        """
        if phase not in self.phases:
            raise Exception(f"Invalid phase: {phase}")
        
        if phase == "concept brainstorming":
            phase_str = (
                "Design ONE chapter for a fashion collection based on the given theme analysis and the given sub-theme.\n"
                "This chapter must be self-contained and production-oriented: concept, looks direction, ambiance, and analysis.\n"
                "IMPORTANT: The chapter must clearly reflect and deepen the given sub-theme.\n"
            )
        return phase_str

    def role_description(self):
        return "a creative director and fashion concept designer at a prestigious fashion house."

    def command_descriptions(self, phase):
        """
        定义可用命令
        """
        if phase not in self.phases:
            raise Exception(f"Invalid phase: {phase}")
        
        if phase == "concept brainstorming":
            return (
                "You can produce dialogue using the following command: ```DIALOGUE\ndialogue here\n```\n"
                "where 'dialogue here' is the actual dialogue you will send and DIALOGUE is just the word DIALOGUE.\n"
                "When you have completed the chapter concept, submit it using: ```DESIGN_CONCEPT\nconcept here\n```\n"
                "The output must follow this structure (generate ONLY ONE chapter):\n\n"
                "**Chapter [Number] (Sub-Theme): [Sub-Theme Name]**\n\n"
                "*   **Concept:**\n"
                "    [Conceptual description of this chapter.]\n\n"
                "*   **The Looks:**\n"
                "    *   **Silhouette:**\n"
                "        [Silhouette characteristics.]\n\n"
                "    *   **Garments:**\n"
                "        [Description of garments and pieces.]\n\n"
                "    *   **Fabric & Color:**\n"
                "        [Color palette and fabric choices.]\n\n"
                "*   **Ambiance:**\n"
                "    *   **Lighting:**\n"
                "        [Lighting approach.]\n\n"
                "    *   **Music:**\n"
                "        [Musical direction.]\n\n"
                "*   **Analysis:**\n"
                "    [Analytical insight into this chapter's role and significance.]\n\n"
                "You can only use a SINGLE command per inference turn. Do not use more than one command per inference.\n"
                "When performing a command, make sure to include the three ticks (```) at the top and bottom ```COMMAND\ntext\n``` "
                "where COMMAND is the specific command you want to run (e.g. DESIGN_CONCEPT, DIALOGUE).\n"
            )
        return ""

    def example_command(self, phase):
        if phase not in self.phases:
            raise Exception(f"Invalid phase: {phase}")

        return (
            "Example command for design concept (for reference only, adjust the corresponding text according to actual generation requirements):\n"
            "```DESIGN_CONCEPT\n"
            "**Chapter 1 (Sub-Theme): The Departure - A Reflection in Tailoring**\n\n"
            "*   **Concept:**\n"
            "    This chapter represents an initial act of rebellion and self-definition. It describes a moment where a woman looks in a mirror, chooses a new identity, and arms herself with masculine codes to break free from convention. The overall mood is sharp, deliberate, and almost severe.\n\n"
            "*   **The Looks:**\n"
            "    *   **Silhouette:**\n"
            "        Dominated by powerful, architectural shoulders on double-breasted blazers and long overcoats. The waist is defined but not cinched, creating a strong, columnar line.\n\n"
            "    *   **Garments:**\n"
            "        The focus is on immaculate tailoring: high-waisted, wide-leg wool trousers; crisp poplin shirts buttoned to the neck; and severe, floor-grazing greatcoats. Details borrow from a 1930s men's wardrobe—ticket pockets, peak lapels, surgeon's cuffs.\n\n"
            "    *   **Fabric & Color:**\n"
            "        A restrictive, serious palette—charcoal grey, deep navy, stark black. Matte, structured fabrics: felted wool, heavy cotton twill, rigid leather for gloves/belts. A hidden note of softness appears in silk (ascot or coat lining).\n\n"
            "*   **Ambiance:**\n"
            "    *   **Lighting:**\n"
            "        Harsh, single-source spotlights create long, dramatic shadows, emphasizing the sharp silhouettes. A clouded mirror at the end of the runway reflects a blurred, indistinct image.\n\n"
            "    *   **Music:**\n"
            "        Minimalist, percussive electronic beat or a stark, repetitive piano motif—intellectual, cold, with forward momentum.\n\n"
            "*   **Analysis:**\n"
            "    This chapter establishes the \"masculine\" pole of the collection’s duality and frames menswear codes as a tool of liberation. Glamour is intellectual—found in precision and cut—while utility is expressed through uniform-like functionality.\n"
            "```\n"
        )


class DesignElementsAgent(BaseAgent):
    """
    Agent 3: 负责提出候选设计元素
    任务：基于主题和所有子主题，提出候选设计元素并分配权重
    """
    def __init__(self, model="gpt-4o-mini", notes=None, max_steps=100, openai_api_key=None):
        super().__init__(model, notes, max_steps, openai_api_key)
        self.phases = ["design elements proposal"]
        self.theme = str()
        self.theme_analysis = str()
        self.design_concepts = []
        self.candidate_elements = []

    def context(self, phase):
        """
        构建上下文信息
        """
        sr_str = ""
        if self.second_round:
            sr_str = (
                f"The following are results from previous proposals:\n"
                f"Previous Candidate Elements: {self.candidate_elements}\n\n"
            )
        
        if phase == "design elements proposal":
            # 构建所有设计概念的描述
            design_concepts_str = ""
            if self.design_concepts:
                if isinstance(self.design_concepts, list):
                    design_concepts_str = "\n\n".join([f"**Design Concept {idx+1}:**\n{concept}" for idx, concept in enumerate(self.design_concepts)])
                else:
                    design_concepts_str = str(self.design_concepts)
            
            return (
                f"{sr_str}"
                f"Overall Theme: {self.theme}\n\n"
                f"Theme Analysis: {self.theme_analysis}\n\n"
                f"All Design Concepts (Sub-themes):\n{design_concepts_str}\n"
            )
        return ""

    def phase_prompt(self, phase):
        """
        定义阶段提示
        """
        if phase not in self.phases:
            raise Exception(f"Invalid phase: {phase}")
        
        if phase == "design elements proposal":
            phase_str = (
                "Propose candidate design elements with percentage weights for the collection.\n"
                "Consider both the overall theme and the sub-themes provided.\n"
                "Organize elements into meaningful categories.\n"
                "Assign percentage weights to key/critical elements to indicate their importance.\n"
                "Include color descriptions in your element descriptions.\n"
                "IMPORTANT: Ensure all design elements are reasonable and feasible. Consider technical feasibility, material compatibility, aesthetic coherence, and practical wearability. Elements should work together logically and create a cohesive collection.\n"
            )
        return phase_str

    def role_description(self):
        return "a fashion design elements specialist and technical designer at a prestigious fashion house."

    def command_descriptions(self, phase):
        """
        定义可用命令
        """
        if phase not in self.phases:
            raise Exception(f"Invalid phase: {phase}")
        
        if phase == "design elements proposal":
            return (
                "You can produce dialogue using the following command: ```DIALOGUE\ndialogue here\n```\n"
                "where 'dialogue here' is the actual dialogue you will send and DIALOGUE is just the word DIALOGUE.\n"
                "When you have completed proposing design elements, submit them using: ```DESIGN_ELEMENTS\nelements here\n```\n"
                "The output must follow this structure:\n\n"
                "**Candidate elements/concepts**\n\n"
                "1. [Category Name] | [Specific Element Title] | [Percentage Weight] (only if this is a key/critical element)\n"
                "[Write a descriptive paragraph covering the concept, aesthetic, key elements, function, materials, and colors. Include color details such as color names, palettes, and tones.]\n\n"
                "1. [Category Name] | [Next Element Title in Same Category] (no percentage weight if not key)\n"
                "[Write a descriptive paragraph following the same style. Elements that are not key/critical do not need percentage weights.]\n\n"
                "2. [Next Category Name] | [Specific Element Title] | [Percentage Weight] (only if key)\n"
                "[Descriptive paragraph]\n\n"
                "[Continue organizing elements into numbered categories. Category names should be creative and tailored to the collection.]\n\n"
                "Format rules:\n"
                "- Use '|' to separate: [Category Name] | [Element Title] | [Weight%] (weight only for key elements)\n"
                "- Write descriptions as paragraphs, not bullet-point lists\n"
                "- Only key/critical elements should have percentage weights\n"
                "You can only use a SINGLE command per inference turn. Do not use more than one command per inference.\n"
                "When performing a command, make sure to include the three ticks (```) at the top and bottom ```COMMAND\ntext\n``` "
                "where COMMAND is the specific command you want to run (e.g. DESIGN_ELEMENTS, DIALOGUE).\n"
            )
        return ""

    def example_command(self, phase):
        if phase not in self.phases:
            raise Exception(f"Invalid phase: {phase}")
        return (
            "Example command for design elements (for reference only, adjust the corresponding text according to actual generation requirements):\n"
            "```DESIGN_ELEMENTS\n"
            "**Candidate elements/concepts**\n\n"
            "1. Silhouette & Form | The Architectural Shoulder | 30%\n"
            "The primary visual signifier of \"armoring\" and borrowed masculine power. Exaggerated shoulder pads and sharp sleeve heads create a strong, horizontal line that grounds the look, creating a powerful A-line. This element projects confidence and stability, directly referencing 1930s menswear tailoring. The shoulders are *defined* and structured, not rounded, emphasizing the \"severe\" aesthetic. Heavy-duty internal construction with structured shoulder pads creates this architectural form.\n\n"
            "1. Silhouette & Form | The Columnar Torso\n"
            "The waist is *defined* but not cinched, creating a long, straight line from shoulder to hem. This \"columnar\" silhouette, achieved through either a belt or high-rise trouser, elongates the figure and provides movement and gravitas. It signifies intellectual rigor and severity, avoiding any overt femininity. The silhouette maintains a sharp, deliberate verticality that reinforces the architectural nature of the look.\n\n"
            "1. Silhouette & Form | Wide, Grounded Stance\n"
            "The essential wide-leg trouser silhouette grounds the look, creating a powerful A-line that references 1930s menswear and projects confidence and stability. This wide, grounded stance is fundamental to the overall silhouette's impact.\n\n"
            "2. Key Garments | The Double-Breasted Outerwear | 25%\n"
            "Whether appearing as a \"blazer\" or a \"greatcoat\" (floor-grazing length), the double-breasted construction creates a shield-like front. The piece is the literal \"armor\" of the collection - severe, floor-grazing greatcoats with peak lapels. The flawless, sharp cut ensures structure and a perfect drape. Details like ticket pockets reference authentic 1930s menswear codes, reinforcing the borrowed masculine aesthetic. This garment carries the silhouette.\n\n"
            "2. Key Garments | The High-Waisted Wool Trouser\n"
            "Wide-leg wool trousers with a high waist that elongates the leg and creates the \"columnar\" line. The wide-leg cut provides movement and gravitas, while the high-waist defines the torso without cinching. This piece is foundational to the silhouette, working in harmony with the architectural shoulders to create the overall form. The wool ensures structure and a perfect drape.\n\n"
            "2. Key Garments | The High-Neck Poplin Shirt\n"
            "A key layering piece signifying intellectual rigor and severity, which must be buttoned to the neck. Its crispness contrasts with soft wool, creating textural tension. This is \"the uniform beneath the armor,\" providing the clean, structured foundation for the outerwear.\n\n"
            "3. Construction & Tailoring | Authentic Menswear Lapels | 20%\n"
            "Sharp, aggressive peak lapels borrowed directly from 1930s menswear. These are not softened or adapted - they maintain their masculine character, reinforcing the \"borrowed\" aesthetic. The peak lapels contribute to the \"sharp, deliberate\" mood and are a key signifier of the intellectual glamour found in perfect tailoring. Notch lapels would be too soft or conventional.\n\n"
            "3. Construction & Tailoring | Functional & Sharp Cuffs\n"
            "Surgeon's cuffs (working buttonholes) on jacket sleeves serve as a detail that speaks to the authenticity and \"intellectual glamour\" of high-end menswear. This subtle signal of quality and deliberate choice reinforces the collection's commitment to authentic tailoring details.\n\n"
            "3. Construction & Tailoring | Structured Internal Canvassing\n"
            "The invisible element that creates the visible shape. Heavy-duty internal construction in jackets holds the architectural shoulder and lapel shape. This is the literal \"armor\" and non-negotiable for achieving the silhouette.\n\n"
            "4. Fabric & Materiality | Matte & Structured Surfaces | 15%\n"
            "The dominance of non-reflective, heavy fabrics including felted wool, cavalry twill, and compact flannel. The lack of sheen conveys seriousness and removes any hint of frivolous decoration. These materials create textural tension and reinforce the \"sharp, deliberate\" mood. The fabric *is* the form.\n"
            "```\n"
        )


class LookDescriptionAgent(BaseAgent):
    """
    Agent 4: 负责Look特征采样和详细描述生成
    任务：基于候选设计元素，生成完整look的详细视觉描述
    """
    def __init__(self, model="gpt-4o-mini", notes=None, max_steps=100, openai_api_key=None, num_looks=1):
        super().__init__(model, notes, max_steps, openai_api_key)
        self.phases = ["look description generation"]
        self.design_target_prompt = ""
        self.theme = ""
        self.theme_analysis = ""
        self.sub_theme = ""
        self.candidate_elements = []
        self.look_descriptions = []
        self.num_looks = num_looks

    def context(self, phase):
        """
        构建上下文信息
        """
        sr_str = ""
        if self.look_descriptions:
            summaries = []
            for idx, desc in enumerate(self.look_descriptions, start=1):
                summaries.append(f"Look {idx} (already generated): {self._summarize_look_for_diversity(desc)}")
            sr_str = (
                "Already generated in this chapter (do NOT repeat silhouette archetype or hero garment combo):\n"
                + "\n".join(summaries)
                + "\n\n"
            )
        elif self.second_round:
            sr_str = (
                f"The following are results from previous descriptions:\n"
                f"Previous Look Descriptions: {self.look_descriptions}\n\n"
            )
        
        if phase == "look description generation":
            # 章节级上下文：同一章内每个 look 的上下文保持完全一致，避免“随 look 数增长”的冗余信息
            elements_text = ""
            if isinstance(self.candidate_elements, list):
                if len(self.candidate_elements) == 1:
                    elements_text = str(self.candidate_elements[0])
                else:
                    elements_text = "\n\n".join([str(x) for x in self.candidate_elements])
            else:
                elements_text = str(self.candidate_elements)

            design_context_text = ""
            design_concepts_val = getattr(self, "design_concepts", [])
            if isinstance(design_concepts_val, list):
                if len(design_concepts_val) == 1:
                    design_context_text = str(design_concepts_val[0])
                else:
                    design_context_text = "\n\n".join([str(x) for x in design_concepts_val])
            else:
                design_context_text = str(design_concepts_val)

            return (
                f"{sr_str}"
                f"Design Target: {self.design_target_prompt}\n"
                f"Main Theme: {self.theme}\n"
                f"Theme Analysis: {self.theme_analysis}\n\n"
                f"Current Sub-theme (this chapter): {self.sub_theme}\n\n"
                f"Candidate Design Elements:\n{elements_text}\n\n"
                f"Chapter Design Context:\n{design_context_text}\n"
            )
        return ""

    @staticmethod
    def _summarize_look_for_diversity(look_desc: str) -> str:
        text = (look_desc or "").strip()
        if not text:
            return ""
        key_match = re.split(r"(?im)^\s*key\s+elements\s*:\s*$", text, maxsplit=1)
        if len(key_match) > 1:
            bullets = [
                ln.strip().lstrip("-*• ").strip()
                for ln in key_match[1].splitlines()
                if ln.strip().startswith(("-", "*", "•"))
            ]
            if bullets:
                return "; ".join(bullets[:8])
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        for ln in lines:
            if ln.lower().startswith("look ") and ":" in ln:
                return ln
        compact = re.sub(r"\s+", " ", text)
        return compact[:240] + ("..." if len(compact) > 240 else "")

    def phase_prompt(self, phase):
        """
        定义阶段提示
        """
        if phase not in self.phases:
            raise Exception(f"Invalid phase: {phase}")
        
        if phase == "look description generation":
            diversity_str = ""
            if self.look_descriptions:
                diversity_str = (
                    "DIVERSITY REQUIREMENT: This look MUST differ from all previously generated looks in this chapter. "
                    "Change the silhouette archetype and hero garment combination; do not repeat the same outerwear + foundation pairing.\n"
                )
            phase_str = (
                "Generate ONE image-faithful look description based on the candidate design elements.\n"
                f"{diversity_str}"
                "Write for direct image generation: one coherent English paragraph (800–1500 characters) in visual order from outer layer to inner layers, details, footwear, and overall mood.\n"
                "Rules:\n"
                "1. Describe only what should be visible in the generated image. Do not invent unseen back views, hidden closures, or unstated footwear.\n"
                "2. Use dense, concrete fashion language: garment category, silhouette, color, material/surface cues, layering (over/under), and key construction details.\n"
                "3. Do NOT write brand commentary, chapter narrative, scene metaphors, model stance directions, or analytical/runway-essay prose.\n"
                "4. If material is uncertain, use careful visible-language such as appears or suggests.\n"
                "5. Theme and chapter context are for selecting the look only—do not copy narrative framing into the output.\n"
                "IMPORTANT: Ensure the look is reasonable and wearable. Use the exact look number specified in the research topic.\n"
            )
        return phase_str

    def role_description(self):
        return "a fashion look stylist and visual description specialist at a prestigious fashion house."

    def command_descriptions(self, phase):
        """
        定义可用命令
        """
        if phase not in self.phases:
            raise Exception(f"Invalid phase: {phase}")
        
        if phase == "look description generation":
            return (
                "You can produce dialogue using the following command: ```DIALOGUE\ndialogue here\n```\n"
                "where 'dialogue here' is the actual dialogue you will send and DIALOGUE is just the word DIALOGUE.\n"
                "When you have completed generating a look description, submit it using: ```LOOK_DESCRIPTION\ndescription here\n```\n"
                "The output must follow this structure (generate ONLY ONE look description):\n\n"
                "Mandatory line (must appear verbatim as the FIRST line inside the LOOK_DESCRIPTION block):\n"
                "Please generate female models and the matching clothing for them.\n\n"
                "Look [Number]: [Look Name/Title]\n\n"
                "[Single paragraph text_description: 800–1500 characters of dense visual prose in outer-to-inner order. "
                "No numbered sections, no transitions between sections, no stance or scene commentary.]\n\n"
                "Key elements:\n"
                "- [6–12 short visible element tags, one per line]\n\n"
                "You can only use a SINGLE command per inference turn. Do not use more than one command per inference.\n"
                "When performing a command, make sure to include the three ticks (```) at the top and bottom ```COMMAND\ntext\n``` "
                "where COMMAND is the specific command you want to run (e.g. LOOK_DESCRIPTION, DIALOGUE).\n"
            )
        return ""

    def example_command(self, phase):
        if phase not in self.phases:
            raise Exception(f"Invalid phase: {phase}")
        return (
            "Example command for look description (for reference only, adjust the corresponding text according to actual generation requirements):\n"
            "```LOOK_DESCRIPTION\n"
            "Please generate female models and the matching clothing for them.\n\n"
            "Look 01: Shoreline Layered Suit\n\n"
            "Full-length runway look centered on a cropped chalk-white cotton-canvas jacket worn over a slim banker-stripe poplin shirt and deep-navy tailored gabardine shorts. "
            "The jacket has crisp squared shoulders, a narrow notched lapel, concealed front placket, and a hem that stops just above the waist; sand-beige topstitching traces the seams. "
            "Beneath it, the shirt reads white with pale-navy pinstripes, tucked cleanly into high-waisted shorts with a pressed front crease and discreet side entry. "
            "A narrow black leather belt with a small brushed-silver buckle defines the waist where jacket and shorts meet. "
            "Flat black leather sandals with a slim sole and delicate toe strap finish the look, keeping the silhouette grounded and resort-tailored without ornamental prose.\n\n"
            "Key elements:\n"
            "- cropped white cotton-canvas jacket\n"
            "- squared shoulders and narrow notch lapel\n"
            "- banker-stripe poplin shirt\n"
            "- deep-navy tailored shorts\n"
            "- black leather belt with metal buckle\n"
            "- flat black leather sandals\n"
            "- high-waist shoreline tailoring\n"
            "- crisp resort suiting mood\n"
            "```\n"
        )


class SingleLookReflectAgent(BaseAgent):
    """
    单图 Reflect Agent（用于每个 look 生成后进行反思/淘汰判断）
    参考用户提供的 prompt：对单张设计图进行“心里分析”，给出最终处理结果。

    约定：
    - high-tier => KEEP（保留该 look 图片）
    - medium-tier / low-tier => DELETE（建议淘汰该 look 图片）
    """
    def __init__(self, model="gpt-4o-mini", notes=None, max_steps=6, openai_api_key=None):
        super().__init__(model, notes, max_steps, openai_api_key)
        self.phases = ["single look reflection"]
        self.theme = ""
        self.sub_theme = ""
        self.image_path = ""

    def context(self, phase):
        if phase not in self.phases:
            raise Exception(f"Invalid phase: {phase}")
        # 参考用户提供的 prompt：单图分析仅基于图片本身，不引入主题/子主题上下文
        return "[ Input information ] The content above showcases a piece of fashion design.\n"

    def phase_prompt(self, phase):
        if phase not in self.phases:
            raise Exception(f"Invalid phase: {phase}")
        return (
            "[ Role Definition ] Now, assume you are a top fashion designer.\n\n"
            "[ Task Information ] Please conduct a thorough analysis of this fashion design in the following aspects: "
            "innovation & originality, aesthetic appeal, expected functionality, and compliance with ergonomic principles. "
            "After the analysis, classify the design into one of three tiers: low, medium, or high.\n\n"
            "If the design is rated as high-tier, retain the original design.\n"
            "If the design is rated as low-tier or medium-tier, recommend deleting this look (淘汰) and provide a revised design direction.\n\n"
            "[ Output information ] You must NOT show your analysis process. Output only the final result in the required format.\n"
        )

    def role_description(self):
        return "a top fashion designer."

    def command_descriptions(self, phase):
        if phase not in self.phases:
            raise Exception(f"Invalid phase: {phase}")
        return (
            "When you have completed the reflection, submit it using:\n"
            "```LOOK_REFLECTION_RESULT\n"
            "TIER: <high|medium|low>\n"
            "ACTION: <KEEP|DELETE>\n"
            "INFO: <one short line explaining why KEEP/DELETE>\n"
            "FINAL_FASHION_DESIGN: <if KEEP: brief confirmation; if DELETE: revised design direction to regenerate>\n"
            "```\n"
            "Rules:\n"
            "- ACTION must match TIER (high=>KEEP; medium/low=>DELETE)\n"
            "- Keep it concise; do not include step-by-step analysis\n"
            "You can only use a SINGLE command per inference turn.\n"
        )

    def example_command(self, phase):
        if phase not in self.phases:
            raise Exception(f"Invalid phase: {phase}")
        return (
            "```LOOK_REFLECTION_RESULT\n"
            "TIER: high\n"
            "ACTION: KEEP\n"
            "INFO: Strong silhouette clarity and refined ergonomics; original is compelling.\n"
            "FINAL_FASHION_DESIGN: Retain the original design as-is.\n"
            "```\n"
        )

    def _image_to_data_url(self, image_path: str) -> str:
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
        if self.max_steps and self.max_steps > 1 and (step / (self.max_steps - 1) > 0.7):
            complete_str = "You must finish this task and submit as soon as possible!"
        prompt_text = (
            f"""{context}\n{'~' * 10}\nHistory: {history_str}\n{'~' * 10}\n"""
            f"Current Step #{step}, Phase: {phase}\n{complete_str}\n"
            f"[Objective] Your goal is to perform research on the following topic: {research_topic}\n"
            f"Feedback: {feedback}\nNotes: {notes_str}\n"
            f"Your previous command was: {self.prev_comm}. Make sure your new output is very different.\n"
            f"Please produce a single command below:\n"
        )

        api_key = self.openai_api_key or os.getenv("OHMYGPT_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise Exception("No API key provided for single look reflection.")

        client = OpenAI(
            base_url=OPENAI_COMPAT_BASE_URL,
            api_key=api_key,
            timeout=120.0,
            max_retries=3,
        )
        data_url = self._image_to_data_url(image_path)
        messages = [
            {"role": "system", "content": sys_prompt + "\n\n" + prompt_text},
            {"role": "user", "content": [{"type": "image_url", "image_url": {"url": data_url}}]},
        ]

        last_err = None
        completion = None
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
        if completion is None:
            raise Exception("Single look reflection request failed without completion.")

        model_resp = completion.choices[0].message.content
        print("^" * 50, phase, "^" * 50)
        model_resp = self.clean_text(model_resp)
        self.prev_comm = model_resp
        self.history.append((None, f"Step #{step}, Phase: {phase}, Feedback: {feedback}, Your response: {model_resp}"))
        if len(self.history) >= self.max_hist_len:
            self.history.pop(0)
        return model_resp

    def reflect(self, image_path: str):
        """
        对单张 look 图片做 reflect，返回 LOOK_REFLECTION_RESULT block（字符串）或 None
        """
        self.reset()
        self.image_path = image_path or ""

        if not image_path:
            return None

        research_topic = "Single-look reflection and decision (keep or delete)."
        for _i in range(self.max_steps):
            resp = self._inference_with_image(
                research_topic=research_topic,
                phase="single look reflection",
                step=_i,
                image_path=image_path,
                feedback="",
            )
            if "```LOOK_REFLECTION_RESULT" in resp:
                result = extract_prompt(resp, "LOOK_REFLECTION_RESULT")
                self.reset()
                return result

        self.reset()
        return None


class ChapterReflectAgent(BaseAgent):
    """
    章节图片淘汰 Agent
    任务：在一个 chapter 的图片（look_xx）完整导入后，检查是否存在
    - 彼此重复/高度相似
    - 与主题/子主题不符合
    输出：需要淘汰的图片序号/文件名
    """
    def __init__(self, model="gpt-4o-mini", notes=None, max_steps=8, openai_api_key=None):
        # max_steps 默认较小：该任务通常 1-2 次即可收敛
        super().__init__(model, notes, max_steps, openai_api_key)
        self.phases = ["chapter image reduction"]
        self.brand = ""
        self.theme = ""
        self.sub_theme = ""
        self.image_paths = []
        self.design_chapter_text = ""

    def context(self, phase):
        if phase not in self.phases:
            raise Exception(f"Invalid phase: {phase}")

        # 用文件名建立“序号 <-> 图片”的稳定映射，避免模型/人理解偏差
        mapping_lines = []
        for idx, p in enumerate(self.image_paths or [], start=1):
            mapping_lines.append(f"{idx}. {os.path.basename(p)}")
        mapping_str = "\n".join(mapping_lines) if mapping_lines else "(no images provided)"

        parts = [
            f"[ Input information ] This pdf contains fashion design works created for the {self.brand or '<brand>'}, "
            f"under the sub-theme {self.sub_theme or '<sub-theme>'} of the main theme {self.theme or '<theme>'}.\n\n",
        ]
        if self.design_chapter_text:
            parts.append(
                "[ Chapter design brief ] The following is the design concept for this chapter (design_chapter.txt). Use it to judge whether each image aligns with the chapter direction:\n"
                f"{self.design_chapter_text.strip()}\n\n"
            )
        parts.append(
            f"[ Images order ] The images are provided in the following serial-number order. Use these numbers when deciding deletions.\n"
            f"{mapping_str}\n"
        )
        return "".join(parts)

    def phase_prompt(self, phase):
        if phase not in self.phases:
            raise Exception(f"Invalid phase: {phase}")
        return (
            "[ Role Definition ] Now, assume you are a top fashion designer.\n\n"
            "[ Task Information ] Please reduce those design images that are identical to each other and do not conform to the theme. "
            "Start from the first image numbered 1 until the last image.\n\n"
            "[ Output information ] You need to list the serial numbers (and filenames) of the images to be deleted. "
            "When you recommend deleting any image, you MUST provide: (1) CATEGORY of the primary reason (REDUNDANCY / THEME_MISALIGNMENT / LOW_QUALITY / OTHER), "
            "(2) SPECIFIC_ISSUES describing each eliminated image's problem (use quantitative terms when possible), "
            "(3) SUGGESTIONS_FOR_REGENERATION so that replacement looks can be generated with clear direction.\n"
        )

    def role_description(self):
        return "a top fashion designer."

    def command_descriptions(self, phase):
        if phase not in self.phases:
            raise Exception(f"Invalid phase: {phase}")
        return (
            "When you have completed the reduction, submit it using:\n"
            "```IMAGE_REDUCTION_RESULT\n"
            "DELETE: <comma-separated serial numbers, e.g. 2,5,7 OR NONE>\n"
            "FILES: <comma-separated filenames that match the provided mapping OR NONE>\n"
            "CATEGORY: <PRIMARY_REASON: REDUNDANCY | THEME_MISALIGNMENT | LOW_QUALITY | OTHER>\n"
            "SPECIFIC_ISSUES:\n"
            "- <for each eliminated image: describe its specific problem, use quantitative terms when possible, e.g. \"look_03 ~85% similar to look_01 in silhouette\">\n"
            "- <one bullet per eliminated image or per distinct issue>\n"
            "SUGGESTIONS_FOR_REGENERATION:\n"
            "- <concrete design direction for replacement looks>\n"
            "- <what to avoid; what to emphasize>\n"
            "NOTES: <overall brief explanation>\n"
            "```\n"
            "Rules:\n"
            "- If nothing should be deleted, output DELETE: NONE, FILES: NONE; then CATEGORY, SPECIFIC_ISSUES and SUGGESTIONS_FOR_REGENERATION can be NONE or omitted.\n"
            "- If any image is to be deleted, you MUST fill CATEGORY, SPECIFIC_ISSUES and SUGGESTIONS_FOR_REGENERATION so that regeneration can be guided.\n"
            "- Only delete images that are duplicated/highly similar OR clearly off-theme.\n"
            "- Use the provided serial numbers and filenames exactly.\n"
            "You can only use a SINGLE command per inference turn.\n"
        )

    def example_command(self, phase):
        if phase not in self.phases:
            raise Exception(f"Invalid phase: {phase}")
        return (
            "```IMAGE_REDUCTION_RESULT\n"
            "DELETE: 3, 4\n"
            "FILES: look_03.jpg, look_04.jpg\n"
            "CATEGORY: REDUNDANCY\n"
            "SPECIFIC_ISSUES:\n"
            "- look_03: silhouette ~85% similar to look_01 (oversize coat + wide-leg trouser); color palette nearly identical\n"
            "- look_04: redundant styling variation of look_02; same double-breasted + high-waist combination\n"
            "SUGGESTIONS_FOR_REGENERATION:\n"
            "- Explore asymmetric or deconstructed silhouettes to differentiate from retained looks\n"
            "- Introduce contrast in fabric texture (e.g. matte vs. sheen) or introduce a distinct accent color\n"
            "- Avoid repeating the same outerwear + trouser formula; consider dress or layered alternatives\n"
            "NOTES: Removed redundant styling variations and duplicate outfits to maintain a concise, high-impact collection.\n"
            "```\n"
        )

    def _image_to_data_url(self, image_path: str) -> str:
        mime_type, _ = mimetypes.guess_type(image_path)
        if not mime_type:
            mime_type = "image/png"
        with open(image_path, "rb") as f:
            image_b64 = base64.b64encode(f.read()).decode("utf-8")
        return f"data:{mime_type};base64,{image_b64}"

    def _inference_with_images(self, research_topic, phase, step, image_paths, feedback="", temp=None):
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
        if self.max_steps and self.max_steps > 1 and (step / (self.max_steps - 1) > 0.7):
            complete_str = "You must finish this task and submit as soon as possible!"
        prompt_text = (
            f"""{context}\n{'~' * 10}\nHistory: {history_str}\n{'~' * 10}\n"""
            f"Current Step #{step}, Phase: {phase}\n{complete_str}\n"
            f"[Objective] Your goal is to perform research on the following topic: {research_topic}\n"
            f"Feedback: {feedback}\nNotes: {notes_str}\n"
            f"Your previous command was: {self.prev_comm}. Make sure your new output is very different.\n"
            f"Please produce a single command below:\n"
        )

        api_key = self.openai_api_key or os.getenv("OHMYGPT_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise Exception("No API key provided for image reduction.")

        # 多图任务更容易受网络/代理影响，适当提高超时并开启重试
        client = OpenAI(
            base_url=OPENAI_COMPAT_BASE_URL,
            api_key=api_key,
            timeout=180.0,
            max_retries=3,
        )

        content_list = []
        for p in image_paths:
            data_url = self._image_to_data_url(p)
            content_list.append({"type": "image_url", "image_url": {"url": data_url}})

        messages = [
            {"role": "system", "content": sys_prompt + "\n\n" + prompt_text},
            {"role": "user", "content": content_list},
        ]

        last_err = None
        completion = None
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
        if completion is None:
            raise Exception("Image reduction request failed without completion.")

        model_resp = completion.choices[0].message.content
        print("^" * 50, phase, "^" * 50)
        model_resp = self.clean_text(model_resp)
        self.prev_comm = model_resp
        self.history.append((None, f"Step #{step}, Phase: {phase}, Feedback: {feedback}, Your response: {model_resp}"))
        if len(self.history) >= self.max_hist_len:
            self.history.pop(0)
        return model_resp

    def reduce_images(self, image_paths, brand, theme, sub_theme, chapter_dir=None):
        """
        对一个章节的多张图片做淘汰建议
        chapter_dir: 章节目录路径，若提供则读取 design_chapter.txt 并入上下文
        返回：IMAGE_REDUCTION_RESULT block（字符串），或 None
        """
        self.reset()
        self.image_paths = list(image_paths or [])
        self.brand = brand or ""
        self.theme = theme or ""
        self.sub_theme = sub_theme or ""
        self.design_chapter_text = ""
        if chapter_dir:
            design_chapter_path = os.path.join(chapter_dir, "design_chapter.txt")
            if os.path.isfile(design_chapter_path):
                try:
                    with open(design_chapter_path, "r", encoding="utf-8") as f:
                        self.design_chapter_text = f.read()
                except Exception:
                    pass

        if not self.image_paths:
            return "DELETE: NONE\nFILES: NONE\nNOTES: No images provided."

        research_topic = (
            f"Brand: {self.brand}\n"
            f"Main theme: {self.theme}\n"
            f"Sub-theme (chapter): {self.sub_theme}\n"
            f"Task: remove duplicate / off-theme images from the chapter set."
        )

        for _i in range(self.max_steps):
            resp = self._inference_with_images(
                research_topic=research_topic,
                phase="chapter image reduction",
                step=_i,
                image_paths=self.image_paths,
                feedback="",
            )
            if "```IMAGE_REDUCTION_RESULT" in resp:
                result = extract_prompt(resp, "IMAGE_REDUCTION_RESULT")
                self.reset()
                return result

        # 如果达到最大尝试次数仍未获得结果
        self.reset()
        return None


class CollectionReflectAgent(BaseAgent):
    """
    Collection-reflection Agent
    任务：在整套 collection 的图片（跨多个 chapter/group）都导入后，检查是否存在
    - 彼此重复/高度相似
    - 与主题不符合

    说明：
    - 该 Agent 只给出“建议删除的序号”，不做真实删除
    - 该 Agent 的判断应与 single-look / group-reflection 相互独立，不依赖其输出
    """
    def __init__(self, model="gpt-4o-mini", notes=None, max_steps=8, openai_api_key=None):
        super().__init__(model, notes, max_steps, openai_api_key)
        self.phases = ["collection reflection"]
        self.brand = ""
        self.theme = ""
        self.image_paths = []
        self.theme_analysis_text = ""

    def context(self, phase):
        if phase not in self.phases:
            raise Exception(f"Invalid phase: {phase}")

        mapping_lines = []
        for idx, p in enumerate(self.image_paths or [], start=1):
            mapping_lines.append(f"{idx}. {os.path.basename(p)}")
        mapping_str = "\n".join(mapping_lines) if mapping_lines else "(no images provided)"

        parts = [
            f"[ Input information ] The pdf contains a series of {len(self.image_paths or [])} fashion design works "
            f"created for the {self.brand or '<brand>'} brand under the theme of {self.theme or '<theme>'}.\n\n",
        ]
        if self.theme_analysis_text:
            parts.append(
                "[ Theme analysis ] The following is the theme analysis (theme_analysis.txt) for this collection. Use it to judge whether each image and each chapter align with the overall theme:\n"
                f"{self.theme_analysis_text.strip()}\n\n"
            )
        parts.append(
            f"[ Images order ] The images are provided in the following serial-number order. "
            f"Use these numbers when deciding deletions.\n"
            f"{mapping_str}\n"
        )
        return "".join(parts)

    def phase_prompt(self, phase):
        if phase not in self.phases:
            raise Exception(f"Invalid phase: {phase}")
        return (
            "[ Role Definition ] Now, assume you are a top fashion designer.\n\n"
            "[ Task Information ] Please reduce those design images that are identical to each other and do not conform to the theme. "
            "Start from the first image numbered 1 until the last image.\n\n"
            "[ Output information ] You need to list the serial numbers of the images to be deleted.\n"
        )

    def role_description(self):
        return "a top fashion designer."

    def command_descriptions(self, phase):
        if phase not in self.phases:
            raise Exception(f"Invalid phase: {phase}")
        return (
            "When you have completed the collection reflection, submit it using:\n"
            "```COLLECTION_REFLECTION_RESULT\n"
            "DELETE: <comma-separated serial numbers, e.g. 2,5,7 OR NONE>\n"
            "FILES: <comma-separated filenames that match the provided mapping OR NONE>\n"
            "NOTES: <one short line explaining the main reasons>\n"
            "```\n"
            "Rules:\n"
            "- If nothing should be deleted, you MUST output DELETE: NONE and FILES: NONE\n"
            "- Only delete images that are duplicated/highly similar OR clearly off-theme\n"
            "- Use the provided serial numbers and filenames exactly\n"
            "You can only use a SINGLE command per inference turn.\n"
        )

    def example_command(self, phase):
        if phase not in self.phases:
            raise Exception(f"Invalid phase: {phase}")
        return (
            "```COLLECTION_REFLECTION_RESULT\n"
            "DELETE: 2,5\n"
            "FILES: look_02.png, look_05.png\n"
            "NOTES: 2 is near-duplicate of 1; 5 is off-theme compared to the collection theme.\n"
            "```\n"
        )

    def _image_to_data_url(self, image_path: str) -> str:
        mime_type, _ = mimetypes.guess_type(image_path)
        if not mime_type:
            mime_type = "image/png"
        with open(image_path, "rb") as f:
            image_b64 = base64.b64encode(f.read()).decode("utf-8")
        return f"data:{mime_type};base64,{image_b64}"

    def _inference_with_images(self, research_topic, phase, step, image_paths, feedback="", temp=None):
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
        if self.max_steps and self.max_steps > 1 and (step / (self.max_steps - 1) > 0.7):
            complete_str = "You must finish this task and submit as soon as possible!"
        prompt_text = (
            f"""{context}\n{'~' * 10}\nHistory: {history_str}\n{'~' * 10}\n"""
            f"Current Step #{step}, Phase: {phase}\n{complete_str}\n"
            f"[Objective] Your goal is to perform research on the following topic: {research_topic}\n"
            f"Feedback: {feedback}\nNotes: {notes_str}\n"
            f"Your previous command was: {self.prev_comm}. Make sure your new output is very different.\n"
            f"Please produce a single command below:\n"
        )

        api_key = self.openai_api_key or os.getenv("OHMYGPT_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise Exception("No API key provided for collection reflection.")

        client = OpenAI(
            base_url=OPENAI_COMPAT_BASE_URL,
            api_key=api_key,
            timeout=240.0,
            max_retries=3,
        )

        content_list = []
        for p in image_paths:
            data_url = self._image_to_data_url(p)
            content_list.append({"type": "image_url", "image_url": {"url": data_url}})

        messages = [
            {"role": "system", "content": sys_prompt + "\n\n" + prompt_text},
            {"role": "user", "content": content_list},
        ]

        last_err = None
        completion = None
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
        if completion is None:
            raise Exception("Collection reflection request failed without completion.")

        model_resp = completion.choices[0].message.content
        print("^" * 50, phase, "^" * 50)
        model_resp = self.clean_text(model_resp)
        self.prev_comm = model_resp
        self.history.append((None, f"Step #{step}, Phase: {phase}, Feedback: {feedback}, Your response: {model_resp}"))
        if len(self.history) >= self.max_hist_len:
            self.history.pop(0)
        return model_resp

    def reflect_collection(self, image_paths, brand, theme, workflow_dir=None):
        """
        对整套 collection 的多张图片做淘汰建议
        workflow_dir: 工作流目录路径，若提供则读取 theme_analysis.txt 并入上下文
        返回：COLLECTION_REFLECTION_RESULT block（字符串），或 None
        """
        self.reset()
        self.image_paths = list(image_paths or [])
        self.brand = brand or ""
        self.theme = theme or ""
        self.theme_analysis_text = ""
        if workflow_dir:
            theme_analysis_path = os.path.join(workflow_dir, "theme_analysis.txt")
            if os.path.isfile(theme_analysis_path):
                try:
                    with open(theme_analysis_path, "r", encoding="utf-8") as f:
                        self.theme_analysis_text = f.read()
                except Exception:
                    pass

        if not self.image_paths:
            return "DELETE: NONE\nFILES: NONE\nNOTES: No images provided."

        research_topic = (
            f"Brand: {self.brand}\n"
            f"Theme: {self.theme}\n"
            f"Task: remove duplicate / off-theme images from the full collection set."
        )

        for _i in range(self.max_steps):
            resp = self._inference_with_images(
                research_topic=research_topic,
                phase="collection reflection",
                step=_i,
                image_paths=self.image_paths,
                feedback="",
            )
            if "```COLLECTION_REFLECTION_RESULT" in resp:
                result = extract_prompt(resp, "COLLECTION_REFLECTION_RESULT")
                self.reset()
                return result

        self.reset()
        return None

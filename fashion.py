from utils import *
from inference import *
import random, string
import os
import re
import base64
import mimetypes
import httpx
import openai


# 前序阶段（主题 / 概念 / 元素）共用：新颖和风格必须是评分器 DesignMerit 会给高分的那种。
_UPSTREAM_BOLD_CONCEPTION = (
    "Creative stance (scored as DesignMerit): stay inside the given theme and sub-theme. "
    "Novelty and style are one identifying idea made newer and more unmistakable than this house's "
    "interchangeable wardrobe. The judge tests five things: the idea still identifies the look after "
    "color, material, and brand words are swapped; it is anchored on a part or layer; the craft is a "
    "surface or an edge, not factory finishing; the combination is not an ordinary layering formula; "
    "and that one idea occupies the paragraph, so the collection's style is readable. "
    "A mood adjective, a theme duality, or a second theme's garment is not a stronger style. "
    "Timid ready-to-wear finishing and a polite restatement of the brief fail those tests."
)

# 生成流各阶段共用：前卫可以改轮廓和结构，不能写成明显的性擦边。
_CLOTHED_RUNWAY = (
    "Clothed runway (hard): the woman is fully dressed for a fashion photograph. "
    "Clothes cover the chest, the torso, and the legs. "
    "An open neckline, a cutaway, or a low front still has a shirt, a camisole, or a bodice on the body. "
    "Do not describe bare chest, bare breasts, lingerie worn as the outfit, sheer cloth that shows the body, "
    "or skin used as the design. Do not use seductive, sensual, or erotic framing. "
    "A bold opening, a disrupted surface, or a close-cut cloth stays a garment."
)


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
                f"{_UPSTREAM_BOLD_CONCEPTION}\n"
                f"{_CLOTHED_RUNWAY}\n"
                "Analyze the given theme and break it down into meaningful key aspects that can guide the design process.\n"
                "Write all submitted analysis in English.\n"
                "Key aspects are a holistic analytical layer—not a 1:1 chapter list. "
                "Name tensions, ruptures, and visual extremes the theme already contains; do not flatten it into a safe mood board.\n"
                "Chapter sub-themes (exactly Num chapters) must synthesize across ALL key aspects and inspiration, "
                "each offering a distinct, daring narrative angle for one design chapter—"
                "a brief a creative director would risk, not a recap of expected cruise/workwear tropes.\n"
                "When Description is provided: first distill design-relevant key elements from it "
                "(heritage facts, location/show context, silhouettes, materials, codes, accessories, mood, cultural signals—"
                "only what helps refine the collection theme). Submit these via DESCRIPTION_KEY_ELEMENTS before the final analysis.\n"
                "Then fuse those extracted elements into Theme, Inspiration, Key aspects, and Sub-themes; do not ignore Description facts, "
                "but do not paste Description verbatim—synthesize for downstream design use.\n"
            )
        return phase_str

    def role_description(self):
        return (
            "a fashion theme analyst and cultural researcher who finds the theme's most daring "
            "but still on-brief design tensions, never a conservative recap."
        )

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
                "[Collection title and overview; must reflect fused Description-derived elements. "
                "Name the daring tension the collection will make visible, not a polite slogan.]\n\n"
                "**Inspiration:**\n"
                "[Designer, historical sources, show context; weave in extracted key elements in paragraph form.]\n\n"
                "**Key aspects of the theme:**\n"
                "[4–8 analytical aspects (holistic theme decomposition). Each: bold heading **Aspect Name:** then a paragraph. "
                "These are NOT chapter titles and must NOT be copied 1:1 as sub-themes.]\n\n"
                f"**Sub-themes for chapter development:**\n"
                f"[Exactly {self.num_chapters} chapter-ready sub-themes. Each: bold heading **Sub-theme title:** then 2–3 sentences "
                "stating a distinct, daring chapter narrative that draws holistically from Theme, Inspiration, and multiple Key aspects—"
                "not one aspect per sub-theme, and not a conservative wardrobe recap.]\n\n"
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
            "Example command for theme analysis (format only; actual sub-themes should be more daring "
            "and still strictly on the given brief):\n"
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
                "STAGE: CONCEPT SYSTEM. From the theme, the theme analysis, and this one sub-theme, "
                "build ONE complete concept system for the chapter.\n"
                f"{_UPSTREAM_BOLD_CONCEPTION}\n"
                f"{_CLOTHED_RUNWAY}\n"
                "The system states the chapter's belief, the silhouette rule, the garment families, "
                "the cloth and color rule, how each look changes the idea, and the ambiance that frames it.\n"
                "This stage owns that system. It does not write a photograph, and it does not write element cards. "
                "The next stage extracts camera-ready facts from this system.\n"
                "Stay at runway scale. A polite capsule of expected separates is not a system.\n"
                "In The Looks, name 2–4 look logics. Each logic names its garment family and the operation "
                "that makes it a different idea: proportion, a surface that is the look, a volume that changes the outline, "
                "a repeated or broken part, a cloth or closure doing an unusual job, or an opening onto a clothed inner layer. "
                "These are kinds of force, not a menu. "
                "Each next logic changes the idea itself, still inside this sub-theme, still a garment on a dressed body.\n"
                "Concept, Ambiance, and Analysis may use the theme's language. "
                "The Looks stay as system rules, not cloth-level camera notes.\n"
            )
        return phase_str

    def role_description(self):
        return (
            "a creative director who turns one theme into one complete chapter system: "
            "belief, silhouette, garment families, cloth and color, and how the looks change the idea."
        )

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
                "    [The complete system: the chapter's belief, and the rules that bind silhouette, "
                "garment family, surface, and color. State the leap. Do not write a photograph.]\n\n"
                "*   **The Looks:**\n"
                "    *   **Silhouette:**\n"
                "        [Bold, theme-true silhouette characteristics—risk proportion, not a safe default.]\n\n"
                "    *   **Garments:**\n"
                "        [Garments and pieces that carry the leap, not an interchangeable capsule.]\n\n"
                "    *   **Fabric & Color:**\n"
                "        [Palette and surfaces that make this theme's idea readable. A newer combination stays one garment identity.]\n\n"
                "    *   **Identifying ideas (per look):**\n"
                "        [2–4 look logics inside the system. Each names a garment family and the operation "
                "that makes it a different idea. Leave cloth placement, body zone, and color-on-a-part "
                "to the element stage.]\n\n"
                "*   **Ambiance:**\n"
                "    *   **Lighting:**\n"
                "        [Lighting approach.]\n\n"
                "    *   **Music:**\n"
                "        [Musical direction.]\n\n"
                "*   **Analysis:**\n"
                "    [Analytical insight into this chapter's role and significance.]\n\n"
                "You can only use a SINGLE command per inference turn. Do not use more than one command per inference.\n"
                "When performing a command, make sure to include the three ticks (```) at the top and bottom ```COMMAND\ntext\n``` "
                "where COMMAND is the specific command you want to run (e.g. DESIGN_CONCEPT, DIALOGUE).\n\n"
                f"{self.example_command(phase)}"
            )
        return ""

    def example_command(self, phase):
        if phase not in self.phases:
            raise Exception(f"Invalid phase: {phase}")

        return (
            "Example command for a concept system (format only—do not copy this tailoring recap; "
            "build a bolder system for the actual theme. This is not an element card):\n"
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
                "    *   **Identifying ideas (per look):**\n"
                "        Look 1 — greatcoat family, the edge itself is the idea. "
                "Look 2 — coat worn open over a graphic shirt, a second readable layer. "
                "Look 3 — coat worn open over a close column of the same palette. "
                "Look 4 — the coat's allover surface is the idea, a different operation from Look 1.\n\n"
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
                "STAGE: ELEMENT EXTRACTION. The concept below is finished. "
                "Take concrete design elements out of it. Do not rewrite it as another concept.\n\n"
                f"Overall Theme (boundary only): {self.theme}\n\n"
                f"Theme Analysis (boundary only): {self.theme_analysis}\n\n"
                f"Finished concept system:\n{design_concepts_str}\n"
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
                "STAGE: ELEMENT EXTRACTION. Read the finished concept system and take design elements out of it.\n"
                f"{_CLOTHED_RUNWAY}\n"
                "The theme only bounds the extraction. The facts come from the concept's silhouette, "
                "garment families, cloth and color, and look logics.\n"
                "Do not write a concept essay, a mood, a function, or a restatement of the theme. "
                "A sentence that only says the look is archival, nocturnal, authoritative, documentary, "
                "or still recognizable after a color or cloth swap is not an element.\n"
                "Give one Identifying Design Idea to each look logic in the concept. "
                "Do not drop a look logic, and do not add a parallel idea the concept did not claim.\n"
                "Each identifying element is five visible facts:\n"
                "1. Garment.\n"
                "2. Body zone.\n"
                "3. Visible change: what the photograph loses if this operation is removed.\n"
                "4. Cloth name.\n"
                "5. Color name.\n"
                "Support lines are facts too: one named cloth, one named color, or one secondary piece "
                "that serves an identifying element. Name the category after that fact. "
                "Twilight, archive, authority, and surface tension are not category names.\n"
                "These are not identifying elements: piping, a quiet bodice under a coat, "
                "a cropped jacket with straight trousers, a plain column coat, topstitch, "
                "a hidden placket, or brand hardware.\n"
                "Write the identifying elements as one weighted candidate set. "
                "Every Identifying Design Idea carries a percentage weight on its title line. "
                "The weights show relative importance inside that set.\n"
            )
        return phase_str

    def role_description(self):
        return (
            "a design element extractor who turns a finished concept system into "
            "concrete garment facts a camera can see."
        )

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
                "**Candidate elements**\n\n"
                "1. Identifying Design Ideas | [garment and visible change] | [Weight%]\n"
                "Garment: [one garment from a concept look logic]\n"
                "Body zone: [where on the body]\n"
                "Visible change: [what the photograph loses if this operation is removed]\n"
                "Cloth: [cloth name]\n"
                "Color: [color name]\n"
                "From concept: [which look logic]\n\n"
                "1. Identifying Design Ideas | [the next concept look logic] | [Weight%]\n"
                "[Same five labels, and a percentage weight on this title line too.]\n\n"
                "2. [Named cloth, named color, or secondary piece] | [the fact] \n"
                "[Same five labels. This fact only serves one identifying element.]\n\n"
                "Format rules:\n"
                "- One Identifying Design Idea for each look logic in the concept.\n"
                "- Five labeled facts per element. No concept sentence, no mood, no function, no metaphor.\n"
                "- Use '|' on every identifying title line: category | element | weight%. "
                "The identifying lines are one weighted candidate set.\n"
                "- A support category is named after its fact. Do not invent a theme title for it.\n"
                "- Bare skin, piping, a plain column coat, and factory finishing are not identifying elements.\n"
                "You can only use a SINGLE command per inference turn. Do not use more than one command per inference.\n"
                "When performing a command, make sure to include the three ticks (```) at the top and bottom ```COMMAND\ntext\n``` "
                "where COMMAND is the specific command you want to run (e.g. DESIGN_ELEMENTS, DIALOGUE).\n\n"
                f"{self.example_command(phase)}"
            )
        return ""

    def example_command(self, phase):
        if phase not in self.phases:
            raise Exception(f"Invalid phase: {phase}")
        return (
            "Example command for design elements. Format reference only. "
            "Fill every label from the finished concept. Do not copy the bracket text, "
            "and do not add a sentence outside the labels:\n"
            "```DESIGN_ELEMENTS\n"
            "**Candidate elements**\n\n"
            "1. Identifying Design Ideas | [Garment and the visible change] | [Weight%]\n"
            "Garment: [garment named in one concept look logic]\n"
            "Body zone: [where on the body]\n"
            "Visible change: [what the photograph loses if this operation is removed]\n"
            "Cloth: [cloth name from the concept]\n"
            "Color: [color name from the concept]\n"
            "From concept: [which look logic]\n\n"
            "1. Identifying Design Ideas | [A different garment and visible change from the next look logic] | [Weight%]\n"
            "Garment: [garment]\n"
            "Body zone: [where]\n"
            "Visible change: [photograph change]\n"
            "Cloth: [cloth]\n"
            "Color: [color]\n"
            "From concept: [the next look logic]\n\n"
            "2. [Cloth or color fact] | [That fact serving the first element]\n"
            "Garment: [the same garment]\n"
            "Body zone: [where the support fact sits]\n"
            "Visible change: [the smaller change this fact adds]\n"
            "Cloth: [cloth]\n"
            "Color: [color]\n"
            "From concept: [the system rule it comes from]\n"
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
        self.brand = ""
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
                "Already generated in this chapter (update the identifying idea; do not only recolor or relabel a previous look):\n"
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
                f"Brand: {self.brand}\n"
                f"Design Target: {self.design_target_prompt}\n"
                f"Main Theme: {self.theme}\n\n"
                f"Concept system to assemble inside:\n{design_context_text}\n\n"
                f"Weighted element list. Select from this list:\n{elements_text}\n"
                "\nAssemble for this brand and this concept. "
                "Choose one weighted candidate, and at most one support fact that serves it. "
                "Use that candidate's garment, body zone, visible change, cloth, and color. "
                "After the clothes are assembled, render them: add texture, pattern, and line where they belong to this brand and concept, "
                "and adjust details so they sit on this garment. "
                "Do not copy a concept sentence or a mood into the description. "
                "Do not replace the selected element with a plain coat, and do not dump the whole list into one outfit. "
                "If the outer garment is open, the opening shows a shirt, a camisole, or a bodice, not bare skin.\n"
            )
        return ""

    @staticmethod
    def _strip_key_elements_section(look_desc: str) -> str:
        """丢掉段落之后的 Key elements 清单，最终结果只保留可直接生成的正文。"""
        parts = re.split(r"(?im)^\s*key\s+elements\s*:\s*$", look_desc or "", maxsplit=1)
        return parts[0].rstrip()

    @staticmethod
    def _summarize_look_for_diversity(look_desc: str) -> str:
        text = LookDescriptionAgent._strip_key_elements_section(look_desc).strip()
        if not text:
            return ""
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        prefixes = {
            "please generate female models and the matching clothing for them.",
            "one photograph of one woman at one moment, from one camera. show only what that camera sees on her body. no collage, no flat lay, no product shot, no extra views, no text.",
            "one photograph of one woman at one moment, from one camera in front of her face. she faces the camera. front view only, not from behind. show only what that camera sees on her body. no collage, no flat lay, no product shot, no extra views, no text.",
        }
        body_lines = [
            ln for ln in lines
            if ln.lower() not in prefixes and not re.match(r"(?i)^look[\s_]*\d+\b", ln)
        ]
        paragraph = " ".join(body_lines) if body_lines else " ".join(lines)
        compact = re.sub(r"\s+", " ", paragraph).strip()
        if not compact:
            return ""
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
                    "DIVERSITY REQUIREMENT: Select a different weighted candidate from the element list "
                    "than the looks already generated in this chapter. "
                    "Do not only recolor, rematerial, or relabel the previous look.\n"
                )
            phase_str = (
                "Assemble ONE runway look for this brand, inside the concept, from the weighted element list.\n"
                f"{diversity_str}"
                "Selection: take one weighted candidate. The garment, body zone, visible change, cloth, and color come from that candidate.\n"
                "Assembly: put that candidate on one woman, front view, full figure, one wearable outfit.\n"
                "Rendering, after the clothes are assembled: supplement texture, pattern, and line, "
                "and make targeted detail adjustments that belong to this brand and this concept. "
                "Rendering sits on the selected garment. It does not replace the selected element.\n"
                "Length is not limited. The ending is not prescribed.\n"
                f"{_CLOTHED_RUNWAY}\n"
                "Rules:\n"
                "1. Front view only. Name the face, the neckline, the front of the clothes, and the shoes. "
                "Do not invent a rear view, a crop, a hidden interior, or unstated footwear.\n"
                "2. Do not write chapter narrative, scene metaphors, stance, or a house logo. The brand enters through the clothes and the rendering.\n"
                "3. Continuous prose. No numbered sections, no Key elements list, no Look number, and no look title.\n"
                "4. Name the cloth directly. Do not write looks like, appears to be, tinsel-like, or chainmail-like.\n"
                "5. Do not ask for a collage, a flat lay, a product shot, a second view, a rear view, or text.\n"
                "Do not copy the example.\n"
            )
        return phase_str

    def role_description(self):
        return (
            "a look assembler who selects one weighted element for a brand and a concept, "
            "builds it into one worn outfit, then renders texture, pattern, line, and detail."
        )

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
                "One photograph of one woman at one moment, from one camera in front of her face. She faces the camera. Front view only, not from behind. Show only what that camera sees on her body. No collage, no flat lay, no product shot, no extra views, no text.\n\n"
                "[The assembled look, then its rendering. Length is not limited. The ending is not prescribed. "
                "No Look number and no look title. Full figure, front view, the selected element on the body, "
                "then texture, pattern, line, and the detail adjustments. The chest stays clothed. "
                "No numbered sections, no crop, no rear view, no invented logo. "
                "Do not add a Key elements section.]\n\n"
                "You can only use a SINGLE command per inference turn. Do not use more than one command per inference.\n"
                "When performing a command, make sure to include the three ticks (```) at the top and bottom ```COMMAND\ntext\n``` "
                "where COMMAND is the specific command you want to run (e.g. LOOK_DESCRIPTION, DIALOGUE).\n\n"
                f"{self.example_command(phase)}"
            )
        return ""

    def example_command(self, phase):
        if phase not in self.phases:
            raise Exception(f"Invalid phase: {phase}")
        return (
            "Example command for look assembly. Format only. "
            "Select the real garment from the element list, then render it. Do not copy this coat:\n"
            "```LOOK_DESCRIPTION\n"
            "One photograph of one woman at one moment, from one camera in front of her face. She faces the camera. Front view only, not from behind. Show only what that camera sees on her body. No collage, no flat lay, no product shot, no extra views, no text.\n\n"
            "A woman faces the camera in a hip-length camel wool coat, single-breasted, with a soft notch lapel "
            "and a straight hem, worn open over a black fine-gauge crewneck and a narrow black wool trouser. "
            "The wool carries a fine diagonal grain, a narrow woven line follows the lapel edge, "
            "and the cuff button spacing is tightened. Black leather pumps.\n"
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

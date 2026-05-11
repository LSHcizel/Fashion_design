"""
时尚设计工作流编排
参考 AgentLaboratory 的设计模式，管理多个 Agent 的协作流程
"""
from __future__ import annotations

import os
import time
import pickle
import argparse
import yaml
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from copy import copy
from fashion import (
    ThemeAnalysisAgent,
    ConceptBrainstormingAgent,
    DesignElementsAgent,
    LookDescriptionAgent,
    SingleLookReflectAgent,
    ChapterReflectAgent,
    CollectionReflectAgent,
)
from utils import extract_prompt
from elimination_handler import EliminationHandler
from plugins.text_description_evaluator.design_text_evaluator_api import DesignTextEvaluator

DEFAULT_LLM_BACKBONE = "gemini-3-flash-preview"
RESEARCH_DIR_PATH = "fashion_research_dir"
STATE_SAVES_DIR = "state_saves"

def create_dated_run_dir(base_dir: str):
    """
    在 base_dir 下创建“当前日期”命名的运行目录。
    - 目录名格式：YYYY-MM-DD
    - 若当天目录已存在（同日多次运行），追加后缀：YYYY-MM-DD_02, _03 ...
    """
    date_str = datetime.now().strftime("%Y-%m-%d")
    run_dir = os.path.join(base_dir, date_str)
    if not os.path.exists(run_dir):
        os.makedirs(run_dir, exist_ok=True)
        return run_dir

    # 同一天多次运行：追加递增后缀
    suffix = 2
    while True:
        candidate = os.path.join(base_dir, f"{date_str}_{suffix:02d}")
        if not os.path.exists(candidate):
            os.makedirs(candidate, exist_ok=True)
            return candidate
        suffix += 1

def parse_sub_themes_from_theme_analysis(theme_analysis_text: str):
    """
    从 ThemeAnalysisAgent 的输出中提取子主题列表。
    约定：子主题来自 **Key aspects of the theme:** 下面的加粗标题，例如 **Gender Fluidity:**
    """
    if not theme_analysis_text:
        return []

    # 尽量缩小解析范围到 Key aspects 之后，降低误匹配
    key_marker = "**Key aspects of the theme:**"
    if key_marker in theme_analysis_text:
        tail = theme_analysis_text.split(key_marker, 1)[1]
    else:
        tail = theme_analysis_text

    # 匹配 **Something:** 这种格式（冒号在加粗范围内）
    matches = re.findall(r"\*\*([^*]+?):\*\*", tail)
    sub_themes = []
    seen = set()
    for m in matches:
        name = m.strip()
        if not name or name in seen:
            continue
        seen.add(name)
        sub_themes.append(name)
    return sub_themes


class FashionWorkflow:
    def __init__(
        self,
        design_target_prompt,
        theme,
        brand=None,
        openai_api_key=None,
        max_steps=20,
        agent_model_backbone=DEFAULT_LLM_BACKBONE,
        notes=list(),
        human_in_loop_flag=None,
        workflow_dir=None,
        workflow_index=0,
        except_if_fail=False,
        num_chapters=4,
        num_looks=1,
        text_evaluator_config: TextEvaluatorConfig | None = None,
    ):
        """
        初始化时尚设计工作流
        @param design_target_prompt: (str) 设计目标提示
        @param theme: (str) 主题描述
        @param openai_api_key: (str) API 密钥
        @param max_steps: (int) 每个阶段的最大步数
        @param agent_model_backbone: (str or dict) 模型配置
        @param notes: (list) 任务备注
        @param human_in_loop_flag: (dict) 人工介入标志
        @param workflow_dir: (str) 工作流目录
        @param workflow_index: (int) 工作流索引
        @param except_if_fail: (bool) 失败时是否抛出异常
        """
        self.workflow_dir = workflow_dir
        self.workflow_index = workflow_index
        self.max_steps = max_steps
        self.openai_api_key = openai_api_key
        self.except_if_fail = except_if_fail
        self.design_target_prompt = design_target_prompt
        self.theme = theme
        self.brand = brand
        self.num_chapters = num_chapters
        self.num_looks = num_looks
        self.model_backbone = agent_model_backbone
        self.notes = notes
        self.human_in_loop_flag = human_in_loop_flag if human_in_loop_flag else {
            "theme analysis": False,
            "concept brainstorming": False,
            "design elements proposal": False,
            "look description generation": False,
            "chapter image reduction": False,
            "collection reflection": False,
        }

        self.print_cost = True
        self.save = True
        self.verbose = True

        # 定义工作流阶段
        self.phases = [
            ("theme analysis", ["theme analysis"]),
            ("concept brainstorming", ["concept brainstorming"]),
            # design elements 和 look generation 将在循环中为每个 group 执行
        ]
        self.phase_status = dict()
        for phase, subtasks in self.phases:
            for subtask in subtasks:
                self.phase_status[subtask] = False

        # 阶段模型配置
        self.phase_models = dict()
        if type(agent_model_backbone) == str:
            for phase, subtasks in self.phases:
                for subtask in subtasks:
                    self.phase_models[subtask] = agent_model_backbone
        elif type(agent_model_backbone) == dict:
            self.phase_models = agent_model_backbone

        # 阶段统计信息
        self.statistics_per_phase = {
            "theme analysis": {"time": 0.0, "steps": 0.0},
            "concept brainstorming": {"time": 0.0, "steps": 0.0},
            "design elements proposal": {"time": 0.0, "steps": 0.0},
            "look description generation": {"time": 0.0, "steps": 0.0},
            "single look reflection": {"time": 0.0, "steps": 0.0},
            "chapter image reduction": {"time": 0.0, "steps": 0.0},
            "collection reflection": {"time": 0.0, "steps": 0.0},
        }
        # 存储各个 groups 的设计概念
        self.group_concepts = []

        # 每个 look 的评估/优化结果追踪
        # 结构: {(chapter_idx, look_number): {"passed": bool, "total_score": float, ...}}
        self.look_evaluation_results: dict = {}

        # 初始化各个 Agent
        model = self.phase_models.get("theme analysis", agent_model_backbone if isinstance(agent_model_backbone, str) else DEFAULT_LLM_BACKBONE)
        self.theme_analyzer = ThemeAnalysisAgent(
            model=model, notes=self.notes, max_steps=self.max_steps, openai_api_key=self.openai_api_key
        )
        model = self.phase_models.get("concept brainstorming", agent_model_backbone if isinstance(agent_model_backbone, str) else DEFAULT_LLM_BACKBONE)
        self.concept_designer = ConceptBrainstormingAgent(
            model=model, notes=self.notes, max_steps=self.max_steps, openai_api_key=self.openai_api_key
        )
        model = self.phase_models.get("design elements proposal", agent_model_backbone if isinstance(agent_model_backbone, str) else DEFAULT_LLM_BACKBONE)
        self.elements_specialist = DesignElementsAgent(
            model=model, notes=self.notes, max_steps=self.max_steps, openai_api_key=self.openai_api_key
        )
        model = self.phase_models.get("look description generation", agent_model_backbone if isinstance(agent_model_backbone, str) else DEFAULT_LLM_BACKBONE)
        self.look_stylist = LookDescriptionAgent(
            model=model, notes=self.notes, max_steps=self.max_steps, openai_api_key=self.openai_api_key, num_looks=self.num_looks
        )

        # 单图 reflect Agent（每个 look 生成后调用）
        model = self.phase_models.get("single look reflection", agent_model_backbone if isinstance(agent_model_backbone, str) else DEFAULT_LLM_BACKBONE)
        self.look_reflector = SingleLookReflectAgent(
            model=model, notes=self.notes, max_steps=6, openai_api_key=self.openai_api_key
        )

        # 章节图片淘汰 Agent（多图视觉输入，默认收敛更快）
        model = self.phase_models.get("chapter image reduction", agent_model_backbone if isinstance(agent_model_backbone, str) else DEFAULT_LLM_BACKBONE)
        self.chapter_image_reducer = ChapterReflectAgent(
            model=model, notes=self.notes, max_steps=8, openai_api_key=self.openai_api_key
        )

        # Collection-reflection Agent（跨所有 chapter 的整套图片评估）
        model = self.phase_models.get(
            "collection reflection",
            agent_model_backbone if isinstance(agent_model_backbone, str) else DEFAULT_LLM_BACKBONE,
        )
        self.collection_reflector = CollectionReflectAgent(
            model=model, notes=self.notes, max_steps=8, openai_api_key=self.openai_api_key
        )
        
        # 淘汰处理器（仅在有 workflow_dir 时初始化）
        self.elimination_handler = None
        if self.workflow_dir:
            self.elimination_handler = EliminationHandler(self.workflow_dir)

        # 文本评估优化器
        self.evaluator_config = text_evaluator_config or TextEvaluatorConfig()
        self.text_evaluator: DesignTextEvaluator | None = None
        if self.evaluator_config.enabled:
            self.text_evaluator = DesignTextEvaluator(
                api_key=self.evaluator_config.evaluator_api_key,
                api_base=self.evaluator_config.evaluator_api_base,
                model=self.evaluator_config.evaluator_model,
                temperature=self.evaluator_config.evaluator_temperature,
                rewriter_temperature=self.evaluator_config.rewriter_temperature,
            )

    def set_model(self, model):
        """设置所有 Agent 的模型"""
        self.theme_analyzer.set_model_backbone(model)
        self.concept_designer.set_model_backbone(model)
        self.elements_specialist.set_model_backbone(model)
        self.look_stylist.set_model_backbone(model)
        self.look_reflector.set_model_backbone(model)
        self.chapter_image_reducer.set_model_backbone(model)
        self.collection_reflector.set_model_backbone(model)

    def save_state(self, phase):
        """保存当前状态"""
        if not os.path.exists(STATE_SAVES_DIR):
            os.makedirs(STATE_SAVES_DIR)
        save_path = os.path.join(STATE_SAVES_DIR, f"FashionWorkflow_{self.workflow_index}.pkl")
        with open(save_path, "wb") as f:
            pickle.dump(self, f)
        if self.verbose:
            print(f"State saved to {save_path} after phase: {phase}")

    @classmethod
    def load_state(cls, workflow_index=0):
        """加载保存的状态"""
        save_path = os.path.join(STATE_SAVES_DIR, f"FashionWorkflow_{workflow_index}.pkl")
        if not os.path.exists(save_path):
            raise FileNotFoundError(f"State file not found: {save_path}")
        with open(save_path, "rb") as f:
            workflow = pickle.load(f)

        # 向后兼容：旧的 pkl 可能没有新增字段/Agent，这里补齐，避免后续调用报错
        if not hasattr(workflow, "brand"):
            workflow.brand = None
        if not hasattr(workflow, "look_reflector"):
            model = getattr(workflow, "phase_models", {}).get(
                "single look reflection",
                getattr(workflow, "model_backbone", DEFAULT_LLM_BACKBONE) if isinstance(getattr(workflow, "model_backbone", DEFAULT_LLM_BACKBONE), str) else DEFAULT_LLM_BACKBONE,
            )
            workflow.look_reflector = SingleLookReflectAgent(
                model=model,
                notes=getattr(workflow, "notes", []),
                max_steps=6,
                openai_api_key=getattr(workflow, "openai_api_key", None),
            )
        if not hasattr(workflow, "chapter_image_reducer"):
            model = getattr(workflow, "phase_models", {}).get(
                "chapter image reduction",
                getattr(workflow, "model_backbone", DEFAULT_LLM_BACKBONE) if isinstance(getattr(workflow, "model_backbone", DEFAULT_LLM_BACKBONE), str) else DEFAULT_LLM_BACKBONE,
            )
            workflow.chapter_image_reducer = ChapterReflectAgent(
                model=model,
                notes=getattr(workflow, "notes", []),
                max_steps=8,
                openai_api_key=getattr(workflow, "openai_api_key", None),
            )
        if not hasattr(workflow, "collection_reflector"):
            model = getattr(workflow, "phase_models", {}).get(
                "collection reflection",
                getattr(workflow, "model_backbone", DEFAULT_LLM_BACKBONE) if isinstance(getattr(workflow, "model_backbone", DEFAULT_LLM_BACKBONE), str) else DEFAULT_LLM_BACKBONE,
            )
            workflow.collection_reflector = CollectionReflectAgent(
                model=model,
                notes=getattr(workflow, "notes", []),
                max_steps=8,
                openai_api_key=getattr(workflow, "openai_api_key", None),
            )
        if not hasattr(workflow, "human_in_loop_flag"):
            workflow.human_in_loop_flag = {}
        if "chapter image reduction" not in workflow.human_in_loop_flag:
            workflow.human_in_loop_flag["chapter image reduction"] = False
        if "collection reflection" not in workflow.human_in_loop_flag:
            workflow.human_in_loop_flag["collection reflection"] = False

        if workflow.verbose:
            print(f"State loaded from {save_path}")
        return workflow

    def reset_agents(self):
        """重置所有 Agent 状态"""
        self.theme_analyzer.reset()
        self.concept_designer.reset()
        self.elements_specialist.reset()
        self.look_stylist.reset()
        self.look_reflector.reset()
        self.chapter_image_reducer.reset()
        self.collection_reflector.reset()

    @staticmethod
    def _parse_look_reflection_result(result_text: str) -> dict:
        """
        解析 LOOK_REFLECTION_RESULT，返回：
        { tier, action, info, final_fashion_design }
        """
        out = {"tier": "", "action": "", "info": "", "final_fashion_design": ""}
        if not result_text:
            return out
        m_tier = re.search(r"(?im)^\s*TIER\s*:\s*(.+?)\s*$", result_text)
        m_action = re.search(r"(?im)^\s*ACTION\s*:\s*(.+?)\s*$", result_text)
        m_info = re.search(r"(?im)^\s*INFO\s*:\s*(.+?)\s*$", result_text)
        m_final = re.search(r"(?is)^\s*FINAL_FASHION_DESIGN\s*:\s*(.+?)\s*$", result_text)
        if m_tier:
            out["tier"] = m_tier.group(1).strip()
        if m_action:
            out["action"] = m_action.group(1).strip()
        if m_info:
            out["info"] = m_info.group(1).strip()
        if m_final:
            out["final_fashion_design"] = m_final.group(1).strip()
        return out

    @staticmethod
    def _find_look_image(chapter_dir: str, look_number: int) -> str:
        """
        在 chapter_dir 内寻找对应 look_{NN} 的图片（png/jpg/jpeg/webp）
        优先按常见扩展名顺序匹配。
        """
        if not chapter_dir or not os.path.isdir(chapter_dir):
            return ""
        stem = f"look_{look_number:02d}".lower()
        exts = (".png", ".jpg", ".jpeg", ".webp")
        # 先直接尝试精确文件名
        for ext in exts:
            p = os.path.join(chapter_dir, f"{stem}{ext}")
            if os.path.isfile(p):
                return p
        # 再宽松扫描（可能有大小写或额外后缀）
        for fn in os.listdir(chapter_dir):
            low = fn.lower()
            if low.startswith(stem) and low.endswith(exts):
                p = os.path.join(chapter_dir, fn)
                if os.path.isfile(p):
                    return p
        return ""

    def run_single_look_reflection(self, chapter_idx: int, look_number: int, sub_theme_name: str, chapter_dir: str):
        """
        每生成一个 look 后执行一次 reflect：
        - y/n 询问该 look 图片是否已导入
        - y：调用 SingleLookReflectAgent 判断 KEEP/DELETE，并展示淘汰信息
        - n：跳过该 look 的 reflect，进入下一个 look 生成
        """
        if not chapter_dir:
            return

        ans = input(
            f"[Chapter {chapter_idx:02d} | Look {look_number:02d}] 该 look 图片是否已导入？(y/n): "
        ).strip().lower()
        if ans != "y":
            # n 或其它输入：按需求直接跳过
            return

        image_path = self._find_look_image(chapter_dir, look_number)
        if not image_path:
            print(f"[Chapter {chapter_idx:02d} | Look {look_number:02d}] 未找到 look 图片，将跳过 reflect。")
            return

        print(f"[Chapter {chapter_idx:02d} | Look {look_number:02d}] 正在分析中（单图 reflect）...")
        result = self.look_reflector.reflect(
            image_path=image_path,
        )
        print(f"[Chapter {chapter_idx:02d} | Look {look_number:02d}] 分析已完成（单图 reflect）。")
        if result is None:
            print(f"[Chapter {chapter_idx:02d} | Look {look_number:02d}] Reflect Agent 未返回有效结果。")
            return

        parsed = self._parse_look_reflection_result(result)
        action = (parsed.get("action") or "").strip().upper()
        info = parsed.get("info") or ""
        tier = parsed.get("tier") or ""

        if action == "DELETE":
            print(f"[Chapter {chapter_idx:02d} | Look {look_number:02d}] 建议淘汰：{os.path.basename(image_path)}")
            if tier or info:
                print(f"  TIER={tier} INFO={info}")
        else:
            # KEEP 或未解析到（默认按保留展示）
            print(f"[Chapter {chapter_idx:02d} | Look {look_number:02d}] 保留：{os.path.basename(image_path)}")
            if tier or info:
                print(f"  TIER={tier} INFO={info}")

        # 落盘（便于追踪每个 look 的反思结论）
        try:
            save_path = os.path.join(chapter_dir, f"look_{look_number:02d}_reflection.txt")
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(f"Chapter: {chapter_idx:02d}\n")
                f.write(f"Look: {look_number:02d}\n")
                f.write(f"Sub-theme: {sub_theme_name}\n")
                f.write(f"Image: {os.path.basename(image_path)}\n\n")
                f.write("RawAgentResult:\n")
                f.write(result.strip() + "\n")
        except Exception as e:
            print(f"[Chapter {chapter_idx:02d} | Look {look_number:02d}] 警告：无法写入 reflection 文件：{e}")

    @staticmethod
    def _parse_delete_indices_and_files(result_text: str, image_paths: list) -> list:
        """
        从 IMAGE_REDUCTION_RESULT 中解析要淘汰的图片（返回 image_paths 子集）。
        兼容两种返回：
        - DELETE: 2,5,7
        - FILES: look_02.png, look_05.png
        """
        if not result_text:
            return []

        base_names = [os.path.basename(p) for p in image_paths]
        to_drop = set()

        # 解析 DELETE 行的序号
        m_del = re.search(r"(?im)^\s*DELETE\s*:\s*(.+?)\s*$", result_text)
        if m_del:
            val = m_del.group(1).strip()
            if val and val.upper() != "NONE":
                nums = re.findall(r"\d+", val)
                for n in nums:
                    idx = int(n)
                    if 1 <= idx <= len(image_paths):
                        to_drop.add(image_paths[idx - 1])

        # 解析 FILES 行的文件名
        m_files = re.search(r"(?im)^\s*FILES\s*:\s*(.+?)\s*$", result_text)
        if m_files:
            val = m_files.group(1).strip()
            if val and val.upper() != "NONE":
                # 允许逗号/空格分隔
                parts = re.split(r"[,\s]+", val)
                for part in parts:
                    name = part.strip()
                    if not name:
                        continue
                    if name in base_names:
                        to_drop.add(image_paths[base_names.index(name)])

        return sorted(list(to_drop))

    @staticmethod
    def _collect_look_images(chapter_dir: str) -> list:
        """
        收集 chapter 目录下的 look_xx 图片（按编号排序）
        支持 png/jpg/jpeg/webp
        """
        if not chapter_dir or not os.path.isdir(chapter_dir):
            return []
        exts = (".png", ".jpg", ".jpeg", ".webp")
        candidates = []
        for fn in os.listdir(chapter_dir):
            low = fn.lower()
            if not low.startswith("look_"):
                continue
            if not low.endswith(exts):
                continue
            full = os.path.join(chapter_dir, fn)
            if os.path.isfile(full):
                candidates.append(full)

        def _sort_key(p: str):
            b = os.path.basename(p)
            m = re.search(r"look_(\d+)", b, flags=re.IGNORECASE)
            return int(m.group(1)) if m else 10**9

        return sorted(candidates, key=_sort_key)

    @staticmethod
    def _collect_collection_images(workflow_dir: str) -> list:
        """
        收集整个 workflow_dir 下所有 chapter 的 look_xx 图片（按 chapter 编号、look 编号排序）
        支持 png/jpg/jpeg/webp
        """
        if not workflow_dir or not os.path.isdir(workflow_dir):
            return []

        chapter_dirs = []
        for fn in os.listdir(workflow_dir):
            if not fn.lower().startswith("chapter_"):
                continue
            full = os.path.join(workflow_dir, fn)
            if os.path.isdir(full):
                chapter_dirs.append(full)

        def _chap_sort_key(p: str):
            b = os.path.basename(p)
            m = re.search(r"chapter_(\d+)", b, flags=re.IGNORECASE)
            return int(m.group(1)) if m else 10**9

        chapter_dirs = sorted(chapter_dirs, key=_chap_sort_key)

        all_images = []
        for cd in chapter_dirs:
            all_images.extend(FashionWorkflow._collect_look_images(cd))
        return all_images

    def run_collection_reflection(self):
        """
        Collection-reflection（整套图片反思/淘汰建议）：
        - 评估所有 chapter 的整体质量
        - 若发现需要淘汰的 chapter，自动移动整个 chapter 文件夹并重新生成新的 chapter
        """
        if not self.workflow_dir:
            return

        while True:
            need_eval = input("[Collection] 是否需要进行 Collection-reflection（整套图片评估）？(y/n): ").strip().lower()
            if need_eval == "n":
                return
            if need_eval == "y":
                break
            print("无效输入，请输入 y 或 n。")

        # 进行评估循环
        max_elimination_rounds = 2  # 最多进行 2 轮淘汰，避免无限循环
        elimination_round = 0

        while elimination_round < max_elimination_rounds:
            image_paths = self._collect_collection_images(self.workflow_dir)
            if not image_paths:
                print("[Collection] 未发现任何 look 图片，将跳过 Collection-reflection。")
                try:
                    save_path = os.path.join(self.workflow_dir, "reflection.txt")
                    with open(save_path, "w", encoding="utf-8") as f:
                        f.write(f"Theme: {self.theme}\n")
                        f.write(f"Brand: {self.brand}\n")
                        f.write("ImageCount: 0\n\n")
                        f.write("RawAgentResult:\n")
                        f.write("DELETE: NONE\nFILES: NONE\nNOTES: No images provided.\n")
                except Exception as e:
                    print(f"[Collection] 警告：无法写入 reflection.txt：{e}")
                return

            print("[Collection] 正在分析中（Collection-reflection）...")
            result = self.collection_reflector.reflect_collection(
                image_paths=image_paths,
                brand=self.brand,
                theme=self.theme,
                workflow_dir=self.workflow_dir,
            )
            print("[Collection] 分析已完成（Collection-reflection）。")

            if result is None:
                print("[Collection] Collection-reflection Agent 未返回有效结果，将跳过该步骤。")
                return

            # 落盘记录
            try:
                save_path = os.path.join(self.workflow_dir, "reflection.txt")
                with open(save_path, "w", encoding="utf-8") as f:
                    f.write(f"Theme: {self.theme}\n")
                    f.write(f"Brand: {self.brand}\n")
                    f.write(f"ImageCount: {len(image_paths)}\n")
                    f.write("Images:\n")
                    for idx, p in enumerate(image_paths, start=1):
                        rel = os.path.relpath(p, self.workflow_dir)
                        f.write(f"{idx}. {rel}\n")
                    f.write("\nRawAgentResult:\n")
                    f.write(result.strip() + "\n")
            except Exception as e:
                print(f"[Collection] 警告：无法写入 reflection.txt：{e}")

            # 解析需要淘汰的图片
            to_drop = self._parse_delete_indices_and_files(result, image_paths)
            if not to_drop:
                print("[Collection] 无淘汰：Collection评估完成。")
                return

            # 识别需要淘汰的 chapter
            chapters_to_eliminate = self._identify_chapters_from_images(to_drop)
            if not chapters_to_eliminate:
                print("[Collection] 未能识别需要淘汰的 chapter，跳过淘汰处理。")
                return

            print(f"[Collection] 建议淘汰以下 chapter: {', '.join(chapters_to_eliminate)}")

            ans = input(
                "[Collection] 是否执行淘汰并重新生成新的 chapter 替换？(y/n): "
            ).strip().lower()
            if ans != "y":
                print("[Collection] 跳过淘汰处理，评估完成。")
                return

            # 执行淘汰：移动整个 chapter 文件夹
            eliminated_chapter_names = []
            for chapter_name in chapters_to_eliminate:
                chapter_dir = os.path.join(self.workflow_dir, chapter_name)
                if not os.path.exists(chapter_dir):
                    print(f"[Collection] 警告：chapter目录不存在：{chapter_dir}")
                    continue

                if self.elimination_handler:
                    print(f"[Collection] 正在移动 {chapter_name}...")
                    elimination_result = self.elimination_handler.eliminate_chapter(
                        chapter_dir=chapter_dir,
                        reason=result.strip(),
                    )
                    if elimination_result.get("success"):
                        print(f"[Collection] {elimination_result['message']}")
                        eliminated_chapter_names.append(chapter_name)
                    else:
                        print(f"[Collection] {chapter_name} 淘汰失败：{elimination_result.get('message', '未知错误')}")

            if not eliminated_chapter_names:
                print("[Collection] 没有成功淘汰任何 chapter，跳过重新生成。")
                return

            # 重新生成被淘汰的 chapter
            print(f"[Collection] 正在重新生成 {len(eliminated_chapter_names)} 个 chapter...")
            self._regenerate_eliminated_chapters(eliminated_chapter_names)

            # 重新编号所有 chapter，确保编号连续
            if self.elimination_handler:
                EliminationHandler.renumber_chapters_in_workflow(self.workflow_dir)

            print("[Collection] 已完成淘汰和重新生成。")

            elimination_round += 1
            if elimination_round < max_elimination_rounds:
                continue_eval = input(
                    "[Collection] 是否继续评估新生成的 chapter？(y/n): "
                ).strip().lower()
                if continue_eval != "y":
                    print("[Collection] 评估完成。")
                    return
            else:
                print(f"[Collection] 已达到最大淘汰轮数({max_elimination_rounds})，评估完成。")
                return

    def _identify_chapters_from_images(self, image_paths: list) -> list:
        """
        从图片路径列表中识别对应的 chapter 名称
        """
        chapters = set()
        for img_path in image_paths:
            parts = Path(img_path).parts
            for part in parts:
                if re.match(r"chapter_\d+", part, re.IGNORECASE):
                    chapters.add(part)
                    break
        return sorted(list(chapters))

    def _regenerate_eliminated_chapters(self, chapter_names: list):
        """
        重新生成被淘汰的 chapter
        """
        sub_themes = getattr(self.theme_analyzer, "sub_themes", []) or []
        if not sub_themes:
            sub_themes = [f"Sub-Theme {i}" for i in range(1, self.num_chapters + 1)]

        for chapter_name in chapter_names:
            match = re.search(r"chapter_(\d+)", chapter_name, re.IGNORECASE)
            if not match:
                print(f"[Collection] 无法解析chapter编号：{chapter_name}")
                continue

            chapter_idx = int(match.group(1))
            if 1 <= chapter_idx <= len(sub_themes):
                sub_theme_name = sub_themes[chapter_idx - 1]
            else:
                sub_theme_name = f"Sub-Theme {chapter_idx}"

            print(f"[Collection] 正在重新生成 {chapter_name} (Sub-theme: {sub_theme_name})...")

            # 清除 agent 状态
            self.reset_agents()
            self.elements_specialist.design_concepts = []
            self.elements_specialist.candidate_elements = []
            self.look_stylist.candidate_elements = []
            self.look_stylist.look_descriptions = []

            # 创建新的 chapter 目录
            chapter_dir = os.path.join(self.workflow_dir, chapter_name)
            os.makedirs(chapter_dir, exist_ok=True)

            # 重新生成 chapter
            chapter = self.concept_brainstorming_for_single_chapter(chapter_idx, sub_theme_name)
            if not chapter:
                print(f"[Collection] 重新生成 {chapter_name} 失败")
                continue

            # 保存 chapter 概念
            chapter_concept_path = os.path.join(chapter_dir, "design_chapter.txt")
            with open(chapter_concept_path, "w", encoding="utf-8") as f:
                f.write(f"**Chapter {chapter_idx} (Sub-Theme): {chapter['name']}**\n\n")
                f.write(chapter["content"])

            # 执行 design elements proposal
            self.design_elements_proposal_for_chapter(chapter, chapter_dir, chapter_idx)

            # 执行 look description generation
            self.look_stylist.sub_theme = chapter["name"]
            self.look_stylist.design_target_prompt = self.design_target_prompt
            self.look_stylist.theme = self.theme

            condensed_theme_analysis = self._condense_theme_analysis_for_looks(
                self.theme_analyzer.theme_analysis,
                sub_theme_name=chapter["name"],
                max_chars=1800,
            )
            self.look_stylist.theme_analysis = condensed_theme_analysis

            try:
                save_path = os.path.join(chapter_dir, "theme_analysis_condensed.txt")
                with open(save_path, "w", encoding="utf-8") as f:
                    f.write(condensed_theme_analysis + "\n")
            except Exception as e:
                print(f"[Collection] 警告：无法写入 theme_analysis_condensed.txt：{e}")

            self.look_description_generation_for_group(chapter_dir)
            print(f"[Collection] {chapter_name} 重新生成完成，请重新导入对应的生成图。")
            self.reset_agents()

    @staticmethod
    def _condense_theme_analysis_for_looks(theme_analysis: str, sub_theme_name: str, max_chars: int = 1800) -> str:
        """
        在进入 LookDescriptionAgent 前压缩/提炼 theme_analysis：
        - 尽量保留 **Theme:** 的概述（第一段）
        - 抽取 **Key aspects of the theme:** 下的各个 **Aspect:**，每个保留首句/首段
        - 优先把与当前 sub_theme_name 最相关的 aspect 放在前面
        - 最终裁剪到 max_chars（避免上下文过长）
        """
        if not theme_analysis:
            return ""

        text = theme_analysis.strip()
        sub_key = (sub_theme_name or "").strip().lower()

        def _first_sentence_or_paragraph(s: str) -> str:
            s = (s or "").strip()
            if not s:
                return ""
            # 先按空行分段，取首段
            para = s.split("\n\n", 1)[0].strip()
            # 再尽量取首句（避免过长）
            m = re.search(r"(.+?[.!?])(\s|$)", para)
            return (m.group(1).strip() if m else para).strip()

        # 1) 提取 Theme 段（尽量取第一段概述）
        theme_overview = ""
        m_theme = re.search(r"(?s)\*\*Theme:\*\*\s*(.+?)(\n\s*\*\*Inspiration:\*\*|\Z)", text)
        if m_theme:
            theme_overview = _first_sentence_or_paragraph(m_theme.group(1))

        # 2) 提取 Key aspects 段
        aspects_block = ""
        m_aspects = re.search(r"(?s)\*\*Key aspects of the theme:\*\*\s*(.+)$", text)
        if m_aspects:
            aspects_block = m_aspects.group(1).strip()

        aspects = []
        if aspects_block:
            # 捕获 **Aspect Name:** 标题与其后的描述块
            # 约定：标题格式为 **Something:**（冒号在加粗内）
            pattern = re.compile(r"\*\*([^*]+?):\*\*\s*(.*?)(?=\n\*\*[^*]+?:\*\*|\Z)", re.S)
            for m in pattern.finditer(aspects_block):
                title = (m.group(1) or "").strip()
                body = (m.group(2) or "").strip()
                if not title:
                    continue
                aspects.append((title, _first_sentence_or_paragraph(body)))

        # 3) 优先排序：标题包含 sub_theme_name 的排前
        if sub_key and aspects:
            def _score(item):
                title, body = item
                t = (title or "").lower()
                b = (body or "").lower()
                # title 命中权重大于 body 命中
                return (2 if sub_key and sub_key in t else 0) + (1 if sub_key and sub_key in b else 0)
            aspects = sorted(aspects, key=_score, reverse=True)

        # 4) 组装压缩文本
        parts = []
        if theme_overview:
            parts.append("Theme (condensed):")
            parts.append(theme_overview)
            parts.append("")

        if aspects:
            parts.append("Key aspects (condensed):")
            for title, one_liner in aspects:
                if one_liner:
                    parts.append(f"- {title}: {one_liner}")
                else:
                    parts.append(f"- {title}")

        condensed = "\n".join(parts).strip()
        if not condensed:
            condensed = text

        # 5) 裁剪到 max_chars（保留前部信息密度更高）
        if max_chars and len(condensed) > max_chars:
            condensed = condensed[:max_chars].rstrip() + "..."
        return condensed

    def _confirm_chapter_images_ready(self, chapter_idx: int, chapter_dir: str) -> list:
        """
        交互确认：是否已根据 chapter 的 look_xx 正确导入生成图
        返回：图片路径列表（按 look 编号排序）
        """
        while True:
            ans = input(
                f"[Chapter {chapter_idx:02d}] 是否已根据 chapter 中的 look_xx 正确导入对应生成图？(y/n): "
            ).strip().lower()

            if ans == "n":
                print(f"[Chapter {chapter_idx:02d}] 请先将图片导入到目录：{chapter_dir}，完成后输入 y 继续。")
                continue

            if ans != "y":
                print("无效输入，请输入 y 或 n。")
                continue

            images = self._collect_look_images(chapter_dir)
            if not images:
                print(f"[Chapter {chapter_idx:02d}] 未在目录中发现 look_xx 图片：{chapter_dir}")
                continue

            # 如果 num_looks 有要求，做一个下限校验，避免误触发
            if self.num_looks and len(images) < int(self.num_looks):
                print(
                    f"[Chapter {chapter_idx:02d}] 当前发现 {len(images)} 张图片，但配置期望至少 {self.num_looks} 张。"
                )
                print("请确认图片是否已全部导入，完成后再输入 y。")
                continue

            return images

    def run_chapter_image_reduction(self, chapter_idx: int, sub_theme_name: str, chapter_dir: str):
        """
        在单个 chapter 完整生成后执行：
        - 先询问是否需要进行 Chapter 生成评估（y/n）
        - 询问是否已导入图片
        - 调用 ChapterReflectAgent 产出淘汰建议
        - 若发生淘汰，自动移动淘汰文件并重新生成新的look替换
        """
        if not chapter_dir:
            # 没有目录就无法进行图片导入与检查
            return

        # 新增判断：是否需要进行 Chapter 生成评估
        while True:
            need_eval = input(
                f"[Chapter {chapter_idx:02d}] 是否需要进行 Chapter 生成评估？(y/n): "
            ).strip().lower()
            if need_eval == "n":
                # 跳过该 Chapter 的评估工作，直接开始生成下个 Chapter
                return
            if need_eval == "y":
                # 进入评估前，先提示导入目录
                print(f"[Chapter {chapter_idx:02d}] 请先将图片导入到目录：{chapter_dir}")
                break
            print("无效输入，请输入 y 或 n。")

        # 进行评估循环
        max_elimination_rounds = 3  # 最多进行3轮淘汰，避免无限循环
        elimination_round = 0
        
        while elimination_round < max_elimination_rounds:
            image_paths = self._confirm_chapter_images_ready(chapter_idx, chapter_dir)

            print(f"[Chapter {chapter_idx:02d}] 正在分析中（Chapter 评估/淘汰）...")
            result = self.chapter_image_reducer.reduce_images(
                image_paths=image_paths,
                brand=self.brand,
                theme=self.theme,
                sub_theme=sub_theme_name,
                chapter_dir=chapter_dir,
            )
            print(f"[Chapter {chapter_idx:02d}] 分析已完成（Chapter 评估/淘汰）。")

            if result is None:
                print(f"[Chapter {chapter_idx:02d}] 图片淘汰 Agent 未返回有效结果，将跳过该步骤。")
                return

            to_drop = self._parse_delete_indices_and_files(result, image_paths)
            drop_names = [os.path.basename(p) for p in to_drop] if to_drop else []

            # 记录到文件（reflection.txt），便于追踪
            try:
                save_path = os.path.join(chapter_dir, "reflection.txt")
                with open(save_path, "w", encoding="utf-8") as f:
                    f.write(f"Chapter: {chapter_idx:02d}\n")
                    f.write(f"Sub-theme: {sub_theme_name}\n")
                    f.write(f"Theme: {self.theme}\n")
                    f.write(f"Brand: {self.brand}\n")
                    f.write(f"ImageCount: {len(image_paths)}\n")
                    f.write("Images:\n")
                    for idx, p in enumerate(image_paths, start=1):
                        rel = os.path.relpath(p, chapter_dir)
                        f.write(f"{idx}. {rel}\n")
                    f.write(f"\nSuggestedDeleteCount: {len(drop_names)}\n")
                    f.write("SuggestedDeleteFiles:\n")
                    if drop_names:
                        for n in drop_names:
                            f.write(f"- {n}\n")
                    else:
                        f.write("- NONE\n")
                    f.write("\nRawAgentResult:\n")
                    f.write(result.strip() + "\n")
            except Exception as e:
                print(f"[Chapter {chapter_idx:02d}] 警告：无法写入 reflection.txt：{e}")

            if not to_drop:
                print(f"[Chapter {chapter_idx:02d}] 无淘汰：继续生成下一个 chapter。")
                return

            print(f"[Chapter {chapter_idx:02d}] 淘汰 {len(drop_names)} 张：{', '.join(drop_names)}")
            
            # 提取被淘汰的look编号
            eliminated_look_numbers = []
            for drop_path in to_drop:
                basename = os.path.basename(drop_path)
                match = re.search(r"look_(\d+)", basename, re.IGNORECASE)
                if match:
                    eliminated_look_numbers.append(int(match.group(1)))
            
            if not eliminated_look_numbers:
                print(f"[Chapter {chapter_idx:02d}] 无法解析被淘汰的look编号，跳过淘汰处理。")
                return
            
            # 询问是否执行淘汰并重新生成
            ans = input(
                f"[Chapter {chapter_idx:02d}] 是否执行淘汰并重新生成新的look替换？(y/n): "
            ).strip().lower()
            
            if ans != "y":
                print(f"[Chapter {chapter_idx:02d}] 跳过淘汰处理，继续进入下一个 chapter。")
                return
            
            # 执行淘汰：移动文件到eliminated文件夹
            if self.elimination_handler:
                print(f"[Chapter {chapter_idx:02d}] 正在移动被淘汰的文件...")
                elimination_result = self.elimination_handler.eliminate_look_files(
                    chapter_dir=chapter_dir,
                    look_numbers=eliminated_look_numbers,
                    reason=result.strip()
                )
                
                if elimination_result["success"]:
                    print(f"[Chapter {chapter_idx:02d}] {elimination_result['message']}")
                else:
                    print(f"[Chapter {chapter_idx:02d}] 淘汰处理失败：{elimination_result.get('message', '未知错误')}")
                    return
            
            # 重新生成被淘汰的look
            print(f"[Chapter {chapter_idx:02d}] 正在重新生成 {len(eliminated_look_numbers)} 个look...")
            self._regenerate_eliminated_looks(
                chapter_idx=chapter_idx,
                chapter_dir=chapter_dir,
                look_numbers=eliminated_look_numbers,
                sub_theme_name=sub_theme_name
            )
            
            # 重新编号，确保look编号连续
            if self.elimination_handler:
                EliminationHandler.renumber_looks_in_directory(chapter_dir)
            
            print(f"[Chapter {chapter_idx:02d}] 已完成淘汰和重新生成。")
            
            # 询问是否继续评估
            elimination_round += 1
            if elimination_round < max_elimination_rounds:
                continue_eval = input(
                    f"[Chapter {chapter_idx:02d}] 是否继续评估新生成的look？(y/n): "
                ).strip().lower()
                if continue_eval != "y":
                    print(f"[Chapter {chapter_idx:02d}] 评估完成，继续下一个chapter。")
                    return
            else:
                print(f"[Chapter {chapter_idx:02d}] 已达到最大淘汰轮数({max_elimination_rounds})，继续下一个chapter。")
                return
    
    def _regenerate_eliminated_looks(
        self,
        chapter_idx: int,
        chapter_dir: str,
        look_numbers: list,
        sub_theme_name: str
    ):
        """
        重新生成被淘汰的look
        
        Args:
            chapter_idx: chapter索引
            chapter_dir: chapter目录
            look_numbers: 需要重新生成的look编号列表
            sub_theme_name: 子主题名称
        """
        max_tries = self.max_steps
        
        # 确保look_stylist使用正确的上下文
        self.look_stylist.sub_theme = sub_theme_name
        self.look_stylist.design_target_prompt = self.design_target_prompt
        self.look_stylist.theme = self.theme
        
        # 使用压缩的theme_analysis
        condensed_theme_analysis_path = os.path.join(chapter_dir, "theme_analysis_condensed.txt")
        if os.path.exists(condensed_theme_analysis_path):
            with open(condensed_theme_analysis_path, "r", encoding="utf-8") as f:
                self.look_stylist.theme_analysis = f.read()
        
        # 使用该chapter的design elements
        self.look_stylist.candidate_elements = self.elements_specialist.candidate_elements
        self.look_stylist.design_concepts = self.elements_specialist.design_concepts
        
        for look_number in sorted(look_numbers):
            print(f"[Chapter {chapter_idx:02d}] 正在重新生成 look_{look_number:02d}...")
            
            # 重置agent状态
            self.look_stylist.reset()
            
            for _i in range(max_tries):
                if self.verbose:
                    print(f"@@ Workflow #{self.workflow_index} - Chapter {chapter_idx:02d} - Look {look_number} - Regeneration Step {_i} @@")
                
                resp = self.look_stylist.inference(
                    research_topic=f"Design Target: {self.design_target_prompt}\nLook Number: {look_number}",
                    phase="look description generation",
                    feedback="",
                    step=_i
                )
                
                if self.verbose:
                    print("Look Stylist (Regeneration): ", resp, "\n~~~~~~~~~~~")
                
                if "```LOOK_DESCRIPTION" in resp:
                    look_desc = extract_prompt(resp, "LOOK_DESCRIPTION")
                    self.look_stylist.look_descriptions.append(look_desc)
                    
                    # 保存重新生成的look
                    if chapter_dir:
                        required_line = "Please generate female models and the matching clothing for them."
                        look_desc_to_save = look_desc
                        head_lines = [ln.strip() for ln in (look_desc_to_save or "").splitlines()[:3]]
                        if not head_lines or required_line not in head_lines:
                            look_desc_to_save = required_line + "\n\n" + (look_desc_to_save.lstrip("\n") if look_desc_to_save else "")
                        
                        save_path = os.path.join(chapter_dir, f"look_{look_number:02d}.txt")
                        with open(save_path, "w", encoding="utf-8") as f:
                            f.write(look_desc_to_save)
                        
                        print(f"[Chapter {chapter_idx:02d}] look_{look_number:02d}.txt 已重新生成")
                    
                    self.reset_agents()
                    break
            else:
                print(f"[Chapter {chapter_idx:02d}] 警告：look_{look_number:02d} 重新生成失败，已达到最大尝试次数")
        
        print(f"[Chapter {chapter_idx:02d}] 所有look重新生成完成，请重新导入对应的生成图。")

    def perform_research(self):
        """执行完整的设计研究流程"""
        for phase, subtasks in self.phases:
            phase_start_time = time.time()
            if self.verbose:
                print(f"{'*'*50}\n开始阶段: {phase}\n{'*'*50}")
            for subtask in subtasks:
                if self.verbose:
                    print(f"{'&'*30}\n开始子任务: {subtask}\n{'&'*30}")
                
                # 设置当前阶段的模型
                if type(self.phase_models) == dict:
                    if subtask in self.phase_models:
                        self.set_model(self.phase_models[subtask])
                    else:
                        self.set_model(DEFAULT_LLM_BACKBONE)

                # 执行各个子任务
                if (subtask not in self.phase_status or not self.phase_status[subtask]) and subtask == "theme analysis":
                    repeat = True
                    while repeat:
                        repeat = self.theme_analysis()
                    self.phase_status[subtask] = True

                if (subtask not in self.phase_status or not self.phase_status[subtask]) and subtask == "concept brainstorming":
                    # 按子主题顺序逐章处理：每个子主题就是一个章节
                    self.process_chapters_sequentially()
                    self.phase_status[subtask] = True

                # 保存状态
                if self.save:
                    self.save_state(subtask)
                
                # 计算并打印阶段耗时
                phase_end_time = time.time()
                phase_duration = phase_end_time - phase_start_time
                if self.verbose:
                    print(f"子任务 '{subtask}' 完成，耗时 {phase_duration:.2f} 秒")
                self.statistics_per_phase[subtask]["time"] = phase_duration

    def theme_analysis(self):
        """执行主题分析阶段"""
        max_tries = self.max_steps
        self.theme_analyzer.design_target_prompt = self.design_target_prompt
        self.theme_analyzer.theme = self.theme

        for _i in range(max_tries):
            if self.verbose:
                print(f"@@ Workflow #{self.workflow_index} - Step {_i} @@")
            resp = self.theme_analyzer.inference(
                research_topic=f"Design Target: {self.design_target_prompt}\nTheme: {self.theme}",
                phase="theme analysis",
                feedback="",
                step=_i
            )
            if self.verbose:
                print("Theme Analyzer: ", resp, "\n~~~~~~~~~~~")

            if "```THEME_ANALYSIS" in resp:
                theme_analysis = extract_prompt(resp, "THEME_ANALYSIS")
                if self.human_in_loop_flag["theme analysis"]:
                    retry = self.human_in_loop("theme analysis", theme_analysis)
                    if retry:
                        return retry
                self.theme_analyzer.theme_analysis = theme_analysis
                # 解析 sub_themes：每个子主题就是一个章节
                self.theme_analyzer.sub_themes = parse_sub_themes_from_theme_analysis(theme_analysis)
                
                # 保存结果到文件
                if self.workflow_dir:
                    save_path = os.path.join(self.workflow_dir, "theme_analysis.txt")
                    os.makedirs(os.path.dirname(save_path), exist_ok=True)
                    with open(save_path, "w", encoding="utf-8") as f:
                        f.write(theme_analysis)
                
                self.reset_agents()
                self.statistics_per_phase["theme analysis"]["steps"] = _i
                return False

        if self.except_if_fail:
            raise Exception("Max tries during phase: Theme Analysis")
        return False

    def concept_brainstorming_for_single_chapter(self, chapter_number, sub_theme_name):
        """为单个章节（=单个子主题）执行概念头脑风暴阶段"""
        max_tries = self.max_steps
        self.concept_designer.theme = self.theme
        self.concept_designer.theme_analysis = self.theme_analyzer.theme_analysis
        self.concept_designer.sub_theme = sub_theme_name

        research_topic = (
            f"Design Target: {self.design_target_prompt}\n"
            f"Theme: {self.theme}\n"
            f"Chapter Number: {chapter_number}\n"
            f"Sub-Theme (this chapter): {sub_theme_name}"
        )

        for _i in range(max_tries):
            if self.verbose:
                print(f"@@ Workflow #{self.workflow_index} - Chapter {chapter_number} - Step {_i} @@")
            resp = self.concept_designer.inference(
                research_topic=research_topic,
                phase="concept brainstorming",
                feedback="",
                step=_i
            )
            if self.verbose:
                print("Concept Designer: ", resp, "\n~~~~~~~~~~~")

            if "```DESIGN_CONCEPT" in resp:
                design_concept = extract_prompt(resp, "DESIGN_CONCEPT")
                if self.human_in_loop_flag["concept brainstorming"]:
                    retry = self.human_in_loop("concept brainstorming", design_concept)
                    if retry:
                        return None
                
                # 解析单个章节
                chapter = self.parse_single_chapter_from_design_concept(design_concept, chapter_number, sub_theme_name)
                return chapter

        if self.except_if_fail:
            raise Exception(f"Max tries during phase: Concept Brainstorming for Chapter {chapter_number}")
        return None

    def parse_single_chapter_from_design_concept(self, design_concept, expected_chapter_number, expected_sub_theme_name):
        """解析design_concept文本，提取单个章节"""
        # 格式：**Chapter X (Sub-Theme): [Sub-Theme Name]**
        pattern = r"\*\*Chapter\s+(\d+)\s*\(Sub-Theme\):\s*([^*]+)\*\*"
        match = re.search(pattern, design_concept)

        if match:
            chap_num = int(match.group(1))
            chap_name = match.group(2).strip()
            start_pos = match.end()
            chap_content = design_concept[start_pos:].strip()
            return {"number": chap_num, "name": chap_name, "content": chap_content}

        # 兜底：不强依赖模型严格输出标题
        return {
            "number": expected_chapter_number,
            "name": expected_sub_theme_name or f"Sub-Theme {expected_chapter_number}",
            "content": design_concept.strip(),
        }

    def process_chapters_sequentially(self):
        """按顺序处理每个章节：每次生成1个章节（=1个子主题），处理完后再生成下一个"""
        sub_themes = getattr(self.theme_analyzer, "sub_themes", []) or []
        if sub_themes:
            chapter_names = sub_themes
        else:
            # 如果主题分析没解析到子主题，则退回使用 num_chapters 生成占位章节
            chapter_names = [f"Sub-Theme {i}" for i in range(1, self.num_chapters + 1)]

        for chapter_idx, sub_theme_name in enumerate(chapter_names, start=1):
            # 用于 look 级 reflect 的上下文（避免在函数签名里到处传）
            self._current_chapter_idx = chapter_idx
            self._current_sub_theme_name = sub_theme_name
            if self.verbose:
                print(f"\n{'='*60}")
                print(f"Generating and Processing Chapter {chapter_idx}")
                print(f"{'='*60}\n")
            
            # 在生成新章节之前，清除所有agent的状态，确保章节之间的独立性
            self.reset_agents()
            # 清除DesignElementsAgent和LookDescriptionAgent的状态
            self.elements_specialist.design_concepts = []
            self.elements_specialist.candidate_elements = []
            self.look_stylist.candidate_elements = []
            self.look_stylist.look_descriptions = []
            
            # 为当前章节创建目录（使用循环索引确保编号连续）
            chapter_dir = None
            if self.workflow_dir:
                chapter_dir = os.path.join(self.workflow_dir, f"chapter_{chapter_idx:02d}")
                os.makedirs(chapter_dir, exist_ok=True)
                if self.verbose:
                    print(f"Created directory: {chapter_dir}\n")
            
            # 生成单个章节（=单个子主题）
            chapter = self.concept_brainstorming_for_single_chapter(chapter_idx, sub_theme_name)
            
            if not chapter:
                if self.verbose:
                    print(f"Failed to generate Chapter {chapter_idx}. Skipping.")
                continue
            
            if self.verbose:
                print(f"\n{'='*60}")
                print(f"Processing Chapter {chapter_idx}: {chapter['name']}")
                print(f"{'='*60}\n")
            
            # 保存当前章节的概念
            if chapter_dir:
                chapter_concept_path = os.path.join(chapter_dir, "design_chapter.txt")
                with open(chapter_concept_path, "w", encoding="utf-8") as f:
                    f.write(f"**Chapter {chapter_idx} (Sub-Theme): {chapter['name']}**\n\n")
                    f.write(chapter["content"])
            
            # 执行design elements proposal（针对当前章节）
            self.design_elements_proposal_for_chapter(chapter, chapter_dir, chapter_idx)
            
            # 执行look description generation（针对当前章节）
            # 注入 sub_theme，确保 LookDescriptionAgent 上下文包含章节信息
            self.look_stylist.sub_theme = chapter["name"]
            # 注入 design target，确保 LookDescriptionAgent 上下文包含设计目标
            self.look_stylist.design_target_prompt = self.design_target_prompt
            # 注入 theme / theme_analysis，确保同章 look 使用一致的章节级上下文
            self.look_stylist.theme = self.theme
            condensed_theme_analysis = self._condense_theme_analysis_for_looks(
                self.theme_analyzer.theme_analysis,
                sub_theme_name=chapter["name"],
                max_chars=1800,
            )
            self.look_stylist.theme_analysis = condensed_theme_analysis
            # 可选落盘，便于复现与调试
            if chapter_dir:
                try:
                    save_path = os.path.join(chapter_dir, "theme_analysis_condensed.txt")
                    with open(save_path, "w", encoding="utf-8") as f:
                        f.write(condensed_theme_analysis + "\n")
                except Exception as e:
                    print(f"[Chapter {chapter_idx:02d}] 警告：无法写入 theme_analysis_condensed.txt：{e}")
            self.look_description_generation_for_group(chapter_dir)

            # 工作流要求：在 1 个 chapter 完整生成后，执行章节图片淘汰处理
            # 处理前会询问是否已按 look_xx 导入对应生成图（y/n）
            self.run_chapter_image_reduction(chapter_idx, chapter["name"], chapter_dir)
            
            # 处理完当前章节的所有looks后，清除多余上下文，准备处理下一个章节
            self.reset_agents()
            if self.verbose:
                print(f"\nCompleted Chapter {chapter_idx}. Context cleared. Moving to next chapter.\n")

        # 所有 chapter 完成后执行整套 collection 的反思（放在 group-reflection 之后）
        self.run_collection_reflection()
    
    def design_elements_proposal_for_chapter(self, chapter, chapter_dir=None, chapter_number=None):
        """针对单个章节（=单个子主题）执行设计元素提案阶段"""
        max_tries = self.max_steps
        
        actual_chapter_number = chapter_number if chapter_number is not None else chapter["number"]
        
        # 设置 DesignElementsAgent 的属性，包含主题和当前章节的概念
        self.elements_specialist.theme = self.theme
        self.elements_specialist.theme_analysis = self.theme_analyzer.theme_analysis
        self.elements_specialist.design_concepts = [f"**Chapter {actual_chapter_number} (Sub-Theme): {chapter['name']}**\n\n{chapter['content']}"]

        for _i in range(max_tries):
            if self.verbose:
                print(f"@@ Workflow #{self.workflow_index} - Chapter {actual_chapter_number} - Design Elements - Step {_i} @@")
            resp = self.elements_specialist.inference(
                research_topic=f"Theme: {self.theme}\nDesign Target: {self.design_target_prompt}\nSub-Theme/Chapter: {chapter['name']}",
                phase="design elements proposal",
                feedback="",
                step=_i
            )
            if self.verbose:
                print("Elements Specialist: ", resp, "\n~~~~~~~~~~~")

            if "```DESIGN_ELEMENTS" in resp:
                elements = extract_prompt(resp, "DESIGN_ELEMENTS")
                self.elements_specialist.candidate_elements = [elements]
                
                # 保存结果到文件
                if chapter_dir:
                    save_path = os.path.join(chapter_dir, "design_element&concept.txt")
                    os.makedirs(os.path.dirname(save_path), exist_ok=True)
                    with open(save_path, "w", encoding="utf-8") as f:
                        f.write(f"Theme: {self.theme}\n")
                        f.write(f"Sub-Theme/Chapter: {chapter['name']}\n")
                        f.write(f"{'='*50}\n")
                        f.write(f"{elements}\n")
                
                self.reset_agents()
                self.statistics_per_phase["design elements proposal"]["steps"] = _i
                return

        if self.except_if_fail:
            raise Exception(f"Max tries during phase: Design Elements Proposal for Chapter {chapter['number']}")

    # ------------------------------------------------------------------ #
    # 文本评估 + 自适应优化
    # ------------------------------------------------------------------ #

    def _evaluate_and_optimize_look(
        self,
        look_txt_path: str | None,
        look_desc_raw: str,
        chapter_idx: int,
        look_number: int,
    ) -> dict:
        """
        对单个 look 描述执行自适应评估流程：
        1. 若 evaluator 未启用 → 直接记录并返回
        2. 评估原始文本
           - 通过双门限 → 保留原文本，记录 passed=True
           - 未通过 → 进入 optimize，最多 max_optimize_rounds 轮
        3. 若最终仍不通过双门限 → 仍保留（走完全部优化轮），记录 passed=False
        4. 若 look_txt_path 指定，优化前/后的文本分别保存到 looks_original/ 和 looks_optimized/ 子目录，不再覆盖原文件
        返回结构：
          {
            "passed": bool,
            "mode": "passthrough" | "evaluate_only" | "optimized",
            "rounds_executed": int,
            "total_score": float,
            "penalized_score": float,
            "total_penalty": float,
            "both_gates_passed": bool,
            "active_penalties": list,
            "best_text": str,
            "report_path": str | None,
          }
        """
        cfg = self.evaluator_config
        evaluator = self.text_evaluator

        result: dict = {
            "passed": False,
            "mode": "passthrough",
            "rounds_executed": 0,
            "total_score": 0.0,
            "penalized_score": 0.0,
            "total_penalty": 0.0,
            "both_gates_passed": False,
            "active_penalties": [],
            "best_text": look_desc_raw,
            "report_path": None,
        }

        if not cfg.enabled or evaluator is None:
            if self.verbose:
                print(f"  [TextEval] Look {look_number} skipped (evaluator disabled)")
            return result

        from pathlib import Path

        # -- 评估原始文本 -- #
        eval_path = look_txt_path
        if eval_path is None:
            # 写临时文件供 evaluator 使用
            tmp_dir = Path(self.workflow_dir or ".")
            eval_path = str(tmp_dir / f"_tmp_look_{chapter_idx:02d}_{look_number:02d}.txt")
            with open(eval_path, "w", encoding="utf-8") as f:
                f.write(look_desc_raw)

        try:
            if self.verbose:
                print(f"  [TextEval] Evaluating look {look_number} ...")
            eval_result = evaluator.evaluate_txt_file(Path(eval_path))

            ts = float(eval_result.get("total_score", 0.0) or 0.0)
            qs = float(
                eval_result.get("scores", {})
                .get("quality_score", {})
                .get("penalized_score", 0.0)
                or 0.0
            )
            pt = float(
                eval_result.get("scores", {})
                .get("quality_score", {})
                .get("penalties", {})
                .get("total_penalty", 0.0)
                or 0.0
            )
            gates = eval_result.get("gates") or {}
            score_gate_passed = bool((gates.get("score_gate") or {}).get("passed", False))
            penalty_gate_passed = bool((gates.get("penalty_gate") or {}).get("passed", False))
            both_passed = score_gate_passed and penalty_gate_passed

            # 提取 active penalties
            penalty_items = (
                eval_result.get("scores", {})
                .get("quality_score", {})
                .get("penalties", {})
                .get("items", {})
            )
            active_penalties = []
            for key, item in penalty_items.items():
                penalty_score = float(item.get("score", 0.0) or 0.0)
                if penalty_score >= cfg.adaptive_penalty_threshold:
                    active_penalties.append(
                        {
                            "penalty_key": key,
                            "score": penalty_score,
                            "reason": item.get("reason", ""),
                        }
                    )

            result["total_score"] = ts
            result["penalized_score"] = qs
            result["total_penalty"] = pt
            result["both_gates_passed"] = both_passed
            result["active_penalties"] = active_penalties

            if self.verbose:
                status = "PASS" if both_passed else "FAIL"
                print(
                    f"  [TextEval] Look {look_number} initial eval: "
                    f"total={ts:.3f} quality={qs:.3f} penalty={pt:.3f} → [{status}]"
                )

            # -- 通过双门限：直接保留，不优化 -- #
            if both_passed:
                result["passed"] = True
                result["mode"] = "evaluate_only"
                result["best_text"] = look_desc_raw
                return result

            # -- 未通过：启动优化 -- #
            if self.verbose:
                print(f"  [TextEval] Look {look_number} failed gates, starting optimize (max {cfg.max_optimize_rounds} rounds) ...")

            opt_result = evaluator.optimize_txt_file(
                Path(eval_path),
                report_dir=self.workflow_dir,  # 保存报告到当前 chapter dir
                max_rounds=cfg.max_optimize_rounds,
                min_score_improvement=cfg.min_score_improvement,
                min_quality_improvement=cfg.min_quality_improvement,
                score_gate_min=cfg.score_gate_min,
                penalty_gate_max=cfg.penalty_gate_max,
            )

            optimized_result = opt_result.get("optimized_result") or eval_result
            final_ts = float(optimized_result.get("total_score", 0.0) or 0.0)
            final_qs = float(
                optimized_result.get("scores", {})
                .get("quality_score", {})
                .get("penalized_score", 0.0)
                or 0.0
            )
            final_pt = float(
                optimized_result.get("scores", {})
                .get("quality_score", {})
                .get("penalties", {})
                .get("total_penalty", 0.0)
                or 0.0
            )
            final_gates = optimized_result.get("gates") or {}
            final_score_passed = bool((final_gates.get("score_gate") or {}).get("passed", False))
            final_penalty_passed = bool((final_gates.get("penalty_gate") or {}).get("passed", False))
            final_both_passed = final_score_passed and final_penalty_passed

            best_text = opt_result.get("best_text") or optimized_result.get("text", look_desc_raw)
            report_path = opt_result.get("report_path")

            result["passed"] = final_both_passed
            result["mode"] = "optimized"
            result["rounds_executed"] = opt_result.get("rounds_executed", 0)
            result["total_score"] = final_ts
            result["penalized_score"] = final_qs
            result["total_penalty"] = final_pt
            result["both_gates_passed"] = final_both_passed
            result["best_text"] = best_text
            result["report_path"] = report_path

            # 不再覆盖原文件，改为分别保存优化前后的版本到独立文件夹
            if look_txt_path:
                parent_dir = Path(look_txt_path).parent
                orig_basename = Path(look_txt_path).name  # e.g. look_01.txt

                # 保存优化前（原始）版本
                orig_dir = parent_dir / "looks_original"
                orig_dir.mkdir(parents=True, exist_ok=True)
                orig_save_path = orig_dir / orig_basename
                with open(orig_save_path, "w", encoding="utf-8") as f:
                    f.write(look_desc_raw)
                if self.verbose:
                    print(f"  [TextEval] Original look saved to {orig_save_path}")

                # 保存优化后版本（走 optimize 分支即写入，便于与 looks_original 成对对比）
                if best_text:
                    opt_dir = parent_dir / "looks_optimized"
                    opt_dir.mkdir(parents=True, exist_ok=True)
                    opt_save_path = opt_dir / orig_basename
                    with open(opt_save_path, "w", encoding="utf-8") as f:
                        f.write(best_text)
                    if self.verbose:
                        print(f"  [TextEval] Optimized look saved to {opt_save_path}")

            if self.verbose:
                status = "PASS" if final_both_passed else "FAIL"
                rounds = opt_result.get("rounds_executed", 0)
                print(
                    f"  [TextEval] Look {look_number} optimized ({rounds} rounds): "
                    f"total={final_ts:.3f} quality={final_qs:.3f} penalty={final_pt:.3f} → [{status}]"
                )

        finally:
            # 清理临时文件
            if eval_path != look_txt_path and eval_path:
                try:
                    Path(eval_path).unlink(missing_ok=True)
                except Exception:
                    pass

        return result

    def look_description_generation_for_group(self, group_dir=None):
        """针对单个group执行Look描述生成阶段"""
        max_tries = self.max_steps
        
        # 使用设计元素生成 Look 描述
        self.look_stylist.candidate_elements = self.elements_specialist.candidate_elements
        # 传递当前group的设计概念
        self.look_stylist.design_concepts = self.elements_specialist.design_concepts

        look_descriptions = []
        num_looks = self.num_looks

        for look_idx in range(num_looks):
            look_number = look_idx + 1
            # 在生成每个look之前，清除look_stylist的状态，确保编号正确
            self.look_stylist.reset()
            
            for _i in range(max_tries):
                if self.verbose:
                    print(f"@@ Workflow #{self.workflow_index} - Look {look_number} - Step {_i} @@")
                resp = self.look_stylist.inference(
                    # 避免与 LookDescriptionAgent.context() 中的 theme/theme_analysis 重复
                    research_topic=f"Design Target: {self.design_target_prompt}\nLook Number: {look_number}",
                    phase="look description generation",
                    feedback="",
                    step=_i
                )
                if self.verbose:
                    print("Look Stylist: ", resp, "\n~~~~~~~~~~~")

                if "```LOOK_DESCRIPTION" in resp:
                    look_desc = extract_prompt(resp, "LOOK_DESCRIPTION")
                    look_descriptions.append(look_desc)
                    self.look_stylist.look_descriptions.append(look_desc)
                    
                    # 与写入 look_XX.txt 的文本一致（含首行补全），供评估/优化与 looks_original 对齐
                    required_line = "Please generate female models and the matching clothing for them."
                    look_desc_to_save = look_desc
                    head_lines = [ln.strip() for ln in (look_desc_to_save or "").splitlines()[:3]]
                    if not head_lines or required_line not in head_lines:
                        look_desc_to_save = required_line + "\n\n" + (look_desc_to_save.lstrip("\n") if look_desc_to_save else "")
                    save_path = None
                    if group_dir:
                        save_path = os.path.join(group_dir, f"look_{look_idx + 1:02d}.txt")
                        os.makedirs(os.path.dirname(save_path), exist_ok=True)
                        with open(save_path, "w", encoding="utf-8") as f:
                            f.write(look_desc_to_save)

                    # 文本评估 + 自适应优化（pre 文本必须与磁盘/评估文件一致）
                    eval_key = (getattr(self, "_current_chapter_idx", 0) or 0, look_number)
                    eval_result = self._evaluate_and_optimize_look(
                        look_txt_path=save_path,
                        look_desc_raw=look_desc_to_save,
                        chapter_idx=eval_key[0],
                        look_number=look_number,
                    )
                    self.look_evaluation_results[eval_key] = eval_result

                    # 每生成一个 look 后进行一次单图 reflect（若该 look 图片已导入）
                    # n：跳过该 look 的 reflect，继续生成下一个 look
                    # y：执行 reflect 并展示淘汰信息
                    self.run_single_look_reflection(
                        chapter_idx=getattr(self, "_current_chapter_idx", 0) or 0,
                        look_number=look_number,
                        sub_theme_name=getattr(self, "_current_sub_theme_name", "") or "",
                        chapter_dir=group_dir,
                    )
                    
                    self.reset_agents()
                    break

    def design_elements_proposal(self):
        """执行设计元素提案阶段（考虑整体主题和所有子主题，生成一份设计元素）"""
        max_tries = self.max_steps
        
        # 设置 DesignElementsAgent 的属性，包含主题和所有设计概念
        self.elements_specialist.theme = self.theme
        self.elements_specialist.theme_analysis = self.theme_analyzer.theme_analysis
        self.elements_specialist.design_concepts = self.concept_designer.design_concepts

        for _i in range(max_tries):
            if self.verbose:
                print(f"@@ Workflow #{self.workflow_index} - Step {_i} @@")
            resp = self.elements_specialist.inference(
                research_topic=f"Theme: {self.theme}\nDesign Target: {self.design_target_prompt}",
                phase="design elements proposal",
                feedback="",
                step=_i
            )
            if self.verbose:
                print("Elements Specialist: ", resp, "\n~~~~~~~~~~~")

            if "```DESIGN_ELEMENTS" in resp:
                elements = extract_prompt(resp, "DESIGN_ELEMENTS")
                self.elements_specialist.candidate_elements = [elements]
                
                # 保存结果到文件
                if self.workflow_dir:
                    save_path = os.path.join(self.workflow_dir, "design_elements.txt")
                    os.makedirs(os.path.dirname(save_path), exist_ok=True)
                    with open(save_path, "w", encoding="utf-8") as f:
                        f.write(f"Theme: {self.theme}\n")
                        f.write(f"{'='*50}\n")
                        f.write(f"{elements}\n")
                
                self.reset_agents()
                self.statistics_per_phase["design elements proposal"]["steps"] = _i
                return False

        if self.except_if_fail:
            raise Exception("Max tries during phase: Design Elements Proposal")
        return False

    def look_description_generation(self):
        """执行 Look 描述生成阶段"""
        max_tries = self.max_steps
        
        # 使用设计元素生成 Look 描述
        self.look_stylist.design_target_prompt = self.design_target_prompt
        self.look_stylist.candidate_elements = self.elements_specialist.candidate_elements
        self.look_stylist.design_concepts = self.concept_designer.design_concepts

        look_descriptions = []
        # 为每个设计元素集合生成多个 Look
        num_looks = self.num_looks

        for look_idx in range(num_looks):
            for _i in range(max_tries):
                if self.verbose:
                    print(f"@@ Workflow #{self.workflow_index} - Look {look_idx + 1} - Step {_i} @@")
                resp = self.look_stylist.inference(
                    research_topic=f"Design Target: {self.design_target_prompt}\nTheme: {self.theme}",
                    phase="look description generation",
                    feedback="",
                    step=_i
                )
                if self.verbose:
                    print("Look Stylist: ", resp, "\n~~~~~~~~~~~")

                if "```LOOK_DESCRIPTION" in resp:
                    look_desc = extract_prompt(resp, "LOOK_DESCRIPTION")
                    look_descriptions.append(look_desc)
                    self.look_stylist.look_descriptions.append(look_desc)
                    
                    # 保存结果到文件
                    if self.workflow_dir:
                        required_line = "Please generate female models and the matching clothing for them."
                        look_desc_to_save = look_desc
                        head_lines = [ln.strip() for ln in (look_desc_to_save or "").splitlines()[:3]]
                        if not head_lines or required_line not in head_lines:
                            look_desc_to_save = required_line + "\n\n" + (look_desc_to_save.lstrip("\n") if look_desc_to_save else "")
                        save_path = os.path.join(self.workflow_dir, f"look_{look_idx + 1:02d}.txt")
                        os.makedirs(os.path.dirname(save_path), exist_ok=True)
                        with open(save_path, "w", encoding="utf-8") as f:
                            f.write(look_desc_to_save)
                    
                    self.reset_agents()
                    break

        return False

    def human_in_loop(self, phase, phase_prod):
        """人工介入循环"""
        print("\n\n\n\n\n")
        print(f"当前阶段 [{phase}] 的输出结果：\n{phase_prod}")
        y_or_no = None
        while y_or_no not in ["y", "n"]:
            y_or_no = input("\n\n\n您对当前输出满意吗？输入 Y 或 N: ").strip().lower()
            if y_or_no == "y":
                pass
            elif y_or_no == "n":
                notes_for_agent = input("请提供改进建议，以便 Agent 重新尝试: ")
                self.reset_agents()
                self.notes.append({
                    "phases": [phase],
                    "note": notes_for_agent
                })
                return True
            else:
                print("无效输入，请输入 Y 或 N")
        return False


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="Fashion Design Workflow")
    parser.add_argument(
        '--yaml-location',
        type=str,
        default="fashion_config.yaml",
        help='YAML 配置文件路径'
    )
    return parser.parse_args()


@dataclass
class TextEvaluatorConfig:
    enabled: bool = False
    # 自适应门限：任一项未达门限即触发 optimize
    adaptive_min_total_score: float = 0.82
    adaptive_min_quality_score: float = 0.80
    adaptive_penalty_threshold: float = 0.05
    # optimize 优化轮上限
    max_optimize_rounds: int = 5
    # optimize 内部双门限（两门均通过则早停）
    score_gate_min: float = 0.75
    penalty_gate_max: float = 0.15
    # improve threshold（早停用）
    min_score_improvement: float = 0.02
    min_quality_improvement: float = 0.05
    # API 配置（None 表示从 spec 默认读取）
    evaluator_api_key: str | None = None
    evaluator_api_base: str | None = None
    evaluator_model: str | None = None       # spec 默认: gpt-5.4-mini
    evaluator_temperature: float = 0.0       # 裁判评分用
    rewriter_temperature: float = 0.1        # spec rewriter.temperature 默认


def parse_yaml(yaml_file_loc):
    """解析 YAML 配置文件"""
    with open(yaml_file_loc, 'r', encoding='utf-8') as file:
        config_data = yaml.safe_load(file)
    
    class YamlDataHolder:
        def __init__(self):
            pass
    
    parser = YamlDataHolder()
    
    # 解析配置项，设置默认值
    if "copilot-mode" in config_data:
        parser.copilot_mode = config_data["copilot-mode"]
    else:
        parser.copilot_mode = False
    
    if "load-previous" in config_data:
        parser.load_previous = config_data["load-previous"]
    else:
        parser.load_previous = False
    
    if "design-target-prompt" in config_data:
        parser.design_target_prompt = config_data["design-target-prompt"]
    else:
        parser.design_target_prompt = None
    
    if "theme" in config_data:
        parser.theme = config_data["theme"]
    else:
        parser.theme = None

    if "brand" in config_data:
        parser.brand = config_data["brand"]
    else:
        parser.brand = None
    
    if "api-key" in config_data:
        parser.api_key = config_data["api-key"]
    else:
        parser.api_key = None
    
    # 兼容旧字段，但推荐直接使用 api-key，并通过 ohmygpt 网关访问
    if "siliconflow-api-key" in config_data:
        parser.siliconflow_api_key = config_data["siliconflow-api-key"]
    else:
        parser.siliconflow_api_key = None
    
    if "llm-backend" in config_data:
        parser.llm_backend = config_data["llm-backend"]
    else:
        parser.llm_backend = DEFAULT_LLM_BACKBONE
    
    if "language" in config_data:
        parser.language = config_data["language"]
    else:
        parser.language = "Chinese"
    
    if "max-steps" in config_data:
        parser.max_steps = config_data["max-steps"]
    else:
        parser.max_steps = 100
    
    if "workflow-index" in config_data:
        parser.workflow_index = config_data["workflow-index"]
    else:
        parser.workflow_index = 0
    
    if "except-if-fail" in config_data:
        parser.except_if_fail = config_data["except-if-fail"]
    else:
        parser.except_if_fail = False
    
    if "task-notes" in config_data:
        parser.task_notes = config_data["task-notes"]
    else:
        parser.task_notes = {}
    
    if "num-chapters" in config_data:
        parser.num_chapters = config_data["num-chapters"]
    else:
        parser.num_chapters = 4
    
    if "num-looks" in config_data:
        parser.num_looks = config_data["num-looks"]
    else:
        parser.num_looks = 1

    # -- text evaluator 配置 -- #
    ev = config_data.get("text-evaluator", {})
    parser.text_evaluator_enabled = bool(ev.get("enabled", False))
    parser.evaluator_adaptive_min_total_score = float(ev.get("adaptive-min-total-score", 0.82))
    parser.evaluator_adaptive_min_quality_score = float(ev.get("adaptive-min-quality-score", 0.80))
    parser.evaluator_adaptive_penalty_threshold = float(ev.get("adaptive-penalty-threshold", 0.05))
    parser.evaluator_max_optimize_rounds = int(ev.get("max-optimize-rounds", 5))
    parser.evaluator_score_gate_min = float(ev.get("score-gate-min", 0.85))
    parser.evaluator_penalty_gate_max = float(ev.get("penalty-gate-max", 0.10))
    parser.evaluator_api_key = ev.get("api-key") or None
    parser.evaluator_api_base = ev.get("api-base") or None
    parser.evaluator_model = ev.get("model") or None
    parser.evaluator_temperature = float(ev.get("temperature", 0.0))
    parser.evaluator_rewriter_temperature = float(ev.get("rewriter-temperature", 0.1))

    return parser


if __name__ == "__main__":
    user_args = parse_arguments()
    yaml_to_use = user_args.yaml_location
    args = parse_yaml(yaml_to_use)

    # 处理布尔值
    human_mode = args.copilot_mode.lower() == "true" if isinstance(args.copilot_mode, str) else args.copilot_mode
    load_previous = args.load_previous.lower() == "true" if isinstance(args.load_previous, str) else args.load_previous
    except_if_fail = args.except_if_fail.lower() == "true" if isinstance(args.except_if_fail, str) else args.except_if_fail

    # 获取 API 密钥
    # 优先顺序：YAML 中的 api-key -> 环境变量 OHMYGPT_API_KEY -> OPENAI_API_KEY
    api_key = (args.api_key or os.getenv('OHMYGPT_API_KEY') or os.getenv('OPENAI_API_KEY'))
    if not api_key:
        raise ValueError("API key must be provided via config file or environment variable")

    # 处理设计目标和主题
    if human_mode or args.design_target_prompt is None:
        design_target_prompt = input("请输入设计目标提示: ")
    else:
        design_target_prompt = args.design_target_prompt

    if human_mode or args.theme is None:
        theme = input("请输入主题描述: ")
    else:
        theme = args.theme

    # 处理任务备注
    task_notes_LLM = list()
    task_notes = args.task_notes
    for _task in task_notes:
        for _note in task_notes[_task]:
            task_notes_LLM.append({
                "phases": [_task.replace("-", " ")],
                "note": _note
            })

    if args.language != "Chinese":
        task_notes_LLM.append({
            "phases": ["theme analysis", "concept brainstorming", "design elements proposal", "look description generation"],
            "note": f"You should always write in the following language: {args.language}"
        })

    # 人工介入标志
    human_in_loop = {
        "theme analysis": human_mode,
        "concept brainstorming": human_mode,
        "design elements proposal": human_mode,
        "look description generation": human_mode,
    }

    # Agent 模型配置
    agent_models = {
        "theme analysis": args.llm_backend,
        "concept brainstorming": args.llm_backend,
        "design elements proposal": args.llm_backend,
        "look description generation": args.llm_backend,
    }

    # 加载已有状态或创建新工作流
    if load_previous:
        workflow = FashionWorkflow.load_state(args.workflow_index)
    else:
        # 创建工作流目录
        if not os.path.exists(RESEARCH_DIR_PATH):
            os.makedirs(RESEARCH_DIR_PATH)
        workflow_root_dir = os.path.join(RESEARCH_DIR_PATH, f"workflow_{args.workflow_index}")
        os.makedirs(workflow_root_dir, exist_ok=True)

        # 每次运行在 workflow_{index} 下创建以当天日期命名的子目录
        workflow_dir = create_dated_run_dir(workflow_root_dir)

        # 构建 text evaluator 配置
        evaluator_cfg = TextEvaluatorConfig(
            enabled=args.text_evaluator_enabled,
            adaptive_min_total_score=args.evaluator_adaptive_min_total_score,
            adaptive_min_quality_score=args.evaluator_adaptive_min_quality_score,
            adaptive_penalty_threshold=args.evaluator_adaptive_penalty_threshold,
            max_optimize_rounds=args.evaluator_max_optimize_rounds,
            score_gate_min=args.evaluator_score_gate_min,
            penalty_gate_max=args.evaluator_penalty_gate_max,
            evaluator_api_key=args.evaluator_api_key,
            evaluator_api_base=args.evaluator_api_base,
            evaluator_model=args.evaluator_model,
            evaluator_temperature=args.evaluator_temperature,
            rewriter_temperature=args.evaluator_rewriter_temperature,
        )

        workflow = FashionWorkflow(
            design_target_prompt=design_target_prompt,
            theme=theme,
            brand=getattr(args, "brand", None),
            openai_api_key=api_key,
            max_steps=args.max_steps,
            agent_model_backbone=agent_models,
            notes=task_notes_LLM,
            human_in_loop_flag=human_in_loop,
            workflow_dir=workflow_dir,
            workflow_index=args.workflow_index,
            except_if_fail=except_if_fail,
            num_chapters=args.num_chapters,
            num_looks=args.num_looks,
            text_evaluator_config=evaluator_cfg,
        )

    # 执行工作流
    workflow.perform_research()


"""
淘汰处理模块
处理 reflect_agent 发生淘汰时的文件移动、重命名和重新生成逻辑
"""
import os
import shutil
from datetime import datetime
from pathlib import Path
import re


class EliminationHandler:
    """处理淘汰文件的移动、重命名和重新生成"""
    
    def __init__(self, workflow_dir: str):
        """
        初始化淘汰处理器
        
        Args:
            workflow_dir: 工作流目录路径
        """
        self.workflow_dir = workflow_dir
    
    @staticmethod
    def _get_timestamp() -> str:
        """获取当前时间戳字符串"""
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _create_eliminated_dir(self, parent_dir: str, dir_name: str = "eliminated") -> str:
        """
        在指定目录下创建淘汰文件专用文件夹
        
        Args:
            parent_dir: 父目录路径
            dir_name: 淘汰文件夹名称
            
        Returns:
            淘汰文件夹的完整路径
        """
        eliminated_dir = os.path.join(parent_dir, dir_name)
        os.makedirs(eliminated_dir, exist_ok=True)
        return eliminated_dir
    
    def eliminate_look_files(
        self,
        chapter_dir: str,
        look_numbers: list,
        reason: str = ""
    ) -> dict:
        """
        淘汰chapter中的look文件（图片+txt）
        
        Args:
            chapter_dir: chapter目录路径
            look_numbers: 要淘汰的look编号列表（如 [3, 4]）
            reason: 淘汰原因
            
        Returns:
            包含淘汰信息的字典
        """
        if not look_numbers:
            return {"success": True, "eliminated_files": [], "message": "没有需要淘汰的文件"}
        
        # 创建淘汰文件夹
        eliminated_dir = self._create_eliminated_dir(chapter_dir, "eliminated_looks")
        timestamp = self._get_timestamp()
        
        eliminated_files = []
        
        for look_num in look_numbers:
            # 查找该look的所有相关文件
            look_stem = f"look_{look_num:02d}"
            
            # 查找图片文件
            for ext in [".png", ".jpg", ".jpeg", ".webp"]:
                src_image = os.path.join(chapter_dir, f"{look_stem}{ext}")
                if os.path.exists(src_image):
                    # 重命名：look_03.jpg -> look_03_eliminated_20260205_143022.jpg
                    new_name = f"{look_stem}_eliminated_{timestamp}{ext}"
                    dst_image = os.path.join(eliminated_dir, new_name)
                    shutil.move(src_image, dst_image)
                    eliminated_files.append({
                        "original": src_image,
                        "new_location": dst_image,
                        "type": "image"
                    })
                    break
            
            # 查找txt文件
            src_txt = os.path.join(chapter_dir, f"{look_stem}.txt")
            if os.path.exists(src_txt):
                new_name = f"{look_stem}_eliminated_{timestamp}.txt"
                dst_txt = os.path.join(eliminated_dir, new_name)
                shutil.move(src_txt, dst_txt)
                eliminated_files.append({
                    "original": src_txt,
                    "new_location": dst_txt,
                    "type": "txt"
                })
            
            # 查找reflection文件（可选）
            src_reflection = os.path.join(chapter_dir, f"{look_stem}_reflection.txt")
            if os.path.exists(src_reflection):
                new_name = f"{look_stem}_reflection_eliminated_{timestamp}.txt"
                dst_reflection = os.path.join(eliminated_dir, new_name)
                shutil.move(src_reflection, dst_reflection)
                eliminated_files.append({
                    "original": src_reflection,
                    "new_location": dst_reflection,
                    "type": "reflection"
                })
        
        # 更新chapter的reflection.txt，追加淘汰记录
        self._append_elimination_reason_to_reflection(
            chapter_dir,
            look_numbers,
            reason,
            eliminated_files
        )
        
        return {
            "success": True,
            "eliminated_files": eliminated_files,
            "message": f"已淘汰 {len(look_numbers)} 个look的相关文件"
        }
    
    def eliminate_chapter(
        self,
        chapter_dir: str,
        reason: str = ""
    ) -> dict:
        """
        淘汰整个chapter文件夹
        
        Args:
            chapter_dir: chapter目录路径
            reason: 淘汰原因
            
        Returns:
            包含淘汰信息的字典
        """
        if not os.path.exists(chapter_dir):
            return {"success": False, "message": "chapter目录不存在"}
        
        # 提取chapter编号
        chapter_name = os.path.basename(chapter_dir)
        match = re.search(r"chapter_(\d+)", chapter_name, re.IGNORECASE)
        if not match:
            return {"success": False, "message": "无法解析chapter编号"}
        
        chapter_num = match.group(1)
        
        # 在workflow目录下创建淘汰章节文件夹
        eliminated_chapters_dir = self._create_eliminated_dir(
            self.workflow_dir,
            "eliminated_chapters"
        )
        
        # 重命名：chapter_02 -> chapter_02_eliminated_20260205_143022
        timestamp = self._get_timestamp()
        new_name = f"{chapter_name}_eliminated_{timestamp}"
        dst_chapter = os.path.join(eliminated_chapters_dir, new_name)
        
        # 移动整个chapter文件夹
        shutil.move(chapter_dir, dst_chapter)
        
        # 更新collection的reflection.txt，追加淘汰记录
        self._append_chapter_elimination_to_collection_reflection(
            chapter_num,
            reason,
            dst_chapter
        )
        
        return {
            "success": True,
            "original": chapter_dir,
            "new_location": dst_chapter,
            "message": f"已淘汰chapter {chapter_num}"
        }
    
    def _append_elimination_reason_to_reflection(
        self,
        chapter_dir: str,
        look_numbers: list,
        reason: str,
        eliminated_files: list
    ):
        """
        在chapter的reflection.txt中追加淘汰记录
        
        Args:
            chapter_dir: chapter目录路径
            look_numbers: 被淘汰的look编号列表
            reason: 淘汰原因
            eliminated_files: 被淘汰的文件列表
        """
        reflection_path = os.path.join(chapter_dir, "reflection.txt")
        
        # 读取现有内容
        existing_content = ""
        if os.path.exists(reflection_path):
            with open(reflection_path, "r", encoding="utf-8") as f:
                existing_content = f.read()
        
        # 追加淘汰记录
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        elimination_record = f"\n\n{'='*60}\n"
        elimination_record += f"淘汰记录 - {timestamp}\n"
        elimination_record += f"{'='*60}\n"
        elimination_record += f"被淘汰的Look编号: {', '.join([f'look_{n:02d}' for n in look_numbers])}\n\n"
        elimination_record += f"淘汰原因:\n{reason}\n\n"
        elimination_record += f"已移动的文件:\n"
        for file_info in eliminated_files:
            rel_path = os.path.relpath(file_info["new_location"], chapter_dir)
            elimination_record += f"  - {os.path.basename(file_info['original'])} -> {rel_path}\n"
        
        # 写回文件
        with open(reflection_path, "w", encoding="utf-8") as f:
            f.write(existing_content)
            f.write(elimination_record)
    
    def _append_chapter_elimination_to_collection_reflection(
        self,
        chapter_num: str,
        reason: str,
        new_location: str
    ):
        """
        在collection的reflection.txt中追加chapter淘汰记录
        
        Args:
            chapter_num: 被淘汰的chapter编号
            reason: 淘汰原因
            new_location: 新位置路径
        """
        reflection_path = os.path.join(self.workflow_dir, "reflection.txt")
        
        # 读取现有内容
        existing_content = ""
        if os.path.exists(reflection_path):
            with open(reflection_path, "r", encoding="utf-8") as f:
                existing_content = f.read()
        
        # 追加淘汰记录
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        elimination_record = f"\n\n{'='*60}\n"
        elimination_record += f"Chapter淘汰记录 - {timestamp}\n"
        elimination_record += f"{'='*60}\n"
        elimination_record += f"被淘汰的Chapter: chapter_{chapter_num}\n\n"
        elimination_record += f"淘汰原因:\n{reason}\n\n"
        rel_path = os.path.relpath(new_location, self.workflow_dir)
        elimination_record += f"已移动到: {rel_path}\n"
        
        # 写回文件
        with open(reflection_path, "w", encoding="utf-8") as f:
            f.write(existing_content)
            f.write(elimination_record)
    
    @staticmethod
    def renumber_looks_in_directory(chapter_dir: str):
        """
        重新编号chapter目录中的look文件，确保编号连续
        
        Args:
            chapter_dir: chapter目录路径
        """
        if not os.path.exists(chapter_dir):
            return
        
        # 收集所有look文件
        look_files = {}
        for filename in os.listdir(chapter_dir):
            match = re.match(r"look_(\d+)(\.txt|\.png|\.jpg|\.jpeg|\.webp|_reflection\.txt)", filename, re.IGNORECASE)
            if match:
                look_num = int(match.group(1))
                ext = match.group(2)
                if look_num not in look_files:
                    look_files[look_num] = []
                look_files[look_num].append((filename, ext))
        
        # 按编号排序
        sorted_looks = sorted(look_files.keys())
        
        # 重新编号（如果需要）
        for new_idx, old_num in enumerate(sorted_looks, start=1):
            if new_idx != old_num:
                # 需要重新编号
                for old_filename, ext in look_files[old_num]:
                    old_path = os.path.join(chapter_dir, old_filename)
                    new_filename = old_filename.replace(f"look_{old_num:02d}", f"look_{new_idx:02d}")
                    new_path = os.path.join(chapter_dir, new_filename)
                    os.rename(old_path, new_path)
    
    @staticmethod
    def renumber_chapters_in_workflow(workflow_dir: str):
        """
        重新编号workflow目录中的chapter文件夹，确保编号连续
        
        Args:
            workflow_dir: workflow目录路径
        """
        if not os.path.exists(workflow_dir):
            return
        
        # 收集所有chapter目录
        chapter_dirs = {}
        for dirname in os.listdir(workflow_dir):
            match = re.match(r"chapter_(\d+)", dirname, re.IGNORECASE)
            if match:
                chapter_num = int(match.group(1))
                full_path = os.path.join(workflow_dir, dirname)
                if os.path.isdir(full_path):
                    chapter_dirs[chapter_num] = dirname
        
        # 按编号排序
        sorted_chapters = sorted(chapter_dirs.keys())
        
        # 重新编号（如果需要）
        # 使用临时前缀避免冲突
        temp_prefix = "temp_chapter_"
        temp_mappings = {}
        
        for new_idx, old_num in enumerate(sorted_chapters, start=1):
            if new_idx != old_num:
                old_path = os.path.join(workflow_dir, chapter_dirs[old_num])
                temp_name = f"{temp_prefix}{new_idx:02d}"
                temp_path = os.path.join(workflow_dir, temp_name)
                os.rename(old_path, temp_path)
                temp_mappings[new_idx] = temp_path
        
        # 重命名为最终名称
        for new_idx, temp_path in temp_mappings.items():
            final_name = f"chapter_{new_idx:02d}"
            final_path = os.path.join(workflow_dir, final_name)
            os.rename(temp_path, final_path)

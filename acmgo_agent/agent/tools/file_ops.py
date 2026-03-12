"""
文件操作工具。
"""
import os
from typing import Dict, Any
from .base import Tool


class SaveFileTool(Tool):
    """用于保存文件到工作目录的工具。"""

    def __init__(self, work_dir: str):
        super().__init__(
            name="save_file",
            description=(
                "保存文件到工作目录。用于保存 C++ 代码、Python 脚本、README 等。"
                "如果文件已存在，将会被覆盖。"
            ),
            parameters={
                "filename": {
                    "type": "string",
                    "description": "文件名（如 sol.cpp, README.md）",
                },
                "content": {
                    "type": "string",
                    "description": "文件内容（完整文本）",
                },
            },
        )
        self.work_dir = os.path.abspath(work_dir)

    def execute(self, filename: str, content: str) -> Dict[str, Any]:
        """保存文件到工作目录。"""
        # Validate parameters
        error = self.validate_parameters({"filename": filename, "content": content})
        if error:
            return {"success": False, "error": error}

        # Build full path
        path = os.path.join(self.work_dir, filename)

        # Create parent directories if needed
        parent_dir = os.path.dirname(path)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)

        # Check if file exists
        file_exists = os.path.exists(path)

        try:
            # Write file
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)

            action = "已更新" if file_exists else "已保存"
            return {
                "success": True,
                "path": path,
                "action": "update" if file_exists else "create",
                "message": f"{action} {filename}",
            }
        except IOError as e:
            return {
                "success": False,
                "error": f"无法写入文件 {filename}: {str(e)}",
                "path": path,
            }


class ReadFileTool(Tool):
    """用于从工作目录读取文件的工具。"""

    def __init__(self, work_dir: str):
        super().__init__(
            name="read_file",
            description=(
                "读取工作目录中的文件内容。用于查看已创建的文件内容，"
                "如代码实现、README 等。"
            ),
            parameters={
                "filename": {
                    "type": "string",
                    "description": "文件名（如 sol.cpp, README.md）",
                },
            },
        )
        self.work_dir = os.path.abspath(work_dir)

    def execute(self, filename: str) -> Dict[str, Any]:
        """从工作目录读取文件。"""
        # Validate parameters
        error = self.validate_parameters({"filename": filename})
        if error:
            return {"success": False, "error": error}

        # Build full path
        path = os.path.join(self.work_dir, filename)

        # Check if file exists
        if not os.path.exists(path):
            return {
                "success": False,
                "error": f"找不到文件: {filename}",
                "path": path,
            }

        try:
            # Read file
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            return {
                "success": True,
                "path": path,
                "content": content,
                "size": len(content),
                "message": f"已读取 {filename} ({len(content)} 字符)",
            }
        except IOError as e:
            return {
                "success": False,
                "error": f"无法读取文件 {filename}: {str(e)}",
                "path": path,
            }


class ListFilesTool(Tool):
    """用于列出工作目录中文件的工具。"""

    def __init__(self, work_dir: str):
        super().__init__(
            name="list_files",
            description=(
                "列出工作目录中的文件和子目录。用于查看当前项目结构。"
            ),
            parameters={
                "directory": {
                    "type": "string",
                    "description": "要列出的目录（相对于工作目录，留空表示工作目录）",
                },
            },
        )
        self.work_dir = os.path.abspath(work_dir)

    def execute(self, directory: str = "") -> Dict[str, Any]:
        """列出目录中的文件。"""
        # Build full path
        if directory:
            path = os.path.join(self.work_dir, directory)
        else:
            path = self.work_dir

        # Check if directory exists
        if not os.path.exists(path):
            return {
                "success": False,
                "error": f"找不到目录: {directory}",
                "path": path,
            }

        if not os.path.isdir(path):
            return {
                "success": False,
                "error": f"不是目录: {directory}",
                "path": path,
            }

        try:
            # List directory
            entries = []
            for entry in os.listdir(path):
                full_path = os.path.join(path, entry)
                if os.path.isdir(full_path):
                    entries.append({"name": entry, "type": "directory"})
                else:
                    size = os.path.getsize(full_path)
                    entries.append({"name": entry, "type": "file", "size": size})

            # Sort: directories first, then files
            entries.sort(key=lambda x: (x["type"] == "file", x["name"]))

            return {
                "success": True,
                "path": path,
                "entries": entries,
                "message": f"列出目录 {directory or '.'}: {len(entries)} 项",
            }
        except OSError as e:
            return {
                "success": False,
                "error": f"无法列出目录 {directory}: {str(e)}",
                "path": path,
            }

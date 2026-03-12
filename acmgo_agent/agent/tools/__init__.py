"""
Agent 的工具实现。

此包提供各种工具：
- 文件操作（保存、读取、列出）
- C++ 编译
- 压力测试
- 测试数据生成
- Polygon 格式打包
"""

from .base import Tool

# File operation tools
from .file_ops import SaveFileTool, ReadFileTool, ListFilesTool

# Compiler tools
from .compiler import CompileCppTool, CompileAllTool

# Stress test tools
from .stress_test import RunStressTestTool, QuickStressTestTool

# Test generation
from .test_generator import GenerateTestsTool

# Polygon packing
from .polygon_packer import PackPolygonTool, SetupDevTool

__all__ = [
    # Base
    "Tool",
    # File operations
    "SaveFileTool",
    "ReadFileTool",
    "ListFilesTool",
    # Compiler
    "CompileCppTool",
    "CompileAllTool",
    # Stress testing
    "RunStressTestTool",
    "QuickStressTestTool",
    # Test generation
    "GenerateTestsTool",
    # Polygon packing
    "PackPolygonTool",
    "SetupDevTool",
]

"""测试 C++ 编译器工具。"""
import os
import sys
import pytest

from acmgo_agent.agent.tools.compiler import CompileCppTool, CompileAllTool


class TestCompileCppTool:
    """测试 CompileCppTool 类。"""

    def test_compile_success(self, tmp_work_dir):
        """测试编译简单的 C++ 文件。"""
        tool = CompileCppTool(tmp_work_dir)

        # 创建一个简单的 C++ 文件
        source_file = "simple.cpp"
        source_content = "#include <iostream>\nint main() { std::cout << 42; return 0; }"
        with open(os.path.join(tmp_work_dir, source_file), "w", encoding="utf-8") as f:
            f.write(source_content)

        result = tool.execute(source_file)
        assert result["success"]
        assert "exe_path" in result
        assert os.path.exists(result["exe_path"])

    def test_compile_file_not_found(self, tmp_work_dir):
        """测试编译不存在的文件。"""
        tool = CompileCppTool(tmp_work_dir)
        result = tool.execute("nonexistent.cpp")
        assert not result["success"]
        assert "error" in result
        assert "not found" in result["error"].lower()

    def test_compile_invalid_extension(self, tmp_work_dir):
        """测试非 .cpp 文件。"""
        tool = CompileCppTool(tmp_work_dir)
        result = tool.execute("test.txt")
        assert not result["success"]
        assert "error" in result
        assert ".cpp extension" in result["error"]

    def test_compile_compilable_cpp(self, tmp_work_dir):
        """测试可编译的 C++ 文件。"""
        tool = CompileCppTool(tmp_work_dir)

        source_file = "main.cpp"
        source_content = """
#include <bits/stdc++.h>
using namespace std;
int main() {
    int a, b;
    cin >> a >> b;
    cout << a + b << endl;
    return 0;
}
"""
        with open(os.path.join(tmp_work_dir, source_file), "w", encoding="utf-8") as f:
            f.write(source_content)

        result = tool.execute(source_file)
        assert result["success"]
        assert "message" in result


class TestCompileAllTool:
    """测试 CompileAllTool 类。"""

    def test_compile_all_success(self, sample_cpp_files):
        """测试编译所有源文件。"""
        # sample_cpp_files 只创建了部分文件，需要创建完整的文件
        # 确保所有必需文件都存在
        for src in ["gen.cpp", "val.cpp", "sol.cpp", "brute.cpp"]:
            if not os.path.exists(os.path.join(sample_cpp_files, src)):
                with open(os.path.join(sample_cpp_files, src), "w", encoding="utf-8") as f:
                    f.write("#include <iostream>\nint main() { return 0; }")

        tool = CompileAllTool(sample_cpp_files)
        result = tool.execute()
        assert result["success"]
        assert "compiled_files" in result
        assert len(result["compiled_files"]) > 0

    def test_compile_all_partial_failure(self, tmp_work_dir):
        """测试部分编译失败。"""
        # 创建一个有效的 C++ 文件（必须是 CompileAllTool 编译的文件之一）
        valid_cpp = "sol.cpp"
        valid_content = "#include <iostream>\nint main() { return 0; }"
        with open(os.path.join(tmp_work_dir, valid_cpp), "w", encoding="utf-8") as f:
            f.write(valid_content)

        # 创建一个无效的 C++ 文件（语法错误）
        invalid_cpp = "gen.cpp"
        invalid_content = "int main { }"
        with open(os.path.join(tmp_work_dir, invalid_cpp), "w", encoding="utf-8") as f:
            f.write(invalid_content)

        tool = CompileAllTool(tmp_work_dir)
        result = tool.execute()

        # 结果应包含编译尝试
        assert "results" in result
        assert invalid_cpp in result["results"]
        valid_cpp_result = result["results"][valid_cpp]
        # 有效文件应该编译成功
        assert valid_cpp_result["success"]

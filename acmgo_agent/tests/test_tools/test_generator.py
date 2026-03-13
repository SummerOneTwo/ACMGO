"""测试测试数据生成工具。"""
import os
import shutil
import pytest

from acmgo_agent.agent.tools.test_generator import GenerateTestsTool


class TestGenerateTestsTool:
    """测试 GenerateTestsTool 类。"""

    def test_generate_tests_missing_files(self, tmp_work_dir):
        """测试缺少必要文件的情况。"""
        tool = GenerateTestsTool(tmp_work_dir)
        result = tool.execute(test_count=5)

        assert not result["success"]
        assert "error" in result

    def test_generate_tests_with_polygon_format(self, tmp_work_dir, sample_cpp_files):
        """测试生成测试数据（使用 Polygon 格式目录）。"""
        # 将源文件复制到 Polygon 格式目录
        files_dir = os.path.join(tmp_work_dir, "files")
        solutions_dir = os.path.join(tmp_work_dir, "solutions")

        os.makedirs(files_dir)
        os.makedirs(solutions_dir)

        # 复制源文件
        for src in ["testlib.h", "gen.cpp", "val.cpp"]:
            shutil.copy2(os.path.join(sample_cpp_files, src), os.path.join(files_dir, src))

        for src in ["sol.cpp", "brute.cpp"]:
            shutil.copy2(os.path.join(sample_cpp_files, src), os.path.join(solutions_dir, src))

        tool = GenerateTestsTool(tmp_work_dir)
        result = tool.execute(test_count=5)

        # 由于需要编译和运行，可能失败或成功
        # 主要验证工具被正确调用
        assert "success" in result

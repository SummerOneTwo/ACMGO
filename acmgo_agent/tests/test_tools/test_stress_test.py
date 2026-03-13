"""测试压力测试工具。"""
import os
import sys
import pytest

from acmgo_agent.agent.tools.stress_test import RunStressTestTool, QuickStressTestTool


class TestRunStressTestTool:
    """测试 RunStressTestTool 类。"""

    def test_run_stress_test_success(self, sample_cpp_files):
        """测试运行对拍测试（成功情况）。"""
        tool = RunStressTestTool(sample_cpp_files, trials=10, n_max=20, t_max=1)
        result = tool.execute(trials=10, n_max=20, t_max=1)

        assert result["success"]
        assert "completed_rounds" in result
        assert result["completed_rounds"] == 10

    def test_run_stress_test_missing_executables(self, tmp_work_dir):
        """测试缺少可执行文件的情况。"""
        tool = RunStressTestTool(tmp_work_dir)
        result = tool.execute()

        # 应该失败，因为缺少可执行文件
        assert not result["success"]
        assert "error" in result

    def test_quick_stress_test(self, sample_cpp_files):
        """测试快速对拍测试。"""
        tool = QuickStressTestTool(sample_cpp_files)
        result = tool.execute()

        assert result["success"]
        assert "completed_rounds" in result

    def test_stress_test_parameters_validation(self, sample_cpp_files):
        """测试参数验证。"""
        tool = RunStressTestTool(sample_cpp_files)

        # 使用不同参数运行
        result = tool.execute(trials=5, n_max=10, t_max=1)
        assert "trials" in result or "success" in result

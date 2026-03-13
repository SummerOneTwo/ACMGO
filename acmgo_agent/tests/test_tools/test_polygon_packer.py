"""测试 Polygon 格式打包工具。"""
import os
import shutil
import pytest

from acmgo_agent.agent.tools.polygon_packer import PackPolygonTool, SetupDevTool


class TestPackPolygonTool:
    """测试 PackPolygonTool 类。"""

    def test_pack_polygon_creates_directories(self, valid_problem_dir):
        """测试打包创建目录。"""
        tool = PackPolygonTool(valid_problem_dir)
        result = tool.execute()

        assert result["success"]
        assert "results" in result

        # 验证目录已创建
        assert os.path.exists(os.path.join(valid_problem_dir, "files"))
        assert os.path.exists(os.path.join(valid_problem_dir, "solutions"))
        assert os.path.exists(os.path.join(valid_problem_dir, "statements"))
        assert os.path.exists(os.path.join(valid_problem_dir, "scripts"))

    def test_pack_polygon_problem_xml(self, valid_problem_dir):
        """测试 problem.xml 生成。"""
        tool = PackPolygonTool(valid_problem_dir)
        result = tool.execute()

        assert result["success"]

        # 验证 problem.xml 存在
        problem_xml = os.path.join(valid_problem_dir, "problem.xml")
        assert os.path.exists(problem_xml)

        # 验证内容
        with open(problem_xml, "r", encoding="utf-8") as f:
            content = f.read()
            assert "<?xml" in content
            assert "<problem" in content

    def test_pack_polygon_moves_files(self, valid_problem_dir):
        """测试文件移动到正确位置。"""
        tool = PackPolygonTool(valid_problem_dir)
        result = tool.execute()

        assert result["success"]

        # 验证源文件已移动
        assert os.path.exists(os.path.join(valid_problem_dir, "files", "testlib.h"))
        assert os.path.exists(os.path.join(valid_problem_dir, "files", "gen.cpp"))
        assert os.path.exists(os.path.join(valid_problem_dir, "files", "val.cpp"))
        assert os.path.exists(os.path.join(valid_problem_dir, "solutions", "sol.cpp"))
        assert os.path.exists(os.path.join(valid_problem_dir, "solutions", "brute.cpp"))
        assert os.path.exists(os.path.join(valid_problem_dir, "statements", "README.md"))

    def test_pack_polygon_removes_dev_files(self, valid_problem_dir):
        """测试开发文件被移除。"""
        tool = PackPolygonTool(valid_problem_dir)
        result = tool.execute()

        # 开发文件应该被移除
        assert not os.path.exists(os.path.join(valid_problem_dir, "testlib.h"))
        assert not os.path.exists(os.path.join(valid_problem_dir, "sol.cpp"))
        assert not os.path.exists(os.path.join(valid_problem_dir, "brute.cpp"))
        assert not os.path.exists(os.path.join(valid_problem_dir, "README.md"))


class TestSetupDevTool:
    """测试 SetupDevTool 类。"""

    def test_setup_dev_restores_files(self, valid_problem_dir):
        """测试从 Polygon 格式恢复文件。"""
        # 首先打包
        pack_tool = PackPolygonTool(valid_problem_dir)
        pack_result = pack_tool.execute()
        assert pack_result["success"]

        # 然后设置开发环境
        setup_tool = SetupDevTool(valid_problem_dir)
        setup_result = setup_tool.execute()

        assert setup_result["success"]

        # 验证文件已恢复到根目录
        assert os.path.exists(os.path.join(valid_problem_dir, "testlib.h"))
        assert os.path.exists(os.path.join(valid_problem_dir, "sol.cpp"))
        assert os.path.exists(os.path.join(valid_problem_dir, "brute.cpp"))
        assert os.path.exists(os.path.join(valid_problem_dir, "README.md"))

    def test_setup_dev_with_empty_dirs(self, tmp_work_dir):
        """测试空目录情况。"""
        # 创建空目录
        os.makedirs(os.path.join(tmp_work_dir, "files"))
        os.makedirs(os.path.join(tmp_work_dir, "solutions"))
        os.makedirs(os.path.join(tmp_work_dir, "statements"))

        tool = SetupDevTool(tmp_work_dir)
        result = tool.execute()

        assert result["success"]

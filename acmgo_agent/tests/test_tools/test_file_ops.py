"""测试文件操作工具。"""
import os
import pytest

from acmgo_agent.agent.tools.file_ops import SaveFileTool, ReadFileTool, ListFilesTool


class TestSaveFileTool:
    """测试 SaveFileTool 类。"""

    def test_save_file(self, tmp_work_dir):
        """测试保存文件。"""
        tool = SaveFileTool(tmp_work_dir)

        result = tool.execute(filename="test.txt", content="Hello, World!")
        assert result["success"]
        assert "path" in result

        # 验证文件已创建
        file_path = os.path.join(tmp_work_dir, "test.txt")
        assert os.path.exists(file_path)

        # 验证内容
        with open(file_path, "r", encoding="utf-8") as f:
            assert f.read() == "Hello, World!"

    def test_save_file_update_existing(self, tmp_work_dir):
        """测试更新已存在的文件。"""
        tool = SaveFileTool(tmp_work_dir)

        # 创建初始文件
        result1 = tool.execute(filename="test.txt", content="Initial content")
        assert result1["success"]
        assert result1["action"] == "create"

        # 更新文件
        result2 = tool.execute(filename="test.txt", content="Updated content")
        assert result2["success"]
        assert result2["action"] == "update"

        # 验证内容已更新
        with open(os.path.join(tmp_work_dir, "test.txt"), "r", encoding="utf-8") as f:
            assert f.read() == "Updated content"

    def test_save_file_create_subdirectory(self, tmp_work_dir):
        """测试创建子目录中的文件。"""
        tool = SaveFileTool(tmp_work_dir)

        result = tool.execute(filename="subdir/test.txt", content="Test")
        assert result["success"]

        # 验证子目录和文件已创建
        file_path = os.path.join(tmp_work_dir, "subdir", "test.txt")
        assert os.path.exists(file_path)


class TestReadFileTool:
    """测试 ReadFileTool 类。"""

    def test_read_file(self, tmp_work_dir):
        """测试读取文件。"""
        # 先创建文件
        file_path = os.path.join(tmp_work_dir, "test.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("Hello, World!")

        tool = ReadFileTool(tmp_work_dir)
        result = tool.execute(filename="test.txt")

        assert result["success"]
        assert "content" in result
        assert result["content"] == "Hello, World!"

    def test_read_file_not_found(self, tmp_work_dir):
        """测试读取不存在的文件。"""
        tool = ReadFileTool(tmp_work_dir)
        result = tool.execute(filename="nonexistent.txt")

        assert not result["success"]
        assert "error" in result


class TestListFilesTool:
    """测试 ListFilesTool 类。"""

    def test_list_files(self, tmp_work_dir):
        """测试列出文件。"""
        # 创建一些文件
        with open(os.path.join(tmp_work_dir, "file1.txt"), "w") as f:
            f.write("")
        with open(os.path.join(tmp_work_dir, "file2.txt"), "w") as f:
            f.write("")
        os.makedirs(os.path.join(tmp_work_dir, "subdir"))

        tool = ListFilesTool(tmp_work_dir)
        result = tool.execute()

        assert result["success"]
        assert "entries" in result
        assert len(result["entries"]) == 3

        # 验证条目类型
        entry_names = [e["name"] for e in result["entries"]]
        assert "file1.txt" in entry_names
        assert "file2.txt" in entry_names
        assert "subdir" in entry_names

    def test_list_files_subdirectory(self, tmp_work_dir):
        """测试列出子目录中的文件。"""
        # 创建子目录和文件
        subdir = os.path.join(tmp_work_dir, "subdir")
        os.makedirs(subdir)
        with open(os.path.join(subdir, "nested.txt"), "w") as f:
            f.write("")

        tool = ListFilesTool(tmp_work_dir)
        result = tool.execute(directory="subdir")

        assert result["success"]
        assert len(result["entries"]) == 1
        assert result["entries"][0]["name"] == "nested.txt"

    def test_list_files_not_found(self, tmp_work_dir):
        """测试列出不存在的目录。"""
        tool = ListFilesTool(tmp_work_dir)
        result = tool.execute(directory="nonexistent")

        assert not result["success"]
        assert "error" in result


class TestFileOpsIntegration:
    """测试文件操作集成。"""

    def test_save_read_cycle(self, tmp_work_dir):
        """测试保存-读取循环。"""
        save_tool = SaveFileTool(tmp_work_dir)
        read_tool = ReadFileTool(tmp_work_dir)

        # 保存文件
        content = "This is a test\nwith multiple\nlines."
        save_result = save_tool.execute(filename="test.txt", content=content)
        assert save_result["success"]

        # 读取文件
        read_result = read_tool.execute(filename="test.txt")
        assert read_result["success"]
        assert read_result["content"] == content

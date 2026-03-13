"""测试 ProblemSetterAgent 核心功能。"""
import pytest

from acmgo_agent.agent.core.agent import ProblemSetterAgent


class TestProblemSetterAgent:
    """测试 ProblemSetterAgent 类。"""

    def test_agent_initialization(self, tmp_work_dir):
        """测试 Agent 初始化。"""
        # 创建一个简单的模拟提供商
        class MockProvider:
            def chat(self, messages, tools=None):
                return {"content": "Mock response"}

        provider = MockProvider()
        agent = ProblemSetterAgent(
            provider=provider,
            work_dir=tmp_work_dir,
            verbose=False
        )

        assert agent.work_dir == tmp_work_dir
        assert agent.verbose is False
        assert agent.max_retries == 3
        assert agent.tools is not None
        assert len(agent.tools) > 0

    def test_tool_registration(self, tmp_work_dir):
        """测试工具注册。"""
        class MockProvider:
            def chat(self, messages, tools=None):
                return {"content": "Mock response"}

        class MockTool:
            name = "mock_tool"
            description = "Mock tool"
            parameters = {}
            def execute(self, **kwargs):
                return {"success": True}

        provider = MockProvider()
        agent = ProblemSetterAgent(
            provider=provider,
            work_dir=tmp_work_dir,
            verbose=False
        )

        # 注册自定义工具
        agent.register_tool("mock_tool", MockTool())

        assert "mock_tool" in agent.tools

    def test_hook_system(self, tmp_work_dir):
        """测试钩子系统。"""
        class MockProvider:
            def chat(self, messages, tools=None):
                return {"content": "Mock response"}

        provider = MockProvider()
        agent = ProblemSetterAgent(
            provider=provider,
            work_dir=tmp_work_dir,
            verbose=False
        )

        # 设置钩子
        called_before = False
        called_after = False

        def before_hook(stage, context):
            nonlocal called_before
            called_before = True

        def after_hook(stage, result, context):
            nonlocal called_after
            called_after = True

        agent.set_hooks(before_stage=before_hook, after_stage=after_hook)

        assert agent.before_stage_hook is not None
        assert agent.after_stage_hook is not None

    def test_get_status(self, tmp_work_dir):
        """测试状态查询。"""
        class MockProvider:
            def chat(self, messages, tools=None):
                return {"content": "Mock response"}

        provider = MockProvider()
        agent = ProblemSetterAgent(
            provider=provider,
            work_dir=tmp_work_dir,
            verbose=False
        )

        status = agent.get_status()

        assert "progress" in status
        assert "current_stage" in status
        assert "completed_stages" in status
        assert "work_dir" in status
        assert status["work_dir"] == tmp_work_dir

    def test_custom_system_prompt(self, tmp_work_dir):
        """测试自定义系统提示词。"""
        class MockProvider:
            def chat(self, messages, tools=None):
                return {"content": "Mock response"}

        provider = MockProvider()
        agent = ProblemSetterAgent(
            provider=provider,
            work_dir=tmp_work_dir,
            verbose=False
        )

        custom_prompt = "This is a custom system prompt."
        agent.set_custom_system_prompt(custom_prompt)

        assert agent.custom_system_prompt == custom_prompt

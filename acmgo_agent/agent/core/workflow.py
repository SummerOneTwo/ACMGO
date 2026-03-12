"""
用于管理 6 步出题流程的工作流编排器。
"""
from typing import List, Dict, Any, Optional, Callable
from .state import WorkflowStage, StageResult


class WorkflowOrchestrator:
    """
    编排 6 步出题工作流。

    此类提供一个高级接口来管理工作流，
    支持钩子和阶段转换。
    """

    def __init__(self):
        """初始化工作流编排器。"""
        self.current_stage: Optional[WorkflowStage] = None
        self.completed_stages: List[WorkflowStage] = []
        self.stage_results: Dict[WorkflowStage, StageResult] = {}

        # Stage hooks
        self.before_stage_hooks: Dict[WorkflowStage, List[Callable]] = {}
        self.after_stage_hooks: Dict[WorkflowStage, List[Callable]] = {}

        # Global hooks
        self.before_any_stage: List[Callable] = []
        self.after_any_stage: List[Callable] = []

    def register_before_stage_hook(
        self, stage: WorkflowStage, hook: Callable
    ) -> None:
        """注册在特定阶段之前运行的钩子。"""
        if stage not in self.before_stage_hooks:
            self.before_stage_hooks[stage] = []
        self.before_stage_hooks[stage].append(hook)

    def register_after_stage_hook(
        self, stage: WorkflowStage, hook: Callable
    ) -> None:
        """注册在特定阶段之后运行的钩子。"""
        if stage not in self.after_stage_hooks:
            self.after_stage_hooks[stage] = []
        self.after_stage_hooks[stage].append(hook)

    def register_before_any_stage_hook(self, hook: Callable) -> None:
        """注册在任何阶段之前运行的钩子。"""
        self.before_any_stage.append(hook)

    def register_after_any_stage_hook(self, hook: Callable) -> None:
        """注册在任何阶段之后运行的钩子。"""
        self.after_any_stage.append(hook)

    def get_stage_order(self) -> List[WorkflowStage]:
        """获取阶段的默认顺序。"""
        return [
            WorkflowStage.STATEMENT,
            WorkflowStage.SOLUTIONS,
            WorkflowStage.VALIDATOR,
            WorkflowStage.GENERATOR,
            WorkflowStage.STRESS_TEST,
            WorkflowStage.PACKAGE,
        ]

    def get_next_stage(self) -> Optional[WorkflowStage]:
        """获取工作流中的下一阶段。"""
        if self.current_stage is None:
            return self.get_stage_order()[0]

        stages = self.get_stage_order()
        try:
            idx = stages.index(self.current_stage)
            if idx + 1 < len(stages):
                return stages[idx + 1]
        except ValueError:
            pass

        return None

    def get_previous_stage(self) -> Optional[WorkflowStage]:
        """获取工作流中的上一阶段。"""
        if self.current_stage is None:
            return None

        stages = self.get_stage_order()
        try:
            idx = stages.index(self.current_stage)
            if idx > 0:
                return stages[idx - 1]
        except ValueError:
            pass

        return None

    def get_remaining_stages(self) -> List[WorkflowStage]:
        """获取尚未完成的阶段列表。"""
        all_stages = self.get_stage_order()
        return [s for s in all_stages if s not in self.completed_stages]

    def can_proceed_to_stage(self, stage: WorkflowStage) -> bool:
        """
        检查阶段是否可以开始。

        阶段只有在所有前置阶段都完成后才能开始。
        """
        stages = self.get_stage_order()
        stage_index = stages.index(stage)

        for i in range(stage_index):
            if stages[i] not in self.completed_stages:
                return False

        return True

    def get_stage_dependencies(self, stage: WorkflowStage) -> List[WorkflowStage]:
        """获取在此阶段之前必须完成的阶段列表。"""
        stages = self.get_stage_order()
        stage_index = stages.index(stage)
        return stages[:stage_index]

    def execute_before_stage_hooks(
        self, stage: WorkflowStage, context: Dict[str, Any]
    ) -> None:
        """执行给定阶段的所有前置钩子。"""
        # Global hooks
        for hook in self.before_any_stage:
            hook(stage.value, context)

        # Stage-specific hooks
        if stage in self.before_stage_hooks:
            for hook in self.before_stage_hooks[stage]:
                hook(context)

    def execute_after_stage_hooks(
        self, stage: WorkflowStage, result: StageResult, context: Dict[str, Any]
    ) -> None:
        """执行给定阶段的所有后置钩子。"""
        # Stage-specific hooks
        if stage in self.after_stage_hooks:
            for hook in self.after_stage_hooks[stage]:
                hook(result, context)

        # Global hooks
        for hook in self.after_any_stage:
            hook(stage.value, result.__dict__, context)

    def complete_stage(self, stage: WorkflowStage, result: StageResult) -> None:
        """将阶段标记为完成并记录结果。"""
        self.stage_results[stage] = result
        if stage not in self.completed_stages:
            self.completed_stages.append(stage)
        self.current_stage = stage

    def is_complete(self) -> bool:
        """检查所有阶段是否都已完成。"""
        return len(self.completed_stages) == len(self.get_stage_order())

    def reset(self) -> None:
        """将工作流重置为初始状态。"""
        self.current_stage = None
        self.completed_stages = []
        self.stage_results = {}

    def get_summary(self) -> Dict[str, Any]:
        """获取工作流状态的摘要。"""
        all_stages = self.get_stage_order()
        completed_count = len(self.completed_stages)

        return {
            "total_stages": len(all_stages),
            "completed_stages": completed_count,
            "progress_percentage": (completed_count / len(all_stages)) * 100,
            "current_stage": self.current_stage.value if self.current_stage else None,
            "completed_stage_names": [s.value for s in self.completed_stages],
            "remaining_stages": [s.value for s in self.get_remaining_stages()],
        }

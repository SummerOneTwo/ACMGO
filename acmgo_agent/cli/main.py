#!/usr/bin/env python3
"""
ACMGO 出题 AI Agent 的 CLI 入口点。

Usage:
    python -m acmgo_agent.cli.main "dynamic programming problem"
    python -m acmgo_agent.cli.main --provider anthropic "graph theory problem"
"""
import argparse
import sys
import os
import io

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

from ..providers.factory import create_provider
from ..core.agent import ProblemSetterAgent
from ..config.settings import get_settings, print_settings


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="ACMGO Problem Setter AI Agent - AI 辅助的竞赛编程出题工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 使用 Anthropic Claude 创建新题目
  python -m acmgo_agent.cli.main "动态规划问题"

  # 使用 OpenAI
  python -m acmgo_agent.cli.main --provider openai "图论问题"

  # 指定自定义工作目录
  python -m acmgo_agent.cli.main --work-dir ./problems/my_problem "DP 问题"

  # 列出可用的提供商
  python -m acmgo_agent.cli.main --list-providers

环境变量:
  ANTHROPIC_API_KEY   Anthropic API 密钥（用于 --provider anthropic 或 litellm 的 anthropic/ 模型）
  OPENAI_API_KEY       OpenAI API 密钥（用于 --provider openai 或 litellm 的 openai/ 模型）
  LITELLM_API_KEY     通用 API 密钥（用于 litellm）
  ACMGO_PROVIDER       LLM 提供商（默认：litellm）
  ACMGO_MODEL         模型名称（默认：anthropic/claude-opus-4-6）
  ACMGO_WORK_DIR      工作目录（默认：./problems/new_problem）
  ACMGO_MAX_RETRIES   自愈最大重试次数（默认：3）
  ACMGO_AUTO_PROGRESS  自动进入下一阶段（默认：false）
  ACMGO_VERBOSE       详细输出（默认：true）

LiteLLM 模型:
  使用 --provider litellm 时，可使用如下模型名：
    - anthropic/claude-opus-4-6
    - openai/gpt-4o
    - google/gemini-pro
    - cohere/command-r
  详见 https://docs.litellm.ai/ 查看所有支持的模型
        """,
    )

    # Positional arguments
    parser.add_argument(
        "description",
        nargs="?",
        help="题目核心算法描述（如 '动态规划问题'）",
    )

    # Provider options
    parser.add_argument(
        "--provider",
        choices=["anthropic", "openai", "litellm"],
        default=None,
        help="LLM 提供商（默认：从 ACMGO_PROVIDER 环境变量或 'litellm'）",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="LLM 模型名称（默认：从 ACMGO_MODEL 环境变量）",
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help="API 密钥（默认：从 ANTHROPIC_API_KEY 或 OPENAI_API_KEY 环境变量读取）",
    )

    # Agent options
    parser.add_argument(
        "--work-dir",
        default=None,
        help="工作目录（默认：./problems/new_problem）",
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=None,
        help="最大重试次数（默认：3）",
    )
    parser.add_argument(
        "--auto-progress",
        action="store_true",
        help="自动进入下一步（默认：false）",
    )
    parser.add_argument(
        "--no-verbose",
        action="store_true",
        help="禁用详细输出",
    )

    # Utility options
    parser.add_argument(
        "--list-providers",
        action="store_true",
        help="列出可用的 LLM 提供商",
    )
    parser.add_argument(
        "--show-config",
        action="store_true",
        help="显示当前配置",
    )

    args = parser.parse_args()

    # Handle utility commands
    if args.list_providers:
        print("可用的 LLM 提供商：")
        print("  - anthropic: Anthropic Claude（需要 ANTHROPIC_API_KEY）")
        print("  - openai: OpenAI GPT（需要 OPENAI_API_KEY）")
        print("  - litellm: 统一接口支持 100+ 提供商（支持多种 API Key）")
        print("")
        print("LiteLLM 模型示例：")
        print("  - anthropic/claude-opus-4-6")
        print("  - openai/gpt-4o")
        print("  - google/gemini-pro")
        print("  - cohere/command-r")
        print("")
        print("API Key 优先级（litellm）：")
        print("  1. 提供商特定的密钥（如 ANTHROPIC_API_KEY）")
        print("  2. LITELLM_API_KEY")
        return 0

    # Get settings
    try:
        settings = get_settings(
            provider=args.provider,
            api_key=args.api_key,
            model=args.model,
            work_dir=args.work_dir,
            max_retries=args.max_retries,
            auto_progress=args.auto_progress,
            verbose=not args.no_verbose,
        )
    except ValueError as e:
        print(f"配置错误：{e}", file=sys.stderr)
        return 1

    # Show config if requested
    if args.show_config:
        print_settings(settings)
        return 0

    # Validate API key
    if not settings.validate_api_key():
        print(
            f"错误：未找到 {settings.provider} 的 API 密钥。",
            file=sys.stderr,
        )
        if settings.provider == "anthropic":
            print("请设置 ANTHROPIC_API_KEY 环境变量或使用 --api-key 参数。", file=sys.stderr)
        elif settings.provider == "openai":
            print("请设置 OPENAI_API_KEY 环境变量或使用 --api-key 参数。", file=sys.stderr)
        elif settings.provider == "litellm":
            print("请设置相应的 API 密钥：", file=sys.stderr)
            print("  - ANTHROPIC_API_KEY（用于 anthropic/ 模型）", file=sys.stderr)
            print("  - OPENAI_API_KEY（用于 openai/ 模型）", file=sys.stderr)
            print("  - LITELLM_API_KEY（通用）", file=sys.stderr)
            print("或使用 --api-key 参数。", file=sys.stderr)
        return 1

    # Check for problem description
    if not args.description:
        print("错误：请提供题目核心算法描述。", file=sys.stderr)
        print("示例：python -m acmgo_agent.cli.main '动态规划问题'", file=sys.stderr)
        return 1

    # Create provider
    try:
        provider = create_provider(
            settings.provider,
            api_key=settings.api_key,
            model=settings.model,
        )
    except ValueError as e:
        print(f"错误：{e}", file=sys.stderr)
        return 1

    # Create and run agent
    try:
        print(f"ACMGO Problem Setter AI Agent")
        print(f"工作目录：{settings.work_dir}")
        print(f"使用提供商：{settings.provider} ({settings.model})")
        print("=" * 60)

        agent = ProblemSetterAgent(
            provider=provider,
            work_dir=settings.work_dir,
            max_retries=settings.max_retries,
            auto_progress=settings.auto_progress,
            verbose=settings.verbose,
        )

        result = agent.run(args.description)

        # Print results
        print("=" * 60)
        if result["status"] == "success":
            print(f"出题完成！文件保存在：{result['work_dir']}")
            return 0
        else:
            print(f"出题失败：{result.get('error', '未知错误')}")
            if "stage" in result:
                print(f"失败阶段：{result['stage']}")
            return 1

    except KeyboardInterrupt:
        print("\n用户中断。", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"\n错误：{e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

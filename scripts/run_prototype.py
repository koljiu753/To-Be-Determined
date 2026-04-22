"""
TBD Phase 0 原型批量测试脚本

用法:
    1. pip install -r requirements.txt
    2. cp .env.example .env 并填入你的 API Key
    3. python run_prototype.py [--model MODEL_NAME] [--limit N]

支持的模型 (通过 --model 指定):
    - claude-sonnet-4-6 (默认，推荐)
    - claude-opus-4-7
    - gpt-4o
    - glm-4
    - deepseek-chat

示例:
    python run_prototype.py                          # 用 Claude Sonnet 4.6 跑全部 20 个用例
    python run_prototype.py --model glm-4 --limit 5  # 用 GLM-4 跑前 5 个用例
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# ============================================================
# 配置区
# ============================================================

REPO_ROOT = Path(__file__).parent.parent
CASES_PATH = REPO_ROOT / "test_cases" / "cases.json"
PROMPT_PATH = REPO_ROOT / "prompts" / "05_full_pipeline.md"
OUTPUT_DIR = REPO_ROOT / "scripts" / "results"

MODEL_REGISTRY = {
    "claude-sonnet-4-6": {
        "provider": "anthropic",
        "model_id": "claude-sonnet-4-6",
        "env_key": "ANTHROPIC_API_KEY",
    },
    "claude-opus-4-7": {
        "provider": "anthropic",
        "model_id": "claude-opus-4-7",
        "env_key": "ANTHROPIC_API_KEY",
    },
    "gpt-4o": {
        "provider": "openai",
        "model_id": "gpt-4o",
        "env_key": "OPENAI_API_KEY",
    },
    "glm-4": {
        "provider": "zhipu",
        "model_id": "glm-4",
        "env_key": "ZHIPU_API_KEY",
    },
    "deepseek-chat": {
        "provider": "deepseek",
        "model_id": "deepseek-chat",
        "env_key": "DEEPSEEK_API_KEY",
    },
}


# ============================================================
# Prompt 加载
# ============================================================

def load_system_prompt() -> str:
    """从 05_full_pipeline.md 提取可用的 Prompt"""
    if not PROMPT_PATH.exists():
        raise FileNotFoundError(f"找不到 Prompt 文件: {PROMPT_PATH}")

    content = PROMPT_PATH.read_text(encoding="utf-8")

    # 提取三个反引号包裹的代码块中最大的那个（就是完整 Prompt）
    import re
    blocks = re.findall(r"```\n(.*?)\n```", content, re.DOTALL)
    if not blocks:
        raise ValueError("Prompt 文件中找不到代码块")

    # 取最长的代码块
    return max(blocks, key=len).strip()


def load_cases(limit: int = None) -> list:
    """加载测试用例"""
    if not CASES_PATH.exists():
        raise FileNotFoundError(f"找不到用例文件: {CASES_PATH}")

    data = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    cases = data["cases"]
    if limit:
        cases = cases[:limit]
    return cases


# ============================================================
# 模型调用抽象层
# ============================================================

class ModelClient:
    """统一的模型调用接口，支持多个供应商"""

    def __init__(self, model_name: str):
        if model_name not in MODEL_REGISTRY:
            raise ValueError(f"未知模型: {model_name}。可选: {list(MODEL_REGISTRY.keys())}")

        config = MODEL_REGISTRY[model_name]
        self.provider = config["provider"]
        self.model_id = config["model_id"]
        self.api_key = os.getenv(config["env_key"])

        if not self.api_key:
            raise ValueError(f"环境变量 {config['env_key']} 未设置，请检查 .env 文件")

        self._init_client()

    def _init_client(self):
        """按 provider 初始化 SDK"""
        if self.provider == "anthropic":
            from anthropic import Anthropic
            self.client = Anthropic(api_key=self.api_key)
        elif self.provider == "openai":
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
        elif self.provider == "zhipu":
            from zhipuai import ZhipuAI
            self.client = ZhipuAI(api_key=self.api_key)
        elif self.provider == "deepseek":
            from openai import OpenAI  # DeepSeek 兼容 OpenAI SDK
            self.client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.deepseek.com/v1"
            )

    def chat(self, system_prompt: str, messages: list) -> str:
        """
        统一的聊天接口
        messages 格式: [{"role": "user"/"assistant", "content": "..."}]
        """
        if self.provider == "anthropic":
            resp = self.client.messages.create(
                model=self.model_id,
                max_tokens=4096,
                system=system_prompt,
                messages=messages,
            )
            return resp.content[0].text

        elif self.provider in ("openai", "deepseek"):
            full_messages = [{"role": "system", "content": system_prompt}] + messages
            resp = self.client.chat.completions.create(
                model=self.model_id,
                messages=full_messages,
                max_tokens=4096,
            )
            return resp.choices[0].message.content

        elif self.provider == "zhipu":
            full_messages = [{"role": "system", "content": system_prompt}] + messages
            resp = self.client.chat.completions.create(
                model=self.model_id,
                messages=full_messages,
                max_tokens=4096,
            )
            return resp.choices[0].message.content


# ============================================================
# 测试流程
# ============================================================

def simulate_user_response(case: dict) -> str:
    """
    为澄清阶段模拟用户回答。
    简化版本：直接基于 expected_signals 生成一个合理的补充回答。
    """
    signals = case.get("expected_signals", [])
    return (
        f"（以下为模拟的用户补充回答）\n"
        f"基于你问的问题，我再补充一些信息：\n"
        f"- {signals[0] if signals else '情况就是我描述的那样'}\n"
        f"- 我希望你直接帮我推演所有可能的路径，可以开始 Step 2 了。"
    )


def run_single_case(client: ModelClient, system_prompt: str, case: dict) -> dict:
    """
    跑单个测试用例，返回完整对话记录。
    """
    print(f"\n{'='*60}")
    print(f"▶ 运行 {case['id']} - {case['category']} (难度: {case['difficulty']})")
    print(f"{'='*60}")
    print(f"用户输入: {case['input'][:80]}...")

    result = {
        "case_id": case["id"],
        "category": case["category"],
        "difficulty": case["difficulty"],
        "input": case["input"],
        "timestamp": datetime.now().isoformat(),
        "rounds": [],
    }

    # Round 1: 用户首次输入 → AI 澄清
    messages = [{"role": "user", "content": case["input"]}]
    try:
        clarify_response = client.chat(system_prompt, messages)
        result["rounds"].append({
            "user": case["input"],
            "assistant": clarify_response,
        })
        print(f"\n[Round 1 - AI 澄清]\n{clarify_response[:300]}...")
    except Exception as e:
        print(f"❌ Round 1 出错: {e}")
        result["error"] = str(e)
        return result

    # CASE_020 特殊处理：如果是敏感用例，只跑 1 轮看 AI 是否识别危机
    if case["id"] == "CASE_020":
        result["note"] = "敏感用例，只跑一轮验证危机识别能力"
        return result

    # Round 2: 模拟用户回答 → AI 推演
    user_response = simulate_user_response(case)
    messages.append({"role": "assistant", "content": clarify_response})
    messages.append({"role": "user", "content": user_response})
    try:
        simulate_response = client.chat(system_prompt, messages)
        result["rounds"].append({
            "user": user_response,
            "assistant": simulate_response,
        })
        print(f"\n[Round 2 - AI 推演]\n{simulate_response[:300]}...")
    except Exception as e:
        print(f"❌ Round 2 出错: {e}")
        result["error"] = str(e)

    return result


def main():
    parser = argparse.ArgumentParser(description="TBD Phase 0 批量测试")
    parser.add_argument(
        "--model",
        default="claude-sonnet-4-6",
        choices=list(MODEL_REGISTRY.keys()),
        help="使用的模型",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="只跑前 N 个用例（调试用）",
    )
    parser.add_argument(
        "--case-id",
        default=None,
        help="只跑特定用例 ID（如 CASE_001）",
    )
    args = parser.parse_args()

    # 准备
    OUTPUT_DIR.mkdir(exist_ok=True)
    print(f"📦 加载 Prompt...")
    system_prompt = load_system_prompt()
    print(f"📦 加载用例...")
    cases = load_cases(limit=args.limit)

    if args.case_id:
        cases = [c for c in cases if c["id"] == args.case_id]
        if not cases:
            print(f"❌ 找不到用例 {args.case_id}")
            sys.exit(1)

    print(f"🤖 初始化模型 {args.model}...")
    client = ModelClient(args.model)

    # 跑
    results = []
    for i, case in enumerate(cases, 1):
        print(f"\n进度: {i}/{len(cases)}")
        result = run_single_case(client, system_prompt, case)
        results.append(result)

    # 保存
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = OUTPUT_DIR / f"results_{args.model}_{timestamp}.json"
    output_file.write_text(
        json.dumps(
            {
                "model": args.model,
                "total_cases": len(results),
                "timestamp": timestamp,
                "results": results,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(f"\n{'='*60}")
    print(f"✅ 完成！结果已保存到:")
    print(f"   {output_file}")
    print(f"\n📊 下一步: 打开结果 JSON 对照 test_cases/evaluation_rubric.md 打分")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()

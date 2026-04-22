# To Be Determined (TBD)

> 一款以大模型为基座的人生决策推演游戏。
> 帮你把模糊的困境，变成看得见的选择地图。

## 📌 当前阶段：Phase 0 - 原型验证

在写一行产品代码之前，我们先验证核心假设：**大模型能否在真实困境上产出高质量的决策推演？**

Phase 0 只做一件事：用 Prompt 在任意大模型上测试 20+ 真实场景，评估可行性。

## 🗂️ 仓库结构

```
.
├── README.md                    # 你正在看的文件
├── docs/
│   └── PROJECT_SPEC.md          # 完整项目文档（产品/技术/商业化）
├── prompts/
│   ├── 00_system_persona.md     # L1 全局人格设定
│   ├── 01_triage_agent.md       # 分流 Agent
│   ├── 02_clarify_agent.md      # 澄清 Agent
│   ├── 03_simulator_agent.md    # 推演 Agent（核心）
│   ├── 04_critic_agent.md       # 自检 Agent
│   └── 05_full_pipeline.md      # 完整流水线拼接示例
├── test_cases/
│   ├── README.md                # 测试方法说明
│   ├── cases.json               # 20个真实困境测试用例
│   └── evaluation_rubric.md     # 评分标准
└── scripts/
    ├── requirements.txt         # Python 依赖
    ├── run_prototype.py         # 一键跑所有测试用例
    └── .env.example             # 环境变量模板
```

## 🚀 快速开始

### 方式 1：手动测试（零代码，推荐先用这个）

1. 打开 `prompts/05_full_pipeline.md`
2. 复制其中的完整 Prompt
3. 粘贴到 Claude / ChatGPT / GLM / DeepSeek 任意对话窗
4. 输入 `test_cases/cases.json` 中的一个困境描述
5. 对照 `test_cases/evaluation_rubric.md` 评分

### 方式 2：批量脚本测试

```bash
cd scripts
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env，填入你的 API Key（支持 Anthropic / OpenAI / 智谱 任一）
python run_prototype.py
```

## ✅ Phase 0 通过标准

- 20 个测试用例平均评分 ≥ 3.5 / 5
- 至少在 3 个场景类别（职场/情感/人生大事）上表现稳定
- 推演"有用度"评分高于"娱乐度"评分

达不到标准 → 迭代 Prompt 或重新评估产品方向。
达到标准 → 进入 Phase 1 正式开发。

## 📖 完整项目文档

见 [`docs/PROJECT_SPEC.md`](./docs/PROJECT_SPEC.md)

## 📜 License

MIT

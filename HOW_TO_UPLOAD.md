# 如何上传到 GitHub 仓库

> 由于 Claude 无法直接访问你的 GitHub 账号，需要你在本地执行以下步骤。
> 整个过程大约 2 分钟。

## 前置条件

- 本地已安装 Git（`git --version` 能正常输出）
- 已登录 GitHub，并创建好仓库 `koljiu753/To-Be-Determined`（空仓库，不要初始化 README）
- 已下载 `tbd-repo.zip` 到本地并解压

## 操作步骤

### Step 1: 进入项目目录

```bash
cd path/to/tbd-repo
```

### Step 2: 初始化 Git

```bash
git init
git branch -M main
```

### Step 3: 添加远程仓库

**HTTPS 方式**（推荐新手）：
```bash
git remote add origin https://github.com/koljiu753/To-Be-Determined.git
```

**SSH 方式**（已配置 SSH key）：
```bash
git remote add origin git@github.com:koljiu753/To-Be-Determined.git
```

### Step 4: 提交并推送

```bash
git add .
git commit -m "Phase 0: prompt prototypes + test cases + project spec"
git push -u origin main
```

如果这是空仓库首次推送，上面命令应该直接成功。
如果 GitHub 上仓库已有内容（比如自动创建了 README），先：
```bash
git pull origin main --rebase
# 然后再 push
git push -u origin main
```

### Step 5: 验证

打开 https://github.com/koljiu753/To-Be-Determined 检查以下目录结构是否都在：

```
├── README.md
├── LICENSE
├── .gitignore
├── docs/
│   └── PROJECT_SPEC.md
├── prompts/
│   ├── 00_system_persona.md
│   ├── 01_triage_agent.md
│   ├── 02_clarify_agent.md
│   ├── 03_simulator_agent.md
│   ├── 04_critic_agent.md
│   └── 05_full_pipeline.md
├── test_cases/
│   ├── README.md
│   ├── cases.json
│   └── evaluation_rubric.md
└── scripts/
    ├── requirements.txt
    ├── run_prototype.py
    └── .env.example
```

## 常见问题

### Q: `Permission denied (publickey)` 错误
用 HTTPS 方式而不是 SSH，或配置 SSH key。

### Q: 推送时要求用户名密码
现在 GitHub 不支持密码登录，需要使用 Personal Access Token：
1. 到 https://github.com/settings/tokens 创建 classic token
2. 勾选 `repo` 权限
3. 推送时用户名填 `koljiu753`，密码填生成的 token

### Q: 仓库已经有 README，push 被拒绝
```bash
git pull origin main --allow-unrelated-histories
# 解决可能的冲突后
git push -u origin main
```

### Q: 想先在本地看看效果
```bash
# 在 tbd-repo 目录里
cat README.md
ls -la prompts/
```

## 后续开发提示

- `scripts/results/` 已在 `.gitignore` 中忽略，测试结果不会进仓库（隐私保护）
- `.env` 也被忽略，API Key 不会泄露
- 可以在仓库 Settings → Pages 开启 GitHub Pages，把 docs 渲染成网站

## 第一次跑 Phase 0 测试

仓库推上去之后，建议你：

1. **手动测试优先**：不需要 API Key，直接把 `prompts/05_full_pipeline.md` 的 Prompt 复制到 Claude 对话窗，跑 `test_cases/cases.json` 里的前 5 个用例感受一下
2. **按 rubric 打分**：用 `test_cases/evaluation_rubric.md` 评分，看平均分
3. **如果分数 ≥ 3.5**：启动 Phase 1 开发
4. **如果分数 < 3.5**：先改 Prompt 再跑，不着急写代码

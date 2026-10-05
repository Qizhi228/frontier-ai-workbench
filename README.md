# Frontier AI Workbench

前沿 AI 技术研究工作台，面向 AI 应用开发和 FDE 求职展示。

## 产品演示

```text
输入主题
  -> 发现来源
  -> 去重与提取
  -> 生成技术简报
  -> 保存 Markdown
  -> 在工作台查看任务、报告和来源
```

第一版刻意控制边界：

- 单用户，不做注册和计费
- 默认 Mock 模式，不需要 API Key
- 可选真实网页来源和 OpenAI 兼容模型
- 研究、抓取、写报告属于低风险动作
- 修改代码、删除文件、发送消息、部署服务默认需要审批
- SQLite + Markdown，适合个人工作台和求职 Demo

## 本地运行

### 后端

```bash
python3 -m venv .venv
.venv/bin/pip install -r backend/requirements.txt
PYTHONPATH=backend .venv/bin/uvicorn app.main:app --app-dir backend --reload --port 8000
```

### 前端

```bash
cd frontend
npm install
npm run dev
```

打开 `http://localhost:5173/workbench/` 或 Vite 输出的地址。

### 测试

```bash
PYTHONPATH=backend .venv/bin/python -m unittest discover -s backend/tests -p 'test_*.py' -v
```

## 接入真实来源和模型

```bash
export SOURCE_MODE=web
export MODEL_MODE=api
export OPENAI_BASE_URL=https://api.openai.com/v1
export OPENAI_API_KEY=your-key
export OPENAI_MODEL=your-model
```

API Key 只放在后端环境变量中，不要放进 Vue 前端或 GitHub。

## 目录

```text
backend/
  app/                 核心领域、服务、HTTP 适配器
  tests/               行为测试
frontend/              Vue3 + Vite 工作台
deploy/                腾讯云 Nginx、systemd 和部署文件
docs/                  产品规格和面试讲解
```

## 面试讲法

这个项目不是“把模型接到聊天框”，而是一个受控的研究工作流：模型负责总结，来源层负责提供证据，任务层负责状态，存储层负责记忆，策略层负责限制高风险动作。

## 免责声明

这是学习和求职展示用原型。Mock 来源不代表真实市场结论；接入真实来源后仍需人工核验。

# CLAUDE.md

本文件为 Claude Code (claude.ai/code) 在此仓库中工作时提供指引。

## 项目概述

ClawFeed 是一个 AI 驱动的新闻摘要工具，从 Twitter、RSS、HackerNews、Reddit、GitHub Trending 等信息源中策展内容，生成结构化摘要（4小时/日报/周报/月报）。支持微信小程序 + Web H5 双端。

**技术栈：**
- 后端：Python FastAPI + SQLAlchemy + Alembic
- 前端：uni-app (Vue 3) → 微信小程序 + H5
- 数据库：SQLite（开发）/ MySQL（生产）
- 认证：微信登录 + JWT（开发环境有 dev-login 免微信）
- 部署：Docker → 腾讯云 VPS

## 常用命令

### 后端

```bash
pip install -r requirements.txt           # 安装 Python 依赖
uvicorn app.main:app --reload --port 8000 # 开发模式（自动重载）
uvicorn app.main:app --port 8000          # 生产模式
```

启动后访问：
- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 前端 (uni-app)

```bash
cd clawfeed-app
npm install                    # 安装前端依赖
npm run dev:h5                 # H5 开发 → http://localhost:5173（自动代理 /api → 8000）
npm run build:h5               # H5 构建
npm run dev:mp-weixin          # 微信小程序开发
npm run build:mp-weixin        # 微信小程序构建 → dist/build/mp-weixin/
```

### 数据库迁移

```bash
# 开发阶段 — 表在 FastAPI 启动时自动创建（Base.metadata.create_all）
# 生产部署 — 使用 Alembic 管理迁移
alembic upgrade head           # 执行迁移
alembic revision --autogenerate -m "描述"  # 生成新迁移
```

## 架构

### 后端结构

```
app/
├── main.py              # FastAPI 入口，挂载路由，CORS，startup 创建表
├── config.py            # 读取 .env，Pydantic Settings
├── database.py          # SQLAlchemy engine + SessionLocal
├── models.py            # 9 个 ORM 模型（对应原 9 个 SQL 迁移）
├── schemas.py           # Pydantic 请求/响应模型
├── deps.py              # 依赖注入：get_db, get_current_user, require_user, verify_api_key
├── crud.py              # 所有 CRUD 操作（对应原 db.mjs 的 40+ 导出函数）
├── routers/
│   ├── auth.py          # 微信登录 + dev-login + JWT 签发
│   ├── digests.py       # 摘要 CRUD
│   ├── marks.py         # 书签 CRUD + 向后兼容端点
│   ├── sources.py       # 信息源 CRUD + URL 智能识别
│   ├── subscriptions.py # 订阅管理
│   ├── packs.py         # Source Pack CRUD + 安装
│   ├── feedback.py      # 用户反馈 + Lark webhook 通知
│   ├── feed.py          # JSON Feed / RSS 输出
│   └── config.py        # 配置 + Changelog + Roadmap
└── services/
    ├── wechat.py        # 微信 code2session API
    ├── source_resolver.py # URL 自动识别信息源类型
    └── feed_generator.py  # RSS/JSON Feed 生成器
```

### 前端结构

```
clawfeed-app/src/
├── pages/               # 8 个页面
│   ├── index/           # 首页：摘要列表（4h/daily/weekly/monthly 标签切换）
│   ├── digest/          # 摘要详情
│   ├── marks/           # 书签收藏
│   ├── sources/         # 信息源管理（CRUD + URL 智能识别）
│   ├── packs/           # Pack 市场 + 详情
│   ├── feedback/        # 反馈
│   └── profile/         # 个人中心（登录/登出）
├── components/          # 可复用组件：DigestCard, MarkCard, SourceCard, PackCard
├── composables/
│   ├── useApi.js        # uni.request 封装（含 JWT + 代理配置）
│   └── useAuth.js       # 微信登录 / dev-login / 登出
├── store/user.js        # Pinia 用户状态
├── utils/format.js      # 日期格式化、timeAgo、truncate
├── pages.json           # 路由 + TabBar 配置
└── manifest.json        # H5 代理 + 微信 appid 配置
```

### 数据库

SQLite 存储在 `data/clawfeed.db`（可通过 `DATABASE_URL` 切换 MySQL）。表在 FastAPI 启动时自动创建。Alembic 迁移文件在 `alembic/versions/`，初始迁移 `001_init.py` 合并了原 9 个 SQL 迁移。

核心表：`users`、`digests`、`marks`、`sources`、`sessions`、`user_subscriptions`、`source_packs`、`feedback`、`config`

### 认证模型

- 微信小程序：`wx.login()` → code → 后端调微信 `code2session` → 获取 openid → JWT
- H5 开发调试：`POST /api/auth/dev-login` → 自动创建测试用户 → JWT
- 后续请求：`Authorization: Bearer <token>`
- 管理接口（创建摘要、管理反馈等）：`Authorization: Bearer <API_KEY>`

### 多租户模型

- 未登录用户看到公开 Digest（只读）
- 新用户注册时自动订阅所有公开 Sources
- Source 按用户创建，可设为公开或私有
- Source Pack 将多个 Source 打包分享；安装 Pack 自动订阅
- Source 删除为软删除（`is_deleted` 标记）

## 代码规范

- **Python 3.11+** — 使用类型提示，f-string
- **FastAPI 装饰器路由** — 每个资源一个 router 文件
- **SQLAlchemy 2.0 风格** — 使用 `Session.query()` 查询
- **Pydantic v2** — 请求/响应校验，`model_config = {"from_attributes": True}`
- **依赖注入** — `get_db`、`get_current_user`、`require_user`、`verify_api_key`
- **DB 迁移** — 开发用 `create_all`，生产用 Alembic
- **环境变量** — 通过 `config.py` 手动读取 `.env`（和原 Node.js 版保持一致）
- **前端** — Vue 3 Composition API + `<script setup>` 语法，uni-app 跨端 API

## 模板

- `templates/curation-rules.md` — AI 策展的内容筛选规则
- `templates/digest-prompt.md` — 摘要生成的 AI 提示词模板

## 部署

```bash
# Docker 构建
docker build -t clawfeed .
docker run -p 8000:8000 -v $(pwd)/data:/app/data clawfeed

# 腾讯云 VPS
# Nginx 反向代理 → uvicorn:8000
# HTTPS: Let's Encrypt 免费证书
# 微信小程序要求：域名 ICP 备案 + HTTPS
```

## 分支策略

- `main` 受保护——所有变更通过 PR
- 从 `main` 创建功能分支：`feature/xxx`
- CI 运行：Python 语法检查 + 启动测试 + pip-audit

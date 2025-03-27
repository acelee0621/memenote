# Memenote 项目 📝✨

欢迎体验 **Memenote**！这是一个基于 FastAPI 的笔记工具，专为记录和管理你的灵感与任务而设计。使用 `uv` 管理依赖，支持用户注册、笔记创建、待办事项 (Todo)、提醒 (Reminder)，还有 Celery 驱动的实时提醒功能，通过 SSE（服务器推送事件）送到你的客户端！📩 项目使用Alembic配置数据库迁移并且已 Docker 化，支持开发模式和 Traefik 引入 HTTPS 的生产配置。快来试试吧！🚀

---

## 项目简介 🌟

Memenote 是一个轻量但功能强大的笔记管理工具，旨在帮助你：
- 📋 创建和管理个人笔记 (Note)
- ✅ 在笔记下添加待办事项 (Todo) 或独立创建 Todo
- ⏰ 设置提醒 (Reminder)，支持关联笔记或独立存在
- 🔒 用户注册与认证，确保数据安全
- 📡 通过 Celery 和 SSE 实现实时提醒推送
- 🐳 Docker 部署，支持开发与生产环境

无论你是想记录灵感、规划任务，还是设置定时提醒，Memenote 都能助你一臂之力！💪

---

## 快速开始 🚀

Memenote 使用 `uv` 管理依赖和运行环境。如果你没用过 `uv`，别担心！下面是详细步骤，手把手带你跑起来~ 😎

### 1. 前置条件 ⚙️
- **Python 版本**: 3.8+  
- **安装 uv**:  
  在终端运行：
  ```bash
  pip install uv
  ```
  或参考 [uv 官方文档](https://github.com/astral-sh/uv)。

### 2. 克隆项目 📥
获取代码到本地：
```bash
git clone https://github.com/acelee0621/memenote.git
cd memenote
```

### 3. 使用 uv 安装依赖 📦
依赖都定义在 `pyproject.toml` 中，使用 `uv` 快速安装：
```bash
uv sync
```

### 4. 配置环境变量 🌍
复制 `.env.example` 到 `.env`，并根据需要修改：
```bash
cp .env.example .env
```
- `JWT_SECRET`: 用于用户认证的密钥
- `SQLITE_DB_PATH`: 数据库路径（默认 `data/memenote.sqlite3`）
- `BROKER_HOST` 和 `REDIS_HOST`: Celery 的消息队列和结果存储地址

### 5. 运行数据库迁移 🗄️
初始化数据库表结构：
```bash
uv run alembic upgrade head
```

### 6. 启动 FastAPI 服务 ▶️
运行主程序：
```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```
访问 `http://localhost:8000/docs` 查看 API 文档！📖

### 7. 启动 Celery Worker 🕒
提醒功能依赖 Celery，另开一个终端运行：
```bash
uv run celery -A app.core.celery_app worker --loglevel=info --pool=threads -Q celery,reminder_queue --autoscale=4,2
```

---

## Docker 部署 🐳

想用 Docker 跑起来？我们提供了两种配置：

### 开发模式 🛠️
```bash
docker compose -f compose.dev.yaml up -d
```
- 包含 FastAPI、Celery Worker 和 Redis，适合本地开发。

### 生产模式 + HTTPS 🔐
使用 Traefik 引入 HTTPS：
```bash
docker compose -f compose.traefik.yaml up -d
```
- 需要在 `traefik/certs/` 下准备 `cert.pem` 和 `key.pem`。
- 默认监听 `443` 端口，确保证书配置正确。

---

## 项目结构 🗂️
快速了解代码布局：
```
memenote/
├── app/                # 主应用目录
│   ├── core/           # 核心配置（数据库、Celery、认证等）
│   ├── models/         # 数据模型（User、Note、Todo、Reminder）
│   ├── repository/     # 数据操作层
│   ├── routes/         # API 路由（认证、笔记、提醒等）
│   ├── schemas/        # 数据校验 schema
│   ├── service/        # 业务逻辑层
│   ├── tasks/          # Celery 任务
│   └── main.py         # FastAPI 入口
├── alembic/            # 数据库迁移
├── tests/              # 测试用例
├── traefik/            # Traefik 配置（生产环境）
├── Dockerfile          # Docker 镜像定义
├── pyproject.toml      # uv 依赖管理文件
└── README.md           # 你正在看的文档！😊
```

---

## 功能亮点 🌈
- **用户管理** 👤: 注册、登录，JWT 认证保护你的数据。
- **笔记系统** 📝: 创建、编辑、删除笔记，每个笔记可关联 Todo 和 Reminder。
- **待办事项** ✅: 支持独立或归属笔记的 Todo，标记完成状态。
- **提醒功能** ⏰: 设置提醒时间，Celery 定时任务通过 SSE 实时推送。
- **实时通知** 📡: 使用 Server-Sent Events (SSE) 接收提醒。
- **Docker 支持** 🐳: 一键部署，开发和生产环境全搞定！

---

## 注意事项 ⚠️
- **数据库**: 默认使用 SQLite，生产环境建议换成 PostgreSQL。
- **Celery**: 确保 Redis 和 RabbitMQ（或替代 broker）运行正常。
- **HTTPS**: 生产环境需配置 Traefik 和证书。
- **问题反馈**: 遇到问题？提个 issue 吧，我会尽快回复！✨

---

## 贡献代码 🤝
喜欢 Memenote 想加点料？欢迎参与：
1. Fork 项目
2. 创建分支 (`git checkout -b feature/cool-idea`)
3. 提交代码 (`git commit -m "✨ 添加超赞功能"`)
4. Push 到仓库 (`git push origin feature/cool-idea`)
5. 创建 Pull Request

---

## 联系我 📬
有问题或建议？欢迎在 GitHub 上提 issue。  
让我们一起让 Memenote 更强大！🌟

---

## 致谢 🙏
感谢 FastAPI、Celery、uv 和所有开源社区的支持！也谢谢你使用 Memenote！💖

---

## Acknowledgments

- Inspired by [Memos](https://github.com/usememos/memos).
# -------------- 构建阶段 --------------
FROM python:3.13.2-slim AS builder

WORKDIR /app

# 安装 uv 到全局
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# 复制项目依赖文件
COPY pyproject.toml uv.lock ./

# 创建虚拟环境并安装依赖
RUN uv sync --frozen --no-cache

# 复制项目代码
COPY . .

# -------------- 运行阶段 --------------
FROM python:3.13.2-slim

# 安装系统依赖 curl
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app    

# 创建非特权用户 appuser
RUN useradd --create-home appuser

# 复制应用代码
COPY --from=builder --chown=appuser:appuser /app /app
USER appuser 

# 设置环境变量，使用 `.venv`
ENV PATH="/app/.venv/bin:$PATH"
ENV SQLITE_DB_PATH="/app/data/memenote.sqlite3"

# 创建数据库文件夹并保证权限属于 appuser
RUN mkdir -p /app/data && chown appuser:appuser /app/data

# 确保数据库目录存在（生产环境使用）
# RUN mkdir -p /var/lib/app/data

# 在容器内运行应用时，设置数据库路径到 /var/lib/app/data/ （生产环境使用）
# ENV SQLITE_DB_PATH="/var/lib/app/data/todos.sqlite3"

# Health Check
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD [ "curl", "-f", "http://localhost:8000/health" ]    

# 运行 FastAPI 应用
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]   
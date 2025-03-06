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
    
    WORKDIR /app    
    
    # 复制应用代码
    COPY --from=builder /app /app 
    
    # 设置环境变量，使用 `.venv`
    ENV PATH="/app/.venv/bin:$PATH"    
        
    # 确保数据库目录存在（生产环境使用）
    # RUN mkdir -p /var/lib/app/data

    # 在容器内运行应用时，设置数据库路径到 /var/lib/app/data/ （生产环境使用）
    # ENV SQLITE_DB_PATH="/var/lib/app/data/todos.sqlite3"        
    
    # 运行 FastAPI 应用
    CMD ["fastapi", "run", "--host", "0.0.0.0", "--port", "8000"]    
    
    
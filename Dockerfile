# 使用官方 Python 3.12 镜像作为基础镜像
FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 安装 UV 包管理器（支持通过 build-arg 切换镜像源）
ARG UV_IMAGE=ghcr.io/astral-sh/uv:0.9.8
COPY --from=$UV_IMAGE /uv /usr/local/bin/uv

# 先复制依赖文件并安装（利用 Docker 缓存层）
COPY pyproject.toml uv.lock ./
# 使用 cache mount 缓存 UV 下载的包，即使在不同构建节点也能复用
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# 再复制应用代码（代码变化不会导致依赖重装）
COPY main.py ./

# 暴露端口
EXPOSE 8000

# 设置入口点（使用虚拟环境中的 Python）
CMD [".venv/bin/python", "main.py"]

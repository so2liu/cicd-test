# 使用官方 Python 3.12 镜像作为基础镜像
FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 安装 UV 包管理器
COPY --from=bladeai-cn-beijing.cr.volces.com/base/uv:0.9.8 /uv /usr/local/bin/uv

# 先复制依赖文件并安装（利用 Docker 缓存层）
COPY pyproject.toml ./
COPY uv.lock* ./
RUN uv sync --frozen --no-dev

# 再复制应用代码（代码变化不会导致依赖重装）
COPY main.py ./

# 暴露端口
EXPOSE 8000

# 设置入口点（使用虚拟环境中的 Python）
CMD [".venv/bin/python", "main.py"]

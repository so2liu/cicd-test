# 使用官方 Python 3.12 镜像作为基础镜像
FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 安装 UV 包管理器
COPY --from=bladeai-cn-beijing.cr.volces.com/base/uv:0.9.8 /uv /usr/local/bin/uv

# 复制项目文件
COPY pyproject.toml ./
COPY main.py ./

# 安装项目依赖
RUN uv pip install --system -e .

# 设置入口点
CMD ["python", "main.py"]

# 基础镜像：使用轻量级的Python 3.10（alpine版本体积小）
FROM python:3.10-alpine

# 设置工作目录（容器内的目录，类似本地的文件夹）
WORKDIR /app

# 复制后端依赖文件到容器内（先复制requirements.txt，避免每次改代码都重新装依赖）
COPY requirements.txt ./

# 安装依赖（--no-cache-dir 避免缓存，减小镜像体积）
RUN pip install --no-cache-dir -r requirements.txt

# 复制所有后端代码到容器内（除了.dockerignore排除的文件）
COPY . .

# 暴露容器的5000端口（和app.py中启动的端口一致）
EXPOSE 5000

# 容器启动时执行的命令（启动后端服务）
CMD ["python", "app.py"]
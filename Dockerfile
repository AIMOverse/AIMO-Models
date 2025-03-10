# 使用官方 Python 3.11 slim 版本作为基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装 `git` 以支持 `git clone`
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# 先复制 requirements.txt 以利用 Docker 缓存
COPY requirements.txt .

# 安装依赖
RUN pip install --upgrade pip && pip install -r requirements.txt

# 设置环境变量（NEBULA_API_KEY 用于应用运行时）
ENV NEBULA_API_KEY=${NEBULA_API_KEY}

# 克隆 Hugging Face 模型（避免暴露 HF_ACCESS_TOKEN）
ARG HF_ACCESS_TOKEN
RUN git clone https://Wes1eyyy:${HF_ACCESS_TOKEN}@huggingface.co/Wes1eyyy/AIMO-EmotionModule app/ai/static/models/EmotionModule

# 复制应用代码到容器中
COPY . .

# 暴露端口
EXPOSE 8000

# 运行命令
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-w", "4", "-b", "0.0.0.0:8000", "app.main:app"]

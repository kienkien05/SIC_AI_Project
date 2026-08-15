FROM python:3.11-slim
RUN useradd -m -u 1000 user && mkdir -p /data /models && chmod 777 /data /models
WORKDIR /home/user/app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PORT=7860 HOME=/home/user
RUN apt-get update && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu torch==2.2.2 torchvision==0.17.2 \
    && pip install --no-cache-dir -r requirements.txt
COPY --chown=user:user server.py seed.json ./
USER user
CMD ["sh", "-c", "uvicorn server:app --host 0.0.0.0 --port ${PORT}"]

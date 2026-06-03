# 部署指南

本文档说明如何将鸟趣后端部署到服务器，供前端调用。

## 目录

1. [环境要求](#环境要求)
2. [部署方式一：直接部署（推荐）](#部署方式一直接部署推荐)
3. [部署方式二：Docker 部署](#部署方式二docker-部署)
4. [部署方式三：使用进程管理器](#部署方式三使用进程管理器)
5. [Nginx 反向代理配置](#nginx-反向代理配置)
6. [生产环境配置清单](#生产环境配置清单)
7. [常见问题](#常见问题)

---

## 环境要求

| 组件 | 版本要求 | 说明 |
|------|----------|------|
| Python | 3.10+ | 推荐 3.11/3.12 |
| MySQL | 8.0+ | 生产环境必需 |
| 内存 | ≥ 512MB | 推荐 1GB+ |
| 磁盘 | ≥ 1GB | 取决于图片存储量 |

---

## 部署方式一：直接部署（推荐）

### 1. 安装系统依赖

```bash
# Ubuntu/Debian
apt update
apt install -y python3 python3-pip python3-venv mysql-server

# CentOS/RHEL
yum install -y python3 python3-pip mysql-server
```

### 2. 上传项目

```bash
# 使用 scp 上传
scp -r bird-backend/ user@your-server:/opt/

# 或使用 git
git clone <your-repo-url>
cd bird-backend
```

### 3. 配置 Python 虚拟环境

```bash
cd /opt/bird-backend

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/Mac
# 或 .\venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 可选：安装生产环境额外依赖
pip install gunicorn aiomysql
```

### 4. 配置 MySQL

```bash
# 登录 MySQL
mysql -u root -p

# 创建数据库和用户
CREATE DATABASE bird_watching CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'birdapp'@'localhost' IDENTIFIED BY 'your_strong_password';
GRANT ALL PRIVILEGES ON bird_watching.* TO 'birdapp'@'localhost';
FLUSH PRIVILEGES;
EXIT;

# 导入表结构和种子数据
mysql -u birdapp -p bird_watching < sql/schema.sql
mysql -u birdapp -p bird_watching < sql/seed.sql
```

### 5. 配置环境变量

编辑 `.env` 文件：

```env
# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_USER=birdapp
DB_PASSWORD=your_strong_password
DB_NAME=bird_watching

# JWT 密钥（务必修改为随机字符串！）
JWT_SECRET_KEY=$(openssl rand -hex 32)

# 服务器配置
HOST=0.0.0.0
PORT=8000

# 百度 AI 识别（可选）
# BAIDU_APP_ID=your_app_id
# BAIDU_API_KEY=your_api_key
# BAIDU_SECRET_KEY=your_secret_key
```

### 6. 启动服务

```bash
# 测试启动（验证配置是否正确）
uvicorn app.main:app --host 0.0.0.0 --port 8000

# 生产启动（推荐使用 gunicorn + uvicorn workers）
nohup gunicorn -w 4 -k uvicorn.workers.UvicornWorker \
  app.main:app \
  --bind 0.0.0.0:8000 \
  --timeout 120 \
  --max-requests 1000 \
  --max-requests-jitter 50 \
  --access-logfile logs/access.log \
  --error-logfile logs/error.log \
  > /dev/null 2>&1 &
```

### 7. 验证部署

```bash
# 健康检查
curl http://localhost:8000/api/health

# 预期响应：{"status": "ok", "message": "服务运行正常"}
```

---

## 部署方式二：Docker 部署

### 1. 创建 Dockerfile

项目根目录下已包含配置，可按需创建：

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir gunicorn

# 复制项目文件
COPY . .

# 创建必要目录
RUN mkdir -p uploads/images uploads/recognition logs

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", \
     "app.main:app", "--bind", "0.0.0.0:8000", \
     "--access-logfile", "logs/access.log", \
     "--error-logfile", "logs/error.log"]
```

### 2. 创建 docker-compose.yml

```yaml
version: "3.8"

services:
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: root_password
      MYSQL_DATABASE: bird_watching
      MYSQL_USER: birdapp
      MYSQL_PASSWORD: your_strong_password
    volumes:
      - mysql_data:/var/lib/mysql
      - ./sql/schema.sql:/docker-entrypoint-initdb.d/01-schema.sql
      - ./sql/seed.sql:/docker-entrypoint-initdb.d/02-seed.sql
    ports:
      - "3306:3306"
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build: .
    environment:
      DB_HOST: mysql
      DB_PORT: 3306
      DB_USER: birdapp
      DB_PASSWORD: your_strong_password
      DB_NAME: bird_watching
      JWT_SECRET_KEY: ${JWT_SECRET_KEY:-change-this-in-production}
    ports:
      - "8000:8000"
    volumes:
      - ./uploads:/app/uploads
      - ./logs:/app/logs
    depends_on:
      mysql:
        condition: service_healthy

volumes:
  mysql_data:
```

### 3. 启动

```bash
docker-compose up -d
docker-compose logs -f
```

---

## 部署方式三：使用进程管理器

### 使用 Supervisor

```ini
; /etc/supervisor/conf.d/bird-backend.conf

[program:bird-backend]
directory=/opt/bird-backend
command=/opt/bird-backend/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000
user=www-data
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stdout_logfile=/opt/bird-backend/logs/supervisor_stdout.log
stderr_logfile=/opt/bird-backend/logs/supervisor_stderr.log
environment=PATH="/opt/bird-backend/venv/bin"
```

```bash
supervisorctl reread
supervisorctl update
supervisorctl start bird-backend
```

### 使用 systemd

```ini
; /etc/systemd/system/bird-backend.service

[Unit]
Description=Bird Watching Backend API
After=network.target mysql.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/bird-backend
Environment=PATH=/opt/bird-backend/venv/bin
ExecStart=/opt/bird-backend/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000
Restart=always
RestartSec=5
StandardOutput=append:/opt/bird-backend/logs/stdout.log
StandardError=append:/opt/bird-backend/logs/stderr.log

[Install]
WantedBy=multi-user.target
```

```bash
systemctl daemon-reload
systemctl enable bird-backend
systemctl start bird-backend
systemctl status bird-backend
```

---

## Nginx 反向代理配置

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # API 请求转发到后端
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket 支持（如需）
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # 静态文件（上传的图片）
    location /uploads/ {
        alias /opt/bird-backend/uploads/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Swagger 文档
    location /docs {
        proxy_pass http://127.0.0.1:8000;
    }
    location /openapi.json {
        proxy_pass http://127.0.0.1:8000;
    }

    # 根路径
    location / {
        proxy_pass http://127.0.0.1:8000;
    }

    # 启用 HTTPS（推荐使用 certbot）
    # listen 443 ssl;
    # ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    # ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
}
```

---

## 生产环境配置清单

部署前逐项检查：

- [ ] **JWT 密钥**：已修改为随机字符串（`openssl rand -hex 32`）
- [ ] **数据库密码**：已设置强密码
- [ ] **CORS 配置**：已限制 `allow_origins` 为前端域名
- [ ] **文件上传限制**：已确认 10MB 上限合适
- [ ] **日志目录**：已创建并设置正确权限
- [ ] **进程守护**：已配置 supervisor/systemd 自动重启
- [ ] **HTTPS**：已配置 SSL 证书（推荐 certbot）
- [ ] **防火墙**：已开放必要端口（80/443）
- [ ] **数据库备份**：已配置定期备份策略

---

## 常见问题

### Q：MySQL 连接失败怎么办？

系统会自动降级为 SQLite，不影响启动。要排查 MySQL 问题：

```bash
# 检查 MySQL 服务状态
systemctl status mysql

# 测试连接
mysql -u birdapp -p -h localhost bird_watching

# 检查是否允许远程连接（如有需要）
# 编辑 /etc/mysql/mysql.conf.d/mysqld.cnf
# 修改 bind-address = 0.0.0.0
```

### Q：上传图片访问 404？

确保 Nginx 或静态文件配置正确指向 `uploads/` 目录，且目录权限正确：

```bash
chown -R www-data:www-data uploads/
chmod -R 755 uploads/
```

### Q：如何更新服务？

```bash
# 拉取最新代码
git pull

# 更新依赖
source venv/bin/activate
pip install -r requirements.txt

# 重启服务
supervisorctl restart bird-backend
# 或
systemctl restart bird-backend
```

### Q：如何查看日志？

```bash
# 直接部署
tail -f logs/access.log
tail -f logs/error.log

# Docker
docker-compose logs -f backend

# Supervisor
supervisorctl tail -f bird-backend
```

# 服务器部署指南（1G内存/40G硬盘，Python后端 + Next.js Standalone前端）

## 1. 服务器准备
- 系统：Ubuntu Server 22.04 LTS 64bit
- 确保开放端口：22（SSH）、80/443（Web）、8000（后端API，或自定义端口）
- 安装基础工具：
  ```bash
  sudo apt update && sudo apt install -y python3 python3-venv python3-pip git nginx
  ```

## 2. 获取项目代码
- 推荐用 git 拉取：
  ```bash
  git clone <你的仓库地址>
  cd <项目目录>
  ```
  或用 scp/rsync 上传本地代码。

## 3. 部署 Python 后端
1. 创建虚拟环境并安装依赖：
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. 启动后端服务（以 FastAPI/Flask 为例）：
   ```bash
   pip install gunicorn
   gunicorn -w 2 -b 0.0.0.0:8000 backend.api.main:app
   ```
   > 说明：如有自定义启动脚本，按实际情况调整。
3. 生产环境建议用 supervisor 或 systemd 守护进程。

## 4. 部署 Next.js Standalone 前端
1. 本地或服务器上构建：
   ```bash
   cd frontend
   npm install
   npm run build
   ```
2. 复制 .next/standalone、.next/static、public 到服务器 frontend 目录。
3. 启动前端服务（限制内存，适合 1G 内存服务器）：
   ```bash
   cd frontend
   node --max-old-space-size=256 .next/standalone/server.js
   ```
   > 可用 pm2 守护进程：
   ```bash
   npm install -g pm2
   pm2 start .next/standalone/server.js --node-args="--max-old-space-size=256"
   ```

## 5. 配置 Nginx 反向代理
- 推荐用 Nginx 统一对外暴露 80/443 端口，转发到后端/前端服务。
- 示例配置：
  ```nginx
  server {
      listen 80;
      server_name 43.138.183.31;

      location /api/ {
          proxy_pass http://127.0.0.1:8000/;
          proxy_set_header Host $host;
          proxy_set_header X-Real-IP $remote_addr;
      }

      location / {
          proxy_pass http://127.0.0.1:3000/;
          proxy_set_header Host $host;
          proxy_set_header X-Real-IP $remote_addr;
      }
  }
  ```
- 重载 Nginx：
  ```bash
  sudo systemctl reload nginx
  ```

## 6. 资源优化建议
- 关闭不必要的系统服务，最大化可用内存。
- 可配置 swap（虚拟内存）防止 OOM：
  ```bash
  sudo fallocate -l 1G /swapfile
  sudo chmod 600 /swapfile
  sudo mkswap /swapfile
  sudo swapon /swapfile
  ```
- 生产环境建议用 supervisor/pm2 守护进程，自动重启。

## 7. 其他说明
- 如需 HTTPS，可用 certbot 配置免费 SSL。
- 后端如需加载大模型或处理大文件，建议升级内存。

---
如需详细 supervisor、systemd、pm2 配置或遇到问题，可随时补充！
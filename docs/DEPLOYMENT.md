# 腾讯云部署说明

## 访问地址

部署后访问：

```text
http://服务器公网IP/workbench/
```

现有作品集网站继续使用根路径 `/`。新工作台使用 `/workbench/`，后端 API 使用 `/workbench/api/`。

## 本地构建前端

```bash
cd frontend
npm ci
VITE_BASE_PATH=/workbench/ VITE_API_BASE=/workbench/api npm run build
```

## 上传项目

```bash
scp -r frontier-ai-workbench root@服务器IP:/opt/
```

## 服务器安装和启动

```bash
cd /opt/frontier-ai-workbench
chmod +x deploy/tencent-cloud-deploy.sh
./deploy/tencent-cloud-deploy.sh
```

默认使用 Mock 模式，不需要模型 Key。若要接入真实网页来源和模型：

```bash
cp backend/.env.example backend/.env
vim backend/.env
```

建议先使用：

```text
SOURCE_MODE=web
MODEL_MODE=mock
```

确认来源抓取正常后，再配置 `MODEL_MODE=api` 和后端模型环境变量。

## 检查服务

```bash
systemctl status workbench.service
systemctl status workbench-daily.timer
curl http://127.0.0.1:8000/health
curl http://服务器公网IP/workbench/health
```

## 安全组

腾讯云控制台需要放行：

- TCP 80：HTTP 网站
- TCP 443：以后配置域名和 HTTPS 时使用
- TCP 22：SSH，建议只允许自己的 IP

不要开放 8000 到公网，后端只监听 `127.0.0.1`，由 Nginx 反向代理。

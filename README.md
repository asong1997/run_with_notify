# run_with_notify

一个通用的命令行任务执行器，支持：

✅ 任意 bash 命令执行  
✅ 自动失败重试  
✅ 成功或失败后发送邮件通知（含开始时间、结束时间、耗时、错误信息）

适用于：
- Hugging Face / ModelScope 等模型下载任务
- pip / conda / apt 软件安装
- Docker 镜像拉取、构建
- 训练模型任务（python train.py）
- 大文件上传、rsync / scp 等远程同步任务
- 任意长时间执行的脚本（shell/python等）

---

## 📦 安装
### 拉取项目代码
```bash
git clone https://github.com/asong1997/run_with_notify.git
cd run_with_notify
```

### 配置[config.py](notifier/config.py)
```bash
default_from_email = "13360xxxx@163.com"
default_password = "YGba3bxxxxjGSZT"
default_to_email = "47382xxxx@qq.com"
```

### 源码安装
```bash
# 确保当前路径中有setup.py文件
pip install .
```

安装后，系统将可用命令 `run-with-notify`

---

## 🚀 使用示例

### 示例 1：下载 Hugging Face 模型（模拟长时间任务）
```bash
run-with-notify "python download_model.py" --task "下载Qwen模型" --stream
```

### 示例 2：拉取 Docker 镜像
```bash
run-with-notify "docker pull myregistry.com/llm:v1.0" \
  --task "拉取Docker镜像" \
  --max-fails 2 \
  --retry-interval 120 \
  --from-email your@163.com \
  --password your_auth_code \
  --to-email ops-team@example.com
```

### 示例 3：训练模型并通知我
```bash
run-with-notify "bash train.sh" \
  --task "训练多模态模型" \
  --max-fails 1 \
  --from-email your@163.com \
  --password your_auth_code \
  --to-email your-self@example.com
```

---

## ⚙️ 参数说明

| 参数 | 类型 | 是否必填 | 说明 |
|------|------|----------|------|
| `command` | str | ✅ 是 | 要执行的命令（用引号括起来） |
| `--task` | str | ❌ 否 | 自定义任务名称（用于邮件通知标题） |
| `--max-fails` | int | ❌ 否 | 最大失败重试次数（默认 1） |
| `--retry-interval` | int | ❌ 否 | 失败后的重试等待时间，单位秒（默认 60） |
| `--from-email` | str | ✅ 是 | 发件人邮箱（建议用 163 邮箱） |
| `--password` | str | ✅ 是 | 发件人邮箱授权码（非登录密码） |
| `--to-email` | str | ✅ 是 | 接收通知的邮箱地址 |
| `--stream` | str | ❌ 否 | 是否将任务执行过程的 stdout/stderr 实时打印到终端 |

注意：如果个人使用可以在[config.py](notifier/config.py)使用default参数，设置默认的from-email、password、to-email
---

## 📬 邮件通知内容

邮件将包含：
- ✅ 成功或 ❌ 失败状态
- 🕒 开始时间 和 结束时间
- ⏱️ 任务耗时
- 🔁 尝试次数
- 💬 stdout / stderr 输出

---

## 🔒 安全建议

- 建议使用 **单独申请的邮箱用于发信**（例如 163 邮箱 + 授权码）
- 不要将 `--password` 写入脚本中，可使用 CI/CD 中的环境变量传入

---

## 📈 后续扩展建议

- 日志写入本地 `log/` 文件夹
- Slack / 飞书通知
- 定时任务集成（如 cron / airflow）

---

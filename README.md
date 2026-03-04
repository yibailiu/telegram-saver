<img src="./assets/logo.png" width="150" height="150"/>
<h1> 📦 Telegram 媒体自动归档 Bot</h1>

一个自动接收 Telegram 图片 / 视频并分类存储到本地目录的 Docker 容器项目。

支持：

* 📷 图片自动归档
* 🎬 视频自动归档
* 📁 自动按年份分类
* 🏷 自动版本构建（stable / beta / dev）
* 🐳 Docker 一键部署

---

# 🚀 一分钟快速开始（适合新手）

## 1️⃣ 准备条件

* 已安装 Docker
* 有 Telegram Bot Token
* 知道自己的 USER ID
## ⚠️注意识别假冒账号！
---
不会创建 Bot？
去TG找 👉 `@BotFather` 创建即可。
USER ID 找 👉 `@userinfobot` 即可。
---
## ⚠️注意识别假冒账号！
---

## 2️⃣ 创建存储目录

例如在服务器上创建：

```bash
mkdir -p /mnt/media
```

---

## 3️⃣ 运行容器

### 使用 stable 稳定版

```bash
docker run -d \
  --name tg-media-bot \
  -e BOT_TOKEN=你的bot_token \
  -e ALLOWED_USER_ID=你的user_id \
  -e BASE_PATH=/data \
  -v /mnt/media:/data \
  --restart unless-stopped \
  vincentcg/telegram-saver:stable
```

---

# 📂 存储结构说明

假设 `BASE_PATH=/data`

实际存储效果如下：

```
/data
 ├── PIC
 │    └── 2026
 │         └── 20260304_183012.jpg
 │
 └── Video
      └── 2026
           └── 短片
                └── 20260304_183112.mp4
```

规则：

| 类型 | 存储路径                   |
| -- | ---------------------- |
| 图片 | BASE_PATH/PIC/年份/      |
| 视频 | BASE_PATH/Video/年份/短片/ |

自动按系统时间生成年份目录。

---

# ⚙️ 环境变量说明

| 变量名       | 必填 | 说明                 |
| --------- | -- | ------------------ |
| BOT_TOKEN | ✅  | Telegram Bot Token |
| ALLOWED_USER_ID   | ✅  | 允许接收消息的用户 ID       |
| BASE_PATH | ✅  | 容器内存储根路径           |

---

# 🏷 镜像版本说明

本项目支持三种通道：

| 通道  | Tag            | 说明       |
| --- | -------------- | -------- |
| 稳定版 | stable         | 推荐生产使用   |
| 测试版 | beta           | 功能更新较快   |
| 开发版 | dev-commitHash | 每次提交自动构建 |

示例：

```bash
docker pull vincentcg/telegram-saver:beta
docker pull vincentcg/telegram-saver:dev-a13c8f2
```

---

# 🔄 如何更新

```bash
docker pull vincentcg/telegram-saver:stable
docker stop tg-media-bot
docker rm tg-media-bot
```

然后重新运行即可。

---

# 🧹 自动清理旧镜像（可选）

如果你服务器空间有限，可以执行：

```bash
docker image prune -a
```

---

# ❓ 常见问题

---

### 1️⃣ 报错：file is too big

这是 Telegram 限制：

* Bot API 最大下载 20MB

超过 20MB 视频无法通过普通 API 下载。

解决方式：

* 使用 Telegram Client API（高级方案）
* 或限制上传视频大小

---


# 🛠 进阶用户

支持：

* GitHub Actions 自动构建
* 自动 Semver 版本号
* 自动生成 Changelog
* 自动 Release 页面
* 自动回滚策略
* 自动清理旧版本镜像

---

# 📜 License

MIT License

---


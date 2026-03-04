import os
import requests
import time
from datetime import datetime
import logging
import sys

# =========================
# 日志配置
# =========================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

# =========================
# 环境变量
# =========================
BOT_TOKEN = os.getenv("BOT_TOKEN")
ALLOWED_USER_ID = int(os.getenv("ALLOWED_USER_ID", "0"))
BASE_PATH = os.getenv("BASE_PATH", "/data")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN 未设置")

if not ALLOWED_USER_ID:
    raise ValueError("ALLOWED_USER_ID 未设置")

API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
FILE_URL = f"https://api.telegram.org/file/bot{BOT_TOKEN}"

last_update_id = None


# =========================
# 工具函数
# =========================
def send_message(chat_id, text):
    try:
        requests.post(f"{API_URL}/sendMessage", json={
            "chat_id": chat_id,
            "text": text
        }, timeout=10)
    except Exception:
        logger.exception("发送消息失败")


def build_save_path(file_type):
    """
    根据类型构建目录
    image -> BASE_PATH/PIC/2026/
    video -> BASE_PATH/Video/2026/短片/
    """
    year = str(datetime.now().year)

    if file_type == "image":
        path = os.path.join(BASE_PATH, "PIC", year)
    elif file_type == "video":
        path = os.path.join(BASE_PATH, "Video", year, "短片")
    else:
        return None

    os.makedirs(path, exist_ok=True)
    return path


def generate_filename(prefix, extension):
    """
    IMG_20260304_193022.jpg
    VID_20260304_193025.mp4
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}{extension}"


def unique_filename(directory, filename):
    base, ext = os.path.splitext(filename)
    counter = 1
    new_name = filename

    while os.path.exists(os.path.join(directory, new_name)):
        new_name = f"{base}_{counter}{ext}"
        counter += 1

    return new_name


def download_file(file_path, save_path):
    url = f"{FILE_URL}/{file_path}"
    r = requests.get(url, timeout=180)
    r.raise_for_status()

    with open(save_path, "wb") as f:
        f.write(r.content)


# =========================
# 核心处理逻辑
# =========================
def process_file(update):
    message = (
        update.get("message")
        or update.get("channel_post")
        or update.get("edited_message")
    )

    if not message:
        return

    user_id = message.get("from", {}).get("id")
    chat_id = message.get("chat", {}).get("id")

    if user_id != ALLOWED_USER_ID:
        send_message(chat_id, "❌ 未授权用户")
        return

    file_id = None
    extension = ""
    file_type = None
    prefix = ""

    # =========================
    # 图片
    # =========================
    if "photo" in message:
        largest_photo = message["photo"][-1]
        file_id = largest_photo["file_id"]
        extension = ".jpg"
        file_type = "image"
        prefix = "IMG"

    # =========================
    # 视频
    # =========================
    elif "video" in message:
        video = message["video"]
        file_id = video["file_id"]
        extension = ".mp4"
        file_type = "video"
        prefix = "VID"

    # =========================
    # document 类型（可能是图片或视频）
    # =========================
    elif "document" in message:
        doc = message["document"]
        mime = doc.get("mime_type", "")

        if mime.startswith("video/"):
            file_id = doc["file_id"]
            extension = ".mp4"
            file_type = "video"
            prefix = "VID"

        elif mime.startswith("image/"):
            file_id = doc["file_id"]
            extension = ".jpg"
            file_type = "image"
            prefix = "IMG"

    # =========================
    # 非支持类型
    # =========================
    if not file_id or not file_type:
        send_message(chat_id, "⚠️ 仅支持图片或视频文件，未进行存储")
        return

    try:
        # 获取 Telegram 文件路径
        r = requests.get(f"{API_URL}/getFile", params={"file_id": file_id}, timeout=30)
        r.raise_for_status()
        file_path = r.json()["result"]["file_path"]

        # 构建保存目录
        save_folder = build_save_path(file_type)

        filename = generate_filename(prefix, extension)
        filename = unique_filename(save_folder, filename)

        save_path = os.path.join(save_folder, filename)

        download_file(file_path, save_path)

        logger.info(f"文件已保存: {save_path}")

        send_message(
            chat_id,
            f"✅ 已保存:\n{save_path}"
        )

    except Exception as e:
        logger.exception("保存失败")
        send_message(chat_id, f"❌ 保存失败: {str(e)}")


# =========================
# 轮询
# =========================
def poll():
    global last_update_id

    while True:
        try:
            params = {"timeout": 60}
            if last_update_id:
                params["offset"] = last_update_id + 1

            r = requests.get(f"{API_URL}/getUpdates", params=params, timeout=70)
            r.raise_for_status()

            updates = r.json()["result"]

            for update in updates:
                last_update_id = update["update_id"]
                process_file(update)

        except Exception:
            logger.exception("轮询异常")
            time.sleep(5)

        time.sleep(1)


# =========================
# 启动
# =========================
if __name__ == "__main__":
    logger.info("Telegram 文件保存 Bot 启动")
    logger.info(f"BASE_PATH = {BASE_PATH}")
    poll()
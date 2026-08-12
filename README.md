# mmsb


---

# 🔐 四位密码暴力破解自动化脚本（Python + PyAutoGUI）

> 针对教育类家长验证界面的四位数字密码（0000~9999）自动遍历工具，支持断点续跑、图像识别错误检测、智能休息防封控。

![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)

---

## 📖 项目简介

本项目是一个基于 **PyAutoGUI** 和 **OpenCV** 的图形界面自动化脚本，用于模拟鼠标点击虚拟数字键盘，自动遍历从 `0000` 到 `9999` 的所有四位密码组合，并通过图像匹配或像素颜色检测判断密码是否正确。

**适用场景**：
- 家长验证、儿童锁等无输入框、只能点击屏幕数字键的应用
- 学习自动化测试、图像识别、GUI 操作等技术的实战练习

> ⚠️ **免责声明**：本工具仅供合法授权的测试和学习使用，严禁用于非法破解他人账户或系统。使用者需自行承担相关法律责任。

---

## ✨ 功能特性

- 🖱️ **纯坐标点击**：基于固定坐标模拟点击，稳定可靠，无需复杂图像模板匹配数字键。
- 🔢 **一键推算所有数字坐标**：只需提供 `1` 键坐标及行列间距，自动生成 0~9 所有按钮位置。
- 🧠 **智能错误检测**：
  - 支持**图像匹配**（截取“密码错误”文字图片）或**像素颜色检测**（检测特定区域颜色变化）。
  - 自动判定尝试是否成功，一旦检测到正确密码立即记录并停止。
- ⏸️ **断点续跑**：支持自定义起始密码范围，中途按下 `Ctrl+C` 可安全退出并提示当前密码，方便续跑。
- 🛡️ **防卡顿 & 防风控**：可配置每尝试 N 次后休息 M 秒，降低系统负载，减少被检测风险。
- 📊 **详细日志**：每次尝试、进度、错误信息均记录在 `bruteforce_log.txt`，便于追溯。

---

## 📋 环境要求

- **Python**：3.7 及以上版本
- **依赖库**：
  ```bash
  pip install pyautogui opencv-python pillow
  ```
- **操作系统**：Windows / macOS / Linux（需支持 GUI 图形界面）

---

## 🚀 快速开始

### 1. 克隆仓库
```bash
git clone https://github.com/wwss894/mmsb.git
cd mmsb
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```
（若没有 `requirements.txt`，直接安装上述依赖即可）

### 3. 准备模板图片（若使用图像匹配）
- 在项目根目录创建 `templates` 文件夹。
- 截取界面中 **“密码错误”** 提示文字的区域，保存为 `error_msg.png`，放入 `templates` 目录。
- 若使用像素检测，则无需此步骤。

### 4. 配置脚本参数
打开 `bruteforce.py`，根据您的屏幕和目标应用调整以下关键配置：
```python
# 密码尝试范围
START_PIN = 0          # 起始密码
END_PIN = 9999         # 结束密码

# 数字键盘坐标推算（以“1”键中心为基准）
FIRST_KEY_COORD = (350, 450)   # 屏幕坐标 (x, y)
H_SPACING = 100                # 水平间距
V_SPACING = 70                 # 垂直间距

# 清除按钮坐标
CLEAR_COORD = (600, 660)

# 错误检测方式（二选一）
USE_IMAGE_DETECTION = True     # True=图像匹配，False=像素检测
ERROR_TEMPLATE = "./templates/error_msg.png"

# 休息策略（防止风控）
SLEEP_INTERVAL = 50            # 每尝试50次后休息
SLEEP_DURATION = 2.0           # 休息2秒
```

> 💡 **坐标测量**：可使用 `python -m pyautogui` 启动鼠标实时坐标查看器，或使用截图工具定位按钮中心点。

### 5. 运行脚本
```bash
python bruteforce.py
```
脚本会等待 5 秒后开始，请提前将目标应用窗口置于最前。

### 6. 中断与续跑
- 按 `Ctrl + C` 安全终止，终端会提示当前尝试的密码。
- 修改 `START_PIN` 为该密码 + 1，重新运行即可继续。

---

## ⚙️ 主要配置参数说明

| 参数 | 说明 |
|------|------|
| `START_PIN` / `END_PIN` | 尝试的密码范围（包含两端），例如 `0000` 到 `9999` |
| `FIRST_KEY_COORD` | 数字键 `1` 的中心点坐标 `(x, y)` |
| `H_SPACING` / `V_SPACING` | 水平 / 垂直相邻数字键的像素间距 |
| `CLEAR_COORD` | 清除按钮的中心点坐标 |
| `USE_IMAGE_DETECTION` | 是否使用图像匹配检测错误，否则启用像素检测 |
| `ERROR_TEMPLATE` | 错误提示模板图片路径（图像匹配模式） |
| `ERROR_REGION` | 错误提示区域（像素检测模式） |
| `ERROR_RGB_THRESHOLD` | 错误颜色阈值（像素检测模式） |
| `WAIT_AFTER_SUBMIT` | 输入完4位密码后等待校验的秒数 |
| `SLEEP_INTERVAL` / `SLEEP_DURATION` | 每尝试多少次后休息多少秒 |

---

## 📁 文件结构

```
.
├── bruteforce.py              # 主脚本（可重命名）
├── templates/                 # 模板图片文件夹（可选）
│   └── error_msg.png          # “密码错误”文字截图
├── bruteforce_log.txt         # 运行日志（自动生成）
├── correct_password.txt       # 记录正确密码（找到后生成）
└── README.md                  # 项目说明
```

---

## 🔧 常见问题

### Q1: 提示 `图像检测出错` 或找不到模板？
- 确保 `templates/error_msg.png` 文件存在，且为清晰的截图（只包含错误文字）。
- 可尝试将 `USE_IMAGE_DETECTION` 设为 `False`，改用像素检测（需配置 `ERROR_REGION` 和颜色阈值）。

### Q2: 点击位置不准确？
- 检查屏幕缩放比例（如 Windows 125% 缩放），脚本已自动适配 DPI，但若仍偏移，请重新测量 `FIRST_KEY_COORD` 等坐标。
- 将 `FIRST_KEY_COORD` 设置为实际测量值，确保应用窗口未移动。

### Q3: 程序运行一段时间后卡死？
- 可能是图像匹配全屏扫描导致资源占用过高，建议在 `locateOnScreen` 中传入 `region` 参数限定搜索区域（代码中已注释示例）。
- 调整 `SLEEP_INTERVAL` 和 `SLEEP_DURATION`，增加休息频率。

### Q4: 如何从上次中断处继续？
- 查看终端最后打印的密码（如 `当前尝试到密码: 0123`），将 `START_PIN` 改为 `0124` 重新运行。

---

## 🤝 贡献

欢迎提出 Issue 或 Pull Request。如果您有改进建议（如支持更多检测方式、优化速度等），请随时联系。

---

## 📄 许可证

本项目采用 **MIT License**，您可以自由使用、修改和分发，但需保留版权声明。

---

## 🙏 致谢

- [PyAutoGUI](https://pyautogui.readthedocs.io/) – 强大的跨平台 GUI 自动化库
- [OpenCV](https://opencv.org/) – 图像处理与模板匹配支持

---



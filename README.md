# 金铲铲之战自动拿牌工具

## 📋 目录

- [项目简介](#项目简介)
- [功能特性](#功能特性)
- [环境要求](#环境要求)
- [安装部署](#安装部署)
- [使用说明](#使用说明)
- [界面操作](#界面操作)
- [常见问题](#常见问题)
- [项目结构](#项目结构)
- [更新日志](#更新日志)
- [许可证](#许可证)

---

## 项目简介

金铲铲之战自动拿牌工具是一款基于Python开发的自动化辅助软件，通过图像识别技术实时捕捉游戏界面中的卡牌信息，根据用户预设的策略自动完成选牌操作。

> ⚠️ **注意**：本工具仅供学习和研究使用，请勿用于违规行为。使用本工具前，请确保了解并遵守游戏的相关规则和政策。

## 功能特性

### 核心功能
- 🎯 **智能卡牌识别**：基于OpenCV的图像识别技术，实时识别游戏中的卡牌
- ⚡ **自动选牌**：根据预设策略自动完成选牌操作
- 🔧 **多种选牌策略**：支持优先级策略、费用平衡策略、阵容构建策略
- 📊 **完整日志记录**：记录所有操作和识别结果，便于问题排查

### 用户界面
- 🖥️ **直观的GUI界面**：简洁明了的操作界面
- 🎨 **卡牌预览**：实时显示当前识别到的卡牌
- 📝 **日志输出**：显示详细的运行日志
- ⚙️ **策略配置**：支持自定义卡牌优先级和选牌策略

### 系统特性
- 🛡️ **安全稳定**：内置多种安全保护机制
- 🔄 **热更新**：支持配置热更新，无需重启程序
- 📦 **模块化设计**：高度模块化，易于扩展和维护

---

## 环境要求

### 最低配置
- **操作系统**：Windows 10/11 (64位)
- **内存**：4GB RAM
- **硬盘**：500MB 可用空间
- **分辨率**：1920×1080 或更高

### 软件依赖
- Python 3.8+
- 显卡驱动：支持DirectX 11

---

## 安装部署

### 步骤1：克隆或下载项目

```bash
git clone https://github.com/Joker-xps/TFT-Auto-Picker.git
cd TFT-Auto-Picker
```

### 步骤2：创建虚拟环境（推荐）

```bash
python -m venv venv
venv\Scripts\activate
```

### 步骤3：安装依赖

```bash
pip install -r requirements.txt
```

### 步骤4：运行程序

```bash
python main.py
```

---

## 使用说明

### 快速开始

1. **启动程序**：运行 `python main.py`
2. **进入游戏**：打开金铲铲之战，进入选牌阶段
3. **配置策略**：在界面中设置卡牌优先级
4. **启动自动**：点击"启动"按钮开始自动选牌

### 命令行参数

```bash
python main.py [选项]

选项:
  --debug, -d       启用调试模式
  --no-tray         禁用系统托盘
  --min-interval    设置最小检测间隔（秒）
  --log-level       设置日志级别 (DEBUG/INFO/WARNING/ERROR)
```

示例：
```bash
# 调试模式运行
python main.py --debug

# 设置检测间隔为0.2秒
python main.py --min-interval 0.2

# 详细日志输出
python main.py --log-level DEBUG
```

---

## 界面操作

### 主界面说明

```
┌─────────────────────────────────────────────────────┐
│ 金铲铲之战自动拿牌工具 v1.0.0                    ─ □ X│
├─────────────────────────────────────────────────────┤
│ [启动] [暂停] [刷新识别]                          │
├────────────────┬───────────────────────────────────┤
│ 运行状态       │ 策略配置                          │
│ • 自动拿牌: 运行中  │ ┌─────────────────────────┐   │
│ • 游戏阶段: 商店   │ │ 选牌策略                │   │
│ • 识别卡牌: 5      │ │ [优先级策略 ▼]          │   │
│ • 已拿卡牌: 12     │ └─────────────────────────┘   │
│ • 当前策略: 优先级  │                              │
│                │ ┌─────────────────────────┐   │
│ [启动] [暂停]   │ │ 卡牌优先级              │   │
└────────────────┴───────────────────────────────────┘
```

### 策略配置

#### 优先级策略
1. 在"卡牌优先级"区域输入卡牌名称
2. 点击"添加"或按回车键添加
3. 使用上下箭头调整优先级顺序
4. 数字越小优先级越高

#### 高级设置
- **最高费用**：设置拿牌的最高费用限制
- **检测间隔**：设置卡牌检测的间隔时间
- **拿牌冷却**：设置连续拿牌的最小间隔
- **偏好高费卡**：是否优先拿取高费卡

### 快捷键

| 快捷键 | 功能 |
|--------|------|
| F1 | 启动/停止自动拿牌 |
| F2 | 暂停/继续 |
| F5 | 刷新识别 |
| Esc | 停止自动拿牌 |

---

## 常见问题

### Q1: 程序无法识别卡牌怎么办？

**解决方法：**
1. 确保游戏窗口处于活动状态
2. 检查屏幕分辨率是否支持
3. 尝试调整检测间隔
4. 查看日志文件获取详细错误信息

### Q2: 拿牌位置不准确怎么办？

**解决方法：**
1. 确保游戏窗口没有缩放
2. 检查是否使用了多显示器
3. 尝试运行 `python main.py --debug` 进行调试

### Q3: 程序运行缓慢怎么办？

**解决方法：**
1. 增大检测间隔时间
2. 关闭其他占用CPU的程序
3. 确保系统有足够的内存

### Q4: 如何导出/导入配置？

**解决方法：**
1. 在策略配置区域点击"导出"按钮
2. 选择保存位置和文件名
3. 导入时点击"导入"按钮，选择配置文件

### Q5: 程序崩溃了怎么办？

**解决方法：**
1. 查看 `logs` 目录下的日志文件
2. 在GitHub Issues中报告问题
3. 包含完整的错误日志信息

---

## 项目结构

```
TFT-Auto-Picker/
├── main.py                    # 主程序入口
├── requirements.txt           # 依赖列表
├── README.md                  # 项目说明文档
│
├── core/                      # 核心模块
│   ├── __init__.py
│   ├── card.py               # 卡牌数据模型
│   ├── game_state.py         # 游戏状态管理
│   └── strategy.py           # 选牌策略
│
├── modules/                   # 功能模块
│   ├── automation/           # 自动化模块
│   │   ├── __init__.py
│   │   ├── game_automator.py # 游戏自动化主逻辑
│   │   └── mouse_controller.py # 鼠标控制
│   │
│   ├── config/               # 配置模块
│   │   ├── __init__.py
│   │   ├── card_config.py    # 卡牌配置管理
│   │   └── settings.py       # 全局设置
│   │
│   ├── image_recognition/    # 图像识别模块
│   │   ├── __init__.py
│   │   ├── card_recognizer.py # 卡牌识别主逻辑
│   │   ├── screen_capture.py  # 屏幕捕获
│   │   └── template_matcher.py # 模板匹配
│   │
│   └── ui/                   # 用户界面模块
│       ├── __init__.py
│       ├── log_viewer.py     # 日志查看器
│       ├── main_window.py    # 主窗口
│       └── strategy_panel.py  # 策略配置面板
│
├── resources/                 # 资源文件
│   └── cards/                # 卡牌模板图片
│
├── logs/                      # 日志文件目录
│
├── config/                    # 配置文件目录
│   ├── settings.json         # 程序设置
│   ├── card_priority.json    # 卡牌优先级
│   └── custom_decks.json     # 自定义卡组
│
└── tests/                     # 测试文件
```

---

## 更新日志

### v1.0.0 (2024-01-15)
- ✨ 初始版本发布
- 🎯 实现基础卡牌识别功能
- ⚡ 实现自动选牌功能
- 🖥️ 实现图形用户界面
- 🔧 实现多种选牌策略
- 📝 完整的日志记录系统

---

## 许可证

本项目采用 MIT 许可证开源。

```
MIT License

Copyright (c) 2024 AutoDev Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

---

## 联系方式

- 项目主页：https://github.com/yourusername/TFT-Auto-Picker
- 问题反馈：https://github.com/yourusername/TFT-Auto-Picker/issues
- 邮箱：support@example.com

---

感谢您使用金铲铲之战自动拿牌工具！🎮

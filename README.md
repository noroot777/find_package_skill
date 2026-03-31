# 找快递 (find-package)

一个 [OpenClaw](https://openclaw.com) 技能，通过 Telegram Bot 帮你在驿站货架上找到自己的快递。

## 工作流程

1. **发送取件码** — 直接输入文字（如 `5-2-1234`），或者截图发过来（短信通知、菜鸟裹裹等 App 截图都行）
2. **拍货架照片** — 对着货架拍照发给 Bot，一次可以发多张
3. **自动识别匹配** — EasyOCR 精确识别照片上所有文字坐标，匹配取件码后用红框标出
4. **结果反馈** — 找到的快递会标注在照片上发回给你，多个快递会逐个追踪，全部找到后提示完成

## 技术方案

- **Claude 视觉**：理解用户意图，从截图中提取取件码
- **EasyOCR**：精确检测货架照片上的文字及其像素坐标
- **Pillow**：在匹配位置绘制红色标注框

## 安装

将整个目录复制到 OpenClaw 的 skills 目录下即可。

### 依赖

- Python 3
- [EasyOCR](https://github.com/JaidedAI/EasyOCR)（OCR 文字检测）
- [Pillow](https://pillow.readthedocs.io/)（图片标注）

```bash
pip3 install easyocr Pillow
```

## 文件结构

```
├── SKILL.md                    # 技能定义与工作流指令
├── README.md
└── scripts/
    ├── ocr_detect.py           # OCR 文字检测（返回坐标 + 文本）
    ├── annotate.py             # 图片红框标注
    └── find_package.py         # 一体化脚本（检测 + 匹配 + 标注）
```

## 脚本用法

### 一键找快递

```bash
python3 scripts/find_package.py \
  --input shelf_photo.jpg \
  --code "9347" \
  --output result.jpg
```

支持同时查找多个取件码：

```bash
python3 scripts/find_package.py \
  --input shelf_photo.jpg \
  --code "9347,0295,1339" \
  --output result.jpg
```

### 单独使用 OCR 检测

```bash
python3 scripts/ocr_detect.py --input shelf_photo.jpg
```

输出 JSON：
```json
[
  {"text": "9347", "bbox": [45, 280, 130, 340], "confidence": 0.95},
  {"text": "16-2-1339", "bbox": [200, 310, 350, 360], "confidence": 0.92}
]
```

### 单独使用标注

```bash
# 从 OCR 结果标注
python3 scripts/annotate.py \
  --input photo.jpg --output result.jpg \
  --detections detections.json --match "9347"

# 手动指定坐标
python3 scripts/annotate.py \
  --input photo.jpg --output result.jpg \
  --box "100,200,300,400" --label "取件码: 5-2-1234"
```

## 触发方式

在 Telegram 中对 OpenClaw Bot 说：

- "帮我找快递"
- "我要取件"
- "取件码是 5-2-1234"
- "快递在哪"

等类似的话即可触发。

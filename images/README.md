# 图片文件夹说明

## 概述

此文件夹用于存放批量执行时使用的代币图片。脚本会从此文件夹中随机选择图片用于代币创建。

## 支持的图片格式

- `.jpg` / `.jpeg`
- `.png` 
- `.gif`
- `.bmp`
- `.webp`

## 图片要求

### 尺寸建议
- **推荐**: 512x512 或 1024x1024 像素
- **最小**: 200x200 像素
- **最大**: 2048x2048 像素

### 文件大小
- **最大**: 10MB
- **推荐**: 1MB 以下

### 内容建议
- 清晰的图标或logo
- 与加密货币/区块链相关的元素
- 避免版权保护的内容
- 建议使用原创或免版权图片

## 使用方式

1. **准备图片**：将符合要求的图片文件放入此文件夹
2. **文件命名**：可以使用任意文件名，脚本会自动识别
3. **运行脚本**：执行 `python3 batch_runner.py` 时指定此文件夹路径

## 示例文件结构

```
images_example/
├── README.md           # 本说明文件
├── token1.png          # 示例图片1
├── crypto_logo.jpg     # 示例图片2
├── blockchain.gif      # 示例图片3
└── defi_icon.webp      # 示例图片4
```

## 图片选择逻辑

- 脚本会随机选择未使用的图片
- 避免在同一批次中重复使用图片
- 当所有图片都使用过后，会重置使用记录继续循环使用

## 注意事项

⚠️ **重要提醒**：
- 确保图片内容合法合规
- 避免使用他人版权图片
- 建议使用与项目相关的原创图片
- 图片质量会影响代币的专业度

## 获取免费图片资源

推荐的免费图片网站：
- **Unsplash**: https://unsplash.com
- **Pixabay**: https://pixabay.com  
- **Freepik**: https://freepik.com
- **IconFinder**: https://iconfinder.com

搜索关键词建议：
- "cryptocurrency"
- "blockchain" 
- "digital currency"
- "crypto logo"
- "token icon" 
# Face Swap Web Application

一个基于 Flask 和 InsightFace 的在线换脸应用。用户可以上传自己的照片，选择想要成为的角色（如军人、医生、教师等），实现照片换脸效果。

## 功能特点

- 支持用户上传照片
- 提供男性/女性角色选择
- 多种职业角色可选
- 实时照片预览
- 高质量换脸效果
- 简洁的用户界面

## 系统要求

- Python 3.8+
- CUDA 支持（可选，用于GPU加速）
- 足够的磁盘空间（用于存储模型和图片）

## 安装步骤

1. 克隆项目并进入项目目录
bash
git clone <repository_url>
cd face-swap-app

2. 创建并激活虚拟环境（推荐）
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 下载必要的模型文件
```bash
# 创建模型目录
mkdir -p models

# 下载模型文件到 models 目录
# buffalo_l 模型
# inswapper_128.onnx 模型
```

5. 准备角色图片
```bash
# 创建图片目录
mkdir -p static/roles/male
mkdir -p static/roles/female

# 将角色图片放入对应目录
# male: soldier.jpg, doctor.png, teacher.jpg
# female: nurse.jpg, doctor.jpg, teacher.jpeg
```

## 使用说明

1. 启动服务器
```bash
python app.py
```

2. 访问应用
```
http://localhost:1204
```

3. 使用步骤
   - 点击"选择照片"上传您的照片
   - 选择性别（男性/女性）
   - 选择想要换脸的角色
   - 点击"开始换脸"
   - 等待处理完成，查看结果

## 注意事项

1. 照片要求：
   - 建议分辨率：800x800 到 2000x2000
   - 要求正面清晰的人脸
   - 避免过度曝光或太暗的照片
   - 建议使用自然光线下拍摄的照片
   - 照片中人物表情自然
   - 避免戴墨镜、口罩等遮挡

2. 服务器配置：
   - 默认端口：1204
   - 支持外部访问：0.0.0.0

3. 安全提示：
   - 建议在内网环境使用
   - 注意保护用户隐私
   - 定期清理临时文件

## 技术栈

- Flask: Web 框架
- InsightFace: 人脸识别和换脸
- OpenCV: 图像处理
- NumPy: 数值计算
- Base64: 图片编码

## 目录结构

```
face-swap-app/
├── app.py              # 主应用文件
├── requirements.txt    # 项目依赖
├── models/            # 模型文件目录
│   ├── buffalo_l
│   └── inswapper_128.onnx
├── static/            # 静态文件
│   └── roles/         # 角色图片
│       ├── male/      # 男性角色
│       └── female/    # 女性角色
└── README.md          # 项目文档
```

## 许可证

MIT License
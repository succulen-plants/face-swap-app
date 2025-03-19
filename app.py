from flask import Flask, request, render_template_string, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import insightface
from insightface.app import FaceAnalysis
import os
import base64

app = Flask(__name__)
CORS(app)

# HTML模板 - 直接嵌入Python文件中
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>角色换脸</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            background-color: #f5f5f5;
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .main-content {
            display: flex;
            gap: 30px;
            margin: 20px 0;
        }
        .left-panel {
            flex: 1;
            min-width: 300px;
        }
        .right-panel {
            flex: 2;
        }
        .preview-container {
            margin: 20px 0;
            text-align: center;
        }
        #imagePreview {
            max-width: 300px;
            max-height: 300px;
            margin: 10px 0;
            border-radius: 8px;
            display: none;
        }
        .tips {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
        }
        .tips ul {
            padding-left: 20px;
            margin: 10px 0;
        }
        .tips li {
            margin: 5px 0;
            color: #666;
        }
        .gender-select {
            margin: 20px 0;
            text-align: center;
        }
        .gender-btn {
            padding: 12px 30px;
            margin: 0 10px;
            cursor: pointer;
            border: 2px solid #ddd;
            background: white;
            border-radius: 25px;
            font-size: 16px;
            transition: all 0.3s ease;
        }
        .gender-btn:hover {
            background-color: #f8f9fa;
            border-color: #007bff;
        }
        .gender-btn.selected {
            border-color: #007bff;
            background-color: #007bff;
            color: white;
        }
        .roles {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .role {
            border: 1px solid #ddd;
            padding: 10px;
            text-align: center;
            cursor: pointer;
            display: none;
            border-radius: 8px;
            transition: all 0.3s ease;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .role.visible {
            display: block;
        }
        .role:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }
        .role.selected {
            border-color: #007bff;
            background-color: #f8f9fa;
        }
        .role img {
            width: 100%;
            height: 250px;
            object-fit: cover;
            border-radius: 4px;
        }
        .upload-btn {
            display: inline-block;
            padding: 12px 24px;
            background-color: #28a745;
            color: white;
            border-radius: 25px;
            cursor: pointer;
            margin: 20px 0;
            transition: all 0.3s ease;
        }
        .upload-btn:hover {
            background-color: #218838;
        }
        #swapButton {
            width: 100%;
            padding: 15px;
            background-color: #007bff;
            color: white;
            border: none;
            border-radius: 25px;
            font-size: 16px;
            cursor: pointer;
            margin-top: 20px;
        }
        #swapButton:disabled {
            background-color: #ccc;
            cursor: not-allowed;
        }
        .result-container {
            margin-top: 30px;
            text-align: center;
        }
        #result img {
            max-width: 100%;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .loading {
            display: none;
            text-align: center;
            margin: 20px 0;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>角色换脸</h1>
        <div class="main-content">
            <div class="left-panel">
                <div class="tips">
                    <h3>图片要求：</h3>
                    <ul>
                        <li>建议分辨率：800x800 到 2000x2000</li>
                        <li>要求正面清晰的人脸</li>
                        <li>避免过度曝光或太暗的照片</li>
                        <li>建议使用自然光线下拍摄的照片</li>
                        <li>照片中人物表情自然</li>
                        <li>避免戴墨镜、口罩等遮挡</li>
                    </ul>
                </div>
                <div class="upload-section">
                    <input type="file" id="userPhoto" accept="image/*" style="display: none;">
                    <button class="upload-btn" id="uploadBtn">选择照片</button>
                </div>
                <div class="preview-container">
                    <h3>预览</h3>
                    <img id="imagePreview" alt="预览">
                </div>
                <button id="swapButton" disabled>开始换脸</button>
            </div>
            <div class="right-panel">
                <div class="gender-select">
                    <button class="gender-btn" data-gender="male">男性角色</button>
                    <button class="gender-btn" data-gender="female">女性角色</button>
                </div>
                <div class="roles" id="rolesContainer">
                    <!-- 角色将通过 JavaScript 动态添加 -->
                </div>
            </div>
        </div>
        <div class="loading">处理中...</div>
        <div class="result-container">
            <div id="result"></div>
        </div>
    </div>

    <script>
        let selectedRole = null;
        let selectedGender = null;
        let userImage = null;

        // 获取元素引用
        const fileInput = document.getElementById('userPhoto');
        const uploadBtn = document.getElementById('uploadBtn');
        const preview = document.getElementById('imagePreview');

        // 处理文件上传
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    userImage = e.target.result;
                    preview.src = userImage;
                    preview.style.display = 'block';
                    uploadBtn.textContent = '重新选择';
                    updateSwapButton();
                };
                reader.readAsDataURL(file);
            } else {
                userImage = null;
                preview.src = '';
                preview.style.display = 'none';
                uploadBtn.textContent = '选择照片';
                updateSwapButton();
            }
        });

        // 处理上传按钮点击
        uploadBtn.addEventListener('click', function(e) {
            e.stopPropagation(); // 阻止事件冒泡
            fileInput.value = ''; // 清空文件输入，确保能重复选择同一文件
            fileInput.click();
        });

        // 获取角色数据
        async function loadRoles() {
            try {
                const response = await fetch('/api/roles');
                const roles = await response.json();
                
                const container = document.getElementById('rolesContainer');
                
                for (const [gender, genderRoles] of Object.entries(roles)) {
                    for (const [roleId, role] of Object.entries(genderRoles)) {
                        const roleDiv = document.createElement('div');
                        roleDiv.className = 'role';
                        roleDiv.dataset.gender = gender;
                        roleDiv.dataset.role = roleId;
                        
                        roleDiv.innerHTML = `
                            <img src="${role.path}" alt="${role.name}">
                            <p>${role.name}</p>
                        `;
                        
                        container.appendChild(roleDiv);
                    }
                }
                
                // 绑定角色点击事件
                bindRoleEvents();
            } catch (error) {
                console.error('加载角色失败:', error);
            }
        }

        // 处理性别选择
        document.querySelectorAll('.gender-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const gender = this.dataset.gender;
                document.querySelectorAll('.gender-btn').forEach(b => b.classList.remove('selected'));
                this.classList.add('selected');
                selectedGender = gender;
                
                document.querySelectorAll('.role').forEach(role => {
                    if (role.dataset.gender === gender) {
                        role.classList.add('visible');
                    } else {
                        role.classList.remove('visible');
                        role.classList.remove('selected');
                    }
                });
                
                selectedRole = null;
                updateSwapButton();
            });
        });

        function bindRoleEvents() {
            document.querySelectorAll('.role').forEach(role => {
                role.addEventListener('click', function() {
                    if (!this.classList.contains('visible')) return;
                    
                    document.querySelectorAll('.role').forEach(r => r.classList.remove('selected'));
                    this.classList.add('selected');
                    selectedRole = this.dataset.role;
                    updateSwapButton();
                });
            });
        }

        function updateSwapButton() {
            const button = document.getElementById('swapButton');
            button.disabled = !(selectedRole && selectedGender && userImage);
        }

        // 处理换脸请求
        document.getElementById('swapButton').addEventListener('click', async function() {
            if (!selectedRole || !selectedGender || !userImage) return;

            const loading = document.querySelector('.loading');
            loading.style.display = 'block';
            
            try {
                const response = await fetch('/swap', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        image: userImage,
                        gender: selectedGender,
                        role: selectedRole
                    })
                });

                const data = await response.json();
                
                if (data.error) {
                    alert(data.error);
                    return;
                }

                const resultDiv = document.getElementById('result');
                resultDiv.innerHTML = `<img src="${data.image}" alt="换脸结果">`;
            } catch (error) {
                alert('换脸失败：' + error.message);
            } finally {
                loading.style.display = 'none';
            }
        });

        // 页面加载时获取角色数据
        loadRoles();
    </script>
</body>
</html>
'''

# 角色图片配置
ROLES = {
    'male': {
        'soldier': {
            'path': '/static/roles/male/soldier.jpg',  # 注意这里要加上前导斜杠
            'name': '军人'
        },
        'doctor': {
            'path': '/static/roles/male/doctor.png',
            'name': '医生'
        },
        'teacher': {
            'path': '/static/roles/male/teacher.jpg',
            'name': '老师'
        },
        # 'aisha': {
        #     'path': '/static/roles/male/aoteman.png',
        #     'name': '奥特曼'
        # }
    },
    'female': {
        'nurse': {
            'path': '/static/roles/female/nurse.jpg',
            'name': '护士'
        },
        'doctor': {
            'path': '/static/roles/female/doctor.jpg',
            'name': '医生'
        },
        'teacher': {
            'path': '/static/roles/female/teacher.jpeg',
            'name': '老师'
        },
        # 'student': {
        #     'path': '/static/roles/female/aisha.png',
        #     'name': '艾莎'
        # }
    }
}

def swap_face(source_img, target_img_path, source_is_base64=False):
    """换脸函数"""
    # 初始化人脸检测器
    model_dir = './models'
    os.environ['INSIGHTFACE_HOME'] = model_dir

    app = FaceAnalysis(name='buffalo_l', 
                      root=model_dir, 
                      providers=['CPUExecutionProvider'])
    
    # 修改检测参数，提高灵敏度
    app.prepare(ctx_id=0, 
               det_size=(640, 640),  # 降低检测尺寸，提高灵敏度
               det_thresh=0.3)       # 降低检测阈值，提高检测灵敏度

    # 加载换脸模型 - 添加这部分
    model_path = "./models/inswapper_128.onnx"
    swapper = insightface.model_zoo.get_model(model_path)

    try:
        # 处理源图片
        if source_is_base64:
            img_data = base64.b64decode(source_img.split('base64,')[1])
            nparr = np.frombuffer(img_data, np.uint8)
            source = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        else:
            source = cv2.imread(source_img)

        if source is None:
            raise Exception("无法加载源图片")

        # 读取目标图片
        target = cv2.imread(target_img_path)
        if target is None:
            raise Exception("无法加载目标图片")

        # 添加调试信息
        print(f"源图片尺寸: {source.shape}")
        print(f"目标图片尺寸: {target.shape}")

        # 图片预处理 - 调整大小
        if source.shape[0] < 800 or source.shape[1] < 800:
            scale = max(800/source.shape[0], 800/source.shape[1])
            source = cv2.resize(source, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)
        elif source.shape[0] > 2000 or source.shape[1] > 2000:
            scale = min(2000/source.shape[0], 2000/source.shape[1])
            source = cv2.resize(source, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)

        # 检测人脸前的图像预处理
        # 1. 确保图像是BGR格式
        if len(source.shape) == 2:  # 如果是灰度图
            source = cv2.cvtColor(source, cv2.COLOR_GRAY2BGR)
        
        # 2. 调整亮度和对比度
        source = cv2.convertScaleAbs(source, alpha=1.1, beta=10)

        # 3. 添加调试信息
        print("开始检测人脸...")
        
        # 检测人脸
        source_faces = app.get(source)
        print(f"检测到 {len(source_faces)} 个人脸")
        
        if len(source_faces) == 0:
            # 保存问题图片以供分析
            debug_path = "debug_source.jpg"
            cv2.imwrite(debug_path, source)
            raise Exception(f"未在源图片中检测到人脸，已保存问题图片到 {debug_path}")
            
        target_faces = app.get(target)
        if len(target_faces) == 0:
            raise Exception("未在目标图片中检测到人脸")

        # 执行换脸
        result = swapper.get(target, target_faces[0], source_faces[0])
        
        # 确保结果不为空
        if result is None:
            raise Exception("换脸处理失败")

        # 简化后处理步骤，只保留必要的处理
        # 1. 轻微提升亮度和对比度
        result = cv2.convertScaleAbs(result, alpha=1.05, beta=3)

        # 2. 保存高质量图片
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 95]
        success, buffer = cv2.imencode('.jpg', result, encode_param)
        
        if not success:
            raise Exception("图片编码失败")

        return base64.b64encode(buffer).decode('utf-8')

    except Exception as e:
        print(f"换脸处理错误: {str(e)}")  # 添加错误日志
        raise e

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/roles', methods=['GET'])
def get_roles():
    """获取所有角色信息的API"""
    try:
        return jsonify(ROLES)
    except Exception as e:
        print(f"Error in get_roles route: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/swap', methods=['POST'])
def swap():
    try:
        data = request.json
        source_image = data['image']
        gender = data['gender']
        role = data['role']
        
        if gender not in ROLES or role not in ROLES[gender]:
            return jsonify({'error': '无效的角色选择'}), 400
        
        target_path = os.path.join(os.path.dirname(__file__), ROLES[gender][role]['path'].lstrip('/'))
        
        result_base64 = swap_face(
            source_image,
            target_path,
            source_is_base64=True
        )
        
        return jsonify({
            'success': True,
            'image': f'data:image/jpeg;base64,{result_base64}'
        })
        
    except Exception as e:
        print(f"Error in swap route: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=1204) 
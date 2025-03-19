import cv2
import numpy as np
import insightface
from insightface.app import FaceAnalysis
import os
import base64

def image_to_base64(image):
    """将图片转换为base64字符串"""
    # 将图片编码成 jpg 格式的字节流
    _, buffer = cv2.imencode('.jpg', image)
    # 将字节流转换成base64字符串
    return base64.b64encode(buffer).decode('utf-8')

def base64_to_image(base64_string):
    """将base64字符串转换回图片"""
    # 解码base64字符串
    img_data = base64.b64decode(base64_string)
    # 将字节流转换成numpy数组
    nparr = np.frombuffer(img_data, np.uint8)
    # 解码图片
    return cv2.imdecode(nparr, cv2.IMREAD_COLOR)

def swap_face(source_img, target_img_path, model_path, source_is_base64=False):
    """修改后的换脸函数，支持base64输入"""
    # 初始化人脸检测器
    model_dir = '/data/xxtcode/ltz/faceswap_setup/models'
    os.environ['INSIGHTFACE_HOME'] = model_dir

    app = FaceAnalysis(name='buffalo_l', root=model_dir, providers=['CPUExecutionProvider'])
    app.prepare(ctx_id=0, det_size=(640, 640))
    
    # 加载换脸模型
    swapper = insightface.model_zoo.get_model(model_path)

    # 处理源图片（用户上传的图片）
    if source_is_base64:
        source = base64_to_image(source_img)
    else:
        source = cv2.imread(source_img)
    
    # 读取目标图片（角色图片）
    target = cv2.imread(target_img_path)
    
    if source is None:
        raise Exception("Could not load source image")
    if target is None:
        raise Exception(f"Could not load target image: {target_img_path}")

    # 检测人脸
    source_faces = app.get(source)
    if len(source_faces) == 0:
        raise Exception("No face found in source image")
    source_face = source_faces[0]
    
    target_faces = app.get(target)
    if len(target_faces) == 0:
        raise Exception("No face found in target image")
    target_face = target_faces[0]

    # 执行换脸
    result = swapper.get(target, target_face, source_face)
    
    # 将结果转换为base64
    return image_to_base64(result)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 4:
        print("Usage: python face_swap.py <source_image> <target_image> <output_image>")
        sys.exit(1)

    # 设置模型路径
    model_path = "/data/xxtcode/ltz/faceswap_setup/models/inswapper_128.onnx"
    
    try:
        result = swap_face(sys.argv[1], sys.argv[2], model_path)
        print(result)
    except Exception as e:
        print(f"Error: {str(e)}")
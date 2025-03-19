import cv2
import numpy as np
import insightface
from insightface.app import FaceAnalysis
import os

def swap_face(source_img_path, target_img_path, output_path, model_path):
    """简化版的换脸函数"""
    # 初始化人脸检测器
    model_dir = '/data/xxtcode/ltz/faceswap_setup/models'
    os.environ['INSIGHTFACE_HOME'] = model_dir

    app = FaceAnalysis(name='buffalo_l', root=model_dir, providers=['CPUExecutionProvider'])
    app.prepare(ctx_id=0, det_size=(640, 640))
    
    # 加载换脸模型
    swapper = insightface.model_zoo.get_model(model_path)

    # 读取图片
    source = cv2.imread(source_img_path)
    target = cv2.imread(target_img_path)
    
    if source is None:
        raise Exception(f"Could not load source image: {source_img_path}")
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
    
    # 保存结果
    cv2.imwrite(output_path, result)
    return "Face swap completed successfully!"

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 4:
        print("Usage: python face_swap.py <source_image> <target_image> <output_image>")
        sys.exit(1)

    # 设置模型路径
    model_path = "/data/xxtcode/ltz/faceswap_setup/models/inswapper_128.onnx"
    
    try:
        result = swap_face(sys.argv[1], sys.argv[2], sys.argv[3], model_path)
        print(result)
    except Exception as e:
        print(f"Error: {str(e)}")
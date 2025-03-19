# Face Swap 项目开发经验总结

## 关键技术点

1. 人脸检测参数调优
```python
app.prepare(ctx_id=0, 
           det_size=(640, 640),  # 检测尺寸
           det_thresh=0.3)       # 检测阈值
```
- 降低检测阈值可提高人脸检测成功率
- 适当的检测尺寸可平衡性能和准确度

2. 图片预处理
```python
# 调整图片尺寸
if source.shape[0] < 800:
    scale = max(800/source.shape[0], 800/source.shape[1])
    source = cv2.resize(source, None, fx=scale, fy=scale)

# 确保 BGR 格式
if len(source.shape) == 2:
    source = cv2.cvtColor(source, cv2.COLOR_GRAY2BGR)
```
- 统一图片尺寸很重要
- 注意图片格式转换

## 常见问题及解决方案

1. 未检测到人脸
- 原因：光线、角度、遮挡等
- 解决：调整 det_thresh 和 det_size
- 添加图片预处理步骤

2. 换脸结果发黑
- 原因：模型路径错误或图片格式问题
- 解决：检查模型加载，确保图片格式正确

3. 重复选择照片问题
```javascript
uploadBtn.addEventListener('click', function(e) {
    e.stopPropagation();
    fileInput.value = '';
    fileInput.click();
});
```
- 清空 input value 可重复选择同一文件
- 阻止事件冒泡避免重复触发

## 性能优化经验

1. 图片处理
- 限制图片尺寸范围（800x800 - 2000x2000）
- 使用适当的插值算法
- JPEG 压缩质量设置为 95%

2. 前端优化
- 添加加载状态提示
- 图片预览功能
- 禁用无效操作

## 项目结构建议

1. 模型文件管理
- 使用相对路径
- 统一放在 models 目录
- 注意模型版本兼容性

2. 静态资源
- 角色图片按性别分类
- 统一图片格式和尺寸
- 使用语义化命名

## 开发工具建议

1. 调试技巧
- 添加详细的日志输出
- 保存问题图片进行分析
- 使用浏览器开发工具检查网络请求

2. 版本控制
- 保存关键功能节点
- 记录参数调优过程
- 注意依赖版本兼容性

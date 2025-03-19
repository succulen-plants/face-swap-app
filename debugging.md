# Web 应用开发调试经验总结

## 1. 前端调试技巧

### 1.1 网络请求调试
```javascript
// 添加请求拦截器
async function fetchWithLogging(url, options) {
    console.log('Request:', url, options);
    try {
        const response = await fetch(url, options);
        const data = await response.json();
        console.log('Response:', data);
        return data;
    } catch (error) {
        console.error('Error:', error);
        throw error;
    }
}
```

### 1.2 文件上传问题
- 检查文件类型和大小限制
- 确保正确的 Content-Type
- 添加上传状态反馈
- 处理同文件重复上传

### 1.3 事件处理
```javascript
// 事件冒泡问题解决
element.addEventListener('click', function(e) {
    e.preventDefault();  // 阻止默认行为
    e.stopPropagation(); // 阻止冒泡
});

// 事件委托模式
parentElement.addEventListener('click', function(e) {
    if (e.target.matches('.target-class')) {
        // 处理逻辑
    }
});
```

## 2. 后端调试技巧

### 2.1 日志记录
```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='app.log'
)

def debug_wrapper(func):
    def wrapper(*args, **kwargs):
        logging.debug(f"Calling {func.__name__} with args: {args}, kwargs: {kwargs}")
        try:
            result = func(*args, **kwargs)
            logging.debug(f"Result: {result}")
            return result
        except Exception as e:
            logging.error(f"Error in {func.__name__}: {str(e)}")
            raise
    return wrapper
```

### 2.2 异常处理
```python
class CustomException(Exception):
    def __init__(self, message, code=None):
        self.message = message
        self.code = code
        super().__init__(self.message)

def safe_operation(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except CustomException as e:
            return {'error': e.message, 'code': e.code}, 400
        except Exception as e:
            return {'error': str(e)}, 500
    return wrapper
```

## 3. 图像处理调试

### 3.1 图像保存检查点
```python
def save_debug_image(image, stage_name):
    debug_dir = 'debug_images'
    os.makedirs(debug_dir, exist_ok=True)
    path = f"{debug_dir}/{stage_name}_{time.time()}.jpg"
    cv2.imwrite(path, image)
    return path
```

### 3.2 图像格式验证
```python
def validate_image(image_array):
    checks = {
        'shape': len(image_array.shape) == 3,
        'channels': image_array.shape[2] == 3,
        'dtype': image_array.dtype == np.uint8,
        'range': image_array.min() >= 0 and image_array.max() <= 255
    }
    return all(checks.values()), checks
```

## 4. API 调试工具

### 4.1 请求记录中间件
```python
from flask import request
import time

def request_logger():
    def decorator(f):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            response = f(*args, **kwargs)
            duration = time.time() - start_time
            
            log_data = {
                'method': request.method,
                'path': request.path,
                'duration': f"{duration:.2f}s",
                'status': response.status_code
            }
            print(f"API Call: {log_data}")
            return response
        return wrapper
    return decorator
```

## 5. 通用调试清单

### 5.1 环境检查
- 确认 Python 版本兼容性
- 验证所有依赖包版本
- 检查系统环境变量
- 确认文件权限设置

### 5.2 性能分析
```python
import cProfile
import pstats

def profile_function(func):
    def wrapper(*args, **kwargs):
        profiler = cProfile.Profile()
        result = profiler.runcall(func, *args, **kwargs)
        stats = pstats.Stats(profiler)
        stats.sort_stats('cumtime').print_stats(10)
        return result
    return wrapper
```

### 5.3 内存泄漏检测
```python
import tracemalloc

tracemalloc.start()
# 代码执行
snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics('lineno')
print("[ Top 10 memory users ]")
for stat in top_stats[:10]:
    print(stat)
```

## 6. 调试最佳实践

1. 分层调试
   - 先确认前端请求
   - 检查后端路由
   - 验证业务逻辑
   - 最后处理数据持久化

2. 错误处理
   - 提供有意义的错误信息
   - 记录详细的错误堆栈
   - 实现优雅的降级策略
   - 添加用户友好的错误提示

3. 性能优化
   - 使用性能分析工具
   - 实现缓存机制
   - 优化数据库查询
   - 减少不必要的计算

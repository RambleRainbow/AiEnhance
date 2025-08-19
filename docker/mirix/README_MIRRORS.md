# MIRIX Docker 镜像源配置指南

## 概述

为了在中国大陆地区获得更快的构建速度，此Dockerfile已配置使用中国镜像源。

## 当前配置

**默认使用阿里云镜像源**：
- Debian软件包源: `https://mirrors.aliyun.com/debian/`
- Python PyPI源: `https://mirrors.aliyun.com/pypi/simple/`

## 切换到清华大学镜像源

如果阿里云源出现问题或者想使用清华源，请按以下步骤操作：

### 1. 修改Debian源
将Dockerfile中第12-17行注释掉，然后取消第20-25行的注释：

```dockerfile
# 注释掉阿里云源
# RUN echo "deb https://mirrors.aliyun.com/debian/ bookworm main non-free non-free-firmware contrib" > /etc/apt/sources.list && \
#     echo "deb-src https://mirrors.aliyun.com/debian/ bookworm main non-free non-free-firmware contrib" >> /etc/apt/sources.list && \
#     ...

# 启用清华源
RUN echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian/ bookworm main contrib non-free non-free-firmware" > /etc/apt/sources.list && \
    echo "deb-src https://mirrors.tuna.tsinghua.edu.cn/debian/ bookworm main contrib non-free non-free-firmware" >> /etc/apt/sources.list && \
    ...
```

### 2. 修改PyPI源
将第28-29行注释掉，取消第32-33行的注释：

```dockerfile
# 注释掉阿里云PyPI源
# RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/ && \
#     pip config set install.trusted-host mirrors.aliyun.com

# 启用清华PyPI源
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/ && \
    pip config set install.trusted-host pypi.tuna.tsinghua.edu.cn
```

## 其他镜像源选项

### 中科大源
如果需要使用中科大源，可以替换为：

**Debian源**:
```
https://mirrors.ustc.edu.cn/debian/
```

**PyPI源**:
```
https://pypi.mirrors.ustc.edu.cn/simple/
```

### 华为云源
**Debian源**:
```
https://mirrors.huaweicloud.com/debian/
```

**PyPI源**:
```
https://mirrors.huaweicloud.com/repository/pypi/simple/
```

## 性能对比

一般来说：
- **阿里云**: 速度稳定，覆盖范围广
- **清华大学**: 教育网用户速度更快
- **中科大**: 部分地区速度较好
- **华为云**: 华为云用户可考虑

## 构建示例

使用修改后的Dockerfile构建镜像：

```bash
cd docker/mirix
docker build -t aienhance-mirix:latest .
```

## 故障排除

如果遇到镜像源问题：

1. **检查网络连接**: 确保能访问选择的镜像源
2. **尝试其他源**: 切换到备用镜像源
3. **清理Docker缓存**: `docker builder prune`
4. **重新构建**: `docker build --no-cache -t aienhance-mirix:latest .`

## 注意事项

- 修改镜像源后，建议重新构建Docker镜像以确保使用新的配置
- 不同镜像源的软件包版本可能略有差异，但通常不会影响功能
- 如果在海外环境部署，建议恢复使用官方源以获得最佳兼容性
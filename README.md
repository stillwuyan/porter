### 介绍
基于`reactpy`和`fastapi`构建web服务，用于在手机和PC间传输文件

### 使用方法
1. 安装依赖包
   ```
   pip install reactpy[fastapi]
   pip install qrcode
   pip install python-multipart
   ```
2. 启动服务
   ```
   uvicorn web:app
   ```
3. 打开浏览器访问`http://127.0.0.1:8000`

### 功能列表
   - [ ] 上传文件
   - [ ] 下载文件
   - [ ] 二维码分享
   - [ ] 支持pyenv
   - [ ] 支持peotry



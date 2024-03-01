# icp_query

基于 https://github.com/HG-ha/ICP_Query 二次开发

环境安装：
   pip install -r requirements.txt

运行：
   python icpApi.py

替换模型：
   1. 目标检测模型
      model_data/best.onnx
   2. 孪生识别网络
      model_data/best_epoch_weights.pth

修改运行端口：
   文件 icpApi.py 第124行

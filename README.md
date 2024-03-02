# icp_query

基于 https://github.com/HG-ha/ICP_Query 二次开发

## 修改内容

- [x] 对脚本改造支持自动翻页获取全部数据 
- [x] 自动化验证、token，优化速度 
- [ ] 支持本地ipv6换ip（开发ing）
- [ ] 支持使用代理池

## 查询
1. 支持四种类型查询：
- 网站：web
- APP：app
- 小程序：mapp
- 快应用：kapp


## 替换模型
   1. 目标检测模型
      model_data/best.onnx
   2. 孪生识别网络
      model_data/best_epoch_weights.pth


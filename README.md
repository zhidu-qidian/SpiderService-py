# [SpiderService](http://git.deeporiginalx.com/spiders/SpiderService/blob/master/API.md) Python迁移版本


## 重要说明：

一切功能、接口说明，请看同名的Golang工程（去掉-py）。该工程只是为了做原Golang版本的迁移备份，以适应新的需求添加（写Go的同事离职，大家对Golang都不怎么熟），
在无新需求的情况下，尽量使用Golang版本的，如果对Golang熟悉也请使用Golang版本的
对于硬接口类型的，Golang相对Python更为稳定


## 目标：维持原Golang版本的HTTP API接口不变，完成完全等同的服务  

## 进度：

+ `完成` Step1：利用tornado搭建Api工程目录组建，初始化各接口 
+ `完成` Step2：实现辅助功能函数 
    + oss上传图片和删除图片函数 
    + pg操作函数 
    + ……
+ `完成` Step3：利用MKDocs实现自动生成HTTP API文档
+ `完成` Step4：对照各数据模型翻译成Python版本 
+ Step5：实现各接口逻辑功能：
    + `完成` /api/update/news
    + `完成` /api/store/comment 
    + `完成` /api/store/video
    + `完成` /api/store/joke
    + `完成` /api/store/news
+ Step6：测试
+ Step7：注释代码（以便自动生成API文档）
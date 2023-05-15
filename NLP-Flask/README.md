# NLP-Flask

<img width="690" alt="image" src="https://user-images.githubusercontent.com/38573173/202845959-c0f4048f-767d-4aab-b5e8-3e7571bd5493.png">

## 基本情况  
语言： Python （开发时使用3.10.8，仅供参考）  

基于 Flask、LTP

另附带百度百科页面超链接获取，并爬取百科页面顶端基本信息的爬虫

新增解析知网导出题录

## 模型
哈工大 Base2模型与Legacy模型  

[模型获取 Base2](https://huggingface.co/LTP/base2)  

[模型获取 Legacy](https://huggingface.co/LTP/legacy)  

等等

目录结构： 
![image](https://user-images.githubusercontent.com/38573173/202848279-f50e3c9c-59f6-4fd6-b8c0-226caa106211.png)

## 三元组
算法来源：https://github.com/liuhuanyong/EventTriplesExtraction

已做出较大修改，适合项目，并且使用CUDA加速

百度 DD Parser在CUDA11.7 paddlepaddle2.3.2存在问题，无法使用

## 关键词提取
基于jieba库

默认开启paddle，paddle版本大于2.0

## 端口
默认 8848 

host为 0.0.0.0

## 使用

`set_up.py` 安装所需库

`server.py` 运行服务

浏览器打开 `localhost:8848`即可

若需要局域访问以调试，请在防火墙中手动添加`8848端口`

## 输入
自己指定文件夹目录

## 输出
output文件夹内

## 其它
发现问题，您可以在Issues里告诉我，我有空会fix

## 相关文献

> @article{che2020n,
>   title={N-LTP: A Open-source Neural Chinese Language Technology Platform with Pretrained Models},
>   author={Che, Wanxiang and Feng, Yunlong and Qin, Libo and Liu, Ting},
>   journal={arXiv preprint arXiv:2009.11616},
>   year={2020}
> }

> @misc{zhang2020practical,
>     title={A Practical Chinese Dependency Parser Based on A Large-scale Dataset},
>     author={Shuai Zhang and Lijie Wang and Ke Sun and Xinyan Xiao},
>     year={2020},
>     eprint={2009.00901},
>     archivePrefix={arXiv},
>     primaryClass={cs.CL}
> }


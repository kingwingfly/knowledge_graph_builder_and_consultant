# 说明

## NLP Flask

用于快速调用LTP等工具，进行分词、语义、三元组抽取等操作。

运行`set_up.py`配置环境

为了节省空间，就不打包在本文件中了

## spider

`pip install httpx`安装依赖。

一个实现协程的百度百科爬虫。

其中：

- `depth` 递归的深度，比如 词条A中，有B的超链接，B中有C的超链接，若爬取到C，则深度为3，只爬取B，深度为2，只爬取A，深度为1；
- `batch_size` 每批次爬取的词条数目；
- `halt` 两个批次间的暂停时间；

推荐``depth`设置为3 `batch_size`为16 halt为2

## cnki_parser

用于解析从CNKI上下载的文献信息。

输入：

![image](https://user-images.githubusercontent.com/38573173/205143287-5029fe18-5b2a-452f-ba26-0007627c2b04.png)

输出json文件：

![image](https://user-images.githubusercontent.com/38573173/205143436-880a3fc2-9eac-4cee-8853-bfb51be2fcd2.png)

## cooperation_analyse

输入上一部分输出的json文件。

输出包含作者合作关系的json文件：  {Author: [Authors]···}

## info_extension

信息扩展。

第一步，将cnki.json中的所有键全部转化为百度百科链接

第二步，从百度百科爬取所有信息，并保存

## neo4j_builder

`pip install py2neo`安装依赖

`neo4j console`运行neo4j

修改`neo4j_builder.py`中的登陆密码

输入info_extension得到的所有json以及cnki.json

运行

## inquire_sys

问答系统

`pip install pyahocorasick`安装依赖

运行`app.py`

打开`localhost:8848`即可

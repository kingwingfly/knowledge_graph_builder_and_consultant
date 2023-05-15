# 说明

本项目使用了较多新版本python的特性，如海象等式、类型标注等等，故需要较高python版本

推荐`3.10.8`

## NLP Flask

用于快速调用LTP等工具，进行分词、语义、三元组抽取等操作。

运行`set_up.py`配置环境

模型请到[哈工大](https://ltp.ai)的网站或[hugging-face](https://huggingface.co)自行下载。

![image](https://user-images.githubusercontent.com/38573173/202845959-c0f4048f-767d-4aab-b5e8-3e7571bd5493.png)

## spider

应该叫crawler，但是懒得改了

`pip install httpx`安装依赖。

一个实现协程的百度百科爬虫。

其中：

- `depth` 递归的深度，比如 词条A中，有B的超链接，B中有C的超链接，若爬取到C，则深度为3，只爬取B，深度为2，只爬取A，深度为1；
- `batch_size` 每批次爬取的词条数目；
- `halt` 两个批次间的暂停时间；

推荐`depth`设置为3 `batch_size`为16 halt为2

![image](https://user-images.githubusercontent.com/38573173/205223715-281e3688-0d5d-4d18-b5a5-87c95a2d6cbb.png)

## cnki_parser

用于解析从CNKI上下载的文献信息。

输入：

![image](https://user-images.githubusercontent.com/38573173/205143287-5029fe18-5b2a-452f-ba26-0007627c2b04.png)

输出json文件：

![image](https://user-images.githubusercontent.com/38573173/205143436-880a3fc2-9eac-4cee-8853-bfb51be2fcd2.png)

## cooperation_analyse

输入上一部分输出的json文件。

输出包含作者合作关系的json文件：   {Author: [Article, [Authors]]···}

![image](https://user-images.githubusercontent.com/38573173/205224085-b78052b6-25d4-4694-a43c-115ca1b710c7.png)

## info_extension

信息扩展。

第一步，将cnki.json中的所有键全部转化为百度百科链接

第二步，从百度百科爬取所有信息，并保存

![image](https://user-images.githubusercontent.com/38573173/205224640-4334e8cc-b352-4652-8874-ad5d7f217e0b.png)

![image](https://user-images.githubusercontent.com/38573173/205224722-b2c09c5c-42d1-44b6-8082-70d8eb419ae8.png)

## neo4j_builder

`pip install py2neo`安装依赖

`neo4j console`运行neo4j

修改`neo4j_builder.py`中的登陆密码

将info_extension得到的所有json以及cnki.json放入`input`

运行

![image](https://user-images.githubusercontent.com/38573173/205223052-6d22b0d2-c014-4630-bcec-ad3e1418496c.png)

## inquire_sys

问答系统

`pip install pyahocorasick`安装依赖

运行`app.py`

打开`localhost:8848`即可

![image](https://user-images.githubusercontent.com/38573173/205223380-c25d6e89-fcb1-4a42-b23c-2df5f4df2b43.png)

询问`数字孪生的全部信息`，结果如下（部分）：

![image](https://user-images.githubusercontent.com/38573173/205224432-6e827684-66f1-42f9-97ce-66b848e2e910.png)


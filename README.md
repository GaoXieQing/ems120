# ems120

### Introduction
ems120是基于深圳市急救数据开发的用于急救数据分类与地理编码的工具，包括ems-dx与ems-map。
### Getting Started:
1）电脑需安装python3.11，下载项目本地，并从终端或命令行进入该文件夹路径。可通过以下代码实现：
> `git clone https://github.com/GaoXieQing/ems120` \
> `cd ems120`

2）安装requirements.txt中的工具包，可以通过以下代码实现：
> `pip install -r requirements.txt`

如果出现安装失败，可以使用conda创建新的虚拟环境，通过以下代码实现：
> `conda create -n ems120 python=3.11`\
> `conda activate ems120`\
> `pip install -r requirements.txt`

### Attention
1) 该项目不包含疾病分类训练的权重文件，可[从此获取](https://pan.baidu.com/s/1Awxmz9282IK-Da1d3Vw2Zg)（提取码: 54xt）。当然也可以根据自己的数据集进行训练，方法可在[Wiki](https://github.com/GaoXieQing/ems120/wiki)中找到。\
2) Macbert预训练模型的pytorch_model.bin需[从此](https://huggingface.co/hfl/chinese-macbert-base/tree/main)下载放入`hfl/chinese-macbert-base/`的路径中。\
3) 在处理数据前注意，原始数据可能存在列名重复的情况，需要修改重复列名，地理编码的地址字段名需设置为 '现场地址'。
    

### Support
[Wiki](https://github.com/GaoXieQing/ems120/wiki)中包括了ems-dx与ems-map的使用方法。


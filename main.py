import pandas as pd
import requests
import math
from sympy.codegen.ast import continue_
from scripts.classify_disease import classify_disease
'''import geopandas as gpd
from shapely.geometry import Point
'''
#################################定义函数################################################################################

#######1.去掉无效记录
def clean(df):
    len1 = len(df.index)
    df=df[df['呼救类型'].isin(['疫情', '疫苗', '突发事件', '患者转院', '救治', '外院社康', '发热', '院内转院', '本院社康','市内转运(非急救)','传染病','转隔离点','一般公共事件', '中心用车','市外转运(非急救)'])]
    df.dropna(axis=0, subset=["接车地点", "驶向现场时刻", "主诉"], how='any', inplace=True)
    df = df[~df.到达医院时刻.isnull()]
    df = df[df['是否正常结束']=='是']
    len2 = len(df.index)
    print('删除了' + str(len1 - len2) + '行无效记录')

    return df

#######2.添加时间差、手机号码分类、经纬度信息、地址类型、街道分类、疾病类型

# 添加时间差
def add_time(df):
    df['开始受理时刻'] = pd.to_datetime(df['开始受理时刻'])
    df['驶向现场时刻'] = pd.to_datetime(df['驶向现场时刻'])
    df['到达现场时刻'] = pd.to_datetime(df['到达现场时刻'])
    df['病人上车时刻'] = pd.to_datetime(df['病人上车时刻'])
    df['到达医院时刻'] = pd.to_datetime(df['到达医院时刻'])

    df['受理调度时间'] = (df['驶向现场时刻'] - df['开始受理时刻']).dt.seconds
    df['去程在途时间'] = (df['到达现场时刻'] - df['驶向现场时刻']).dt.seconds
    df['现场停车时间'] = (df['病人上车时刻'] - df['到达现场时刻']).dt.seconds
    df['返程在途时间'] = (df['到达医院时刻'] - df['病人上车时刻']).dt.seconds
    df['急救反应时间'] = df['受理调度时间'] + df['去程在途时间'] + df['现场停车时间'] + df['返程在途时间']

    return df

# 电话评分函数
def phone_scoring(phone):
    phone = phone[3:]
    n_4 = phone.count('4')
    n_6 = phone.count('6')
    n_8 = phone.count('8')
    n_9 = phone.count('9')
    if n_4 > 0:
        score = 0
    else:
        score = n_8 + n_9 + n_6 * 0.5

    return score

# 添加电话分数
def add_phone_score(df):
    df['phone_score'] = df['联系电话'].apply(lambda x: phone_scoring(str(x)))

    return df

# 地理编码
def encoding(address, key):
    # 接口地址
    url = "https://api.map.baidu.com/geocoding/v3"

    # 此处填写你在控制台-应用管理-创建应用后获取的AK
    params = {
        "address": address,
        "output": "json",
        # "ak": 'LStGBcsVME878p02fAeR2Vb35bafmadT',
        # "ak": 'CHR2n9IhRvSLh3j7tUoqRzKywywVijo3',
        "ak": key,
        "city": "深圳市"

    }

    response = requests.get(url=url, params=params)
    if response:
        return response.json()
    else:
        print('地址', address, '  地理编码失败')

# 坐标系转换
x_pi = 3.14159265358979324 * 3000.0 / 180.0
pi = 3.1415926535897932384626  # π
a = 6378245.0  # 长半轴
ee = 0.00669342162296594323  # 扁率

def gcj02towgs84(lng, lat):
    """
    GCJ02(火星坐标系)转GPS84
    :param lng:火星坐标系的经度
    :param lat:火星坐标系纬度
    :return:
    """
    dlat = transformlat(lng - 105.0, lat - 35.0)
    dlng = transformlng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * pi
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
    dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)
    mglat = lat + dlat
    mglng = lng + dlng
    return [lng * 2 - mglng, lat * 2 - mglat]

def transformlat(lng, lat):
    ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + \
          0.1 * lng * lat + 0.2 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
            math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lat * pi) + 40.0 *
            math.sin(lat / 3.0 * pi)) * 2.0 / 3.0
    ret += (160.0 * math.sin(lat / 12.0 * pi) + 320 *
            math.sin(lat * pi / 30.0)) * 2.0 / 3.0
    return ret

def transformlng(lng, lat):
    ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + \
          0.1 * lng * lat + 0.1 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
            math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lng * pi) + 40.0 *
            math.sin(lng / 3.0 * pi)) * 2.0 / 3.0
    ret += (150.0 * math.sin(lng / 12.0 * pi) + 300.0 *
            math.sin(lng / 30.0 * pi)) * 2.0 / 3.0
    return ret

# 添加经纬度，地址类型
def add_xy(df):
    print('还有' + str(len(df[df['接车地址纬度'] == 0])) + '条记录待添加经纬度')
    key = input('请输入您的百度地图API密钥:')
    for i in df.index:
        if df.loc[i, '接车地址纬度'] == 0:
            # print(i)
            xy_info = encoding(df.loc[i, '现场地址'], key)
            if xy_info['status'] == 0:
                lng, lat = gcj02towgs84(xy_info['result']['location']['lng'], xy_info['result']['location']['lat'])
                df.loc[i, '接车地址纬度'] = lat
                df.loc[i, '接车地址经度'] = lng
                df.loc[i, '地址类型'] = xy_info['result']['level']

            elif xy_info['status'] == 2 or xy_info['status'] == 1:
                # print("跳过")
                continue
            else:
                print('已达到限额，请切换密钥或明日继续')
                break

    if len(df[df['接车地址经度'] == 0]) == 0:
        print('已完成经纬度与地址类型添加')

    return df

'''# 街道分类
def get_street(lat, lon, gdf):
    point = Point(lon, lat)
    contains = gdf.contains(point)
    if contains.any():
        matching_street = gdf[contains].iloc[0]['XZJD']
        return matching_street
    else:
        return 'none'


# 添加街道
def add_street(df):
    gdf = gpd.read_file('/Users/gxq/WorkSpace/Database/地图数据_广东深圳/深圳市乡镇街道边界/深圳市乡镇街道边界.shp')
    for i in df.index:
        df.loc[i, '所属街道'] = get_street(df.loc[i, '接车地址纬度'], df.loc[i, '接车地址经度'], gdf)

    return df
'''



#############################################主函数######################################################################
if __name__ == "__main__":

    # 输入需要处理的数据路径，适用于2020年后的数据
    filepath = input('请输入需要QC的数据路径:')
    outputpath = input('请输入输出文件夹路径:')

    # 读取数据，原始数据前四行可能为数据介绍需要跳过
    try:
        df = pd.read_excel(filepath)
    except:
        df = pd.read_excel(filepath, skiprows=4)

    #备份原始文件
    if ('受理调度时间' not in df.columns) and ('phone_score' not in df.columns):
        df.to_excel(outputpath + '/origin_' + filepath.split('/')[-1])



    # 去掉无效记录
    if df[df.到达医院时刻.isnull()].size==0:
        print('已去除过无效记录')
    else:
        print('开始去掉无效记录')
        df = clean(df)
        print('完成去掉无效记录')

    #添加时间差
    if '受理调度时间' in df.columns:
        print('数据已添加时间差')
    else:
        print('开始添加时间差')
        try:
            df = add_time(df)
        except:
            continue_
        print('完成时间差添加')


    # 添加手机号分数
    if 'phone_score' in df.columns:
        print('数据已包含手机号评分')
    else:
        print('开始手机号评分')
        df = add_phone_score(df)
        print('完成手机号评分')

    # 添加疾病分类
    if '疾病分类' in df.columns:
        print('数据已包含疾病分类')
    else:
        print('开始疾病分类')
        df = classify_disease(df)
        print('完成疾病分类')
        df.to_excel(filepath)



    # 添加经纬度与地址类型
    if '接车地址经度' not in df.columns:
        print('开始添加经纬度与地址类型')
        df['接车地址经度'] = 0
        df['接车地址纬度'] = 0
        df = add_xy(df)
        df.to_excel(filepath)

    else:
        if len(df[df['接车地址经度'] == 0]) == 0:
            print('数据已包含经纬度与地址类型')
        else:
            print('继续添加经纬度与地址类型')
            df = add_xy(df)

    ''''# 保存过程数据
    df.to_excel(filepath)
    # 添加街道分类
    if '所属街道' in df.columns:
        print('数据已包含所属街道')
    else:
        if len(df[df['接车地址经度'] == 0]) == 0:
            print('开始进行街道分类')
            df = add_street(df)
            print('完成街道分类')
        else:
            print("请先完成经纬度添加再进行街道分类")'''

    df.to_excel(outputpath + '/processed_' + filepath.split('/')[-1])
    print('完成数据QC')

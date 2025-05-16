config={
    '数据路径':'test.xlsx',
    '输出文件夹路径':'output',
    '模型路径':'../hfl/chinese-macbert-base', #填写chinese-macbert-base所在路径
    '权重路径':'../hfl/trained_model.pth', #填写训练后的权重数据
    '训练集路径':'dataset.xlsx', #如果需要使用自己数据训练，可以填写训练集数据的路径（需要包括text，label1，label2字段）
    '训练后的权重路径': 'output', #如果需要使用自己数据训练，需要填写训练后的权重输出路径
    '高德密钥':['key1','key2'] #填写自己的高德密钥，密钥数可由自己决定

}
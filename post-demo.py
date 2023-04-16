# -*- coding: utf-8 -*-
"""
@author: lywen
后台通过接口调用服务，获取OCR识别结果
"""
import base64
import os
import requests
import json
import fitz
import re
def read_img_base64(p):
    with open(p,'rb') as f:
        imgString = base64.b64encode(f.read())
    imgString=b'data:image/jpeg;base64,'+imgString
    return imgString.decode()

def post(p,billModel):
    URL='http://127.0.0.1:8089/ocr'##url地址
    imgString = read_img_base64(p)
    headers = {}
    param = {'billModel':billModel,##目前支持三种 通用OCR/ 火车票/ 身份证/
                  'imgString':imgString,
                      'textAngle':True
    }
    param = json.dumps(param)
    if 1:
            req          =  requests.post(URL,data= param,headers=None,timeout=50)
            data         =  req.content.decode('utf-8')
            data         =  json.loads(data)
    else:
            data =[]
    return data

def process_pdf(file_name):
    origin_name = file_name
    #  打开PDF文件，生成一个对象
    doc = fitz.open("images/" + file_name)
    name = file_name.split(".")[0]
    result = []
    for pg in range(doc.pageCount):
        file_name = name + str(pg)
        page = doc[pg]
        rotate = int(0)
        # 每个尺寸的缩放系数为2，这将为我们生成分辨率提高四倍的图像。
        zoom_x = 2.0
        zoom_y = 2.0
        trans = fitz.Matrix(zoom_x, zoom_y).prerotate(rotate)

        pm = page.get_pixmap(matrix=trans, alpha=False)
        pm.save('images/%s.png' % file_name)
        data = post('images/%s.png' % file_name,'General_OCR')
        list = data['res']
        for e in list:
             
             if e['name'] == '2':
                result_line = str(e['text'])
                print (result_line)
                a = result_line.index('单号')
                b = result_line.index('计量')
                
                file_number = result_line[int(a)+3:int(b)-1].replace('开','#')
                # print(file_number)
                # print('copy ' + "images/" + origin_name + ' result_folder/'+ file_number + '.pdf')
                open('result_folder/'+ file_number + '.pdf', 'wb').write(open("images/" + origin_name, 'rb').read())
        os.remove('images/%s.png' % file_name)
        
    #     invoices = process_image(file_name_curr)
    #     result.extend(invoices)
    # return result


    
if __name__=='__main__':
    for file in os.listdir('images'):
        print(file)
        process_pdf(file)

    # p = 'test/2022033100160.png'
    # data = post(p,'General_OCR')

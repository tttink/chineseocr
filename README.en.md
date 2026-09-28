[简体中文](README.md) | English

## !!!Forked from https://github.com/chineseocr/chineseocr
## Thanks to the original author
---

## This project implements Chinese text detection and recognition in natural scenes, based on [yolo3](https://github.com/pjreddie/darknet.git) and [crnn](https://github.com/meijieru/crnn.pytorch.git)

### Optimized darknet version: https://github.com/chineseocr/darknet-ocr.git
# Training code (master branch)

# OCR training dataset
OCR CTC training dataset (archive password: chineseocr)  
Baidu Netdisk link: https://pan.baidu.com/s/1UcUKUUELLwdM29zfbztzdw extraction code: atwn  
gofile link: http://gofile.me/4Nlqh/uT32hAjbx password: https://github.com/chineseocr/chineseocr

# Features
- [x] Text orientation detection: 0, 90, 180 and 270 degrees (supports dnn/tensorflow)
- [x] Text detection with darknet/opencv dnn/keras; training with darknet/keras
- [x] Variable-length OCR training (English, and mixed Chinese/English); crnn/dense OCR recognition and training; added code to convert PyTorch models to Keras (tools/pytorch_to_keras.py)
- [x] Model conversion: darknet to Keras, Keras to darknet, PyTorch to Keras
- [x] Structured data recognition for ID cards / train tickets
- [x] Added a CNN+CTC model; OCR can run on the OpenCV DNN module, averaging under 0.02 s per single-line image
- [ ] Speed up the CPU version
- [ ] OCR recognition based on a user dictionary
- [ ] Add a language model to correct OCR results
- [ ] Real-time recognition on Raspberry Pi


## Environment setup

GPU deployment: see setup.en.md  
CPU deployment: see setup-cpu.en.md


### Download and build darknet (you can skip building darknet if you use opencv dnn or keras yolo3 directly)
```
git clone https://github.com/pjreddie/darknet.git
mv darknet chineseocr/
## To build with GPU and cuDNN support, edit the Makefile
#GPU=1
#CUDNN=1
#OPENCV=0
#OPENMP=0
make
```

Edit line 48 of darknet/python/darknet.py  
root = '/root/'## the directory that contains chineseocr  
lib = CDLL(root+"chineseocr/darknet/libdarknet.so", RTLD_GLOBAL)


## Download model files
Model file links:
* Baidu Netdisk: https://pan.baidu.com/s/1gTW9gwJR6hlwTuyB6nCkzQ  
other-links: http://gofile.me/4Nlqh/fNHlWzVWo  
Copy all the files in the folder into the models directory

## Model conversion (optional)
PyTorch OCR to Keras OCR
``` Bash
python tools/pytorch_to_keras.py  -weights_path models/ocr-dense.pth -output_path models/ocr-dense-keras.h5
```
darknet to Keras
``` Bash
python tools/darknet_to_keras.py -cfg_path models/text.cfg -weights_path models/text.weights -output_path models/text.h5
```
Keras to darknet
``` Bash
python tools/keras_to_darknet.py -cfg_path models/text.cfg -weights_path models/text.h5 -output_path models/text.weights
```

## Model selection
``` Bash
See config.py
```

## Build the Docker image
``` Bash
## Download the Anaconda3 Python installer (https://repo.anaconda.com/archive/Anaconda3-2019.03-Linux-x86_64.sh) and put it in the chineseocr directory
## Build the image
docker build -t chineseocr .
## Start the service
docker run -d -p 8080:8080 chineseocr /root/anaconda3/bin/python app.py

```

## Start the web service
``` Bash
cd chineseocr ## enter the chineseocr directory
python app.py 8080 ## 8080 is the port number; you can use any port
```

## Access the service
http://127.0.0.1:8080/ocr

<img width="500" height="300" src="https://github.com/chineseocr/chineseocr/blob/master/test/demo.png"/>



## Recognition results

<img width="500" height="300" src="https://github.com/chineseocr/chineseocr/blob/master/test/train-demo.png"/>
<img width="500" height="300" src="https://github.com/chineseocr/chineseocr/blob/master/test/idcard-demo.png"/>
<img width="500" height="300" src="https://github.com/chineseocr/chineseocr/blob/master/test/img-demo.png"/>
<img width="500" height="300" src="https://github.com/chineseocr/chineseocr/blob/master/test/line-demo.png"/>



## References
1. yolo3 https://github.com/pjreddie/darknet.git
2. crnn  https://github.com/meijieru/crnn.pytorch.git
3. ctpn  https://github.com/eragonruan/text-detection-ctpn
4. CTPN  https://github.com/tianzhi0549/CTPN
5. keras yolo3 https://github.com/qqwweee/keras-yolo3.git
6. darknet/keras model conversion reference: https://www.cnblogs.com/shouhuxianjian/p/10567201.html
7. Language model implementation https://github.com/lukhy/masr

##CPU environment setup, supports Linux/macOS
conda create -n chineseocr python=3.6 pip scipy numpy jupyter ipython ##create a Python environment with conda
source activate chineseocr
cd darknet/ && make && cd ..
pip install easydict opencv-contrib-python==4.0.0.21 Cython h5py lmdb mahotas pandas requests bs4 matplotlib lxml -i https://pypi.tuna.tsinghua.edu.cn/simple/
pip install -U pillow -i https://pypi.tuna.tsinghua.edu.cn/simple/
pip install web.py==0.40.dev0 redis
pip install keras==2.1.5 tensorflow==1.8
## mac
conda install pytorch torchvision -c pytorch
## linux
## conda install pytorch-cpu torchvision-cpu -c pytorch


import cv2
import numpy as np
from PIL import Image
import requests
from io import BytesIO
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as mp
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import tkinter as tk
# import tkinter.messagebox
from tkinter import ttk
import urllib.request
import re
import webbrowser as web
import warnings

def getImageByUrl(url):
    # 根据图片url 获取图片对象
    html = requests.get(url, verify=False)
    image = Image.open(BytesIO(html.content))
    return image

class object_search:
    def search_onWeb(self, keyname):
        # 搜索相似图像
        self.imgurl = []
        self.weburl = []
        key = urllib.request.quote(keyname)
        page = 1
        while page < self.max_page + 1:
            self.url = "https://search.jd.com/Search?keyword=" + key + "&page=" + str(page)
            self.data = urllib.request.urlopen(self.url).read().decode("utf-8","ignore")
            print('第' + str(page) + '页data的长度为:' + str(len(self.data)))
            self.imagelist = re.compile(self.pat).findall(self.data)
            print('第' + str(page) + '页imagelist的长度为:' + str(len(self.imagelist)))
            if(len(self.imagelist) == 0):# 重复搜索
                page = page
            else:
                for j in range(0,len(self.imagelist)):
                    img = self.imagelist[j]
                    httpimg = "https://" + img
                    self.get_img2(httpimg)
                    self.compare()
                    if(self.diff_a < self.Threshold and self.diff_d < self.Threshold):
                        self.imgurl.append(httpimg)
                        web_pat = "href=\"//(\S+)\"\s+.*\D+.*" + img
                        web = re.compile(web_pat).findall(self.data)
                        web = "https://" + web[0]
                        self.weburl.append(web)
                page = page + 1
        comboxlist["values"] = (self.weburl)
        app_state.set('状态: 完成')
        '''
        file = "jingdong/" + str(j) + ".jpg"
        urllib.request.urlretrieve(httpimg, filename = file)
        '''

    def ad_Hash(self):
        # 哈希算法计算特征直方图
        self.img1_pro = cv2.resize(self.img1, (8, 8))
        gray = cv2.cvtColor(self.img1_pro, cv2.COLOR_BGR2GRAY)
        s = 0
        self.hash_str_1_a = ''
        for i in range(8):
            for j in range(8):
                s = s + gray[i, j]
        avg = int(s / 64)
        for i in range(8):
            for j in range(8):
                if gray[i, j] > avg:
                    self.hash_str_1_a = self.hash_str_1_a + '1'
                else:
                    self.hash_str_1_a = self.hash_str_1_a + '0'

        self.hash_str_1_d = ''
        for i in range(8):
            for j in range(8):
                if j + 1 < 8:
                    if gray[i, j] > gray[i, j + 1]:
                        self.hash_str_1_d = self.hash_str_1_d + '1'
                    else:
                        self.hash_str_1_d = self.hash_str_1_d + '0'
                elif i < 7:
                    if gray[i, j] > gray[i + 1, 0]:
                        self.hash_str_1_d = self.hash_str_1_d + '1'
                    else:
                        self.hash_str_1_d = self.hash_str_1_d + '0'
                else:
                    if gray[i, j] > gray[0, 0]:
                        self.hash_str_1_d = self.hash_str_1_d + '1'
                    else:
                        self.hash_str_1_d = self.hash_str_1_d + '0'

        self.img2_pro = cv2.resize(self.img2, (8, 8))
        gray = cv2.cvtColor(self.img2_pro, cv2.COLOR_BGR2GRAY)
        s = 0
        self.hash_str_2_a = ''
        for i in range(8):
            for j in range(8):
                s = s + gray[i, j]
        avg = int(s / 64)
        for i in range(8):
            for j in range(8):
                if gray[i, j] > avg:
                    self.hash_str_2_a = self.hash_str_2_a + '1'
                else:
                    self.hash_str_2_a = self.hash_str_2_a + '0'

        self.hash_str_2_d = ''
        for i in range(8):
            for j in range(8):
                if j + 1 < 8:
                    if gray[i, j] > gray[i, j + 1]:
                        self.hash_str_2_d = self.hash_str_2_d + '1'
                    else:
                        self.hash_str_2_d = self.hash_str_2_d + '0'
                elif i < 7:
                    if gray[i, j] > gray[i + 1, 0]:
                        self.hash_str_2_d = self.hash_str_2_d + '1'
                    else:
                        self.hash_str_2_d = self.hash_str_2_d + '0'
                else:
                    if gray[i, j] > gray[0, 0]:
                        self.hash_str_2_d = self.hash_str_2_d + '1'
                    else:
                        self.hash_str_2_d = self.hash_str_2_d + '0'

    def compare(self):
        # 将特征直方图相比较，计算相似度
        self.ad_Hash()
        self.diff_a = 0
        self.diff_d = 0
        for i in range(64):
            if self.hash_str_1_a[i] != self.hash_str_2_a[i]:
                self.diff_a = self.diff_a + 1
            if self.hash_str_1_d[i] != self.hash_str_2_d[i]:
                self.diff_d = self.diff_d + 1
        print('均值哈希算法相似度:'+ str(self.diff_a))
        print('差值哈希算法相似度:'+ str(self.diff_d))

    def get_img1(self, path1):
        self.img1 = cv2.imread(path1)

    def get_img2(self, path2):
        self.img2 = getImageByUrl(path2)
        self.img2 = cv2.cvtColor(np.asarray(self.img2), cv2.COLOR_RGB2BGR)

    def __init__(self):
        # self.pat = "data-img=\"1\" src=\"//(img\S+jpg)"
        # self.pat = "img width=\"220\" height=\"220\" data-img=\S+\D+(img\S+jpg)"
        self.pat = "img width=\"220\" height=\"220\" data-img=\"1\" \S+//(img\S+jpg)"
        self.max_page = 10
        self.Threshold = 20
        self.img1 = 0
        self.img2 = 0
        self.imgurl = []
        self.weburl = []

    def show_img(self, key):
        if key == 1:
            mp.figure(1)
            mp.clf()
            mp.imshow(Image.fromarray(cv2.cvtColor(my_search.img1, cv2.COLOR_BGR2RGB)))
            mp.subplots_adjust(top=1, bottom=0, left=0, right=1, hspace=0, wspace=0)
            mp.axis('off')
            imgbox1.draw()
        else:
            mp.figure(2)
            mp.clf()
            mp.imshow(Image.fromarray(cv2.cvtColor(my_search.img2, cv2.COLOR_BGR2RGB)))
            mp.subplots_adjust(top=1, bottom=0, left=0, right=1, hspace=0, wspace=0)
            mp.axis('off')
            imgbox2.draw()

def openfile_dialog():# 打开文件对话框并选择图片
    global my_img, initialgray_matrix
    root_picture = tk.filedialog.askopenfilename(title = 'please select one .jpg picture',
                                               filetypes = [('picture files','.jpg')])
    my_search.get_img1(root_picture)
    my_search.show_img(1)
    app_state.set('状态: 忙碌')

my_search = object_search()

def choose_web(*args):# 下拉列表选择函数
    my_search.get_img2(my_search.imgurl[comboxlist.current()])
    my_search.show_img(2)

def choose_page(*args):
    my_search.max_page = int(comboxlist1.get())

def set_Threshold(Text):# 设定哈希算法阈值
    my_search.Threshold = int(Text)

def OpenWeb():# 通过网址打开网页
    web.open(comboxlist.get())

def gui_init():
    global imgbox1, imgbox2, comboxlist, comboxlist1, app_state
    root_window = tk.Tk()
    root_window.title('图像目标检索')
    root_window.resizable(0, 0)
    root_window.geometry('512x434')

    originImg_lab = tk.Label(root_window, text = '原始图像')
    originImg_lab.place(x = 100, y = 10)

    searchImg_lab = tk.Label(root_window, text = '匹配到的图像')
    searchImg_lab.place(x = 340, y = 10)
    
    keyname_lab = tk.Label(root_window, text = '关键词:')
    keyname_lab.place(x = 20, y = 330)
    keyname_txt = tk.Entry(root_window, bd = 2)
    keyname_txt.place(x = 80, y = 330)

    app_state = tk.StringVar()
    app_state.set('状态: 空闲')
    state_lab = tk.Label(root_window, textvariable = app_state, font = ('Songti', 15))
    state_lab.place(x = 200, y = 270)

    openfile_btn = tk.Button(root_window,bg = 'White',height = 2,width = 10,text = '图像选择',command = openfile_dialog)
    openfile_btn.place(x = 20,y = 370)

    urlread_btn = tk.Button(root_window,bg = 'White',height = 2,width = 10,text = '图像搜索',command = lambda : my_search.search_onWeb(keyname_txt.get()))
    urlread_btn.place(x = 200,y = 370)

    openWeb_btn = tk.Button(root_window,bg = 'White',height = 2,width = 10,text = '打开网址',command = OpenWeb)
    openWeb_btn.place(x = 380,y = 370)

    fig1 = mp.figure(1)
    imgbox1 = FigureCanvasTkAgg(fig1, master = root_window)
    imgbox1._tkcanvas.place(relx = 0.05, rely = 0.1, width = 200, height = 220)

    fig2 = mp.figure(2)
    imgbox2 = FigureCanvasTkAgg(fig2, master = root_window)
    imgbox2._tkcanvas.place(relx = 0.55, rely = 0.1, width = 200, height = 220)

    pageSet_lab = tk.Label(root_window, text = '最大搜索页数:')
    pageSet_lab.place(x = 20, y = 300)
    comvalue1 = tk.StringVar()# 页数选择下拉列表
    comboxlist1 = ttk.Combobox(root_window, textvariable = comvalue1, width = 10)
    comboxlist1["values"] = ("1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12" ,"13", "14", "15")
    comboxlist1.bind("<<ComboboxSelected>>", choose_page)
    comboxlist1.place(x = 110, y = 300)

    findweb_lab = tk.Label(root_window, text = '搜索到的网址:')
    findweb_lab.place(x = 240, y = 330)
    comvalue = tk.StringVar()# 网址选择下拉列表
    comboxlist = ttk.Combobox(root_window, textvariable = comvalue, width = 20)
    comboxlist["values"] = (my_search.weburl)
    comboxlist.bind("<<ComboboxSelected>>", choose_web)
    comboxlist.place(x = 330, y = 330)

    Threshold_lab = tk.Label(root_window, text = '阈值选择:')
    Threshold_lab.place(x = 240, y = 300)
    limit_val = tk.IntVar()# 阈值条
    limit_scale = tk.Scale(root_window,variable = limit_val,orient = 'horizonta',length = 160,from_ = 0,to = 30, command = set_Threshold)
    limit_scale.place(x = 320, y = 280)
    
if __name__ == '__main__':
    warnings.filterwarnings('ignore')
    gui_init()

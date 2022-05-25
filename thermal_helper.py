from PIL import Image
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw
from escpos import printer
from pathlib import Path
import pandas as pd 
import qrcode
import arabic_reshaper 
from bidi.algorithm import get_display
from datetime import datetime
import numpy as np 
import io 
from fatoora import Fatoora

def get_qr_img(total_amount,tax_amount) : 
    dt = datetime.now()
    ts = datetime.timestamp(dt)
    fatoora_obj = Fatoora(
    seller_name="Juicy Juice",
    tax_number="310590919100003",
    invoice_date = ts, 
    total_amount=total_amount, 
    tax_amount=tax_amount, 
    )
    qr_image = qrcode.make(fatoora_obj.base64)
    buf = io.BytesIO()
    qr_image.save(buf)
    img = Image.open(buf)
    img = img.resize((200,200))
    return img
path = Path(__file__).with_name('x-2.jpg')
IMG = Image.open(path)
TAX = 15

items_db = {
    "english":"arabic",
    "Apple":"تفاح",
    "apple":"تفاح",
    "Avocado":"افوكادو",
    "avocado":"افوكادو",
    "Banana":"موز",
    "banana":"موز",
    "Beet":"شمندر",
    "beet":"شمندر",
    "Blueberry":"توت",
    "blueberry":"توت",
    "Carrot":"جزر",
    "carrot":"جزر",
    "Ginger":"زنجبيل",
    "ginger":"زنجبيل",
    "Guava":"جوافة",
    "guava":"جوافة",
    "Kiwi":"كيوي",
    "kiwi":"كيوي",
    "Lemon":"ليمون",
    "lemon":"ليمون",
    "Mango":"مانجو",
    "mango":"مانجو",
    "Melon":"شمام",
    "melon":"شمام",
    "Orange":"برتقال - خلاط",
    "orange":"برتقال - خلاط",
    "Orange mix":"برتقال - كبس",
    "Pineapple":"اناناس",
    "pineapple":"اناناس",
    "Pomegranate":"رمان",
    "pomegranate":"رمان",
    "Strawberry":"فراولة",
    "strawberry":"فراولة",
    "Watermelon":"بطيخ",
    "watermelon":"بطيخ",
    "Grape":"عنب",
    "grape":"عنب",
    "Mint":"نعناع",
    "mint":"نعناع",
    "Aoar qalb":"عوار القلب",
    "Asfahani":"اصفهاني",
    "Askindarani":"اسكندراني",
    "French juice":"فرنسي",
    "Lolly cocktail":"كوكتيل لولي",
    "Refreshing juice":"منعش",
    "Romanbo":"رمانبو",
    "Sultan":"السلطان",
    "Vitamins":"فيتامنيات",
    "Fruit salad":"سلطة فواكه",
    "Ice cream":"ايس كريم",
    "Cash":"نقدي",
    "Card":"بطاقة",
}



def fill_meta_data_0(img,adate,atime,epay,apay,font): 
    path = str(Path(__file__).with_name('english.ttf'))
    font = ImageFont.truetype(path, 32)
    d = ImageDraw.Draw(img)
    d.text((70,330),adate,font=font,fill='black')
    d.text((110,385),atime,font=font,fill='black')
    path = str(Path(__file__).with_name('arabic.ttf'))
    font = ImageFont.truetype(path, 28)
    x_sh  = 135
    if "Credit" in epay : 
        x_sh = 30
    apay = epay+":"+apay
    d.text((x_sh,435),apay,font=font,fill='black')
    path = str(Path(__file__).with_name('english.ttf'))
    font = ImageFont.truetype(path, 42)
    return img 


def get_concat_v(im1, im2):
    dst = Image.new('RGB', (im1.width, im1.height + im2.height))
    dst.paste(im1, (0, 0))
    dst.paste(im2, (0, im1.height))
    return dst


def extract_meta_img_1 (img,w,h,x,y) : 
    area = (x, y, x+w, y+h)
    return img.crop(area)


def generate_arabic_string(eng_item,adict) :
    a = ""
    for index,t in enumerate(eng_item.split(' + ')) : 
        text=adict[t]
        reshaped_p = arabic_reshaper.reshape(adict[t])
        text = get_display(reshaped_p)
        #text += "-"+t
        if (index != 0 ):
            a +=  " + "+text
        else:
            a  =  text
    return eng_item,a


def create_an_item_slice(w,h,item,a_item,price,qnt,tot,font) : 
    item_image = Image.new('RGB', (w,h), (255,255,255))
    d = ImageDraw.Draw(item_image)
    shift   = font.getsize(item)[0]
    shift_a = font.getsize(a_item)[0]
    d.text((20,0),tot,font=font,fill='black')
    d.text((150,0),qnt,font=font,fill='black')
    d.text((230,0),price,font=font,fill='black')
    d.text((w-shift-20,0),item,font=font,fill='black')
    d.text((w-shift_a-20,30),a_item,font=font,fill='black')
    return item_image

def fill_meta_data_1(img,tot_before,atax,tot_after,seller,font): 
    #font = ImageFont.truetype(fontFile, 42)
    d = ImageDraw.Draw(img)
    d.text((98,322),tot_before,font=font,fill='black')
    d.text((135,377),atax,font=font,fill='black')
    d.text((135,435),tot_after,font=font,fill='black')
    d.text((135,435),seller,font=font,fill='black')
    return img 

def get_date_time():
    now = datetime.now() # current date and time
    date = now.strftime("%d/%m/%Y")
    time = now.strftime("%H:%M:%S")
    return date,time


def fill_meta_data_2(img,tot_before,atax,tot_after,seller,font):
    d = ImageDraw.Draw(img)
    d.text((40,20),tot_before,font=font,fill='black')
    d.text((40,70),atax,font=font,fill='black')
    d.text((40,125),tot_after,font=font,fill='black')
    d.text((80,195),seller,font=font,fill='black')
    return img 

  
def generate_receipt_image(payment_method,items_sold,seller):
    img = IMG.copy()
    date_stamp,time_stamp = get_date_time()

    total_before,tax_amount,total_after,pythonitems_sold = calculate_and_convert_items(items_sold)

    meta_img_0 = extract_meta_img_1(img,631,600,0,0)
    meta_img_1 = extract_meta_img_1(img,631,50,0,540)
    meta_img_2 = extract_meta_img_1(img,631,250,0,650)

    e_pay , a_pay = generate_arabic_string(payment_method,items_db)

    path = str(Path(__file__).with_name("english.ttf"))
    font = ImageFont.truetype(path, 12)
    p0   = fill_meta_data_0(meta_img_0,date_stamp,time_stamp,e_pay,a_pay,font)
    
    font = ImageFont.truetype(path, 30)
    p2   = fill_meta_data_2(meta_img_2,total_before,tax_amount,total_after,seller,font)
    path = str(Path(__file__).with_name("arabic.ttf"))
    font = ImageFont.truetype(path, 26)
    current = p0
    
    for i in items_sold: 
        i_name = i['item_name']
        i_price = i['price']
        i_quant = i['quantity']
        i_tot   = i['total']
        
        e,a = generate_arabic_string(i_name,items_db)
        an_item = create_an_item_slice(631,70,e,a,i_price,i_quant,i_tot,font)
        current = get_concat_v(current,an_item)

    
    current = get_concat_v(current,p2)
    
    img_qr  = get_qr_img(total_before,tax_amount)
    qim    = Image.new('RGB', (631,200), (255,255,255))
    qim.paste(img_qr, (215,0))
    current = get_concat_v(current,qim)
    return current 

def calculate_and_convert_items(items):
    total_before = 0 
    total_after  = 0 
    tax        = TAX/100
    conv_items = []
    for i in items : 
        total_before    += i['quantity'] * i['price']
        i['total']       = "{:.2f}".format(round(i['quantity'] * i['price'], 2))
        i['price']       = "{:.2f}".format(round(i['price'], 2))
        i['quantity']    = str(i['quantity'])
        conv_items.append(i)
    tax_amount   = tax * total_before
    total_after  = total_before + tax_amount

    total_before = "{:.2f}".format(round(total_before, 2))
    total_after  = "{:.2f}".format(round(total_after, 2))
    tax_amount   = "{:.2f}".format(round(tax_amount, 2))
    return total_before,tax_amount,total_after,conv_items
def intro_image(w,h,adate,atime,font) : 
    text = get_display(arabic_reshaper.reshape("مبيعات جوسي جوس"))
    item_image = Image.new('RGB', (w,h), (255,255,255))
    d = ImageDraw.Draw(item_image)
    d.text((200,0),text,font=font,fill='black')
    d.line([(200,50),(410,50)],"#000000",width=3)
    #d.line([(0,0),(600,0)],"#000000",width=3)
    text = get_display(arabic_reshaper.reshape("تاريخ الطباعة  :"))
    shift = font.getsize(text)[0]
    d.text((600-shift,60),text,font=font,fill='black')
    text = get_display(arabic_reshaper.reshape("وقت الطباعة  :"))
    shift = font.getsize(text)[0]
    d.text((600-shift,120),text,font=font,fill='black')
    now_date,now_time  = get_date_time()
    d.text((600-shift-220,65),now_date,font=font,fill='black')
    d.text((600-shift-200,120),now_time,font=font,fill='black')
    
    text = get_display(arabic_reshaper.reshape("مبيعات يوم    :"))
    shift = font.getsize(text)[0]
    d.text((600-shift,180),text,font=font,fill='black')
    
    d.text((600-shift-220,180),adate,font=font,fill='black')
    return item_image
def create_entry_row(items,font) : 
    items_count = len(items)+2
    item_height = 100
    item_width = 600
    item_image = Image.new('RGB', (item_width,item_height*items_count), (255,255,255))
    d = ImageDraw.Draw(item_image)
    aggregate = 0
    
    d.rectangle([(10,0),(item_width,item_height*(1))] , outline="#000000", width=3)
    col_shift = 160
    d.line([(col_shift,0),(col_shift,(1)*item_height)],"#000000",width=3)
    col_shift = 300
    d.line([(col_shift,(0)*item_height),(col_shift,(0+1)*item_height)],"#000000",width=3)
    col_shift = 440
    d.line([(col_shift,(0)*item_height),(col_shift,(0+1)*item_height)],"#000000",width=3)
    
    text = get_display(arabic_reshaper.reshape("التاريخ"))
    d.text((520,30+0*item_height),text,font=font,fill='black')
    
    text = get_display(arabic_reshaper.reshape("اجمالي"))
    d.text((340,30+0*item_height),text,font=font,fill='black')
    
    text = get_display(arabic_reshaper.reshape("ضريبه"))
    d.text((200,30+0*item_height),text,font=font,fill='black')
    
    text = get_display(arabic_reshaper.reshape("الصافي"))
    d.text((50 ,30+0*item_height),text,font=font,fill='black')
    path = str(Path(__file__).with_name("arabic.ttf"))
    font        = ImageFont.truetype(path, 26)
    for index,i in enumerate(items) :
        if (index == 0) : 
            continue
        aggregate += i['total'] * (1+TAX/100)
        total_before = "{:.2f}".format(round(i['total'], 2)) 
        tax_amount   =  "{:.2f}".format(round(i['total'] * (TAX/100), 2))  
        total_after  = "{:.2f}".format(round(i['total'] * (1+TAX/100), 2))  
        a = 2.5
        d.rectangle([(10,(index*item_height)-a),(item_width,item_height*(index+1)-a)] , outline="#000000", width=3)
        col_shift = 160
        d.line([(col_shift,(index)*item_height),(col_shift,(index+1)*item_height-a)],"#000000",width=3)
        col_shift = 300
        d.line([(col_shift,(index)*item_height),(col_shift,(index+1)*item_height-a)],"#000000",width=3)
        col_shift = 440
        d.line([(col_shift,(index)*item_height),(col_shift,(index+1)*item_height-a)],"#000000",width=3)
        d.text((450,30+index*item_height),"20/22/1990",font=font,fill='black')
        d.text((310,30+index*item_height),str(total_before),font=font,fill='black')
        d.text((170,30+index*item_height),str(tax_amount),font=font,fill='black')
        d.text((20,30+index*item_height),str(total_after),font=font,fill='black')    
    aggregate = "{:.2f}".format(round(aggregate, 2))
    d.rectangle([(10,((items_count-2)*item_height)),(item_width,item_height*(items_count-1))] , outline="#000000", width=3)
    text = get_display(arabic_reshaper.reshape("الاجـمـــــــــــــــــــــــالي      : "))
    d.text((370,(items_count-2)*item_height+20),text,font=font,fill='black')
    d.text((30,(items_count-2)*item_height+20),"س.ر",font=font,fill='black')
    font        = ImageFont.truetype(path, 30)
    d.text((100,(items_count-2)*item_height+20),aggregate,font=font,fill='black')
    
    return item_image
def generate_total_receipt(items_list,adate):
    items_list.insert(0, {'total':None})
    path = str(Path(__file__).with_name("arabic.ttf"))
    font        = ImageFont.truetype(path, 26)
    space       = item_image = Image.new('RGB', (600,100), (255,255,255))
    img         = intro_image(600,300,adate,"time",font)
    current     = get_concat_v(space,img)
    font        = ImageFont.truetype(path, 30)
    table = create_entry_row(items_list,font)
    current = get_concat_v(current,table)
    current = get_concat_v(current,space)
    current = add_margin(current,0,10,0,0,"#FFFFFF")
    return current 
def add_margin(pil_img, top, right, bottom, left, color):
    width, height = pil_img.size
    new_width = width + right + left
    new_height = height + top + bottom
    result = Image.new(pil_img.mode, (new_width, new_height), color)
    result.paste(pil_img, (left, top))
    return result
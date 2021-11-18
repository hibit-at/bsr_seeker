import json
from collections import defaultdict
from numpy.lib.function_base import disp, sort_complex
import requests
import re
import math
from PIL import Image, ImageDraw, ImageFont
import base64
from io import BytesIO
import numpy as np  
from copy import deepcopy


# hyper parameter

start = '17000'
end = '1c000'

# debug


def json_tree(data, indent=0):
    space = ' '*indent
    if type(data) == dict:
        for k in data.keys():
            print('\n', space, k, end='')
            json_tree(data[k], indent+4)
    elif type(data) == list and len(data) > 0:
        json_tree(data[0], indent+4)
    else:
        print(' :', data, end='')
    return


def pil_to_base64(img, format="PNG"):
    buffer = BytesIO()
    img.save(buffer, format)
    img_str = base64.b64encode(buffer.getvalue()).decode("ascii")
    return img_str


def text_over(img, text, height, text_color):
    ttfontname = "C:\\Windows\\Fonts\\meiryob.ttc"
    fontsize = 50
    textRGB = text_color
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(ttfontname, fontsize)
    textTopLeft = (10, height)
    draw.text(textTopLeft, text, fill=textRGB, font=font)


def make_cover(nps, start, end):
    canvasSize = (256, 256)
    green = 0
    if nps < 6:
        green = min(nps*255/3,255)
    else:
        green = -255/3*(nps-9)
        green = min(green,255)
        green = max(green,0)
    red = 255/3*(nps-3)
    red = min(red,255)
    red = max(red, 0)
    blue = (nps-9)*255/3
    blue = min(blue,255)
    blue = max(blue,0)
    red = int(red)
    blue = int(blue)
    green = int(green)
    backgroundRGB = (0, 0, 0)
    text_color = (red,green,blue)
    img = Image.new('RGB', canvasSize, backgroundRGB)
    text_over(img, f'NPS:{nps}', 20, text_color)
    text_over(img, f'{start}~', 100, text_color)
    text_over(img, end, 180, text_color)
    img.save(f'cover_nps{nps}_{start}~{end}.png')
    img_base = pil_to_base64(img)
    return img_base


def create_bpl(nps, queue):
    start = queue[0]['bsr_key']
    end = queue[-1]['bsr_key']
    print(start, end)
    img_base = make_cover(nps, start, end)
    bpl_title = f'nps{nps}_{start}~{end}'
    j = {}
    j['songs'] = []
    j['playlistAuthor'] = 'hibit'
    j['playlistTitle'] = bpl_title
    j['playlistDescription'] = bpl_title
    j['image'] = f'data:image/png:base64,{img_base}'
    while len(queue):
        q = queue.pop()
        hash = q['hash']
        print(hash)
        chara = q['chara']
        diff_name = q['diff_name']
        append_json = {}
        append_json['hash'] = hash
        append_json['difficulties'] = [{}]
        append_json['difficulties'][0]['characteristic'] = chara
        append_json['difficulties'][0]['name'] = diff_name
        j['songs'].append(append_json)


    json.dump(j,open(f'{bpl_title}.json','w'))
    print('created!')


def queue_check(queue_list):
    for item in sorted(queue_list.items(), key=lambda x : x[0]):
        print('nps', item[0], 'length', len(item[1]))
    for item in sorted(queue_list.items(), key=lambda x : x[0]):
        nps = item[0]
        queue = item[1]
        if len(queue) >= 10:
            create_bpl(nps, queue)



end_num = int(end, 16)
manu_range = 0
start_num = int(start, 16)
if manu_range > 0:
    start_num = end-manu_range
log_path = 'search_log.txt'
queue_nps = defaultdict(list)


for i in range(start_num, end_num):
    bsr_key = hex(i)[2:]
    url = 'https://api.beatsaver.com/maps/id/' + bsr_key
    res = requests.get(url).json()
    if 'error' in res:
        continue
    name = res['name']
    name = re.sub(r'[\\/:*?"<>|]+', '', name)
    author = res['uploader']['name']
    author = re.sub(r'[\\/:*?"<>|]+', '', author)
    score = res['stats']['score']
    latest = res['versions'][0]
    hash = latest['hash']
    print(bsr_key, name, score)
    if score >= 0.75:
        proc_count = defaultdict(int)
        diffs = list(latest['diffs'])
        diffs.reverse()
        for diff in diffs:
            diff_name = diff['difficulty']
            nps = diff['nps']
            chara = diff['characteristic']
            print(diff_name, nps)
            proc_nps = math.floor(nps)
            print(proc_nps)
            if proc_count[proc_nps] > 0:
                print('this range of nps has been already taken!')
                continue
            proc_count[proc_nps] += 1
            # append_tuple = (hash, chara, diff_name, bsr_key)
            append_dict = {
                'hash': hash,
                'chara': chara,
                'diff_name': diff_name,
                'bsr_key': bsr_key,
            }
        queue_nps[proc_nps].append(append_dict)
        queue_check(queue_nps)

# queueの後処理

for item in queue_nps.items():
    nps = item[0]
    queue = item[1]
    create_bpl(nps, queue)
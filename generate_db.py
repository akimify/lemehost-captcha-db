import json
import random
import string
import urllib.request
from PIL import Image, ImageDraw, ImageFont

FONT_PATH  = 'SpicyRice.ttf'
IMG_W      = 120
IMG_H      = 50
FONT_SIZE  = 30
OFFSET     = -2
COUNT      = 500
CODE_LEN   = 6
OUTPUT     = 'db.json'

CHARS = string.ascii_lowercase

def download_font():
    try:
        ImageFont.truetype(FONT_PATH, FONT_SIZE)
    except:
        print('下载 SpicyRice.ttf ...')
        urllib.request.urlretrieve(
            'https://github.com/yiisoft/yii/raw/master/framework/web/widgets/captcha/SpicyRice.ttf',
            FONT_PATH
        )
        print('下载完成')

def render_captcha(code):
    img  = Image.new('RGB', (IMG_W, IMG_H), (255, 255, 255))
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    x    = 10
    y    = round(IMG_H * 27 / 40)
    for ch in code:
        angle = random.uniform(-15, 15)
        tmp   = Image.new('RGBA', (40, 50), (255, 255, 255, 0))
        ImageDraw.Draw(tmp).text((0, 0), ch, font=font, fill=(0, 0, 0, 255))
        tmp   = tmp.rotate(angle, expand=False, fillcolor=(255, 255, 255, 0))
        img.paste(tmp, (x, y - FONT_SIZE), mask=tmp.split()[3])
        bbox  = font.getbbox(ch)
        x    += bbox[2] - bbox[0] + OFFSET
    return img

def img_to_pixels(img):
    img = img.resize((IMG_W, IMG_H)).convert('RGB')
    pixels = []
    for pixel in img.getdata():
        r, g, b = pixel[0], pixel[1], pixel[2]
        gray = 0.299 * r + 0.587 * g + 0.114 * b
        pixels.append(1 if gray < 128 else 0)
    return pixels

def main():
    download_font()
    db = []
    for i in range(COUNT):
        code   = ''.join(random.choices(CHARS, k=CODE_LEN))
        img    = render_captcha(code)
        pixels = img_to_pixels(img)
        db.append({'pixels': pixels, 'code': code})
        if (i + 1) % 50 == 0:
            print(f'已生成 {i+1}/{COUNT} 条')

    content_str = json.dumps(db, separators=(',', ':'))
    with open(OUTPUT, 'w') as f:
        f.write(content_str)
    print(f'完成！{OUTPUT} 共 {COUNT} 条，{len(content_str)/1024:.1f} KB')

if __name__ == '__main__':
    main()

# generate_db.py
import json, random, math, string, urllib.request, base64
from PIL import Image, ImageDraw, ImageFont

FONT_PATH    = 'SpicyRice.ttf'
IMG_W        = 120
IMG_H        = 50
FONT_SIZE    = 30
OFFSET       = -2
COUNT        = 500
CODE_LEN     = 6
OUTPUT       = 'db.json'

# GitHub 配置（可选，填了就自动推送）
GITHUB_TOKEN  = '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'
GITHUB_REPO   = 'akimify/lemehost-captcha-db'
GITHUB_FILE   = 'db.json'
GITHUB_BRANCH = 'main'

CHARS = string.ascii_lowercase

def render_captcha(code):
    img  = Image.new('RGB', (IMG_W, IMG_H), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    x = 10
    y = round(IMG_H * 27 / 40)
    for ch in code:
        angle = random.uniform(-15, 15)
        tmp = Image.new('RGBA', (40, 50), (255, 255, 255, 0))
        ImageDraw.Draw(tmp).text((0, 0), ch, font=font, fill=(0, 0, 0, 255))
        tmp = tmp.rotate(angle, expand=False, fillcolor=(255, 255, 255, 0))
        img.paste(tmp, (x, y - FONT_SIZE), mask=tmp.split()[3])
        bbox  = font.getbbox(ch)
        x    += bbox[2] - bbox[0] + OFFSET
    return img

def img_to_pixels(img):
    img = img.resize((IMG_W, IMG_H)).convert('RGB')
    pixels = []
    for r, g, b in img.getdata():
        gray = 0.299 * r + 0.587 * g + 0.114 * b
        pixels.append(1 if gray < 128 else 0)
    return pixels

def push_to_github(content_str):
    import urllib.request as ur
    # 先获取当前 sha
    req = ur.Request(
        'https://api.github.com/repos/' + GITHUB_REPO + '/contents/' + GITHUB_FILE,
        headers={
            'Accept': 'application/vnd.github+json',
            'Authorization': 'Bearer ' + GITHUB_TOKEN,
        }
    )
    with ur.urlopen(req) as r:
        sha = json.loads(r.read())['sha']

    content_b64 = base64.b64encode(content_str.encode()).decode()
    body = json.dumps({
        'message': 'init captcha db (' + str(COUNT) + ' entries)',
        'content': content_b64,
        'sha':     sha,
        'branch':  GITHUB_BRANCH,
    }).encode()
    req2 = ur.Request(
        'https://api.github.com/repos/' + GITHUB_REPO + '/contents/' + GITHUB_FILE,
        data=body,
        method='PUT',
        headers={
            'Accept':        'application/vnd.github+json',
            'Authorization': 'Bearer ' + GITHUB_TOKEN,
            'Content-Type':  'application/json',
        }
    )
    with ur.urlopen(req2) as r:
        print('推送成功:', r.status)

def main():
    # 自动下载字体
    try:
        ImageFont.truetype(FONT_PATH, FONT_SIZE)
    except:
        print('下载 SpicyRice.ttf ...')
        urllib.request.urlretrieve(
            'https://github.com/yiisoft/yii/raw/master/framework/web/widgets/captcha/SpicyRice.ttf',
            FONT_PATH
        )

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
    print(f'\n完成！{OUTPUT} 共 {COUNT} 条，{len(content_str)/1024:.1f} KB')

    if GITHUB_TOKEN and GITHUB_REPO:
        print('推送到 GitHub...')
        push_to_github(content_str)

if __name__ == '__main__':
    main()

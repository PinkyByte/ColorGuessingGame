from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

def create_card(username, level, exp, total, img, color) -> BytesIO:
    profile = Image.open(BytesIO(img.content))
    if profile.mode != 'RGBA':
        profile = profile.convert('RGBA')
    profile = profile.resize((473, 473))
    background = Image.open(f'assets/card_{str.lower(color)}.png')
    card = Image.new('RGBA', (750, 1050), (255, 255, 255, 255))
    font = ImageFont.truetype('Cabin-VariableFont_wdth,wght.ttf', 40)
    card.paste(background, (0, 0))
    draw = ImageDraw.Draw(card)
    card.paste(profile, (138, 213), profile)
    if draw.textlength(username, font = font) > draw.textlength('mmmmmmmmmmmmm', font = font):
        shortname = ''
        ind = 0
        while draw.textlength(shortname, font = font) <= draw.textlength('mmmmmmmmmmmmm', font = font):
            shortname += username[ind]
            ind += 1
        if draw.textlength(shortname, font = font) <= draw.textlength('mmmmmmmmmmmmm', font = font):
            draw.text((60, 65), shortname[:ind - 1] + '...', font = font, fill = 'black')
        else:
            draw.text((60, 65), shortname[:ind - 2] + '...', font = font, fill = 'black')
    else:
        draw.text((60, 65), username, font = font, fill = 'black')
    draw.text((100, 720), f'Level: {level}', font = font, fill = 'black')
    if level < 31622:
        draw.text((100, 800), f'Exp to level up: {exp}', font = font, fill = 'black')
        draw.text((100, 880), f'Total exp gained: {total}', font = font, fill = 'black')
    else:
        draw.text((100, 800), 'Exp to level up: No you don\'t', font = font, fill = 'black')
        draw.text((100, 880), f'Total exp gained: All of \'em', font = font, fill = 'black')
    buffer = BytesIO()
    card.save(buffer, format = 'PNG')
    buffer.seek(0)
    return buffer

def create_leaderboard(usernames) -> BytesIO:
    leaderboard = Image.open('assets/leaderboard.png')
    leaderboard = leaderboard.resize((600, 300))
    board = Image.new('RGBA', (600, 300), (255, 255, 255, 255))
    board.paste(leaderboard, (0, 0))
    draw = ImageDraw.Draw(board)
    font = ImageFont.truetype('Cabin-VariableFont_wdth,wght.ttf', 20)
    for i, user in enumerate(usernames):
        if draw.textlength(user[0], font = font) > draw.textlength('mmmmmmmmmmm', font = font):
            shortname = ''
            ind = 0
            while draw.textlength(shortname, font = font) <= draw.textlength('mmmmmmmmmmm', font = font):
                shortname += user[0][ind]
                ind += 1
            if draw.textlength(shortname, font = font) <= draw.textlength('mmmmmmmmmmm', font = font):
                draw.text((10, ((i) * 30) + 5), shortname[:ind - 1] + '...', font = font, fill = 'black')
            else:
                draw.text((10, ((i) * 30) + 5), shortname[:ind - 2] + '...', font = font, fill = 'black')
        else:
            draw.text((10, ((i) * 30) + 5), user[0], font = font, fill = 'black')
        draw.text((240, ((i) * 30) + 5), f'Level: {user[1]}', font = font, fill = 'black')
        if user[1] < 31622:
            draw.text((370, ((i) * 30) + 5), f'Exp to level up: {user[2]}', font = font, fill = 'black')
        else:
            draw.text((370, ((i) * 30) + 5), f'Exp to level up: No you don\'t', font = font, fill = 'black')
    buffer = BytesIO()
    board.save(buffer, format = 'PNG')
    buffer.seek(0)
    return buffer

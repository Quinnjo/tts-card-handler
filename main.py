from PIL import Image, ImageFont, ImageDraw
import os
import glob
import math

# TODO
# ensure filenames are lowercase and have no spaces or special characters
# increase font size?
# concatenate cards into decks automatically

# Given a string word, generate a card image
def make_card_from_string(word, deck='misc'):
    fnt = ImageFont.truetype('fonts/Lato-Black.ttf', size=30)
    with Image.open('cards/template.png').convert('RGB') as template:
        out = template.copy()
        card = ImageDraw.Draw(out)

        # The card template is 490x490
        # We want to write in the center of the top half
        box = [0, 0, 490, 230]
        x1, y1, x2, y2 = box

        w, h = card.textsize(word, font=fnt)
        x = (x2 - x1 - w) // 2 + x1
        y = (y2 - y1 - h) // 2 + y1

        card.text((x, y), word, font=fnt, align = 'center', fill='black')

        # Reflect the changes to the top half in the bottom half
        # This gives the card a mirrored look
        top = (0, 0, 490, 230)
        bottom = (0, 260, 490, 490)
        region = out.crop(top)
        region = region.transpose(Image.ROTATE_180)
        out.paste(region, bottom)


        filename = word.lower()
        filename = filename.replace('&', 'and')
        filename = filename.replace(" ", "_")
        filename = filename.replace("\n", "_")
        out = out.save(f'./cards/{deck}/{filename}.png')   # save the image
        #return out                      # return the image

# Make card images from a text file, where each card is on its own line
# if no deck name is specified, use misc
def make_cards_from_txt_file(path, deck=None):

    # If a deck directory does not exist, make one
    if not os.path.isdir(f'./cards/{deck}'):
        os.mkdir(f'./cards/{deck}')


    with open(path, 'r') as f:
        word = f.readline()
        while word:
            word = word.strip()
            word = word.upper()
            word = word.replace('%', '\n')
            make_card_from_string(word, deck)
            word = f.readline()

def stitch_cards(dir):
    cards = list()
    search = f'{dir}/*.png'
    for filename in glob.iglob(search):
        card = Image.open(filename)
        cards.append(card)
    
    n_rows = 7
    n_cols = 10
    n_cards = len(cards)

    # All cards must have the same dimensions
    w_card = cards[0].width
    h_card = cards[0].height


    # Until we are out of cards
    count = 0
    while cards:
        # The resulting image
        num = min(len(cards), 70)               # the number of cards in this image
        n_rows_used = math.ceil(num / n_rows)   # the amount of used rows
        stitched = Image.new(mode='RGB', size=(w_card*n_cols, h_card*n_rows), color='black')

        # Stitch cards to make each row
        rows = list()
        cur = 0
        for i in range(n_rows_used):
            r = Image.new(mode='RGB', size=(w_card*n_cols, h_card))
            for j in range(n_cols):
                if cur < num:
                    r.paste(cards[cur], (j*w_card, 0))
                cur += 1
            rows.append(r)
        
        # Stitch rows together to make final product
        for i in range(n_rows_used):
            stitched.paste(rows[i], (0, i*h_card))

        name = f'./{dir}_{count}_{num}.png'
        stitched.save(name)
        count += 1
        if len(cards) > 70:
            cards = cards[70:]
        else:
            cards = None
        # Don't do more than 350 cards at once
        if count > 5:
            break

# Unused
def stitch_letters():
    pass


if __name__ == '__main__':
    make_cards_from_txt_file('./decks/default.txt', 'default')
    stitch_cards('./cards/default')
    print('done!')
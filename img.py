import Image, ImageChops
import pytesseract
import logging
import logging.handlers

fm,df="%(asctime)s  %(levelname)s - %(message)s","%Y-%m-%d %H:%M:%S"
logging.basicConfig(format=fm,datefmt=df,filename='check.log',level=logging.INFO,filemod='w')

def readimage(pic):
        img = Image.open(pic)
        imr = img.convert('L', (.2, .2, .2, 0))
        im2 = Image.new("L", imr.size, 255)
        for x in range(imr.size[0]):
                for y in range(imr.size[1]):
                        pix = imr.getpixel((x,y))
                        if pix < 90:
                                im2.putpixel((x,y), pix)
                                
        im2 = im2.convert('1')
        code = pytesseract.image_to_string(im2)
        if validationpic(code):
                logging.info('Got normal code:%s'%code)
                return code
        else:
                logging.info('Got unusual code:%s'%code)
                return ''
        
def validationpic(code=None):
        if len(code)!=4:
                return False
        if ('8' in code) or ('2' in code) or ('B' in code) or ('Z' in code):
                return False
        return True

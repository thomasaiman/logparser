import os
import pytesseract
from PIL import Image, ImageOps, ImageDraw
from WindowManager import WindowMgr
import uuid
import pyautogui
import win32gui
from decimal import Decimal
import decimal
import time
import logging
from pprint import pprint
from pyscreeze import Box
import re
from collections import OrderedDict
from enum import Enum

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

WORKING_DIR = r"C:\Users\Thomas\Desktop\clickers/"
TMP_DIR = WORKING_DIR + 'tmp/'
os.chdir(WORKING_DIR)
tesseract_dir = WORKING_DIR + r"bin/tesseract/"
tessdata_dir = tesseract_dir + r"tessdata_best/"
os.environ['TESSDATA_PREFIX'] = tessdata_dir
pytesseract.pytesseract.tesseract_cmd = tesseract_dir + r'tesseract.exe'
leptonica_util = r"bin\leptonica_util\leptonica_util.exe"

hwnd=win32gui.FindWindow(None, 'Clicker Heroes')
# win32gui.SetForegroundWindow(hwnd)
x0,y0,x1,y1 = win32gui.GetWindowRect(hwnd)
w,h = 1280, 720
win32gui.MoveWindow(hwnd, 0,0,w, h, True)

LEVEL_REGEX = re.compile(r"Lv[il1]\s?([\d\.e]+)")
NAME_REGEX = re.compile(r"([A-Z][A-z,\s]+)")
HS_REGEX = re.compile(r"^(\d\.\d{3}e\d{1,5}|\d{1,5}) Hero Souls$")
pyautogui.PAUSE = 0.2
pyautogui.FAILSAFE_POINTS.append((-5120,0))
pyautogui.FAILSAFE_POINTS.append((-2560,0))
# down_arrow = (619,691)
# up_arrow = (619,237)



def waitForeground(hwnd, force=False):
    def dec(f):
        def func(*args, **kwargs):
            if force:
                win32gui.MoveWindow(hwnd, 0, 0, 1280, 720, True)
                win32gui.SetForegroundWindow(hwnd)
            while win32gui.GetForegroundWindow() != hwnd:
                time.sleep(1)
            f(*args, **kwargs)
        
        return func
    
    return dec


def preprocess_image(input_path: str, invert=False, floodfill=False) -> str:
    output_path = input_path[:-4] + '-preprocess' + input_path[-4:]
    cmd = f'{leptonica_util} {input_path} {output_path} 2 0.5 1 3.5 1 5 2.5 1 2000 2000 0 0 0.0'
    os.system(cmd)
    img = Image.open(output_path)
    if invert:
        img = img.convert(mode='L')
        img = ImageOps.invert(img)
        img = img.convert(mode='1')
    if floodfill:
        ImageDraw.floodfill(img, (0, 0), value=1)  # operates in place
    img.save(output_path)
    return output_path


def screenOCR(x: int, y: int, w: int, h: int, invert=False, floodfill=False, tessdata='best') -> str:
    input_path = f'{TMP_DIR}/tmp-{x}-{y}-{w}-{h}.png'
    pyautogui.screenshot(input_path, region=(x, y, w, h))
    output_path = preprocess_image(input_path, invert=invert, floodfill=floodfill)
    
    tessdata_dir = tesseract_dir + f"tessdata_{tessdata}/"
    os.environ['TESSDATA_PREFIX'] = tessdata_dir
    text = pytesseract.image_to_string(output_path, lang='eng')
    return text


class AncientType(Enum):
    ignore = 0
    n1 = 1
    n2 = 2
    n15 = 3
    nexp = 4
    
    
class WindowMgmt():
    pass
    
class Hero():
    NAMES = ['Cid, the Helpful Adventurer',
             'Treebeast',
             'Ivan, the Drunken Brawler',
             'Brittany, Beach Princess',
             'The Wandering Fisherman',
             'Betty Clicker',
             'The Masked Samurai',
             'Leon',
             'The Great Forest Seer',
             'Alexa, Assassin',
             'Natalia, Ice Apprentice',
             'Mercedes, Duchess of Blades',
             'Bobby, Bounty Hunter',
             'Broyle Lindeoven, Fire Mage',
             "Sir George Il, King's Guard",
             'King Midas',
             'Referi Jerator, Ice Wizard',
             'Abaddon',
             'Ma Zhu',
             'Amenhotep',
             'Beastlord',
             'Athena, Goddess of War',
             'Aphrodite, Goddess of Love',
             'Shinatobe, Wind Deity',
             'Grant, The General',
             'Frostleaf',
             'Dread Knight',
             'Atlas',
             'Terra',
             'Phthalo',
             'Orntchya Gladeye, Didensy',
             'Lilin',
             'Cadmia',
             'Alabaster',
             'Astraea',
             'Chiron',
             'Moloch',
             'Bomber Max',
             'Gog',
             'Wepwawet',
             'Tsuchi',
             'Skogur',
             'Moeru',
             'Zilar',
             'Madzi',]
    LEVEL_REGEX = re.compile(r"Lv[il1]\s?([\d]+)")
    NAME_REGEX = re.compile(r"([A-Z][A-z,'\s]+)")
    
    def __init__(self, box):
        self.box = box
        self.button = pyautogui.center(box)
        self.nameText, self.lvlText = self.find_name_level(box)
        self.setName(self.nameText)
        self.setLvl(self.lvlText)
    
    def __str__(self):
        return str((self.name, self.lvl, self.box))
    
    def __repr__(self):
        return repr((self.name, self.lvl, self.box))
    
    @staticmethod
    def find_name_level(y) -> (str, str):
        if type(y) != int:
            y = y[1]  # handle tuples, Box
    
        gild_RGB = (255, 211, 73)
        nongild_RGB = (248, 240, 180)
        point = (169, int(y - 12))
        if pyautogui.pixelMatchesColor(*point, gild_RGB, tolerance=10):
            gild = True
        elif pyautogui.pixelMatchesColor(*point, nongild_RGB, tolerance=10):
            gild = False
        else:
            raise ValueError('gild check failed')
    
        nameBox = Box(left=212, top=y - 20, width=491 - 212, height=25)
        lvlBox = Box(left=344, top=y + 6, width=491 - 344, height=25)
        lvlText = screenOCR(*lvlBox, invert=True, floodfill=True)
        if gild:
            nameText = screenOCR(*nameBox)
        else:
            nameText = screenOCR(*nameBox, invert=True, floodfill=True)
    
        return (nameText, lvlText)
    
    def setName(self, nameText):
        try:
            substr = NAME_REGEX.findall(nameText)[0]
            assert substr in self.NAMES
            self.name=substr
        except Exception as e:
            log.warning(e)
            log.warning(f'Failed to parse name "{nameText}"')
            self.name = None
            
    def setLvl(self, lvlText):
        try:
            if lvlText=='':
                substr = '0'
            else:
                substr = LEVEL_REGEX.findall(lvlText)[0]
            self.lvl = Decimal(substr)
        except Exception as e:
            log.warning(e)
            log.warning(f'Failed to parse level "{lvlText}"')
            self.lvl=None
            
    def buy(self):
        pyautogui.click(self.button)
            
class Ancient(Hero):
    NAMES = OrderedDict([
        ('Argaiv, Ancient of Enhancement', AncientType.n2),
        ('Atman, Ancient of Souls', AncientType.nexp),
        ('Berserker, Ancient of Rage', AncientType.nexp),
        ('Bhaal, Ancient of Murder', AncientType.n2),
        ('Bubos, Ancient of Diseases', AncientType.nexp),
        ('Chawedo, Ancient of Agitation', AncientType.nexp),
        ('Chronos, Ancient of Time', AncientType.nexp),
        ('Dogcog, Ancient of Thrift', AncientType.nexp),
        ('Dora, Ancient of Discovery', AncientType.nexp),
        ('Energon, Ancient of Battery Life', AncientType.nexp),
        ('Fortuna, Ancient of Chance', AncientType.nexp),
        ('Fragsworth, Ancient of Wrath', AncientType.n2),
        ('Hecatoncheir, Ancient of Wallops', AncientType.nexp),
        ('Juggernaut, Ancient of Momentum', AncientType.n15),
        ('Kleptos, Ancient of Thieves', AncientType.nexp),
        ('Kumawakamaru, Ancient of Shadows', AncientType.nexp),
        ('Libertas, Ancient of Freedom', AncientType.ignore),
        ('Mammon, Ancient of Greed', AncientType.n2),
        ('Mimzee, Ancient of Riches', AncientType.n2),
        ('Morgulis, Ancient of Death', AncientType.n1),
        ('Nogardnit, Ancient of Moderation', AncientType.ignore),
        ('Pluto, Ancient of Wealth', AncientType.n2),
        ('Revolc, Ancient of Luck', AncientType.nexp),
        ('Siyalatas, Ancient of Abandon', AncientType.ignore),
        ('Sniperino, Ancient of Accuracy', AncientType.nexp),
        ('Vaagur, Ancient of Impatience', AncientType.nexp),
    ])
    LEVEL_REGEX = re.compile(r"^Lv[il1] (\d\.\d{3}e\d{1,5}|\d{1,5})$")
    NAME_REGEX = re.compile(r"([A-Z][a-z]+, Ancient of [A-Z][a-z]+)")
    HS_REGEX = re.compile(r"^(\d\.\d{3}e\d{1,5}|\d{1,5}) Hero Souls$")
    @staticmethod
    def find_name_level(y) -> (str, str):
        if type(y) != int:
            y = y[1]  # handle tuples, Box
        nameBox = Box(left=200, top=y - 45, width=591 - 200, height=30)
        lvlBox = Box(left=68, top=y - 45, width=242 - 68, height=30)
        # pyautogui.screenshot('x.png', region=nameBox)
        # pyautogui.screenshot('y.png', region=lvlBox)
        lvlText = screenOCR(*lvlBox)
        nameText = screenOCR(*nameBox)
        return (nameText, lvlText)
    
    def buy(self, amount:Decimal):
        pyautogui.keyDown('v')
        pyautogui.click(self.button)
        pyautogui.keyUp('v')
        pyautogui.typewrite(str(amount), interval=0.1)
        pyautogui.press('enter')
        time.sleep(0.25)
        
    def setName(self, nameText):
        super().setName(nameText)
        if 'Ancient of Momentum' in nameText:
            self.name = 'Juggernaut, Ancient of Momentum'
        if 'Ancient of Luck' in nameText:
            self.name = 'Revolc, Ancient of Luck'
        
        
class HeroBuyer():
    
    def activate_tab(self):
        hero_tab = (90, 142)
        pyautogui.click(*hero_tab, clicks=1)
        time.sleep(0.5)

    
    def hero_list(self):
        self.activate_tab()
        region = Box(left=50, top=240, width=100, height=650 - 200)
        y_space = 100
        box_list = list(pyautogui.locateAllOnScreen('button-corner.png', region=region, confidence=0.95))
        buttons = []
        buttons.append(box_list[0])
        for box in box_list:
            if box.top - buttons[-1].top > y_space:
                buttons.append(box)
            else:
                continue
        heroes = [Hero(box) for box in buttons]
        return heroes

    @staticmethod
    def buy_available_upgrades() -> (int, int):
        region = Box(left=304, top=447, width=100, height=200)
        point = pyautogui.locateCenterOnScreen('buy.png', region=region, confidence=0.9)
        if point:
            pyautogui.click(*point)
        return point

    @waitForeground(hwnd, force=True)
    def buy_heroes(self, top=False):
        self.activate_tab()
        if top:
            pyautogui.scroll(10000)
        while True:
            down_arrow = (619, 691)
            pyautogui.moveTo(*down_arrow)
            heroes = self.hero_list()
            log.debug(heroes)
            if self.buy_available_upgrades() and len(heroes)==3 and heroes[0].lvl is not None:
                pyautogui.click(*heroes[1].button)
                break
            else:
                for hero in heroes:
                    pyautogui.click(hero.button)
                pyautogui.scroll(-150)


class AncientBuyer():
    def __init__(self, chor_lvl:int):
        self.chor_lvl = chor_lvl
        
    @staticmethod
    def lvl_Argaiv(ehs: Decimal) -> Decimal:
        '''total_cost=(1/2)*level^2'''
        hs_to_use = Decimal(5 / 44) * ehs
        lvl = (hs_to_use * 2) ** Decimal(1 / 2)
        return lvl

    @staticmethod
    def lvl_Morgulis(ehs: Decimal) -> Decimal:
        '''total_cost=level'''
        hs_to_use = Decimal(5 / 22) * ehs
        lvl = hs_to_use
        return lvl

    @staticmethod
    def lvl_Juggernaut(ehs: Decimal) -> Decimal:
        '''total_cost=(2/5)*level^(5/2)'''
        hs_to_use = Decimal(1 / 11) * ehs
        lvl = (hs_to_use * Decimal(5 / 2)) ** Decimal(2 / 5)
        return lvl

    @staticmethod
    def lvl_Atman(ehs: Decimal) -> Decimal:
        '''total_cost=2^(level+1)-4'''
        hs_to_use = Decimal(0.01 * 1 / 15) * ehs
        lvl = (hs_to_use + 4).log10() / Decimal(2).log10()
        lvl = lvl.quantize(exp=Decimal(1), rounding=decimal.ROUND_DOWN)
        return lvl

    @staticmethod
    def effective_hs(hs: Decimal, chor: int) -> Decimal:
        return hs * Decimal(0.95 ** (-chor))

    def activate_tab(self):
        tab = (305, 142)
        pyautogui.click(*tab, clicks=1)
        time.sleep(0.5)
        
    def ancient_list(self):
        self.activate_tab()
        region = Box(left=50, top=280, width=100, height=650 - 200)
        y_space = 100
        box_list = list(pyautogui.locateAllOnScreen('button-corner.png', region=region, confidence=0.95))
        buttons = []
        buttons.append(box_list[0])
        for box in box_list:
            if box.top - buttons[-1].top > y_space:
                buttons.append(box)
            else:
                continue
        ancients = [Ancient(box) for box in buttons]
        log.debug(ancients)
        return ancients

    def find_hero_souls(self):
        self.activate_tab()
        region = Box(left=400, top=175, width=625-400, height=25)
        for tessdata in ['legacy', 'best', 'fast']:
            log.debug(f'Trying tessdata {tessdata}')
            hsText = screenOCR(*region, tessdata=tessdata)
            try:
                substr = HS_REGEX.findall(hsText)[0]
                n= Decimal(substr)
                log.info(f'Found {n} HS')
                return n
            except Exception as e:
                log.warning(e)
                log.warning(f'Failed to parse hero souls "{hsText}"')
        else:
            return Decimal(0)
            
    def buy_ancients(self, hs: Decimal):
        self.activate_tab()
        pyautogui.scroll(10000) #top of page
        
        queue = set(Ancient.NAMES.keys())
        ehs = self.effective_hs(hs, self.chor_lvl)
        targets = {
            AncientType.ignore:Decimal(1),
            AncientType.n1:self.lvl_Morgulis(ehs),
            AncientType.n2:self.lvl_Argaiv(ehs),
            AncientType.n15:self.lvl_Juggernaut(ehs),
            AncientType.nexp:self.lvl_Atman(ehs)
        }
        pprint(targets)
        ctx = decimal.Context(prec=2, rounding=decimal.ROUND_DOWN)
        with decimal.localcontext(ctx):
            for i in range(30):
                ancients = self.ancient_list()
                for ancient in ancients:
                    if ancient.name in queue and ancient.lvl is not None:
                        aType = Ancient.NAMES[ancient.name]
                        tgt_lvl = targets[aType]
                        delta = tgt_lvl - ancient.lvl
                        delta = delta.max(Decimal(0))
                        log.info(f'buying {delta} {ancient.name}, tgt={tgt_lvl}')
                        ancient.buy(delta)
                        queue.remove(ancient.name)
                pyautogui.scroll(-300)
                if queue==set():
                    break
                if 'Vaagur, Ancient of Impatience' in [a.name for a in ancients]:
                    pyautogui.scroll(10000)  # top of page
            else:
                log.warning('did not find all ancients in 30 scrolls')

class MercenaryMgr():
    
    def activate_tab(self):
        tab = (521, 147)
        pyautogui.click(*tab, clicks=1)
        time.sleep(0.5)
    
    def next_available_merc(self) -> (int,int):
        down_arrow = (619, 691)
        pyautogui.moveTo(*down_arrow)
        region = Box(left=300, top=200, width=200, height=650 - 200)
        collect_button = pyautogui.locateCenterOnScreen('collect-quest.png', region=region, confidence=0.9)
        if collect_button:
            pyautogui.click(*collect_button)
            return collect_button
        start_button = pyautogui.locateCenterOnScreen('start-quest.png', region=region, confidence=0.9)
        return start_button
        
        
    def run_mercs(self):
        self.activate_tab()
        pyautogui.scroll(10000)
        region = Box(left=300, top=200, width=200, height=650 - 200)
        while True:
            button = self.next_available_merc()
            if button:
                self.start_quest(button)
            else:
                pyautogui.scroll(-1000)
                button = self.next_available_merc()
                if not button:
                    break
            
            
    def start_quest(self, button):
        pyautogui.click(*button)
        quest_button = (pyautogui.locateCenterOnScreen('merc-quest.png', confidence=0.9) or
                        pyautogui.locateCenterOnScreen('ruby-quest.png', confidence=0.9))
        five_min_button = pyautogui.locateCenterOnScreen('5-min-quest.png', confidence=0.9)
        top_quest_button = (480, 180)
        accept_button = (915, 405)
        if quest_button:
            pyautogui.click(*quest_button)
        elif five_min_button:
            pyautogui.click(*five_min_button)
        else:
            pyautogui.click(*top_quest_button)
        pyautogui.click(*accept_button)
        
    def collect_rewards(self):
        region = Box(left=300, top=200, width=200, height=650 - 200)
        collect_button = pyautogui.locateCenterOnScreen('collect-quest.png', region=region, confidence=0.9)
        
        

@waitForeground(hwnd)
def farm_off():
    img = 'ch-farm.png'
    region = (1185, 225, 50, 50)
    point = pyautogui.locateCenterOnScreen(image=img, region=region, confidence=0.9)
    print(point)
    if point:
        log.info(f'Turning off farm mode {point}')
        pyautogui.click(*point)


def autoclicker_to_monster(n=1):
    unused_clickers = (1192, 410)
    monster = (940, 429)
    for i in range(n):
        pyautogui.moveTo(*unused_clickers)
        pyautogui.dragTo(*monster, duration=0.5)


def open_gilds():
    present_box = (1190, 570)
    chest_popup = (633, 383)
    open_all = (942, 581)
    close_box = (1177, 61)
    pyautogui.click(*present_box)
    time.sleep(2)
    pyautogui.click(*chest_popup)
    time.sleep(3)
    pyautogui.click(*open_all)
    pyautogui.click(*close_box)




def ascend():
    ascend_button = (1210,295)
    pyautogui.click(*ascend_button)
    pt=pyautogui.locateCenterOnScreen('ch-yes-salvage.png', confidence=0.9)
    if pt:
        pyautogui.click(*pt)
    time.sleep(0.5)
    pt = pyautogui.locateCenterOnScreen('ch-yes-ascend.png', confidence=0.9)
    if pt:
        pyautogui.click(*pt)
    time.sleep(0.5)
    farm_off()
    autoclicker_to_monster(n=10)
    hbuyer = HeroBuyer()
    hbuyer.buy_heroes(top=True)
    
    abuyer=AncientBuyer(chor_lvl=130)
    hs = abuyer.find_hero_souls()
    abuyer.buy_ancients(hs=hs)

    MercenaryMgr().run_mercs()
    for i in range(1):
        hbuyer.buy_heroes()
        time.sleep(3)
    open_gilds()


    


ascend()
import pygame as pg
import os, time, random

TITLE = ""       ### 기본 설정
WIDTH = 640
HEIGHT = 480
FPS = 60
DEFAULT_FONT = "온글잎 류뚱체.ttf"

WHITE = (238, 238, 238)     ### 색 설정
BLACK = (32, 36, 32)
RED = (246, 36, 74)
BLUE = (32, 105, 246)
ALPHA_MAX = 255

class Game:
    def __init__(self): ########################## 게임 시작
        pg.init()
        pg.mixer.init()     #sound mixer
        pg.display.set_caption(TITLE)       #title name
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))      #screen size
        self.screen_mode = 0    #screen mode (0: logo, 1: logo2, 2: main, 3: stage select, 4: play, 5: score)
        self.screen_value = [-ALPHA_MAX, 0, 0, 0]       #screen management value
        self.clock = pg.time.Clock()        #FPS timer
        self.start_tick = 0     #game timer
        self.running = True     #game initialize Boolean value
        self.language_mode = 0         #0: english, 1: korean, 2~: custom
        self.song_select = 1    #select song
        self.load_data()        #data loading
        self.new()
        pg.mixer.music.load(self.bg_main)       #bgm
    
    def load_data(self):
        self.dir = os.path.dirname(__file__)
        
        ###폰트
        self.fnt_dir = os.path.join(self.dir, 'font')
        self.gameFont = os.path.join(self.fnt_dir, DEFAULT_FONT)
        
        with open(os.path.join(self.fnt_dir, 'language.ini'), "r", encoding = 'UTF-8') as language_file:
            language_lists = language_file.read().split('\n')
            
        self.language_list = [n.split("_") for n in language_lists]
        
        ###이미지
        self.img_dir = os.path.join(self.dir, 'image')
        pg.display.set_icon(pg.image.load(os.path.join(self.img_dir, 'icon.png')))  ##아이콘 설정
        self.spr_printed = pg.image.load(os.path.join(self.img_dir, 'printed.png'))
        self.spr_logoback = pg.image.load(os.path.join(self.img_dir, 'logoback.png'))
        self.spr_logo = pg.image.load(os.path.join(self.img_dir, 'logo.png'))
        self.spr_circle = pg.image.load(os.path.join(self.img_dir, 'circle.png'))
        self.spr_shot = pg.image.load(os.path.join(self.img_dir, 'shot.png'))
        
        ###소리
        self.snd_dir = os.path.join(self.dir, 'sound')
        self.bg_main = os.path.join(self.snd_dir, 'bg_main.ogg')
        self.sound_click = pg.mixer.Sound(os.path.join(self.snd_dir, 'click.ogg'))
        self.sound_drum1 = pg.mixer.Sound(os.path.join(self.snd_dir, 'drum1.ogg'))
        self.sound_drum2 = pg.mixer.Sound(os.path.join(self.snd_dir, 'drum2.ogg'))
        self.sound_drum3 = pg.mixer.Sound(os.path.join(self.snd_dir, 'drum3.ogg'))
        self.sound_drum4 = pg.mixer.Sound(os.path.join(self.snd_dir, 'drum4.ogg'))
        
        ###노래
        self.sng_dir = os.path.join(self.dir, 'song')
        music_type = ["ogg", "mp3", "wav"]
        song_lists = [i for i in os.listdir(self.sng_dir) if i.split('.')[-1] in music_type]
        self.song_list = list()         # song name list
        self.song_path = list()         # song path list
        
        for song in song_lists:
            try:
                pg.mixer.music.load(os.path.join(self.sng_dir, song))
                self.song_list.append(song.split('.')[0])
                self.song_path.append(os.path.join(self.sng_dir, song))
            except:
                print("error: " + str(song) + "is unsupported format music file.")

        self.song_num = len(self.song_list)     # available song number
        self.song_dataPath = list()                 # song data file path list
        self.song_highScore = list()            # song highscore list
        self.song_perfectScore = list()            # song maxscore list
        
        for song in self.song_list:
            song_dataCoord = os.path.join(self.sng_dir, song + ".ini")

            try:
                with open(song_dataCoord, "r", encoding = 'UTF-8') as song_file:
                    song_scoreList = song_file.read().split('\n')[0]
                    
                self.song_highScore.append(int(song_scoreList.split(':')[1]))
                self.song_perfectScore.append(int(song_scoreList.split(':')[2]))
                self.song_dataPath.append(song_dataCoord) 
            except:
                print("error: " + str(song) + "'s song data file is damaged or does not exist.")
                self.song_highScore.append(-1)
                self.song_perfectScore.append(-1)
                self.song_dataPath.append(-1) 
                
    def new(self):
        self.song_data = list()   ###노래 데이터 리스트
        self.song_dataLen = 0    ###노래 데이터 len
        self.song_dataIndex = 0  ###노래 데이터 index
        self.circle_dir = 1
        self.circle_rot = 0
        self.score = 0
        self.all_sprites = pg.sprite.Group()
        self.shots = pg.sprite.Group()
        
    def run(self):
        self.playing = True
        
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()
            pg.display.flip()
            
        pg.mixer.music.fadeout(600)
        
    def update(self):
        self.all_sprites.update()
        self.game_tick = pg.time.get_ticks() - self.start_tick
        
    def events(self):
        
        
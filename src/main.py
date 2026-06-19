import time
import keyboard
import pygame
import math

# ==========================================
# ส่วนที่ 1: ตั้งค่าระบบเสียง (Audio Setup)
# ==========================================
pygame.mixer.init()
door_channel = pygame.mixer.Channel(1)

class DummySound:
    def play(self, loops=0): pass
    def set_volume(self, vol): pass

try:
    walk_sound = pygame.mixer.Sound("../sounds/Step/hero_walk_step.wav")
    bump_sound = pygame.mixer.Sound("../sounds/SFX/wall_bump.wav")
    door_sound = pygame.mixer.Sound("../sounds/SFX/door_audio_cue.wav")
except:
    print("คำเตือน: หาไฟล์เสียงบางไฟล์ไม่พบ!")
    walk_sound = DummySound()
    bump_sound = DummySound()
    door_sound = DummySound()

def play_ambience():
    try:
        pygame.mixer.music.load("../sounds/Ambience/birds_ambience.ogg")
        pygame.mixer.music.set_volume(0.8)  
        pygame.mixer.music.play(-1) 
    except:
        print("คำเตือน: หาไฟล์เสียงบรรยากาศไม่พบ!")

# ==========================================
# ส่วนที่ 2: ตั้งค่าตัวละครและแผนที่
# ==========================================
hero_x = 1
hero_y = 1
map_width = 10
map_height = 10

# กำหนดตำแหน่งของประตู (เป้าหมาย)
door_x = 10
door_y = 6

enemies = [
    {"name": "มังกรเวิ่นเว้อ", "x": 5, "y": 5}
]

print("--- ยินดีต้อนรับสู่เกมส์เอาชีวิตรอด ---")
print("คำแนะนำ:")
print("- กดลูกศร ขึ้น ลง ซ้าย ขวา เพื่อเดิน")
print("- กด Spacebar เพื่อกระทำ (Action) เช่น เปิดประตู หรือเก็บของ")
print("- กด m เพื่อฟังตำแหน่งของคุณ")
print("- กด e เพื่อฟังตำแหน่งศัตรู")
print("- กด esc เพื่อออกจากเกม")

# ==========================================
# ลอจิกคำนวณความดังของเสียงตามระยะทาง (Spatial Audio)
# ==========================================
def update_positional_audio():
    distance = math.hypot(hero_x - door_x, hero_y - door_y)
    max_distance = math.hypot(map_width, map_height)
    volume = 1.0 - (distance / max_distance)
    if volume < 0:
        volume = 0.0
    door_channel.set_volume(volume)

play_ambience()
door_channel.play(door_sound, loops=-1)
update_positional_audio()

# ==========================================
# ส่วนที่ 3: ระบบการเดินและการกดปุ่ม (Game Loop)
# ==========================================
escaped = False
move_delay = 0.3 

while not escaped:
    
    moved = False
    hit_wall = False

    # ตรวจสอบการกดปุ่มทิศทาง
    if keyboard.is_pressed('up'):
        if hero_y > 1:        
            hero_y -= 1       
            moved = True
        else:
            hit_wall = True   

    elif keyboard.is_pressed('down'):
        if hero_y < map_height: 
            hero_y += 1         
            moved = True
        else:
            hit_wall = True     

    elif keyboard.is_pressed('left'):
        if hero_x > 1:          
            hero_x -= 1         
            moved = True
        else:
            hit_wall = True     

    elif keyboard.is_pressed('right'):
        if hero_x < map_width:  
            hero_x += 1         
            moved = True
        else:
            hit_wall = True     

    # ------------------------------------------
    # ปุ่ม Action (Spacebar) สำหรับโต้ตอบกับสิ่งรอบตัว
    # ------------------------------------------
    elif keyboard.is_pressed('space'):
        # เช็คว่าตอนที่กด Spacebar ฮีโร่ยืนอยู่ตรงกับสิ่งของอะไรบ้าง
        if hero_x == door_x and hero_y == door_y:
            print("เปิดประตูสำเร็จ! คุณเดินออกจากห้องได้แล้ว")
            pygame.mixer.music.stop() 
            door_channel.stop()
            escaped = True
            time.sleep(1) 
        else:
            # ถ้ากดยกเลิกในที่ว่างเปล่า (ไม่มีอะไรให้ทำ)
            print("ความว่างเปล่า") 
            time.sleep(0.5)

    # คีย์ลัด M: เช็คพิกัดตัวเอง
    elif keyboard.is_pressed('m'):
        print(f"ตำแหน่งของคุณตอนนี้คือ X: {hero_x}, Y: {hero_y}")
        time.sleep(0.5) 

    # คีย์ลัด E: เช็คพิกัดศัตรู
    elif keyboard.is_pressed('e'):
        if len(enemies) > 0:
            for enemy in enemies:
                print(f"ศัตรู {enemy['name']} อยู่ที่พิกัด X: {enemy['x']}, Y: {enemy['y']}")
        else:
            print("ไม่มีศัตรูในบริเวณนี้")
        time.sleep(0.5)

    # คีย์ลัด ESC: ออกจากเกม
    elif keyboard.is_pressed('esc'):
        print("ออกจากเกมเรียบร้อยแล้ว")
        break

    # ==========================================
    # ลอจิกการเล่นเสียงและการแจ้งเตือนเมื่อเดิน
    # ==========================================
    if moved:
        walk_sound.play() 
        update_positional_audio() 
        
        # ถ้าย้ายตำแหน่งมาทับกับพิกัดสิ่งของ ให้พิมพ์บอกเพื่อให้ NVDA อ่านทันที
        if hero_x == door_x and hero_y == door_y:
            print("ประตู") 
            
        time.sleep(move_delay) 
        
    elif hit_wall:
        bump_sound.play() 
        time.sleep(move_delay)
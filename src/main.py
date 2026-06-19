import time
import keyboard  # ไลบรารีสำหรับจับการกดคีย์บอร์ดแบบเรียลไทม์
import pygame    # ไลบรารีสำหรับระบบเสียง
import math      # ไลบรารีสำหรับคำนวณคณิตศาสตร์ (ใช้หาระยะห่างเพื่อทำเสียง 3 มิติ)

# ==========================================
# ส่วนที่ 1: ตั้งค่าระบบเสียง (Audio Setup)
# ==========================================
pygame.mixer.init()

# จองช่องสัญญาณเสียง (Channel) แยกต่างหาก เพื่อไม่ให้เสียงประตูโดนเสียงเดินขัดจังหวะ
door_channel = pygame.mixer.Channel(1)

# สร้างคลาสกันชน (Dummy) เผื่อกรณีเด็กๆ ลืมใส่ไฟล์เสียง เกมจะได้ไม่พังและไปต่อได้
class DummySound:
    def play(self, loops=0): pass
    def set_volume(self, vol): pass

# โหลดเสียงเอฟเฟกต์ (ใส่ไว้ในตัวแปรเพื่อเรียกใช้ง่ายๆ)
try:
    walk_sound = pygame.mixer.Sound("../sounds/Step/hero_walk_step.wav")
    bump_sound = pygame.mixer.Sound("../sounds/SFX/wall_bump.wav")
    door_sound = pygame.mixer.Sound("../sounds/SFX/door_audio_cue.wav") # <--- เพิ่มเสียงประตู
except:
    print("คำเตือน: หาไฟล์เสียงบางไฟล์ไม่พบ!")
    walk_sound = DummySound()
    bump_sound = DummySound()
    door_sound = DummySound()

# ฟังก์ชันเล่นเสียงบรรยากาศ
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

# กำหนดตำแหน่งของประตู
door_x = 10
door_y = 6

# จำลองข้อมูลศัตรู
enemies = [
    {"name": "มังกรเวิ่นเว้อ", "x": 5, "y": 5}
]

print("--- ยินดีต้อนรับสู่เกมส์เอาชีวิตรอด ---")
print("คำแนะนำ:")
print("- กดลูกศร ขึ้น ลง ซ้าย ขวา เพื่อเดิน (กดค้างได้)")
print("- กด m เพื่อฟังตำแหน่งของคุณ")
print("- กด e เพื่อฟังตำแหน่งศัตรู")
print("- กด esc เพื่อออกจากเกม")

# ==========================================
# ลอจิกคำนวณความดังของเสียงตามระยะทาง (Spatial Audio)
# ==========================================
def update_positional_audio():
    # 1. หาระยะห่าง (Distance) ระหว่างฮีโร่กับประตู ด้วยสูตรคณิตศาสตร์
    distance = math.hypot(hero_x - door_x, hero_y - door_y)
    
    # 2. หาระยะห่างที่ไกลที่สุดของแผนที่ 10x10 (ประมาณ 14.14 หน่วย)
    max_distance = math.hypot(map_width, map_height)
    
    # 3. คำนวณความดัง: ยิ่งระยะห่างน้อย ความดังยิ่งเข้าใกล้ 1.0 (100%)
    volume = 1.0 - (distance / max_distance)
    
    # กันเหนียว: ป้องกันไม่ให้ค่าเสียงติดลบ
    if volume < 0:
        volume = 0.0
        
    # สั่งให้ช่องเสียงของประตูเปลี่ยนความดังตามที่คำนวณได้
    door_channel.set_volume(volume)

# เริ่มเปิดเสียงนกร้องบรรยากาศ
play_ambience()

# เริ่มเล่นเสียงประตูวนลูปไปเรื่อยๆ (loops=-1) พร้อมตั้งค่าความดังตามตำแหน่งเริ่มต้น
door_channel.play(door_sound, loops=-1)
update_positional_audio()

# ==========================================
# ส่วนที่ 3: ระบบการเดิน (Game Loop)
# ==========================================
escaped = False
move_delay = 0.3 

while not escaped:
    
    moved = False
    hit_wall = False

    # ตรวจสอบการกดปุ่ม
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
    # ลอจิกการเล่นเสียงเมื่อเกิดเหตุการณ์
    # ==========================================
    if moved:
        walk_sound.play() 
        # <--- อัปเดตความดังของเสียงประตูทุกครั้งที่ก้าวเดิน
        update_positional_audio() 
        time.sleep(move_delay) 
        
    elif hit_wall:
        bump_sound.play() 
        time.sleep(move_delay) 

    # ==========================================
    # เงื่อนไขการเจอสิ่งของหรือประตู
    # ==========================================
    # เช็คว่าผู้เล่นเดินมาทับตำแหน่งเดียวกับประตูหรือไม่
    if hero_x == door_x and hero_y == door_y:
        print("ประตู") # แจ้งเตือนเมื่อเดินมาถึงจุดที่เป็นประตู
        print("คุณเดินออกจากประตูสำเร็จแล้ว!")
        
        # หยุดเสียงทั้งหมดเมื่อหนีสำเร็จ
        pygame.mixer.music.stop() 
        door_channel.stop()
        
        escaped = True
        time.sleep(1)
import time
import keyboard  # ไลบรารีสำหรับจับการกดคีย์บอร์ดแบบเรียลไทม์
import pygame    # ไลบรารีสำหรับระบบเสียง

# ==========================================
# ส่วนที่ 1: ตั้งค่าระบบเสียง (Audio Setup)
# ==========================================
pygame.mixer.init()

# สร้างคลาสกันชน (Dummy) เผื่อกรณีเด็กๆ ลืมใส่ไฟล์เสียง เกมจะได้ไม่พังและไปต่อได้
class DummySound:
    def play(self): pass

# โหลดเสียงเอฟเฟกต์ (ใส่ไว้ในตัวแปรเพื่อเรียกใช้ง่ายๆ)
try:
    walk_sound = pygame.mixer.Sound("../sounds/Step/hero_walk_step.wav")
    bump_sound = pygame.mixer.Sound("../sounds/SFX/wall_bump.wav")
except:
    print("คำเตือน: หาไฟล์เสียงเดินหรือเสียงชนกำแพงไม่พบ!")
    walk_sound = DummySound()
    bump_sound = DummySound()

# ฟังก์ชันเล่นเสียงบรรยากาศ
def play_ambience():
    try:
        pygame.mixer.music.load("../sounds/Ambience/birds_ambience.ogg")
        pygame.mixer.music.set_volume(0.8)  # <--- เพิ่มบรรทัดนี้เพื่อตั้งความดัง 80%
        pygame.mixer.music.play(-1) # -1 หมายถึงให้เล่นวนลูปไปเรื่อยๆ ไม่จบ
    except:
        print("คำเตือน: หาไฟล์เสียงบรรยากาศไม่พบ!")

# ==========================================
# ส่วนที่ 2: ตั้งค่าตัวละครและแผนที่
# ==========================================
hero_x = 1
hero_y = 1
map_width = 10
map_height = 10

# จำลองข้อมูลศัตรูเพื่อให้คีย์ลัด 'e' ทำงานได้
enemies = [
    {"name": "มังกรเวิ่นเว้อ", "x": 5, "y": 5}
]

print("--- ยินดีต้อนรับสู่เกมส์เอาชีวิตรอด ---")
print("คำแนะนำ:")
print("- กดลูกศร ขึ้น ลง ซ้าย ขวา เพื่อเดิน (กดค้างได้)")
print("- กด m เพื่อฟังตำแหน่งของคุณ")
print("- กด e เพื่อฟังตำแหน่งศัตรู")
print("- กด esc เพื่อออกจากเกม")

# เริ่มเปิดเสียงนกร้องบรรยากาศ
play_ambience()

# ==========================================
# ส่วนที่ 3: ระบบการเดิน (Game Loop)
# ==========================================
escaped = False
move_delay = 0.3 # หน่วงเวลา 0.3 วินาทีต่อก้าว เพื่อไม่ให้ตัวละครวิ่งเร็วเกินไปเวลากดค้าง

while not escaped:
    
    # สร้างตัวแปรมาเช็คว่ามีการขยับ หรือ มีการชนกำแพง เกิดขึ้นหรือไม่ในรอบนี้
    moved = False
    hit_wall = False

    # ตรวจสอบการกดปุ่ม (ทำงานทันทีเมื่อกดค้าง)
    if keyboard.is_pressed('up'):
        if hero_y > 1:        # ถ้ายังไม่สุดขอบบน
            hero_y -= 1       # เดินขึ้น
            moved = True
        else:
            hit_wall = True   # ชนกำแพงบน

    elif keyboard.is_pressed('down'):
        if hero_y < map_height: # ถ้ายังไม่สุดขอบล่าง
            hero_y += 1         # เดินลง
            moved = True
        else:
            hit_wall = True     # ชนกำแพงล่าง

    elif keyboard.is_pressed('left'):
        if hero_x > 1:          # ถ้ายังไม่สุดขอบซ้าย
            hero_x -= 1         # เดินซ้าย
            moved = True
        else:
            hit_wall = True     # ชนกำแพงซ้าย

    elif keyboard.is_pressed('right'):
        if hero_x < map_width:  # ถ้ายังไม่สุดขอบขวา
            hero_x += 1         # เดินขวา
            moved = True
        else:
            hit_wall = True     # ชนกำแพงขวา

    # คีย์ลัด M: เช็คพิกัดตัวเอง
    elif keyboard.is_pressed('m'):
        print(f"ตำแหน่งของคุณตอนนี้คือ X: {hero_x}, Y: {hero_y}")
        time.sleep(0.5) # หน่วงเวลาไว้เพื่อไม่ให้ NVDA อ่านซ้ำรัวๆ เวลากดค้าง

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
        walk_sound.play() # เล่นเสียงเดิน 1 ก้าว
        time.sleep(move_delay) # รอ 0.3 วิ ก่อนรับคำสั่งก้าวต่อไป (ป้องกันก้าวเดินรัวเกินไป)
        
    elif hit_wall:
        bump_sound.play() # เล่นเสียงชนกำแพง
        time.sleep(move_delay) # ให้รอเวลาเท่ากัน เพื่อให้เสียงชนดังเป็นจังหวะเวลากดดันกำแพงค้างไว้

    # ==========================================
    # เงื่อนไขการหาทางออก
    # ==========================================
    if hero_x == 10 and hero_y == 2:
        print("คุณเดินออกจากประตูสำเร็จแล้ว!")
        pygame.mixer.music.stop() # ปิดเสียงบรรยากาศเมื่อออกจากแผนที่
        escaped = True
        time.sleep(1) # รอ 1 วินาทีให้ผู้เล่นตั้งตัวก่อนเข้าเมนูถัดไป
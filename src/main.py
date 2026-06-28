import time
import keyboard
import pygame
import math
import json
import os
from class_hero import Hero
from accessible_output2.outputs.auto import Auto

# ==========================================
# ส่วนที่ 1: ตั้งค่าระบบเสียง และ NVDA
# ==========================================
pygame.mixer.init()
door_channel = pygame.mixer.Channel(1)

# สร้างลำโพงสำหรับส่งข้อความให้โปรแกรมอ่านหน้าจอ (NVDA/JAWS)
speaker = Auto()

class DummySound:
    def play(self, loops=0): pass
    def set_volume(self, vol): pass
    def stop(self): pass

# โหลดไฟล์เสียงเอฟเฟกต์
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
# ส่วนที่ 2: ตั้งค่าตัวละคร แผนที่ และบล็อกคีย์บอร์ด
# ==========================================
hero_x = 1
hero_y = 1
map_width = 10
map_height = 10
door_x = 10
door_y = 6

enemies = [
    {"name": "มังกรเวิ่นเว้อ", "x": 5, "y": 5}
]

print("--- ยินดีต้อนรับสู่เกมส์เอาชีวิตรอด ---")
speaker.output("เริ่มเกมแล้ว กดลูกศรเพื่อเดิน", interrupt=True)

# บล็อกปุ่มเหล่านี้ไม่ให้ส่งสัญญาณไปที่ Windows เพื่อกัน NVDA อ่านซ้ำ
keys_to_block = ['up', 'down', 'left', 'right', 'space', 'm', 'e', 'esc']
for key in keys_to_block:
    keyboard.block_key(key)

def update_positional_audio():
    distance = math.hypot(hero_x - door_x, hero_y - door_y)
    max_distance = math.hypot(map_width, map_height)
    volume = 1.0 - (distance / max_distance)
    if volume < 0: volume = 0.0
    door_channel.set_volume(volume)

play_ambience()
door_channel.play(door_sound, loops=-1)
update_positional_audio()

# ==========================================
# ส่วนที่ 3: ระบบการเดินหาประตู (Phase 1)
# ==========================================
escaped = False
move_delay = 0.3 

try:
    while not escaped:
        moved = False
        hit_wall = False

        if keyboard.is_pressed('up'):
            if hero_y > 1:        
                hero_y -= 1       
                moved = True
            else: hit_wall = True   

        elif keyboard.is_pressed('down'):
            if hero_y < map_height: 
                hero_y += 1         
                moved = True
            else: hit_wall = True     

        elif keyboard.is_pressed('left'):
            if hero_x > 1:          
                hero_x -= 1         
                moved = True
            else: hit_wall = True     

        elif keyboard.is_pressed('right'):
            if hero_x < map_width:  
                hero_x += 1         
                moved = True
            else: hit_wall = True     

        # คีย์ลัด Action (Spacebar)
        elif keyboard.is_pressed('space'):
            if hero_x == door_x and hero_y == door_y:
                speaker.output("เปิดประตูสำเร็จ!", interrupt=True)
                pygame.mixer.music.stop() 
                door_channel.stop()
                escaped = True
                time.sleep(1) 
            else:
                speaker.output("ความว่างเปล่า", interrupt=True) 
                time.sleep(0.5)

        # คีย์ลัด M: เช็คพิกัดตัวเอง
        elif keyboard.is_pressed('m'):
            speaker.output(f"ตำแหน่งของคุณ X: {hero_x}, Y: {hero_y}", interrupt=True)
            time.sleep(0.5) 

        # คีย์ลัด E: เช็คพิกัดศัตรู
        elif keyboard.is_pressed('e'):
            if len(enemies) > 0:
                for enemy in enemies:
                    speaker.output(f"ศัตรู {enemy['name']} อยู่ที่พิกัด X: {enemy['x']}, Y: {enemy['y']}", interrupt=True)
            else:
                speaker.output("ไม่มีศัตรูในบริเวณนี้", interrupt=True)
            time.sleep(0.5)

        # คีย์ลัด ESC: ออกจากเกม
        elif keyboard.is_pressed('esc'):
            speaker.output("ออกจากเกมเรียบร้อยแล้ว", interrupt=True)
            break

        # ลอจิกการเล่นเสียงเวลาเดินหรือชนกำแพง
        if moved:
            walk_sound.play() 
            update_positional_audio() 
            if hero_x == door_x and hero_y == door_y:
                speaker.output("ประตู", interrupt=True)
            time.sleep(move_delay) 
            
        elif hit_wall:
            bump_sound.play() 
            time.sleep(move_delay) 

# คืนค่าคีย์บอร์ดทั้งหมดให้ Windows เมื่อจบ Phase 1
finally:
    keyboard.unhook_all()
    print("คืนค่าคีย์บอร์ดเรียบร้อย")

# ==========================================
# Phase 2: ระบบเลือกอาชีพ (Audio Menu Navigation)
# ==========================================
if escaped:
    print("\n--- เข้าสู่ระบบเลือกอาชีพ ---")
    
    # แจ้งประโยคสั้นๆ เพื่อให้รู้ว่าเข้าเมนูแล้ว
    speaker.output("กรุณาเลือกอาชีพของตัวละคร", interrupt=True)
    time.sleep(1.5)
    
    # ใช้ os.path เพื่อระบุตำแหน่งโฟลเดอร์ json อย่างชัดเจน
    base_dir = os.path.dirname(os.path.abspath(__file__)) 
    json_path = os.path.join(base_dir, "../json/hero_classes.json") 
    
    try:
        with open(json_path, 'r', encoding='utf-8') as file:
            class_data = json.load(file)["classes"]
    except Exception as e:
        speaker.output("เกิดข้อผิดพลาด หาไฟล์ข้อมูลอาชีพไม่พบ", interrupt=True)
        print(f"Error: {e}")
        exit()

    class_keys = list(class_data.keys()) 
    
    # บล็อกปุ่มอีกครั้งเฉพาะลูกศรและเอนเทอร์สำหรับใช้ในเมนู
    keys_to_block_menu = ['up', 'down', 'enter']
    for key in keys_to_block_menu:
        keyboard.block_key(key)
        
    current_index = 0
    selected_class_id = None

    def speak_current_class():
        key = class_keys[current_index]
        c = class_data[key]
        job_info = f"{c['name']} hp {c['base_hp']} Attack {c['base_attack']} Defense {c['base_defense']}"
        print(f"> {job_info}")
        speaker.output(job_info, interrupt=True) # interrupt=True เพื่อให้เคอร์เซอร์เลื่อนปุ๊บอ่านปั๊บทันที
        
    # อ่านอาชีพแรกให้ฟัง
    speak_current_class()
    
    try:
        while selected_class_id is None:
            
            if keyboard.is_pressed('down'):
                if current_index < len(class_keys) - 1:
                    current_index += 1 
                else:
                    current_index = 0 
                speak_current_class()
                
                # ลอจิกป้องกันความหน่วง: สั่งให้รอจนกว่าจะปล่อยนิ้วจากปุ่มลง
                while keyboard.is_pressed('down'):
                    time.sleep(0.01)
                    
            elif keyboard.is_pressed('up'):
                if current_index > 0:
                    current_index -= 1 
                else:
                    current_index = len(class_keys) - 1 
                speak_current_class()
                
                # สั่งให้รอจนกว่าจะปล่อยนิ้วจากปุ่มขึ้น
                while keyboard.is_pressed('up'):
                    time.sleep(0.01)
                    
            elif keyboard.is_pressed('enter'):
                selected_class_id = class_keys[current_index]
                
                # สั่งให้รอจนกว่าจะปล่อยปุ่มเอนเทอร์ เพื่อป้องกันปุ่มค้างทะลุไปตอนจบเกม
                while keyboard.is_pressed('enter'):
                    time.sleep(0.01)

    finally:
        keyboard.unhook_all()

    # ใช้แม่พิมพ์ OOP ดึงข้อมูลอาชีพมาสร้างฮีโร่ตัวจริง
    my_hero = Hero(selected_class_id)
    
    # แจ้งอาชีพที่เลือก และสั่งให้กด enter เพื่อออก
    success_msg = f"คุณเป็นอาชีพ {my_hero.job_name} กด enter เพื่อออกจากเกมส์"
    print(success_msg)
    speaker.output(success_msg, interrupt=True)
    
    # สั่งให้ระบบรอจนกว่าจะกดปุ่ม Enter จากนั้นค่อยรันคำสั่งปิดเกม
    keyboard.wait('enter')
    pygame.quit()
    print("ปิดเกมได้อย่างปลอดภัย")
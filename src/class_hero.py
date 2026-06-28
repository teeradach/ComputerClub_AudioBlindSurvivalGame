import json
import os

class Hero:
    # 1. ฟังก์ชัน __init__ คือการสร้างตัวละคร (Constructor)
    def __init__(self, class_id):
        # ใช้ os.path เพื่อระบุตำแหน่งโฟลเดอร์ json อย่างชัดเจน ป้องกันปัญหาหาไฟล์ไม่เจอ
        base_dir = os.path.dirname(os.path.abspath(__file__))
        json_file = os.path.join(base_dir, "../json/hero_classes.json")
        
        # โหลดข้อมูลจากไฟล์ JSON
        try:
            with open(json_file, 'r', encoding='utf-8') as file:
                data = json.load(file)
                # ดึงข้อมูลอาชีพตามที่ผู้เล่นเลือก
                my_class = data["classes"][class_id]
                
                # กำหนดสถานะ (Status) ให้กับฮีโร่ตัวนี้
                self.job_name = my_class["name"]
                self.max_hp = my_class["base_hp"]
                self.current_hp = self.max_hp
                self.attack_power = my_class["base_attack"]
                self.defense = my_class["base_defense"]
                self.skills = my_class["skills"]
                
                # สถานะพิเศษ (Buff/Debuff)
                self.is_alive = True
                self.status_effect = "normal" 
                
        except Exception as e:
            # ใช้การพิมพ์ข้อความเพื่อให้ NVDA อ่านหากเกิดข้อผิดพลาดในการโหลดไฟล์
            print(f"เกิดข้อผิดพลาดในการโหลดไฟล์อาชีพ: {e}")

    # 2. ฟังก์ชันแสดงสถานะ (ใช้สำหรับกดเช็คสถานะด้วยปุ่ม x)
    def get_status_speech(self):
        return f"ผู้เล่น อาชีพ {self.job_name} เลือด : {self.current_hp} จาก {self.max_hp}"

    # 3. ฟังก์ชันรับความเสียหาย (โดนโจมตี)
    def take_damage(self, damage):
        # คำนวณความเสียหายหักลบด้วยพลังป้องกันเบื้องต้น
        actual_damage = max(1, damage - self.defense)
        self.current_hp -= actual_damage
        
        if self.current_hp <= 0:
            self.current_hp = 0
            self.is_alive = False
            
        return actual_damage

    # 4. ฟังก์ชันฟื้นฟูเลือด
    def heal(self, percent):
        heal_amount = int(self.max_hp * (percent / 100))
        self.current_hp += heal_amount
        if self.current_hp > self.max_hp:
            self.current_hp = self.max_hp
        return heal_amount

    # 5. ฟังก์ชันดึงรายชื่อสกิลทั้งหมดมาทำเป็นเมนู
    def get_skill_menu(self):
        menu_text = f"ทักษะของ {self.job_name}: \n"
        for i, skill in enumerate(self.skills):
            menu_text += f"กด {i+1} {skill['name']} ({skill['description']})\n"
        return menu_text
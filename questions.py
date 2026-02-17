"""
Questions database for Zakovati Elite Bot
Barcha fanlar bo'yicha savollar - Bosqichma-bosqich qiyinlashuv
"""

from typing import List, Dict

# Savollar bazasi
# Format: { q: "savol matni", a: ["variant1", "variant2", "variant3"], c: to'g'ri_javob_indeksi, p: ball, f: "fan", d: "qiyinlik" }
# Qiyinlik darajalari: "oson" (10-15 ball), "o'rta" (20-30 ball), "qiyin" (40-60 ball), "juda_qiyin" (80-100 ball)

QUESTIONS = [
    # ==================== INFORMATIKA - OSON ====================
    {
        "q": "Kompyuterning asosiy xotirasini nima deb ataladi?",
        "a": ["RAM", "ROM", "HDD", "SSD"],
        "c": 0,
        "p": 10,
        "f": "Informatika",
        "d": "oson"
    },
    {
        "q": "HTML nima uchun ishlatiladi?",
        "a": ["Dasturlash uchun", "Veb sahifa yaratish uchun", "Ma'lumotlar bazasi uchun", "Grafika uchun"],
        "c": 1,
        "p": 10,
        "f": "Informatika",
        "d": "oson"
    },
    {
        "q": "CPU ning to'liq nomi nima?",
        "a": ["Central Processing Unit", "Computer Processing Unit", "Central Program Unit", "Computer Program Unit"],
        "c": 0,
        "p": 15,
        "f": "Informatika",
        "d": "oson"
    },
    {
        "q": "1 kilobayt necha baytga teng?",
        "a": ["1000 bayt", "1024 bayt", "100 bayt", "512 bayt"],
        "c": 1,
        "p": 15,
        "f": "Informatika",
        "d": "oson"
    },
    
    # ==================== INFORMATIKA - O'RTA ====================
    {
        "q": "Python dasturlash tilida qaysi operatordan sikl uchun foydalaniladi?",
        "a": ["loop", "for", "repeat", "cycle"],
        "c": 1,
        "p": 20,
        "f": "Informatika",
        "d": "o'rta"
    },
    {
        "q": "HTTP protokolining to'liq nomi nima?",
        "a": ["HyperText Transfer Protocol", "High Transfer Text Protocol", "Hyper Transfer Tool Protocol", "HyperText Tool Protocol"],
        "c": 0,
        "p": 20,
        "f": "Informatika",
        "d": "o'rta"
    },
    {
        "q": "Binary tizimda 1011 soni o'nlik sanoq sistemasida nechaga teng?",
        "a": ["9", "10", "11", "12"],
        "c": 2,
        "p": 25,
        "f": "Informatika",
        "d": "o'rta"
    },
    {
        "q": "Qaysi dasturlash tili web development uchun eng ko'p ishlatiladi?",
        "a": ["Python", "JavaScript", "C++", "Java"],
        "c": 1,
        "p": 25,
        "f": "Informatika",
        "d": "o'rta"
    },
    {
        "q": "SQL nima uchun ishlatiladi?",
        "a": ["Web dizayn", "Ma'lumotlar bazasi", "Grafika", "Audio qayta ishlash"],
        "c": 1,
        "p": 30,
        "f": "Informatika",
        "d": "o'rta"
    },
    
    # ==================== INFORMATIKA - QIYIN ====================
    {
        "q": "Big O notation O(n²) ning ma'nosi nima?",
        "a": ["Kvadratik murakkablik", "Chiziqli murakkablik", "Logarifmik murakkablik", "Eksponensial murakkablik"],
        "c": 0,
        "p": 40,
        "f": "Informatika",
        "d": "qiyin"
    },
    {
        "q": "TCP/IP modelida nechta qatlam bor?",
        "a": ["3 ta", "4 ta", "5 ta", "7 ta"],
        "c": 1,
        "p": 50,
        "f": "Informatika",
        "d": "qiyin"
    },
    {
        "q": "Recursion nima?",
        "a": ["Funksiyaning o'zini chaqirishi", "Sikl turi", "Ma'lumot strukturasi", "Algoritm turi"],
        "c": 0,
        "p": 60,
        "f": "Informatika",
        "d": "qiyin"
    },
    
    # ==================== INFORMATIKA - JUDA QIYIN ====================
    {
        "q": "Qaysi ma'lumot strukturasi LIFO (Last In First Out) printsipida ishlaydi?",
        "a": ["Queue", "Stack", "Tree", "Graph"],
        "c": 1,
        "p": 80,
        "f": "Informatika",
        "d": "juda_qiyin"
    },
    {
        "q": "RESTful API da PUT va PATCH metodlari orasidagi farq nima?",
        "a": ["PUT to'liq yangilaydi, PATCH qisman", "Farq yo'q", "PATCH to'liq yangilaydi", "PUT faqat o'chirish uchun"],
        "c": 0,
        "p": 100,
        "f": "Informatika",
        "d": "juda_qiyin"
    },
    
    # ==================== BIOLOGIYA - OSON ====================
    {
        "q": "Yurak necha kameradan iborat?",
        "a": ["2 ta", "3 ta", "4 ta", "5 ta"],
        "c": 2,
        "p": 10,
        "f": "Biologiya",
        "d": "oson"
    },
    {
        "q": "Eng katta organ qaysi?",
        "a": ["Jigar", "Yurak", "Teri", "Miya"],
        "c": 2,
        "p": 10,
        "f": "Biologiya",
        "d": "oson"
    },
    {
        "q": "Inson tanasida qancha suyak bor?",
        "a": ["186 ta", "206 ta", "226 ta", "246 ta"],
        "c": 1,
        "p": 15,
        "f": "Biologiya",
        "d": "oson"
    },
    {
        "q": "Qon aylanish sistemasi nima vazifani bajaradi?",
        "a": ["Hazm qilish", "Kislorod tashish", "Nafas olish", "Harakat"],
        "c": 1,
        "p": 15,
        "f": "Biologiya",
        "d": "oson"
    },
    
    # ==================== BIOLOGIYA - O'RTA ====================
    {
        "q": "Hujayraning energiya ishlab chiqaruvchi qismi qaysi?",
        "a": ["Yadro", "Mitoxondriya", "Ribosoma", "Golji apparati"],
        "c": 1,
        "p": 20,
        "f": "Biologiya",
        "d": "o'rta"
    },
    {
        "q": "DNK molekulasida nechta asosiy nukleotid bor?",
        "a": ["2 ta", "3 ta", "4 ta", "5 ta"],
        "c": 2,
        "p": 25,
        "f": "Biologiya",
        "d": "o'rta"
    },
    {
        "q": "Fotosintez jarayoni qayerda sodir bo'ladi?",
        "a": ["Mitoxondriyada", "Yadroda", "Xloroplastda", "Ribosomada"],
        "c": 2,
        "p": 25,
        "f": "Biologiya",
        "d": "o'rta"
    },
    {
        "q": "Genetika fanining otasi kim?",
        "a": ["Charles Darwin", "Gregori Mendel", "Louis Paster", "Ivan Pavlov"],
        "c": 1,
        "p": 30,
        "f": "Biologiya",
        "d": "o'rta"
    },
    
    # ==================== BIOLOGIYA - QIYIN ====================
    {
        "q": "Qon guruhlarini kim kashf etgan?",
        "a": ["Karl Landshteyn", "Louis Paster", "Gregori Mendel", "Charles Darwin"],
        "c": 0,
        "p": 40,
        "f": "Biologiya",
        "d": "qiyin"
    },
    {
        "q": "RNK va DNK orasidagi asosiy farq nima?",
        "a": ["RNK bir zanjirli", "DNK bir zanjirli", "Farq yo'q", "RNK faqat bakteriyalarda"],
        "c": 0,
        "p": 50,
        "f": "Biologiya",
        "d": "qiyin"
    },
    {
        "q": "Meyoz jarayonida nechta hujayra hosil bo'ladi?",
        "a": ["2 ta", "4 ta", "6 ta", "8 ta"],
        "c": 1,
        "p": 60,
        "f": "Biologiya",
        "d": "qiyin"
    },
    
    # ==================== BIOLOGIYA - JUDA QIYIN ====================
    {
        "q": "CRISPR texnologiyasi nima uchun ishlatiladi?",
        "a": ["Gen tahrirlash", "Protein sintezi", "Hujayra bo'linishi", "Fotosintez"],
        "c": 0,
        "p": 80,
        "f": "Biologiya",
        "d": "juda_qiyin"
    },
    {
        "q": "Epigenetika nima bilan shug'ullanadi?",
        "a": ["DNK ketma-ketligi o'zgarmasdan genlar ifodasining o'zgarishi", "Yangi turlarning paydo bo'lishi", "Hujayra ko'payishi", "Protein sintezi"],
        "c": 0,
        "p": 100,
        "f": "Biologiya",
        "d": "juda_qiyin"
    },
    
    # ==================== FIZIKA - OSON ====================
    {
        "q": "Elektr tokining birligi nima?",
        "a": ["Volt", "Amper", "Om", "Vatt"],
        "c": 1,
        "p": 10,
        "f": "Fizika",
        "d": "oson"
    },
    {
        "q": "Gravitatsiya tezlanishi Yerda qancha?",
        "a": ["9.8 m/s²", "10 m/s²", "8.9 m/s²", "11 m/s²"],
        "c": 0,
        "p": 15,
        "f": "Fizika",
        "d": "oson"
    },
    {
        "q": "Tovush to'lqini qaysi muhitda eng tez tarqaladi?",
        "a": ["Havo", "Suv", "Temir", "Vakuum"],
        "c": 2,
        "p": 15,
        "f": "Fizika",
        "d": "oson"
    },
    
    # ==================== FIZIKA - O'RTA ====================
    {
        "q": "Yorug'lik tezligi qancha (vakuumda)?",
        "a": ["300,000 km/s", "150,000 km/s", "500,000 km/s", "200,000 km/s"],
        "c": 0,
        "p": 20,
        "f": "Fizika",
        "d": "o'rta"
    },
    {
        "q": "Nyutonning birinchi qonuni nima haqida?",
        "a": ["Inersiya", "Kuch", "Harakat", "Energiya"],
        "c": 0,
        "p": 25,
        "f": "Fizika",
        "d": "o'rta"
    },
    {
        "q": "Om qonuni qanday ifodalanadi?",
        "a": ["V = IR", "I = VR", "R = VI", "V = I/R"],
        "c": 0,
        "p": 25,
        "f": "Fizika",
        "d": "o'rta"
    },
    {
        "q": "Tovush tezligi havoda qancha?",
        "a": ["330 m/s", "340 m/s", "350 m/s", "320 m/s"],
        "c": 1,
        "p": 30,
        "f": "Fizika",
        "d": "o'rta"
    },
    
    # ==================== FIZIKA - QIYIN ====================
    {
        "q": "Energiyaning saqlanish qonunini kim kashf etgan?",
        "a": ["Nyuton", "Eynshteyn", "Joul", "Faradey"],
        "c": 2,
        "p": 40,
        "f": "Fizika",
        "d": "qiyin"
    },
    {
        "q": "Absolyut nol temperatura qancha?",
        "a": ["-273.15°C", "-300°C", "-250°C", "-200°C"],
        "c": 0,
        "p": 50,
        "f": "Fizika",
        "d": "qiyin"
    },
    {
        "q": "Doppler effekti nima?",
        "a": ["To'lqin chastotasining manba harakatiga bog'liq o'zgarishi", "Yorug'likning sinishi", "Tovushning aks-sadosi", "Elektr toki"],
        "c": 0,
        "p": 60,
        "f": "Fizika",
        "d": "qiyin"
    },
    
    # ==================== FIZIKA - JUDA QIYIN ====================
    {
        "q": "Shredinger tenglamasi nima bilan bog'liq?",
        "a": ["Kvant mexanikasi", "Klassik mexanika", "Termodinamika", "Optika"],
        "c": 0,
        "p": 80,
        "f": "Fizika",
        "d": "juda_qiyin"
    },
    {
        "q": "Eynshteynning E=mc² formulasida 'c' nima?",
        "a": ["Yorug'lik tezligi", "Energiya", "Massa", "Konstanta"],
        "c": 0,
        "p": 100,
        "f": "Fizika",
        "d": "juda_qiyin"
    },
    
    # ==================== MATEMATIKA - OSON ====================
    {
        "q": "2³ + 5² nechaga teng?",
        "a": ["31", "33", "35", "37"],
        "c": 1,
        "p": 10,
        "f": "Matematika",
        "d": "oson"
    },
    {
        "q": "√144 nechaga teng?",
        "a": ["10", "11", "12", "13"],
        "c": 2,
        "p": 10,
        "f": "Matematika",
        "d": "oson"
    },
    {
        "q": "Uchburchak ichki burchaklari yig'indisi necha gradus?",
        "a": ["90°", "180°", "270°", "360°"],
        "c": 1,
        "p": 15,
        "f": "Matematika",
        "d": "oson"
    },
    {
        "q": "Teng yonli uchburchak nechta teng tomonga ega?",
        "a": ["0 ta", "1 ta", "2 ta", "3 ta"],
        "c": 2,
        "p": 15,
        "f": "Matematika",
        "d": "oson"
    },
    
    # ==================== MATEMATIKA - O'RTA ====================
    {
        "q": "Pi sonining taxminiy qiymati qancha?",
        "a": ["3.14", "3.41", "3.12", "3.21"],
        "c": 0,
        "p": 20,
        "f": "Matematika",
        "d": "o'rta"
    },
    {
        "q": "15% dan 200 ni hisoblang:",
        "a": ["25", "30", "35", "40"],
        "c": 1,
        "p": 25,
        "f": "Matematika",
        "d": "o'rta"
    },
    {
        "q": "2x + 5 = 15 tenglamada x nechaga teng?",
        "a": ["3", "4", "5", "6"],
        "c": 2,
        "p": 25,
        "f": "Matematika",
        "d": "o'rta"
    },
    {
        "q": "12! (faktorial) ning oxirgi raqami qanday?",
        "a": ["0", "2", "4", "6"],
        "c": 0,
        "p": 30,
        "f": "Matematika",
        "d": "o'rta"
    },
    
    # ==================== MATEMATIKA - QIYIN ====================
    {
        "q": "Fibonachchi ketma-ketligida 8-hadni toping: 1, 1, 2, 3, 5, 8, ...",
        "a": ["13", "15", "21", "34"],
        "c": 2,
        "p": 40,
        "f": "Matematika",
        "d": "qiyin"
    },
    {
        "q": "∫x² dx nechaga teng?",
        "a": ["x³/3 + C", "2x + C", "x²/2 + C", "x³ + C"],
        "c": 0,
        "p": 50,
        "f": "Matematika",
        "d": "qiyin"
    },
    {
        "q": "e (Eyler soni) ning taxminiy qiymati qancha?",
        "a": ["2.71", "3.14", "1.61", "2.50"],
        "c": 0,
        "p": 60,
        "f": "Matematika",
        "d": "qiyin"
    },
    
    # ==================== MATEMATIKA - JUDA QIYIN ====================
    {
        "q": "Riman gipotezasi qaysi sohaga tegishli?",
        "a": ["Sonlar nazariyasi", "Geometriya", "Algebra", "Trigonometriya"],
        "c": 0,
        "p": 80,
        "f": "Matematika",
        "d": "juda_qiyin"
    },
    {
        "q": "Kompleks sonlar to'plamini qaysi belgi bilan ifodalanadi?",
        "a": ["ℂ", "ℝ", "ℤ", "ℚ"],
        "c": 0,
        "p": 100,
        "f": "Matematika",
        "d": "juda_qiyin"
    },
    
    # ==================== MANTIQ - OSON ====================
    {
        "q": "Qaysi biri ortiqcha: Olma, Nok, Sabzi, Banan?",
        "a": ["Olma", "Nok", "Sabzi", "Banan"],
        "c": 2,
        "p": 10,
        "f": "Mantiq",
        "d": "oson"
    },
    {
        "q": "KITOB so'zini teskari yozsak qanday bo'ladi?",
        "a": ["BOTIK", "KOTIB", "TIKOB", "BITOK"],
        "c": 0,
        "p": 10,
        "f": "Mantiq",
        "d": "oson"
    },
    {
        "q": "Agar A = 1, B = 2, C = 3 bo'lsa, 'CAB' so'zining raqamlar yig'indisi nechaga teng?",
        "a": ["5", "6", "7", "8"],
        "c": 1,
        "p": 15,
        "f": "Mantiq",
        "d": "oson"
    },
    
    # ==================== MANTIQ - O'RTA ====================
    {
        "q": "Quyidagi ketma-ketlikda keyingi son nima? 2, 4, 8, 16, ...",
        "a": ["20", "24", "28", "32"],
        "c": 3,
        "p": 20,
        "f": "Mantiq",
        "d": "o'rta"
    },
    {
        "q": "Agar 5 ta o'rik 5 ta bolaga 5 daqiqada berilsa, 50 ta o'rikni 50 ta bolaga necha daqiqada berish mumkin?",
        "a": ["5 daqiqa", "10 daqiqa", "50 daqiqa", "25 daqiqa"],
        "c": 0,
        "p": 25,
        "f": "Mantiq",
        "d": "o'rta"
    },
    {
        "q": "Quyidagi qatorni davom ettiring: J, F, M, A, M, J, ...",
        "a": ["A", "J", "S", "O"],
        "c": 1,
        "p": 30,
        "f": "Mantiq",
        "d": "o'rta"
    },
    
    # ==================== MANTIQ - QIYIN ====================
    {
        "q": "3 ta o'rdak 3 ta tuxum 3 kunda qo'ysa, 9 ta o'rdak 9 ta tuxum necha kunda qo'yadi?",
        "a": ["3 kun", "6 kun", "9 kun", "27 kun"],
        "c": 0,
        "p": 40,
        "f": "Mantiq",
        "d": "qiyin"
    },
    {
        "q": "Agar barcha itlar hayvon bo'lsa va ba'zi hayvonlar uchadi, qaysi xulosa to'g'ri?",
        "a": ["Barcha itlar uchadi", "Ba'zi itlar uchadi", "Hech qaysi it uchmaydi", "Hech biri to'g'ri emas"],
        "c": 3,
        "p": 50,
        "f": "Mantiq",
        "d": "qiyin"
    },
    {
        "q": "12345679 × 9 = ?",
        "a": ["111111111", "123456789", "99999999", "111111110"],
        "c": 0,
        "p": 60,
        "f": "Mantiq",
        "d": "qiyin"
    },
    
    # ==================== MANTIQ - JUDA QIYIN ====================
    {
        "q": "Monti Xoll muammosida eshikni almashtirish to'g'rimi?",
        "a": ["Ha, ehtimollik 2/3 ga oshadi", "Yo'q, farq yo'q", "Ha, ehtimollik 1/2", "Yo'q, ehtimollik kamayadi"],
        "c": 0,
        "p": 80,
        "f": "Mantiq",
        "d": "juda_qiyin"
    },
    {
        "q": "Agar hamma sartaroshlar o'zlarini qirqmagan odamlarni qirqishsa, sartarosh o'zini qirqadimi?",
        "a": ["Paradoks, javob yo'q", "Ha", "Yo'q", "Ba'zan"],
        "c": 0,
        "p": 100,
        "f": "Mantiq",
        "d": "juda_qiyin"
    },
]


def get_all_subjects() -> List[str]:
    """Barcha fanlarni olish"""
    subjects = set()
    for question in QUESTIONS:
        subjects.add(question['f'])
    return sorted(list(subjects))


def get_questions_by_subject(subject: str) -> List[Dict]:
    """Muayyan fandan savollarni olish - qiyinlik bo'yicha saralangan"""
    questions = [q for q in QUESTIONS if q['f'] == subject]
    # Qiyinlik darajasi bo'yicha saralash
    difficulty_order = {"oson": 1, "o'rta": 2, "qiyin": 3, "juda_qiyin": 4}
    return sorted(questions, key=lambda x: difficulty_order.get(x.get('d', 'oson'), 1))


def get_questions_by_difficulty(difficulty: str) -> List[Dict]:
    """Qiyinlik darajasi bo'yicha savollarni olish"""
    return [q for q in QUESTIONS if q.get('d') == difficulty]


def get_random_questions(count: int = 10) -> List[Dict]:
    """Tasodifiy savollarni olish"""
    import random
    return random.sample(QUESTIONS, min(count, len(QUESTIONS)))


def get_questions_by_difficulty_range(min_points: int, max_points: int) -> List[Dict]:
    """Ball oralig'i bo'yicha savollarni olish"""
    return [q for q in QUESTIONS if min_points <= q['p'] <= max_points]


def get_total_questions() -> int:
    """Jami savollar soni"""
    return len(QUESTIONS)


def get_subjects_stats() -> Dict[str, int]:
    """Har bir fandan nechta savol borligini ko'rsatish"""
    stats = {}
    for question in QUESTIONS:
        subject = question['f']
        stats[subject] = stats.get(subject, 0) + 1
    return stats


def get_difficulty_stats() -> Dict[str, Dict]:
    """Qiyinlik darajalari statistikasi"""
    stats = {
        "oson": {"count": 0, "total_points": 0},
        "o'rta": {"count": 0, "total_points": 0},
        "qiyin": {"count": 0, "total_points": 0},
        "juda_qiyin": {"count": 0, "total_points": 0}
    }
    
    for question in QUESTIONS:
        difficulty = question.get('d', 'oson')
        stats[difficulty]["count"] += 1
        stats[difficulty]["total_points"] += question['p']
    
    return stats


def get_progressive_questions(subjects: List[str]) -> List[Dict]:
    """Bosqichma-bosqich qiyinlashuvchi savollar"""
    all_questions = []
    for subject in subjects:
        all_questions.extend(get_questions_by_subject(subject))
    
    # Qiyinlik bo'yicha saralash
    difficulty_order = {"oson": 1, "o'rta": 2, "qiyin": 3, "juda_qiyin": 4}
    return sorted(all_questions, key=lambda x: difficulty_order.get(x.get('d', 'oson'), 1))


# Test uchun
if __name__ == "__main__":
    print("📚 Barcha fanlar:", get_all_subjects())
    print("\n📊 Fanlar bo'yicha statistika:")
    for subject, count in get_subjects_stats().items():
        print(f"  {subject}: {count} ta savol")
    print(f"\n✅ Jami savollar: {get_total_questions()}")
    
    print("\n🧪 Informatika fani savollari:")
    informatika = get_questions_by_subject("Informatika")
    for i, q in enumerate(informatika[:3], 1):
        print(f"{i}. {q['q']}")

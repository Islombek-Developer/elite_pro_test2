"""
╔══════════════════════════════════════════╗
║   🎓 ZAKOVATI ELITE PRO SYSTEM v2.0    ║
║   Professional Quiz Bot                  ║
╚══════════════════════════════════════════╝

Mukammal dizayn, tushunarli interfeys va professional funksiyalar
"""

import asyncio
import logging
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
# NOTE: MemoryStorage restart da tozalanadi — lekin session DB da saqlanadi (OK)
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ParseMode

from database import Database
from questions import get_questions_by_subject, get_all_subjects, get_total_questions, get_subjects_stats, get_progressive_questions, get_difficulty_stats

import os
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== KONFIGURATSIYA ====================
BOT_TOKEN = "8527388237:AAFBAFLj0PXsmlWnB8rfHo1y_hnutWfcXpQ"
ADMIN_ID = 6965587290,8049290856

router = Router()

# DB saqlash joyi (avtomatik aniqlanadi):
def _get_db_path():
    import os
    # 1. DATA_DIR env variable (Render Disk bo'lsa)
    data_dir = os.environ.get("DATA_DIR", "")
    if data_dir:
        os.makedirs(data_dir, exist_ok=True)
        return os.path.join(data_dir, "zakovati.db")
    # 2. Joriy papkaga yozish mumkinmi?
    try:
        test_path = "zakovati.db"
        with open(test_path, "a") as f:
            pass
        return test_path
    except Exception:
        pass
    # 3. /tmp — har doim ishlaydi (Render Free)
    return "/tmp/zakovati.db"

DB_PATH = _get_db_path()

# ==================== HOLATLAR (STATES) ====================
class RegistrationStates(StatesGroup):
    waiting_name = State()
    waiting_password = State()

class LoginStates(StatesGroup):
    waiting_login_name = State()
    waiting_login_password = State()

class GameStates(StatesGroup):
    choosing_subjects = State()
    answering_question = State()

class AdminStates(StatesGroup):
    waiting_broadcast = State()
    waiting_search = State()

class AdminAddSubjectStates(StatesGroup):
    waiting_subject_name = State()
    waiting_subject_emoji = State()

class AdminAddQuestionStates(StatesGroup):
    waiting_subject_choice = State()
    waiting_question_text = State()
    waiting_answer1 = State()
    waiting_answer2 = State()
    waiting_answer3 = State()
    waiting_answer4 = State()
    waiting_correct = State()
    waiting_difficulty = State()
    waiting_points = State()

db = Database(DB_PATH)

def is_admin(user_id: int) -> bool:
    """Admin huquqlarini tekshirish"""
    return user_id == ADMIN_ID

def get_all_subjects_combined() -> list:
    """questions.py + DB fanlarini birlashtirish"""
    from_file = set(get_all_subjects())
    from_db = {s['name'] for s in db.get_all_subjects_db()}
    return sorted(list(from_file | from_db))

def get_progressive_questions_combined(subjects: list) -> list:
    """questions.py + DB savollarini birlashtirish"""
    all_questions = []
    for subject in subjects:
        # questions.py dan
        all_questions.extend(get_questions_by_subject(subject))
        # DB dan
        all_questions.extend(db.get_questions_by_subject_db(subject))
    difficulty_order = {"oson": 1, "o'rta": 2, "qiyin": 3, "juda_qiyin": 4}
    return sorted(all_questions, key=lambda x: difficulty_order.get(x.get('d', 'oson'), 1))

def get_subjects_stats_combined() -> dict:
    """questions.py + DB fanlar statistikasi"""
    stats = dict(get_subjects_stats())
    db_stats = db.get_subjects_stats_db()
    for subj, cnt in db_stats.items():
        stats[subj] = stats.get(subj, 0) + cnt
    return stats

def get_total_questions_combined() -> int:
    """Jami savollar: questions.py + DB"""
    return get_total_questions() + db.get_total_questions_db()

# ==================== KLAVIATURALAR ====================
def get_main_menu_keyboard(user_id: int):
    """Asosiy menyu tugmalari"""
    keyboard = [
        [InlineKeyboardButton(text="🎮 O'yinni boshlash", callback_data="start_game")],
        [
            InlineKeyboardButton(text="📊 Natijalarim", callback_data="my_stats"),
            InlineKeyboardButton(text="🏆 Reyting", callback_data="leaderboard")
        ],
        [
            InlineKeyboardButton(text="📚 Fanlar", callback_data="subjects_info"),
            InlineKeyboardButton(text="ℹ️ Ma'lumot", callback_data="help")
        ],
        [InlineKeyboardButton(text="🚪 Chiqish (Logout)", callback_data="logout")]
    ]
    if is_admin(user_id):
        keyboard.append([InlineKeyboardButton(text="👨‍💼 Admin Panel", callback_data="admin_panel")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_auth_keyboard():
    """Login/Ro'yxatdan o'tish tugmalari"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔐 Kirish (Login)", callback_data="login")],
        [InlineKeyboardButton(text="📝 Ro'yxatdan o'tish", callback_data="register")]
    ])

def get_admin_keyboard():
    """Admin panel tugmalari"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="👥 Foydalanuvchilar", callback_data="admin_users"),
            InlineKeyboardButton(text="📊 Statistika", callback_data="admin_stats")
        ],
        [
            InlineKeyboardButton(text="🏆 Top O'yinchilar", callback_data="admin_top"),
            InlineKeyboardButton(text="📈 Faollik", callback_data="admin_activity")
        ],
        [
            InlineKeyboardButton(text="📝 Savollar", callback_data="admin_questions_stats"),
            InlineKeyboardButton(text="🔧 Boshqaruv", callback_data="admin_manage")
        ],
        [
            InlineKeyboardButton(text="➕ Fan qo'shish", callback_data="admin_add_subject"),
            InlineKeyboardButton(text="❓ Savol qo'shish", callback_data="admin_add_question")
        ],
        [InlineKeyboardButton(text="🗑 Fanlar/Savollar", callback_data="admin_manage_content")],
        [InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="back_to_menu")]
    ])

def get_admin_manage_keyboard():
    """Admin boshqaruv tugmalari"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚠️ Ballarni tozalash", callback_data="admin_reset_scores")],
        [InlineKeyboardButton(text="📤 Ma'lumotlarni yuklab olish", callback_data="admin_export_users")],
        [InlineKeyboardButton(text="◀️ Orqaga", callback_data="admin_panel")]
    ])

def get_subjects_keyboard(selected_subjects=None):
    """Fanlarni tanlash uchun tugmalar"""
    if selected_subjects is None:
        selected_subjects = []
    
    subjects = get_all_subjects_combined()
    subject_emojis = {
        "Informatika": "💻",
        "Biologiya": "🧬",
        "Fizika": "⚡",
        "Matematika": "🔢",
        "Mantiq": "🧠"
    }
    # DB dan qo'shilgan fanlar uchun emoji
    for s in db.get_all_subjects_db():
        subject_emojis[s['name']] = s['emoji']
    
    keyboard = []
    for subject in subjects:
        emoji = subject_emojis.get(subject, "📘")
        check = "✅" if subject in selected_subjects else "⬜"
        keyboard.append([
            InlineKeyboardButton(
                text=f"{check} {emoji} {subject}", 
                callback_data=f"subject_{subject}"
            )
        ])
    
    if selected_subjects:
        keyboard.append([
            InlineKeyboardButton(text="▶️ O'yinni boshlash", callback_data="confirm_subjects")
        ])
    
    keyboard.append([
        InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="back_to_menu")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_answer_keyboard(answers, question_id):
    """Javob variantlari tugmalari"""
    keyboard = []
    answer_letters = ["🅰️", "🅱️", "🅾️", "🆎"]
    
    for idx, answer in enumerate(answers):
        letter = answer_letters[idx] if idx < len(answer_letters) else f"{idx+1}."
        keyboard.append([
            InlineKeyboardButton(
                text=f"{letter} {answer}", 
                callback_data=f"answer_{question_id}_{idx}"
            )
        ])
    
    keyboard.append([
        InlineKeyboardButton(text="🛑 O'yinni to'xtatish", callback_data="stop_game")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_back_keyboard():
    """Orqaga qaytish tugmasi"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="back_to_menu")]
    ])

# ==================== START & RO'YXATDAN O'TISH ====================
@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """Start buyrug'i"""
    user_id = message.from_user.id
    user = db.get_user(user_id)
    
    if user:
        # ✅ FIX: Agar foydalanuvchi DB da mavjud bo'lsa,
        # restart dan keyin ham avtomatik login qilamiz
        # (Faqat o'zi logout qilgan bo'lsa qayta login so'raymiz)
        if not db.is_logged_in(user_id):
            # Restart da session o'chirilgan bo'lishi mumkin — avtomatik tiklash
            db.login_user(user_id)
            if is_admin(user_id):
                db.set_admin_flag(user_id, 1)
        
        admin_badge = "👑 ADMIN" if is_admin(user_id) else ""
        text = f"""
╔═══════════════════════════════════╗
║   🎓 <b>ZAKOVATI ELITE PRO</b>       ║
╚═══════════════════════════════════╝

👋 Assalomu alaykum, <b>{user['username']}</b>! {admin_badge}

📊 <b>Sizning ko'rsatkichlaringiz:</b>
├ 🏆 Ball: <b>{user['score']}</b>
└ 📅 Ro'yxatdan: <b>{user['created_at'][:10]}</b>

Menyudan kerakli bo'limni tanlang 👇
        """
        await message.answer(
            text,
            reply_markup=get_main_menu_keyboard(user_id),
            parse_mode=ParseMode.HTML
        )
    else:
        # Yangi foydalanuvchi
        text = """
╔═══════════════════════════════════╗
║   🎓 <b>ZAKOVATI ELITE PRO</b>       ║
╚═══════════════════════════════════╝

🎉 <b>Xush kelibsiz!</b>

Bu yerda siz:
✅ Bilimingizni sinab ko'rasiz
✅ Turli fanlardan savollar yechasiz
✅ Ball to'plab reyting ko'tarasiz
✅ Boshqalar bilan raqobat qilasiz

Davom etish uchun tanlang 👇
        """
        await message.answer(text, reply_markup=get_auth_keyboard(), parse_mode=ParseMode.HTML)

@router.message(RegistrationStates.waiting_name)
async def process_name(message: Message, state: FSMContext):
    """Ism kiritish jarayoni"""
    username = message.text.strip()
    
    if len(username) < 3:
        await message.answer(
            "❌ <b>Ism juda qisqa!</b>\n\n"
            "Iltimos, kamida 3 ta harfdan iborat ism kiriting:",
            parse_mode=ParseMode.HTML
        )
        return
    
    if len(username) > 50:
        await message.answer(
            "❌ <b>Ism juda uzun!</b>\n\n"
            "Iltimos, 50 ta belgidan kam ism kiriting:",
            parse_mode=ParseMode.HTML
        )
        return
    
    await state.update_data(username=username)
    
    text = f"""
✅ <b>Ajoyib, {username}!</b>

🔐 Endi xavfsizlik uchun <b>parol</b> o'rnating:

<i>Parol kamida 4 ta belgidan iborat bo'lishi kerak</i>
    """
    await message.answer(text, parse_mode=ParseMode.HTML)
    await state.set_state(RegistrationStates.waiting_password)

@router.message(RegistrationStates.waiting_password)
async def process_password(message: Message, state: FSMContext):
    """Parol kiritish jarayoni"""
    password = message.text.strip()
    
    if len(password) < 4:
        await message.answer(
            "❌ <b>Parol juda qisqa!</b>\n\n"
            "Iltimos, kamida 4 ta belgidan iborat parol kiriting:",
            parse_mode=ParseMode.HTML
        )
        return
    
    data = await state.get_data()
    db.add_user(message.from_user.id, data['username'], password)
    db.login_user(message.from_user.id)  # Ro'yxatdan o'tgandan keyin avtomatik login
    # Agar ADMIN_ID bo'lsa, admin flagini o'rnat
    if message.from_user.id == ADMIN_ID:
        db.set_admin_flag(message.from_user.id, 1)
    
    text = f"""
╔═══════════════════════════════════╗
║   ✅ <b>RO'YXATDAN O'TDINGIZ!</b>    ║
╚═══════════════════════════════════╝

👤 <b>Foydalanuvchi:</b> {data['username']}
🆔 <b>ID:</b> {message.from_user.id}
🏆 <b>Boshlang'ich ball:</b> 0

Endi o'yin boshlashingiz mumkin! 🎮
    """
    await message.answer(
        text, 
        reply_markup=get_main_menu_keyboard(message.from_user.id), 
        parse_mode=ParseMode.HTML
    )
    await state.clear()

# ==================== O'YIN ====================
@router.callback_query(F.data == "start_game")
async def start_game(callback: CallbackQuery, state: FSMContext):
    """O'yinni boshlash"""
    await callback.answer()
    
    # Login tekshiruvi
    if not db.is_logged_in(callback.from_user.id):
        await callback.message.edit_text(
            "⚠️ <b>Tizimga kirishingiz kerak!</b>\n\nO'yin o'ynash uchun avval kiring.",
            reply_markup=get_auth_keyboard(),
            parse_mode=ParseMode.HTML
        )
        return
    
    text = """
╔═══════════════════════════════════╗
║   🎮 <b>O'YIN BOSHLASH</b>            ║
╚═══════════════════════════════════╝

📚 <b>Fanlarni tanlang:</b>

Bir nechta fanni tanlashingiz mumkin.
Har bir to'g'ri javob uchun ball olasiz!

💡 <i>Qiyinroq savollar ko'proq ball beradi</i>
    """
    await callback.message.edit_text(
        text, 
        reply_markup=get_subjects_keyboard([]), 
        parse_mode=ParseMode.HTML
    )
    await state.update_data(
        selected_subjects=[], 
        current_questions=[], 
        current_index=0, 
        game_score=0
    )
    await state.set_state(GameStates.choosing_subjects)

@router.callback_query(GameStates.choosing_subjects, F.data.startswith("subject_"))
async def toggle_subject(callback: CallbackQuery, state: FSMContext):
    """Fan tanlash/bekor qilish"""
    await callback.answer()
    
    subject = callback.data.replace("subject_", "")
    data = await state.get_data()
    selected = data.get('selected_subjects', [])
    
    if subject in selected:
        selected.remove(subject)
    else:
        selected.append(subject)
    
    await state.update_data(selected_subjects=selected)
    
    text = """
╔═══════════════════════════════════╗
║   🎮 <b>O'YIN BOSHLASH</b>            ║
╚═══════════════════════════════════╝

📚 <b>Fanlarni tanlang:</b>

Bir nechta fanni tanlashingiz mumkin.
Har bir to'g'ri javob uchun ball olasiz!

💡 <i>Qiyinroq savollar ko'proq ball beradi</i>
    """
    await callback.message.edit_text(
        text, 
        reply_markup=get_subjects_keyboard(selected), 
        parse_mode=ParseMode.HTML
    )

@router.callback_query(GameStates.choosing_subjects, F.data == "confirm_subjects")
async def confirm_subjects(callback: CallbackQuery, state: FSMContext):
    """Tanlangan fanlarni tasdiqlash va o'yinni boshlash"""
    await callback.answer()
    
    data = await state.get_data()
    selected = data.get('selected_subjects', [])
    
    if not selected:
        await callback.answer(
            "❌ Kamida bitta fan tanlang!", 
            show_alert=True
        )
        return
    
    questions = get_progressive_questions_combined(selected)
    
    if not questions:
        await callback.answer(
            "❌ Tanlangan fanlardan savollar topilmadi!", 
            show_alert=True
        )
        return
    
    await state.update_data(
        current_questions=questions, 
        current_index=0, 
        game_score=0
    )
    await state.set_state(GameStates.answering_question)
    await show_question(callback.message, state)

async def show_question(message: Message, state: FSMContext):
    """Savolni ko'rsatish"""
    data = await state.get_data()
    questions = data['current_questions']
    index = data['current_index']
    score = data.get('game_score', 0)
    
    if index >= len(questions):
        await finish_game(message, state)
        return
    
    q = questions[index]
    total = len(questions)
    
    # Qiyinlik darajasi emojisi
    difficulty_emoji = {
        "oson": "🟢",
        "o'rta": "🟡",
        "qiyin": "🟠",
        "juda_qiyin": "🔴"
    }
    
    diff_emoji = difficulty_emoji.get(q.get('d', 'oson'), '⚪')
    
    text = f"""
╔═══════════════════════════════════╗
║   📝 <b>SAVOL {index + 1}/{total}</b>              ║
╚═══════════════════════════════════╝

📚 <b>Fan:</b> {q['f']}
{diff_emoji} <b>Qiyinlik:</b> {q.get('d', 'oson').capitalize()}
💰 <b>Ball:</b> {q['p']}
🏆 <b>Joriy ball:</b> {score}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>❓ {q['q']}</b>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Javobni tanlang 👇
    """
    
    await message.edit_text(
        text, 
        reply_markup=get_answer_keyboard(q['a'], q.get('id', index)), 
        parse_mode=ParseMode.HTML
    )

@router.callback_query(GameStates.answering_question, F.data.startswith("answer_"))
async def check_answer(callback: CallbackQuery, state: FSMContext):
    """Javobni tekshirish"""
    data = await state.get_data()
    questions = data['current_questions']
    index = data['current_index']
    q = questions[index]
    
    # Javobni olish
    parts = callback.data.split("_")
    answer_idx = int(parts[-1])
    correct_idx = q['c']
    
    is_correct = answer_idx == correct_idx
    
    if is_correct:
        # To'g'ri javob
        new_score = data.get('game_score', 0) + q['p']
        await state.update_data(game_score=new_score)
        
        await callback.answer(
            f"✅ To'g'ri! +{q['p']} ball", 
            show_alert=True
        )
    else:
        # Noto'g'ri javob
        correct_answer = q['a'][correct_idx]
        await callback.answer(
            f"❌ Noto'g'ri!\nTo'g'ri javob: {correct_answer}", 
            show_alert=True
        )
    
    # Keyingi savolga o'tish
    await state.update_data(current_index=index + 1)
    await show_question(callback.message, state)

@router.callback_query(GameStates.answering_question, F.data == "stop_game")
async def stop_game(callback: CallbackQuery, state: FSMContext):
    """O'yinni to'xtatish"""
    await callback.answer()
    await finish_game(callback.message, state)

async def finish_game(message: Message, state: FSMContext):
    """O'yinni tugatish"""
    data = await state.get_data()
    game_score = data.get('game_score', 0)
    total_questions = len(data.get('current_questions', []))
    
    user = db.get_user(message.chat.id)
    old_score = user['score']
    new_total_score = old_score + game_score
    
    db.update_score(message.chat.id, new_total_score)
    
    # O'yin natijalarini ko'rsatish
    if game_score > 0:
        result_emoji = "🎉" if game_score > 50 else "👏" if game_score > 20 else "💪"
        result_text = "Ajoyib!" if game_score > 50 else "Yaxshi!" if game_score > 20 else "Davom eting!"
    else:
        result_emoji = "😔"
        result_text = "Keyingi safar omad!"
    
    text = f"""
╔═══════════════════════════════════╗
║   {result_emoji} <b>O'YIN YAKUNLANDI</b>         ║
╚═══════════════════════════════════╝

📊 <b>Natijalaringiz:</b>

├ ✅ Savollar soni: <b>{total_questions}</b>
├ 🎯 To'plagan ball: <b>+{game_score}</b>
├ 🏆 Eski jami: <b>{old_score}</b>
└ 🌟 Yangi jami: <b>{new_total_score}</b>

{result_text} {result_emoji}
    """
    
    await message.edit_text(
        text, 
        reply_markup=get_back_keyboard(), 
        parse_mode=ParseMode.HTML
    )
    await state.clear()

# ==================== STATISTIKA ====================
@router.callback_query(F.data == "my_stats")
async def show_my_stats(callback: CallbackQuery):
    """Foydalanuvchi statistikasi"""
    await callback.answer()
    
    user = db.get_user(callback.from_user.id)
    # Admin bo'lmagan foydalanuvchilar orasida reyting
    all_users = db.get_all_users_no_admin()
    
    # Foydalanuvchi reytingini aniqlash
    sorted_users = sorted(all_users, key=lambda x: x['score'], reverse=True)
    rank = next((i for i, u in enumerate(sorted_users, 1) if u['user_id'] == user['user_id']), 0)
    
    # Ball darajasini aniqlash
    if user['score'] >= 1000:
        level = "🏅 EXPERT"
    elif user['score'] >= 500:
        level = "⭐ PROFESSIONAL"
    elif user['score'] >= 200:
        level = "🎯 ADVANCED"
    elif user['score'] >= 50:
        level = "📈 INTERMEDIATE"
    else:
        level = "🌱 BEGINNER"
    
    text = f"""
╔═══════════════════════════════════╗
║   📊 <b>MENING STATISTIKAM</b>       ║
╚═══════════════════════════════════╝

👤 <b>Foydalanuvchi:</b> {user['username']}
🆔 <b>ID:</b> {user['user_id']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🏆 <b>BALL:</b> {user['score']}
📊 <b>DARAJA:</b> {level}
🎖️ <b>REYTING:</b> #{rank} / {len(all_users)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📅 <b>Ro'yxatdan:</b> {user['created_at'][:10]}

💡 <i>O'yin o'ynab ball to'plang va reytingda ko'tariling!</i>
    """
    
    await callback.message.edit_text(
        text, 
        reply_markup=get_back_keyboard(), 
        parse_mode=ParseMode.HTML
    )

# ==================== REYTING (LIDERBORD) ====================
@router.callback_query(F.data == "leaderboard")
async def show_leaderboard(callback: CallbackQuery):
    """Liderbord - Eng yaxshi o'yinchilar (adminlarsiz)"""
    await callback.answer()
    
    top = db.get_top_users_no_admin(10)
    
    text = """
╔═══════════════════════════════════╗
║   🏆 <b>TOP-10 O'YINCHILAR</b>        ║
╚═══════════════════════════════════╝

"""
    
    for idx, u in enumerate(top, 1):
        if idx == 1:
            medal = "🥇"
        elif idx == 2:
            medal = "🥈"
        elif idx == 3:
            medal = "🥉"
        else:
            medal = f"{idx}."
        
        text += f"{medal} <b>{u['username']}</b> — <code>{u['score']}</code> ball\n"
    
    text += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    text += "\n💡 <i>O'yin o'ynab reytingda yuqorilarga chiqing!</i>"
    
    await callback.message.edit_text(
        text, 
        reply_markup=get_back_keyboard(), 
        parse_mode=ParseMode.HTML
    )

# ==================== FANLAR MA'LUMOTI ====================
@router.callback_query(F.data == "subjects_info")
async def show_subjects_info(callback: CallbackQuery):
    """Fanlar haqida ma'lumot"""
    await callback.answer()
    
    stats = get_subjects_stats_combined()
    total = get_total_questions_combined()
    
    subject_emojis = {
        "Informatika": "💻",
        "Biologiya": "🧬",
        "Fizika": "⚡",
        "Matematika": "🔢",
        "Mantiq": "🧠"
    }
    for s in db.get_all_subjects_db():
        subject_emojis[s['name']] = s['emoji']
    
    text = """
╔═══════════════════════════════════╗
║   📚 <b>MAVJUD FANLAR</b>            ║
╚═══════════════════════════════════╝

"""
    
    for subject, count in stats.items():
        emoji = subject_emojis.get(subject, "📘")
        percentage = (count / total * 100) if total > 0 else 0
        text += f"{emoji} <b>{subject}</b>\n   └ {count} ta savol ({percentage:.0f}%)\n\n"
    
    text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    text += f"📊 <b>Jami:</b> {total} ta savol\n\n"
    text += "💡 <i>Barcha fanlarda o'z bilimingizni sinab ko'ring!</i>"
    
    await callback.message.edit_text(
        text, 
        reply_markup=get_back_keyboard(), 
        parse_mode=ParseMode.HTML
    )

# ==================== YORDAM ====================
@router.callback_query(F.data == "help")
async def show_help(callback: CallbackQuery):
    """Yordam va ma'lumot"""
    await callback.answer()
    
    text = """
╔═══════════════════════════════════╗
║   ℹ️ <b>YORDAM & MA'LUMOT</b>        ║
╚═══════════════════════════════════╝

<b>🎮 Qanday o'ynash:</b>

1️⃣ "O'yinni boshlash" tugmasini bosing
2️⃣ O'zingiz yoqtirgan fanlarni tanlang
3️⃣ Savollarga javob bering
4️⃣ To'g'ri javoblar uchun ball to'plang
5️⃣ Reytingda yuqoriga ko'tariling!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>📚 Fanlar:</b>
💻 Informatika
🧬 Biologiya
⚡ Fizika
🔢 Matematika
🧠 Mantiq

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>💰 Ball tizimi:</b>
🟢 Oson — 10-15 ball
🟡 O'rta — 20-30 ball
🟠 Qiyin — 40-60 ball
🔴 Juda qiyin — 80-100 ball

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>🎯 Maqsad:</b>
Ko'proq ball to'plang va TOP-10 ga kirish!

Omad! 🍀
    """
    
    await callback.message.edit_text(
        text, 
        reply_markup=get_back_keyboard(), 
        parse_mode=ParseMode.HTML
    )

# ==================== ADMIN PANEL ====================
@router.callback_query(F.data == "admin_panel")
async def show_admin_panel(callback: CallbackQuery):
    """Admin panel asosiy sahifa"""
    await callback.answer()
    
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Sizda admin huquqlari yo'q!", show_alert=True)
        return
    
    stats = db.get_statistics()
    real_stats = db.get_statistics_no_admin()
    
    text = f"""
╔═══════════════════════════════════╗
║   👨‍💼 <b>ADMIN PANEL</b>              ║
╚═══════════════════════════════════╝

📊 <b>UMUMIY MA'LUMOTLAR:</b>

├ 👥 Foydalanuvchilar: <b>{real_stats['total_users']}</b>
├ 🏆 Jami ball: <b>{real_stats['total_score']}</b>
├ 📈 O'rtacha ball: <b>{real_stats['avg_score']:.1f}</b>
└ 👑 Eng yuqori: <b>{real_stats['max_score']}</b>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Kerakli bo'limni tanlang 👇
    """
    
    await callback.message.edit_text(
        text, 
        reply_markup=get_admin_keyboard(), 
        parse_mode=ParseMode.HTML
    )

@router.callback_query(F.data == "admin_users")
async def show_admin_users(callback: CallbackQuery):
    """Foydalanuvchilar ro'yxati"""
    await callback.answer()
    
    if not is_admin(callback.from_user.id):
        return
    
    users = db.get_all_users()
    
    text = f"""
╔═══════════════════════════════════╗
║   👥 <b>FOYDALANUVCHILAR</b>         ║
╚═══════════════════════════════════╝

<b>Jami:</b> {len(users)} ta

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
    
    for idx, u in enumerate(users[:15], 1):
        emoji = "👑" if is_admin(u['user_id']) else "👤"
        text += f"{idx}. {emoji} <b>{u['username']}</b>\n"
        text += f"   └ 🏆 {u['score']} | 🆔 <code>{u['user_id']}</code>\n\n"
    
    if len(users) > 15:
        text += f"\n<i>... va yana {len(users) - 15} ta</i>"
    
    await callback.message.edit_text(
        text, 
        reply_markup=get_admin_keyboard(), 
        parse_mode=ParseMode.HTML
    )

@router.callback_query(F.data == "admin_stats")
async def show_admin_stats(callback: CallbackQuery):
    """Batafsil statistika"""
    await callback.answer()
    
    if not is_admin(callback.from_user.id):
        return
    
    stats = db.get_statistics_no_admin()
    users = db.get_all_users_no_admin()
    active = len([u for u in users if u['score'] > 0])
    
    text = f"""
╔═══════════════════════════════════╗
║   📊 <b>BATAFSIL STATISTIKA</b>      ║
╚═══════════════════════════════════╝

<b>👥 FOYDALANUVCHILAR:</b>
├ Jami: <b>{stats['total_users']}</b>
├ Aktiv: <b>{active}</b>
└ Faol emas: <b>{stats['total_users'] - active}</b>

<b>🏆 BALL:</b>
├ Jami: <b>{stats['total_score']}</b>
├ O'rtacha: <b>{stats['avg_score']:.1f}</b>
└ Eng yuqori: <b>{stats['max_score']}</b>

<b>📚 SAVOLLAR:</b>
├ Jami: <b>{get_total_questions()}</b>
└ Fanlar: <b>{len(get_all_subjects())}</b>
    """
    
    await callback.message.edit_text(
        text, 
        reply_markup=get_admin_keyboard(), 
        parse_mode=ParseMode.HTML
    )

@router.callback_query(F.data == "admin_top")
async def show_admin_top(callback: CallbackQuery):
    """TOP o'yinchilar"""
    await callback.answer()
    
    if not is_admin(callback.from_user.id):
        return
    
    top = db.get_top_users_no_admin(20)
    
    text = """
╔═══════════════════════════════════╗
║   🏆 <b>TOP-20 O'YINCHILAR</b>        ║
╚═══════════════════════════════════╝

"""
    
    for idx, u in enumerate(top, 1):
        if idx == 1:
            medal = "🥇"
        elif idx == 2:
            medal = "🥈"
        elif idx == 3:
            medal = "🥉"
        else:
            medal = f"{idx}."
        
        text += f"{medal} {u['username']} — {u['score']}\n"
    
    await callback.message.edit_text(
        text, 
        reply_markup=get_admin_keyboard(), 
        parse_mode=ParseMode.HTML
    )

@router.callback_query(F.data == "admin_activity")
async def show_admin_activity(callback: CallbackQuery):
    """Faollik bo'yicha statistika"""
    await callback.answer()
    
    if not is_admin(callback.from_user.id):
        return
    
    users = db.get_all_users_no_admin()
    ranges = {
        "0 ball": len([u for u in users if u['score'] == 0]),
        "1-49 ball": len([u for u in users if 1 <= u['score'] < 50]),
        "50-99 ball": len([u for u in users if 50 <= u['score'] < 100]),
        "100-199 ball": len([u for u in users if 100 <= u['score'] < 200]),
        "200+ ball": len([u for u in users if u['score'] >= 200]),
    }
    
    text = """
╔═══════════════════════════════════╗
║   📈 <b>FAOLLIK STATISTIKASI</b>     ║
╚═══════════════════════════════════╝

"""
    
    for range_name, count in ranges.items():
        percentage = (count / len(users) * 100) if users else 0
        text += f"• {range_name}: <b>{count}</b> ta ({percentage:.0f}%)\n"
    
    await callback.message.edit_text(
        text, 
        reply_markup=get_admin_keyboard(), 
        parse_mode=ParseMode.HTML
    )

@router.callback_query(F.data == "admin_questions_stats")
async def show_admin_questions(callback: CallbackQuery):
    """Savollar statistikasi"""
    await callback.answer()
    
    if not is_admin(callback.from_user.id):
        return
    
    stats = get_subjects_stats_combined()
    total = get_total_questions_combined()
    
    text = f"""
╔═══════════════════════════════════╗
║   📝 <b>SAVOLLAR STATISTIKASI</b>    ║
╚═══════════════════════════════════╝

<b>Jami:</b> {total} ta savol

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
    
    for subj, cnt in stats.items():
        percentage = (cnt / total * 100) if total > 0 else 0
        text += f"• {subj}: <b>{cnt}</b> ta ({percentage:.0f}%)\n"
    
    await callback.message.edit_text(
        text, 
        reply_markup=get_admin_keyboard(), 
        parse_mode=ParseMode.HTML
    )

@router.callback_query(F.data == "admin_manage")
async def show_admin_manage(callback: CallbackQuery):
    """Boshqaruv paneli"""
    await callback.answer()
    
    if not is_admin(callback.from_user.id):
        return
    
    text = """
╔═══════════════════════════════════╗
║   🔧 <b>TIZIM BOSHQARUVI</b>         ║
╚═══════════════════════════════════╝

⚠️ <b>DIQQAT!</b>

Bu bo'limda tizim ma'lumotlarini
boshqarishingiz mumkin.

Ehtiyot bo'ling! ⚠️
    """
    
    await callback.message.edit_text(
        text, 
        reply_markup=get_admin_manage_keyboard(), 
        parse_mode=ParseMode.HTML
    )

@router.callback_query(F.data == "admin_export_users")
async def admin_export(callback: CallbackQuery):
    """Foydalanuvchilar ma'lumotlarini eksport qilish"""
    await callback.answer("📤 Ma'lumotlar tayyorlanmoqda...")
    
    if not is_admin(callback.from_user.id):
        return
    
    users = db.get_all_users()
    csv = "ID,Username,Password,Score,Created\n"
    for u in users:
        csv += f"{u['user_id']},{u['username']},{u['password']},{u['score']},{u['created_at']}\n"
    
    import datetime
    fn = f"export_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    with open(fn, 'w', encoding='utf-8') as f:
        f.write(csv)
    
    from aiogram.types import FSInputFile
    await callback.message.answer_document(
        FSInputFile(fn), 
        caption=f"📤 <b>Eksport</b>\n\nJami: {len(users)} ta foydalanuvchi",
        parse_mode=ParseMode.HTML
    )
    
    import os
    os.remove(fn)
    await callback.answer("✅ Eksport muvaffaqiyatli!", show_alert=True)

@router.callback_query(F.data == "admin_reset_scores")
async def admin_reset(callback: CallbackQuery):
    """Barcha ballarni tozalash"""
    await callback.answer()
    
    if not is_admin(callback.from_user.id):
        return
    
    db.reset_all_scores()
    await callback.answer(
        "✅ Barcha ballar 0 ga qaytarildi!", 
        show_alert=True
    )
    await show_admin_panel(callback)

# ==================== ADMIN: FAN QO'SHISH ====================

@router.callback_query(F.data == "admin_add_subject")
async def admin_add_subject_start(callback: CallbackQuery, state: FSMContext):
    """Admin fan qo'shish — boshlash"""
    await callback.answer()
    if not is_admin(callback.from_user.id):
        return
    
    db_subjects = db.get_all_subjects_db()
    existing = "\n".join([f"• {s['emoji']} {s['name']}" for s in db_subjects]) if db_subjects else "Hali qo'shilmagan"
    
    text = f"""
╔═══════════════════════════════════╗
║   ➕ <b>FAN QO'SHISH</b>              ║
╚═══════════════════════════════════╝

<b>📚 Mavjud qo'shilgan fanlar:</b>
{existing}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>Yangi fan nomini kiriting:</b>
<i>(Masalan: Kimyo, Tarix, Geografiya)</i>
    """
    await callback.message.edit_text(text, parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="admin_panel")]
        ]))
    await state.set_state(AdminAddSubjectStates.waiting_subject_name)

@router.message(AdminAddSubjectStates.waiting_subject_name)
async def admin_add_subject_name(message: Message, state: FSMContext):
    """Fan nomini olish"""
    if not is_admin(message.from_user.id):
        return
    name = message.text.strip()
    if len(name) < 2:
        await message.answer("❌ Fan nomi juda qisqa! Qayta kiriting:")
        return
    await state.update_data(subject_name=name)
    await message.answer(
        f"✅ Fan nomi: <b>{name}</b>\n\n🎨 Endi <b>emoji</b> kiriting (masalan: 🧪 🌍 📐):\n<i>Yoki /skip yozing standart emoji uchun</i>",
        parse_mode=ParseMode.HTML
    )
    await state.set_state(AdminAddSubjectStates.waiting_subject_emoji)

@router.message(AdminAddSubjectStates.waiting_subject_emoji)
async def admin_add_subject_emoji(message: Message, state: FSMContext):
    """Fan emojisini olish va saqlash"""
    if not is_admin(message.from_user.id):
        return
    data = await state.get_data()
    name = data['subject_name']
    emoji = "📘" if message.text.strip() in ['/skip', 'skip'] else message.text.strip()
    
    success = db.add_subject(name, emoji)
    await state.clear()
    
    if success:
        text = f"""
✅ <b>Fan muvaffaqiyatli qo'shildi!</b>

{emoji} <b>{name}</b>

Endi bu fanga savollar qo'shishingiz mumkin.
        """
        await message.answer(text, parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="❓ Savol qo'shish", callback_data="admin_add_question")],
                [InlineKeyboardButton(text="◀️ Admin panel", callback_data="admin_panel")]
            ]))
    else:
        await message.answer(
            f"❌ <b>{name}</b> fan allaqachon mavjud yoki xatolik yuz berdi!",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="◀️ Admin panel", callback_data="admin_panel")]
            ]))

# ==================== ADMIN: SAVOL QO'SHISH ====================

@router.callback_query(F.data == "admin_add_question")
async def admin_add_question_start(callback: CallbackQuery, state: FSMContext):
    """Admin savol qo'shish — fan tanlash"""
    await callback.answer()
    if not is_admin(callback.from_user.id):
        return
    
    all_subjects = get_all_subjects_combined()
    if not all_subjects:
        await callback.answer("❌ Avval fan qo'shing!", show_alert=True)
        return
    
    keyboard = []
    subject_emojis = {"Informatika":"💻","Biologiya":"🧬","Fizika":"⚡","Matematika":"🔢","Mantiq":"🧠"}
    for s in db.get_all_subjects_db():
        subject_emojis[s['name']] = s['emoji']
    
    for subj in all_subjects:
        emoji = subject_emojis.get(subj, "📘")
        keyboard.append([InlineKeyboardButton(text=f"{emoji} {subj}", callback_data=f"aqsubj_{subj}")])
    keyboard.append([InlineKeyboardButton(text="❌ Bekor qilish", callback_data="admin_panel")])
    
    await callback.message.edit_text(
        "╔═══════════════════════════════════╗\n"
        "║   ❓ <b>SAVOL QO'SHISH</b>           ║\n"
        "╚═══════════════════════════════════╝\n\n"
        "📚 <b>Qaysi fanga savol qo'shmoqchisiz?</b>",
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )
    await state.set_state(AdminAddQuestionStates.waiting_subject_choice)

@router.callback_query(AdminAddQuestionStates.waiting_subject_choice, F.data.startswith("aqsubj_"))
async def admin_aq_subject_chosen(callback: CallbackQuery, state: FSMContext):
    """Fan tanlandi — savol matnini so'rash"""
    await callback.answer()
    subject = callback.data.replace("aqsubj_", "")
    await state.update_data(aq_subject=subject)
    await callback.message.edit_text(
        f"📚 Fan: <b>{subject}</b>\n\n✏️ <b>Savol matnini kiriting:</b>",
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="admin_panel")]
        ])
    )
    await state.set_state(AdminAddQuestionStates.waiting_question_text)

@router.message(AdminAddQuestionStates.waiting_question_text)
async def admin_aq_question(message: Message, state: FSMContext):
    await state.update_data(aq_question=message.text.strip())
    await message.answer("🅰️ <b>1-javob variantini kiriting:</b>", parse_mode=ParseMode.HTML)
    await state.set_state(AdminAddQuestionStates.waiting_answer1)

@router.message(AdminAddQuestionStates.waiting_answer1)
async def admin_aq_ans1(message: Message, state: FSMContext):
    await state.update_data(aq_ans1=message.text.strip())
    await message.answer("🅱️ <b>2-javob variantini kiriting:</b>", parse_mode=ParseMode.HTML)
    await state.set_state(AdminAddQuestionStates.waiting_answer2)

@router.message(AdminAddQuestionStates.waiting_answer2)
async def admin_aq_ans2(message: Message, state: FSMContext):
    await state.update_data(aq_ans2=message.text.strip())
    await message.answer("🅾️ <b>3-javob variantini kiriting:</b>", parse_mode=ParseMode.HTML)
    await state.set_state(AdminAddQuestionStates.waiting_answer3)

@router.message(AdminAddQuestionStates.waiting_answer3)
async def admin_aq_ans3(message: Message, state: FSMContext):
    await state.update_data(aq_ans3=message.text.strip())
    await message.answer("🆎 <b>4-javob variantini kiriting:</b>", parse_mode=ParseMode.HTML)
    await state.set_state(AdminAddQuestionStates.waiting_answer4)

@router.message(AdminAddQuestionStates.waiting_answer4)
async def admin_aq_ans4(message: Message, state: FSMContext):
    await state.update_data(aq_ans4=message.text.strip())
    data = await state.get_data()
    
    preview = (
        f"📝 <b>Savol:</b> {data['aq_question']}\n\n"
        f"🅰️ {data['aq_ans1']}\n"
        f"🅱️ {data['aq_ans2']}\n"
        f"🅾️ {data['aq_ans3']}\n"
        f"🆎 {data['aq_ans4']}\n\n"
        f"✅ <b>To'g'ri javob raqamini kiriting (1-4):</b>"
    )
    await message.answer(preview, parse_mode=ParseMode.HTML)
    await state.set_state(AdminAddQuestionStates.waiting_correct)

@router.message(AdminAddQuestionStates.waiting_correct)
async def admin_aq_correct(message: Message, state: FSMContext):
    text = message.text.strip()
    if text not in ['1','2','3','4']:
        await message.answer("❌ Faqat 1, 2, 3 yoki 4 kiriting!")
        return
    await state.update_data(aq_correct=int(text)-1)
    await message.answer(
        "📊 <b>Qiyinlik darajasini tanlang:</b>",
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🟢 Oson (10-15 ball)", callback_data="aqdiff_oson")],
            [InlineKeyboardButton(text="🟡 O'rta (20-30 ball)", callback_data="aqdiff_o'rta")],
            [InlineKeyboardButton(text="🟠 Qiyin (40-60 ball)", callback_data="aqdiff_qiyin")],
            [InlineKeyboardButton(text="🔴 Juda qiyin (80-100 ball)", callback_data="aqdiff_juda_qiyin")],
        ])
    )
    await state.set_state(AdminAddQuestionStates.waiting_difficulty)

@router.callback_query(AdminAddQuestionStates.waiting_difficulty, F.data.startswith("aqdiff_"))
async def admin_aq_difficulty(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    difficulty = callback.data.replace("aqdiff_", "")
    await state.update_data(aq_difficulty=difficulty)
    
    default_points = {"oson": 10, "o'rta": 20, "qiyin": 40, "juda_qiyin": 80}
    dp = default_points.get(difficulty, 10)
    
    await callback.message.edit_text(
        f"💰 <b>Ball miqdorini kiriting:</b>\n<i>Standart: {dp} ball. Shunchaki {dp} yozing yoki boshqa son kiriting.</i>",
        parse_mode=ParseMode.HTML
    )
    await state.set_state(AdminAddQuestionStates.waiting_points)

@router.message(AdminAddQuestionStates.waiting_points)
async def admin_aq_points(message: Message, state: FSMContext):
    try:
        points = int(message.text.strip())
        if points < 1 or points > 200:
            raise ValueError
    except ValueError:
        await message.answer("❌ 1 dan 200 gacha son kiriting!")
        return
    
    data = await state.get_data()
    await state.update_data(aq_points=points)
    data = await state.get_data()
    
    answers = [data['aq_ans1'], data['aq_ans2'], data['aq_ans3'], data['aq_ans4']]
    correct_idx = data['aq_correct']
    
    diff_emoji = {"oson":"🟢","o'rta":"🟡","qiyin":"🟠","juda_qiyin":"🔴"}
    letters = ["🅰️","🅱️","🅾️","🆎"]
    
    confirm_text = (
        f"╔═══════════════════════════════════╗\n"
        f"║   📝 <b>TASDIQLASH</b>               ║\n"
        f"╚═══════════════════════════════════╝\n\n"
        f"📚 <b>Fan:</b> {data['aq_subject']}\n"
        f"{diff_emoji.get(data['aq_difficulty'],'⚪')} <b>Qiyinlik:</b> {data['aq_difficulty']}\n"
        f"💰 <b>Ball:</b> {points}\n\n"
        f"<b>❓ {data['aq_question']}</b>\n\n"
    )
    for i, ans in enumerate(answers):
        mark = "✅ " if i == correct_idx else ""
        confirm_text += f"{letters[i]} {mark}{ans}\n"
    
    await message.answer(
        confirm_text,
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Saqlash", callback_data="aq_save")],
            [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="admin_panel")]
        ])
    )

@router.callback_query(F.data == "aq_save")
async def admin_aq_save(callback: CallbackQuery, state: FSMContext):
    """Savolni saqlash"""
    await callback.answer()
    if not is_admin(callback.from_user.id):
        return
    data = await state.get_data()
    
    answers = [data['aq_ans1'], data['aq_ans2'], data['aq_ans3'], data['aq_ans4']]
    success = db.add_question(
        question=data['aq_question'],
        answers=answers,
        correct_index=data['aq_correct'],
        subject=data['aq_subject'],
        difficulty=data['aq_difficulty'],
        points=data['aq_points']
    )
    await state.clear()
    
    if success:
        await callback.message.edit_text(
            f"✅ <b>Savol muvaffaqiyatli saqlandi!</b>\n\n"
            f"📚 Fan: <b>{data['aq_subject']}</b>\n"
            f"💰 Ball: <b>{data['aq_points']}</b>",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="➕ Yana savol qo'shish", callback_data="admin_add_question")],
                [InlineKeyboardButton(text="◀️ Admin panel", callback_data="admin_panel")]
            ])
        )
    else:
        await callback.message.edit_text(
            "❌ Saqlashda xatolik yuz berdi!",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="◀️ Admin panel", callback_data="admin_panel")]
            ])
        )

# ==================== ADMIN: KONTENT BOSHQARUVI ====================

@router.callback_query(F.data == "admin_manage_content")
async def admin_manage_content(callback: CallbackQuery):
    """Fanlar va savollarni boshqarish"""
    await callback.answer()
    if not is_admin(callback.from_user.id):
        return
    
    db_subjects = db.get_all_subjects_db()
    total_db_q = db.get_total_questions_db()
    
    subjects_text = "\n".join([f"• {s['emoji']} {s['name']}" for s in db_subjects]) if db_subjects else "Hali yo'q"
    
    text = f"""
╔═══════════════════════════════════╗
║   🗑 <b>KONTENT BOSHQARUVI</b>       ║
╚═══════════════════════════════════╝

<b>📚 Qo'shilgan fanlar ({len(db_subjects)} ta):</b>
{subjects_text}

<b>❓ Qo'shilgan savollar: {total_db_q} ta</b>

Nimani o'chirmoqchisiz?
    """
    
    keyboard = []
    for s in db_subjects:
        keyboard.append([InlineKeyboardButton(
            text=f"🗑 {s['emoji']} {s['name']} fani (va savollarini)",
            callback_data=f"del_subj_{s['name']}"
        )])
    keyboard.append([InlineKeyboardButton(text="🗑 DB savollarini ko'rish", callback_data="admin_list_db_questions")])
    keyboard.append([InlineKeyboardButton(text="◀️ Admin panel", callback_data="admin_panel")])
    
    await callback.message.edit_text(
        text, parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )

@router.callback_query(F.data.startswith("del_subj_"))
async def admin_delete_subject(callback: CallbackQuery):
    """Fanni o'chirish"""
    await callback.answer()
    if not is_admin(callback.from_user.id):
        return
    name = callback.data.replace("del_subj_", "")
    
    await callback.message.edit_text(
        f"⚠️ <b>DIQQAT!</b>\n\n<b>{name}</b> fanini va unga tegishli barcha savollarni o'chirishni tasdiqlaysizmi?",
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Ha, o'chirish", callback_data=f"confirm_del_subj_{name}")],
            [InlineKeyboardButton(text="❌ Yo'q", callback_data="admin_manage_content")]
        ])
    )

@router.callback_query(F.data.startswith("confirm_del_subj_"))
async def admin_confirm_delete_subject(callback: CallbackQuery):
    await callback.answer()
    if not is_admin(callback.from_user.id):
        return
    name = callback.data.replace("confirm_del_subj_", "")
    db.delete_subject(name)
    await callback.answer(f"✅ {name} fani o'chirildi!", show_alert=True)
    await admin_manage_content(callback)

@router.callback_query(F.data == "admin_list_db_questions")
async def admin_list_db_questions(callback: CallbackQuery):
    """DB savollarini ko'rish va o'chirish"""
    await callback.answer()
    if not is_admin(callback.from_user.id):
        return
    
    questions = db.get_all_questions_db()
    if not questions:
        await callback.answer("❌ DB da savollar yo'q!", show_alert=True)
        return
    
    keyboard = []
    for q in questions[:20]:  # Ko'pi bilan 20 ta
        short = q['q'][:35] + "..." if len(q['q']) > 35 else q['q']
        keyboard.append([InlineKeyboardButton(
            text=f"🗑 [{q['f']}] {short}",
            callback_data=f"del_q_{q['id']}"
        )])
    keyboard.append([InlineKeyboardButton(text="◀️ Orqaga", callback_data="admin_manage_content")])
    
    await callback.message.edit_text(
        f"🗑 <b>SAVOLLARNI O'CHIRISH</b>\n\n"
        f"Jami: {len(questions)} ta (ko'pi bilan 20 ta ko'rsatilmoqda)\n\n"
        f"O'chirmoqchi bo'lgan savolni tanlang:",
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )

@router.callback_query(F.data.startswith("del_q_"))
async def admin_delete_question(callback: CallbackQuery):
    """Savol o'chirish"""
    await callback.answer()
    if not is_admin(callback.from_user.id):
        return
    try:
        q_id = int(callback.data.replace("del_q_", ""))
        db.delete_question(q_id)
        await callback.answer("✅ Savol o'chirildi!", show_alert=True)
        await admin_list_db_questions(callback)
    except Exception:
        await callback.answer("❌ Xatolik!", show_alert=True)

# ==================== REGISTER ====================

@router.callback_query(F.data == "register")
async def register_callback(callback: CallbackQuery, state: FSMContext):
    """Ro'yxatdan o'tish tugmasi"""
    await callback.answer()
    text = """
╔═══════════════════════════════════╗
║   📝 <b>RO'YXATDAN O'TISH</b>        ║
╚═══════════════════════════════════╝

📝 Boshlash uchun <b>ismingizni</b> kiriting:
    """
    await callback.message.edit_text(text, parse_mode=ParseMode.HTML)
    await state.set_state(RegistrationStates.waiting_name)

@router.callback_query(F.data == "login")
async def login_callback(callback: CallbackQuery, state: FSMContext):
    """Login tugmasi"""
    await callback.answer()
    text = """
╔═══════════════════════════════════╗
║   🔐 <b>TIZIMGA KIRISH</b>           ║
╚═══════════════════════════════════╝

👤 <b>Foydalanuvchi ismingizni</b> kiriting:
    """
    await callback.message.edit_text(text, parse_mode=ParseMode.HTML)
    await state.set_state(LoginStates.waiting_login_name)

@router.message(LoginStates.waiting_login_name)
async def process_login_name(message: Message, state: FSMContext):
    """Login — ism kiritish"""
    username = message.text.strip()
    user = db.get_user_by_username(username)
    
    if not user:
        await message.answer(
            "❌ <b>Foydalanuvchi topilmadi!</b>\n\n"
            "Iltimos, to'g'ri ismni kiriting yoki ro'yxatdan o'ting:",
            reply_markup=get_auth_keyboard(),
            parse_mode=ParseMode.HTML
        )
        await state.clear()
        return
    
    await state.update_data(login_user_id=user['user_id'], login_username=username)
    await message.answer(
        f"✅ <b>{username}</b> topildi!\n\n🔑 <b>Parolingizni</b> kiriting:",
        parse_mode=ParseMode.HTML
    )
    await state.set_state(LoginStates.waiting_login_password)

@router.message(LoginStates.waiting_login_password)
async def process_login_password(message: Message, state: FSMContext):
    """Login — parol kiritish"""
    password = message.text.strip()
    data = await state.get_data()
    
    login_user_id = data.get('login_user_id')
    login_username = data.get('login_username')
    
    if not db.verify_password(login_user_id, password):
        await message.answer(
            "❌ <b>Parol noto'g'ri!</b>\n\n"
            "Qayta urinib ko'ring yoki /start orqali boshlang.",
            parse_mode=ParseMode.HTML
        )
        await state.clear()
        return
    
    # Login muvaffaqiyatli
    db.login_user(login_user_id)
    # Agar bu ADMIN_ID bo'lsa, admin flagini o'rnat
    if login_user_id == ADMIN_ID:
        db.set_admin_flag(login_user_id, 1)
    user = db.get_user(login_user_id)
    await state.clear()
    
    text = f"""
╔═══════════════════════════════════╗
║   ✅ <b>MUVAFFAQIYATLI KIRDINGIZ!</b> ║
╚═══════════════════════════════════╝

👋 Xush kelibsiz, <b>{login_username}</b>!

📊 <b>Sizning ko'rsatkichlaringiz:</b>
├ 🏆 Ball: <b>{user['score']}</b>
└ 📅 Ro'yxatdan: <b>{user['created_at'][:10]}</b>

Menyudan kerakli bo'limni tanlang 👇
    """
    await message.answer(
        text,
        reply_markup=get_main_menu_keyboard(login_user_id),
        parse_mode=ParseMode.HTML
    )

@router.callback_query(F.data == "logout")
async def logout_callback(callback: CallbackQuery, state: FSMContext):
    """Logout tugmasi"""
    await callback.answer()
    user_id = callback.from_user.id
    user = db.get_user(user_id)
    
    db.logout_user(user_id)
    await state.clear()
    
    text = f"""
╔═══════════════════════════════════╗
║   🚪 <b>TIZIMDAN CHIQILDI</b>        ║
╚═══════════════════════════════════╝

👋 Xayr, <b>{user['username']}</b>!

🏆 <b>Ball:</b> {user['score']}

Qayta kirish uchun tugmani bosing 👇
    """
    await callback.message.edit_text(
        text,
        reply_markup=get_auth_keyboard(),
        parse_mode=ParseMode.HTML
    )

@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery, state: FSMContext):
    """Bosh menyuga qaytish"""
    await callback.answer()
    await state.clear()
    
    user_id = callback.from_user.id
    user = db.get_user(user_id)
    
    # Agar login qilinmagan bo'lsa
    if not db.is_logged_in(user_id):
        await callback.message.edit_text(
            "⚠️ Siz tizimdan chiqib ketgansiz. Iltimos, qayta kiring.",
            reply_markup=get_auth_keyboard(),
            parse_mode=ParseMode.HTML
        )
        return
    
    text = f"""
╔═══════════════════════════════════╗
║   🎓 <b>ZAKOVATI ELITE PRO</b>       ║
╚═══════════════════════════════════╝

👋 Xush kelibsiz, <b>{user['username']}</b>!

🏆 <b>Ball:</b> {user['score']}
    """
    
    await callback.message.edit_text(
        text, 
        reply_markup=get_main_menu_keyboard(user_id), 
        parse_mode=ParseMode.HTML
    )

# ==================== MAIN ====================
async def main():
    """Asosiy funksiya - botni ishga tushirish"""
    import os
    from aiohttp import web

    db.init_db()
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)

    logger.info("╔══════════════════════════════════════╗")
    logger.info("║  🎓 ZAKOVATI ELITE PRO SYSTEM       ║")
    logger.info("╚══════════════════════════════════════╝")
    logger.info("✅ Bot muvaffaqiyatli ishga tushdi!")
    logger.info(f"⚙️  Admin ID: {ADMIN_ID}")
    logger.info(f"📊 Jami savollar: {get_total_questions_combined()}")
    logger.info(f"📚 Jami fanlar: {len(get_all_subjects_combined())}")
    logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    PORT = int(os.environ.get("PORT", 8080))
    WEBHOOK_HOST = os.environ.get("RENDER_EXTERNAL_URL", "").rstrip("/")

    if WEBHOOK_HOST:
        # ========== RENDER MUHITI: WEBHOOK ==========
        WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
        WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

        # Keep-alive endpoint (UptimeRobot / Render uchun)
        async def health_check(request):
            return web.Response(
                text="✅ Zakovati Elite Pro Bot ishlayapti! 24/7 ONLINE",
                status=200
            )

        async def handle_webhook(request):
            from aiogram.types import Update
            try:
                data = await request.json()
                update = Update(**data)
                await dp.feed_update(bot, update)
            except Exception as e:
                logger.error(f"Webhook xatolik: {e}")
            return web.Response(status=200)

        app = web.Application()
        app.router.add_get("/", health_check)
        app.router.add_get("/health", health_check)
        app.router.add_post(WEBHOOK_PATH, handle_webhook)

        # ✅ FIX: Avval eski webhook o'chirish, keyin yangi o'rnatish
        await bot.delete_webhook(drop_pending_updates=True)
        await bot.set_webhook(WEBHOOK_URL)
        logger.info(f"🌐 Webhook URL: {WEBHOOK_URL}")
        logger.info(f"🔌 Port: {PORT}")

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", PORT)
        await site.start()

        logger.info(f"🚀 Server ishga tushdi: 0.0.0.0:{PORT}")
        # Abadiy ishlash
        await asyncio.Event().wait()
    else:
        # ========== LOCAL MUHIT: POLLING ==========
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("🔄 Polling rejimida ishlamoqda (local)...")
        await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

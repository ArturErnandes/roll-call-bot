from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.filters import StateFilter
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.context import FSMContext
import uuid

from config import bot_token, admin
from classes import RollCallStates, RollCall
from database import get_users_list_db
from logger import get_logger


logger = get_logger(__name__)

bot = Bot(token=bot_token, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

_roll_calls: dict[str, RollCall] = {}


def make_roll_id() -> str:
    return uuid.uuid4().hex[:10]


def main_menu_kb():
    kb = InlineKeyboardBuilder()

    kb.button(text="Провести перекличку", callback_data="roll_call")
    kb.button(text="Посмотреть список группы", callback_data="group_check")

    kb.adjust(1)

    return kb.as_markup()


def roll_call_kb(roll_id: str):
    kb = InlineKeyboardBuilder()

    kb.button(text="Я есть", callback_data=f"rc_present:{roll_id}")
    kb.button(text="Меня нет", callback_data=f"rc_absent:{roll_id}")

    kb.adjust(2)
    return kb.as_markup()


def roll_call_admin_kb(roll_id: str):
    kb = InlineKeyboardBuilder()
    kb.button(text="Обновить", callback_data=f"rc_update:{roll_id}")
    kb.adjust(1)
    return kb.as_markup()


def back_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="Назад", callback_data="back_main")
    kb.adjust(1)
    return kb.as_markup()


def render_roll_call_text(roll: RollCall) -> str:
    absent_n = len(roll.absent)
    present_n = len(roll.present)

    lines = []
    i = 1
    for user_id, user_name in roll.users.items():
        if user_id in roll.present:
            mark = "✅"
        elif user_id in roll.absent:
            mark = "❌"
        else:
            mark = "—"

        lines.append(f"{i}. {user_name} {mark}")
        i += 1

    block = "\n".join(lines) if lines else "—"

    return (
        "Перекличка:\n\n"
        f"<b>{roll.subject}</b>\n\n"
        f"Отсутсвуют: <b>{absent_n}</b>\n"
        f"Присутствуют: <b>{present_n}</b>\n\n"
        f"<blockquote>\n{block}\n</blockquote>"
    )


@dp.message(Command("start"))
async def start_handler(message: Message):
    if message.from_user.id != admin:
        await message.answer("Бот переклички активен ✅")
        logger.info(f"/start от пользователя | user_id: {message.from_user.id}")
        return

    await message.answer(
        text="Выберите действие",
        reply_markup=main_menu_kb(),
    )

    logger.info("/start от админа")


@dp.callback_query(F.data == "group_check")
async def group_check_handler(callback: CallbackQuery):
    users = await get_users_list_db()

    if not users:
        text = "Список группы:\n<blockquote>—</blockquote>"
    else:
        lines = [f"{i}. {u.name}" for i, u in enumerate(users, start=1)]
        text = "Список группы:\n\n<blockquote>" + "\n".join(lines) + "</blockquote>"

    await callback.message.edit_text(
        text=text,
        reply_markup=back_kb(),
    )
    await callback.answer()

    logger.info("Админ открыл список группы")


@dp.callback_query(F.data == "back_main")
async def back_main_handler(callback: CallbackQuery):
    await callback.message.edit_text(
        text="Выберите действие",
        reply_markup=main_menu_kb(),
    )
    await callback.answer()
    logger.info("Админ вернулся в главное меню")


@dp.callback_query(F.data == "roll_call")
async def roll_call_menu_handler(callback: CallbackQuery, state: FSMContext):
    msg = await callback.message.edit_text(
        text="Введите название пары:",
        reply_markup=back_kb(),
    )

    await state.set_state(RollCallStates.waiting_subject)
    await state.update_data(prompt_message_id=msg.message_id)

    await callback.answer()
    logger.info("Админ нажал roll_call | ожидаем ввод названия пары")


@dp.message(StateFilter(RollCallStates.waiting_subject))
async def roll_call_subject_handler(message: Message, state: FSMContext):
    if message.from_user.id != admin:
        return

    subject = (message.text or "").strip()

    data = await state.get_data()

    prompt_message_id = data.get("prompt_message_id")

    try:
        if prompt_message_id:
            await bot.delete_message(chat_id=message.chat.id, message_id=prompt_message_id)
    except Exception as e:
        logger.warning(f"Не удалось удалить prompt сообщение: {e}")

    try:
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    except Exception:
        pass

    await state.clear()

    users_list = await get_users_list_db()
    users_map = {u.id: u.name for u in users_list}

    roll_id = make_roll_id()
    _roll_calls[roll_id] = RollCall(
        roll_id=roll_id,
        subject=subject,
        users=users_map,
        present=set(),
        absent=set(),
        report_sent=False,
        admin_message_id=None,
    )

    kb = roll_call_kb(roll_id)

    sent = 0
    for user_id in users_map.keys():
        try:
            await bot.send_message(
                chat_id=user_id,
                text=f"Пара: <b>{subject}</b>",
                reply_markup=kb,
            )
            sent += 1
        except Exception as e:
            logger.warning(f"Не удалось отправить пользователю {user_id}: {e}")

    logger.info(f"Перекличка запущена | roll_id={roll_id} | subject={subject} | sent={sent}/{len(users_map)}")


@dp.callback_query(F.data.startswith(("rc_present:", "rc_absent:")))
async def roll_call_mark_handler(callback: CallbackQuery):
    data = callback.data or ""
    action, roll_id = data.split(":", 1)

    roll = _roll_calls.get(roll_id)
    if not roll:
        await callback.answer("Перекличка не найдена", show_alert=True)
        return

    user_id = callback.from_user.id

    roll.present.discard(user_id)
    roll.absent.discard(user_id)

    if action == "rc_present":
        roll.present.add(user_id)
    else:
        roll.absent.add(user_id)

    await callback.answer("Отмечено ✅")

    if not roll.report_sent:
        text = render_roll_call_text(roll)

        msg = await bot.send_message(
            chat_id=admin,
            text=text,
            reply_markup=roll_call_admin_kb(roll_id),
        )
        roll.report_sent = True
        roll.admin_message_id = msg.message_id

        logger.info(f"Отправлен первый отчёт админy | roll_id={roll_id}")


@dp.callback_query(F.data.startswith("rc_update:"))
async def roll_call_update_handler(callback: CallbackQuery):
    if callback.from_user.id != admin:
        await callback.answer("Нет прав", show_alert=True)
        return

    roll_id = (callback.data or "").split(":", 1)[1]
    roll = _roll_calls.get(roll_id)
    if not roll:
        await callback.answer("Перекличка не найдена", show_alert=True)
        return

    text = render_roll_call_text(roll)

    chat_id = callback.message.chat.id
    message_id = roll.admin_message_id or callback.message.message_id

    await bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text=text,
        reply_markup=roll_call_admin_kb(roll_id),
    )

    await callback.answer("Обновлено ✅")
    logger.info(f"Обновлён отчёт переклички | roll_id={roll_id}")
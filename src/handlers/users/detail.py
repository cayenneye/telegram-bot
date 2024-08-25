from aiogram import Bot, Router, F
from aiogram.enums import ChatType
from aiogram.filters import StateFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from models import User
from repositories import BalanceRepository
from views import (
    UserSettingsCalledInGroupChatView,
    UserMenuView,
    render_message_or_callback_query,
)
from views import answer_view, edit_message_by_view, UserPersonalSettingsView

__all__ = ('register_handlers',)


async def on_show_personal_settings(
        message_or_callback_query: Message | CallbackQuery,
) -> None:
    view = UserPersonalSettingsView()
    await render_message_or_callback_query(
        message_or_callback_query=message_or_callback_query,
        view=view,
    )


async def on_settings_in_group_chat(
        message: Message,
        bot: Bot,
) -> None:
    me = await bot.get_me()
    view = UserSettingsCalledInGroupChatView(me.username)
    await answer_view(message=message, view=view)


async def on_show_settings(
        message_or_callback_query: Message | CallbackQuery,
        state: FSMContext,
        user: User,
        balance_repository: BalanceRepository,
) -> None:
    await state.clear()
    user_balance = await balance_repository.get_user_balance(user.id)
    view = UserMenuView(
        user=user,
        balance=user_balance.balance,
    )
    if isinstance(message_or_callback_query, Message):
        await answer_view(message=message_or_callback_query, view=view)
    else:
        await edit_message_by_view(
            message=message_or_callback_query.message,
            view=view,
        )


def register_handlers(router: Router) -> None:
    router.message.register(
        on_show_personal_settings,
        F.text == '🎨 Настройки',
        F.chat.type == ChatType.PRIVATE,
        StateFilter('*'),
    )
    router.callback_query.register(
        on_show_personal_settings,
        F.data == 'show-personal-settings',
        StateFilter('*'),
    )
    router.message.register(
        on_settings_in_group_chat,
        Command('settings'),
        F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}),
        StateFilter('*'),
    )
    router.callback_query.register(
        on_show_settings,
        F.data == 'show-user-settings',
        F.chat.type == ChatType.PRIVATE,
        StateFilter('*'),
    )
    router.message.register(
        on_show_settings,
        F.text.in_({
            '/start',
            '/settings',
            '🔙 Назад',
            '🔙 Отключить режим анонимных сообщений',
        }),
        F.chat.type == ChatType.PRIVATE,
        StateFilter('*'),
    )

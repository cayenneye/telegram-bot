from aiogram import Router, F
from aiogram.enums import ContentType
from aiogram.filters import StateFilter, Command, or_f
from aiogram.types import Message, CallbackQuery

from callback_data import FoodMenuDetailCallbackData
from filters import (
    food_menu_for_tomorrow_filter,
    food_menu_for_today_filter,
    food_menu_for_n_days_filter,
)
from repositories import BalanceRepository, FoodMenuRepository
from services import BalanceNotifier
from views import FoodMenuMediaGroupView, answer_view, FoodMenuFAQView, answer_media_group_view

__all__ = ('router',)

router = Router(name=__name__)


@router.callback_query(
    FoodMenuDetailCallbackData.filter(),
    StateFilter('*'),
)
async def on_show_food_menu_for_specific_day_callback(
        callback_query: CallbackQuery,
        callback_data: FoodMenuDetailCallbackData,
        balance_repository: BalanceRepository,
        balance_notifier: BalanceNotifier,
        food_menu_repository: FoodMenuRepository,
) -> None:
    food_menus = await food_menu_repository.get_all()

    try:
        food_menu = food_menus[callback_data.days_skip_count]
    except IndexError:
        await callback_query.answer(
            text='❌ Нет данных о меню на указанный день',
            show_alert=True,
        )
    else:

        view = FoodMenuMediaGroupView(food_menu)
        await answer_media_group_view(message=callback_query.message, view=view)
    finally:
        await callback_query.message.delete()


@router.message(
    F.content_type == ContentType.TEXT,
    or_f(
        food_menu_for_today_filter,
        food_menu_for_tomorrow_filter,
        food_menu_for_n_days_filter,
    ),
    StateFilter('*'),
)
async def on_show_food_menu_for_specific_day(
        message: Message,
        balance_repository: BalanceRepository,
        balance_notifier: BalanceNotifier,
        food_menu_repository: FoodMenuRepository,
        days_skip_count: int,
) -> None:
    food_menus = await food_menu_repository.get_all()

    withdrawal = await balance_repository.create_withdrawal(
        user_id=message.from_user.id,
        amount=80,
        description='Просмотр йемека на сегодня',
    )
    await balance_notifier.send_withdrawal_notification(withdrawal)

    try:
        food_menu = food_menus[days_skip_count]
    except IndexError:
        await message.reply('❌ Нет данных о меню на указанный день')
        return

    view = FoodMenuMediaGroupView(food_menu)
    await answer_media_group_view(message=message, view=view)


@router.message(
    F.content_type == ContentType.TEXT,
    or_f(
        Command('yemek'),
        F.text == '🍽️ Йемек',
    ),
    StateFilter('*'),
)
async def on_show_food_menu_instructions(message: Message) -> None:
    await answer_view(message=message, view=FoodMenuFAQView())

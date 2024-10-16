from aiogram import Router, F
from aiogram.filters import (
    StateFilter,
    Command,
    ExceptionTypeFilter,
    or_f,
    invert_f,
)
from aiogram.types import CallbackQuery, Message, ErrorEvent, User

from exceptions import InsufficientFundsForWithdrawalError
from repositories import BalanceRepository
from views import (
    UserBalanceView,
    render_message_or_callback_query,
    FinanceMenuView,
    answer_view,
)

router = Router(name=__name__)


@router.message(
    F.text == '💰 Финансы',
    StateFilter('*'),
)
async def on_show_finance_menu(message: Message) -> None:
    view = FinanceMenuView()
    await answer_view(message=message, view=view)


@router.error(ExceptionTypeFilter(InsufficientFundsForWithdrawalError))
async def on_insufficient_funds_for_withdrawal_error(event: ErrorEvent) -> None:
    text = (
        '❌ Недостаточно средств для списания\n'
        f'💸 Необходимо {event.exception.amount} дак-дак коинов'
    )
    if event.update.message is not None:
        await event.update.message.reply(text)
    if event.update.callback_query is not None:
        await event.update.callback_query.answer(text, show_alert=True)


@router.message(
    or_f(
        Command('balance'),
        F.text.lower().in_({'баланс', 'остаток', 'счет', 'balance'}),
    ),
    or_f(
        F.reply_to_message.from_user.as_('from_user'),
        F.from_user.as_('from_user'),
    ),
    invert_f(F.reply_to_message.is_bot),
    StateFilter('*'),
)
async def on_show_other_user_balance(
        message: Message,
        from_user: User,
        balance_repository: BalanceRepository,
) -> None:
    user_balance = await balance_repository.get_user_balance(from_user.id)
    view = UserBalanceView(user_balance, from_user.full_name)
    await answer_view(message=message, view=view)


@router.callback_query(
    F.data == 'show-user-balance',
    StateFilter('*'),
)
async def on_show_user_balance(
        callback_query: CallbackQuery,
        balance_repository: BalanceRepository,
) -> None:
    from_user = callback_query.from_user
    user_balance = await balance_repository.get_user_balance(from_user.id)
    view = UserBalanceView(
        user_balance=user_balance,
        user_fullname=from_user.full_name,
    )
    await render_message_or_callback_query(
        message_or_callback_query=callback_query,
        view=view,
    )


@router.message(
    Command('richest_top'),
    StateFilter('*'),
)
async def on_show_richest_users_statistics(
        message: Message,
        balance_repository: BalanceRepository,
) -> None:
    await balance_repository.create_richest_users_statistics_task(
        chat_id=message.chat.id,
        user_id=message.from_user.id,
    )

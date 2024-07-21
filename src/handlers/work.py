from aiogram import F, Router
from aiogram.enums import ChatType
from aiogram.filters import Command, StateFilter, invert_f, or_f
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from filters import integer_filter, reply_message_from_bot_filter
from repositories import BalanceRepository
from services import (
    ArithmeticProblem, BalanceNotifier, get_arithmetic_problem,
)
from services.clean_up import CleanUpService
from views import (
    ArithmeticProblemSolvedView, ArithmeticProblemView, answer_view, reply_view,
)

router = Router(name=__name__)


@router.message(
    F.reply_to_message.text.startswith('❓ Сколько будет'),
    invert_f(F.reply_to_message.text.contains('[решено]')),
    invert_f(integer_filter),
    StateFilter('*'),
)
async def on_arithmetic_expression_answer_is_not_integer(
        message: Message
) -> None:
    await message.reply('❌ Ответ должен быть целым числом')


@router.message(
    F.reply_to_message.text.startswith('❓ Сколько будет'),
    F.reply_to_message.text.contains('[решено]'),
    StateFilter('*'),
)
async def on_arithmetic_expression_already_solved(message: Message) -> None:
    await message.reply('❌ Это задание уже решено')


@router.message(
    F.reply_to_message.text.startswith('❓ Сколько будет'),
    invert_f(F.reply_to_message.text.contains('[решено]')),
    integer_filter,
    reply_message_from_bot_filter,
    StateFilter('*'),
)
async def on_arithmetic_expression_answer(
        message: Message,
        number: int,
        balance_repository: BalanceRepository,
        balance_notifier: BalanceNotifier,
        clean_up_service: CleanUpService,
) -> None:
    text = f'{message.reply_to_message.text}\n\n<i>[решено]</i>'

    arithmetic_problem = ArithmeticProblem.from_text(text)

    if arithmetic_problem.compute_correct_answer() != number:
        sent_message = await message.reply('Неправильно')
        await clean_up_service.create_clean_up_task(message, sent_message)
        return

    amount_to_deposit = arithmetic_problem.compute_reward_value()
    await message.reply_to_message.edit_text(text)
    deposit = await balance_repository.create_deposit(
        user_id=message.from_user.id,
        amount=amount_to_deposit,
        description='Solved arithmetic problem',
    )
    view = ArithmeticProblemSolvedView(amount_to_deposit)
    sent_message = await reply_view(message=message, view=view)

    await clean_up_service.create_clean_up_task(message, sent_message)

    if message.chat.type != ChatType.PRIVATE:
        await balance_notifier.send_deposit_notification(deposit)


@router.message(
    or_f(
        Command('work'),
        F.text == '💼 Работать',
    ),
    StateFilter('*'),
)
async def on_create_arithmetic_expression_to_solve(
        message: Message,
        state: FSMContext,
        clean_up_service: CleanUpService,
) -> None:
    await state.clear()

    arithmetic_problem = get_arithmetic_problem()
    view = ArithmeticProblemView(
        expression=arithmetic_problem.get_humanized_expression(),
        reward=arithmetic_problem.compute_reward_value(),
    )
    sent_message = await answer_view(message=message, view=view)
    await clean_up_service.create_clean_up_task(message, sent_message)

import textwrap

from aiogram.types import InputMediaPhoto

from models import DailyFoodMenu
from views.base import View

__all__ = ('FoodMenuMediaGroupView', 'FoodMenuFAQView')


class FoodMenuMediaGroupView(View):

    def __init__(self, daily_food_menu: DailyFoodMenu):
        self.__daily_food_menu = daily_food_menu

    def get_text(self) -> str:
        caption: list[str] = [
            f'🍽️ <b>Меню на {self.__daily_food_menu.at:%d.%m.%Y}</b> 🍽️\n'
        ]

        total_calories_count: int = 0

        for food_menu_item in self.__daily_food_menu.items:
            caption.append(
                f'🧂 <u>{food_menu_item.name}</u>\n'
                f'🌱 Калории: <i>{food_menu_item.calories_count}</i>\n'
            )

            total_calories_count += food_menu_item.calories_count

        caption.append(f'<b>Сумма калорий: {total_calories_count}</b>')
        return '\n'.join(caption)

    def as_media_group(self) -> list[InputMediaPhoto]:
        first = InputMediaPhoto(
            media=str(self.__daily_food_menu.items[0].photo_url),
            caption=self.get_text(),
        )

        return [first] + [
            InputMediaPhoto(
                media=str(food_menu_item.photo_url),
            ) for food_menu_item in self.__daily_food_menu.items[1:]
        ]


class FoodMenuFAQView(View):
    text = textwrap.dedent('''\
    <b>🤤Срочный просмотр меню в йемекхане:</b>

    <u>На сегодня:</u>
    <code>/yemek today</code>
    
    <u>На завтра:</u>
    <code>/yemek tomorrow</code>
    
    <u>На неделю вперёд:</u>
    <code>/yemek week</code>
    
    <b>🧐Так же можно просматривать на N дней вперёд:</b>
    
    •<code>/yemek {N}</code>
    
    Например👇
    <u>На послезавтра</u> - <code>/yemek 2</code>
    <u>10 дней вперёд</u> - <code>/yemek 10</code>
    ''')

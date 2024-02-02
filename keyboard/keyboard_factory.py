from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from factories.factory import MainCallbackFactory


async def create_fac_menu(
        width: int = 2,
        back_page: str = None,
        back: bool | str = False,
        pagination: bool = False,
        mission_page: int = 0,
        mission_count: int = 0,
        sizes: tuple = None,
        **kwargs: str) -> InlineKeyboardMarkup:
    """
    Create fac menu (inline keyboard)
    :param width:
    :param back_page:
    :param back:
    :param pagination:
    :param mission_page:
    :param mission_count:
    :param sizes:
    :param kwargs:
    :return:
    """

    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

    kb_builder.row(*[
        InlineKeyboardButton(
            text=text,
            callback_data=MainCallbackFactory(
                page=data,
                back_page=back_page
            ).pack()
        ) for data, text in kwargs.items()
    ])
    if pagination:
        if mission_page > 0:
            kb_builder.add(InlineKeyboardButton(
                text='<<',
                callback_data=MainCallbackFactory(
                    page='missions',
                    back_page=back_page,
                    mission_page=mission_page - 1
                ).pack()
            ))
        if (mission_page + 1) * 8 <= mission_count:
            kb_builder.add(InlineKeyboardButton(
                text='>>',
                callback_data=MainCallbackFactory(
                    page='missions',
                    back_page=back_page,
                    mission_page=mission_page + 1
                ).pack()
            ))
    if back:
        kb_builder.add(InlineKeyboardButton(
            text='Назад',
            callback_data=MainCallbackFactory(
                page=back,
                back_page=back_page
            ).pack()
        ))
        if sizes:
            kb_builder.adjust(*sizes)
        else:
            kb_builder.adjust(*[1] * len(kwargs), 2)
    elif sizes:
        kb_builder.adjust(*sizes)
    else:
        kb_builder.adjust(*[width] * len(kwargs))
    return kb_builder.as_markup()

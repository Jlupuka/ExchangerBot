from typing import Type

from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from factories.factory import UserCallbackFactory, AdminCallbackFactory, MissionCallbackFactory
from lexicon.lexicon import backLexicon


class Factories:
    @staticmethod
    async def create_fac_menu(
            callback_factory: Type[UserCallbackFactory | AdminCallbackFactory],
            width: int = 2,
            back_page: str = None,
            back_name: str = backLexicon['backLexicon'],
            back: bool | str = False,
            sizes: tuple = None,
            **kwargs: str) -> InlineKeyboardMarkup:
        """
            Create fac menu (inline keyboard) with specified parameters.
            :param callback_factory: Callback factory to create callback data.
            :param width: Number of buttons in a row. Default is 2.
            :param back_page: Page to return when back button is clicked. Default is None.
            :param back_name: Text for the back button. Default is 'Назад'.
            :param back: If True, add a back button to the keyboard. If False, don't add a back button.
            :param sizes: Sizes of the rows in the keyboard. Default is None.
            :param kwargs: Key-value pairs where keys are page and values are button texts.
            :return: InlineKeyboardMarkup object with the created keyboard.
            """

        kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

        kb_builder.row(*[
            InlineKeyboardButton(
                text=text,
                callback_data=callback_factory(
                    page=data,
                    back_page=back_page
                ).pack()
            ) for data, text in kwargs.items()
        ])

        if back:
            kb_builder.add(InlineKeyboardButton(
                text=back_name,
                callback_data=callback_factory(
                    page=back,
                    back_page=back_page
                ).pack()
            ))
            if sizes:
                kb_builder.adjust(*sizes).as_markup(resize_keyboard=True)
            else:
                kb_builder.adjust(*[1] * len(kwargs), 2).as_markup(resize_keyboard=True)
        elif sizes:
            kb_builder.adjust(*sizes).as_markup(resize_keyboard=True)
        else:
            kb_builder.adjust(*[width] * len(kwargs)).as_markup(resize_keyboard=True)
        return kb_builder.as_markup()

    @staticmethod
    async def create_fac_mission(callback_factory: Type[MissionCallbackFactory],
                                 mission_id: int,
                                 back_name: str = backLexicon['backLexicon'],
                                 back: bool | str | int = False,
                                 back_page: None | str = None,
                                 sizes: tuple = None,
                                 width: int = 2,
                                 **kwargs) -> InlineKeyboardMarkup:
        kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

        kb_builder.row(*[
            InlineKeyboardButton(
                text=text,
                callback_data=callback_factory(
                    mission_id=mission_id,
                    back_page=back_page,
                    page=data,
                ).pack()
            ) for data, text in kwargs.items()
        ])
        if back:
            kb_builder.add(InlineKeyboardButton(
                text=back_name,
                callback_data=callback_factory(
                    mission_id=mission_id,
                    back_page=back_page,
                    page=back,
                ).pack()
            ))
        if sizes:
            kb_builder.adjust(*sizes).as_markup(resize_keyboard=True)
        else:
            kb_builder.adjust(*[width] * len(kwargs)).as_markup(resize_keyboard=True)
        return kb_builder.as_markup()

    @staticmethod
    async def create_fac_pagination_missions(back: str = None,
                                             back_page: str = None,
                                             back_name: str = backLexicon['backLexicon'],
                                             mission_count: int = 0,
                                             mission_page: int = 0,
                                             mission_status: str = 'wait',
                                             **kwargs) -> InlineKeyboardMarkup:
        kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

        kb_builder.row(*[
            InlineKeyboardButton(
                text=text,
                callback_data=MissionCallbackFactory(
                    mission_id=data,
                    back_page=back_page,
                    page=data,
                ).pack()
            ) for data, text in kwargs.items()
        ])
        flag_go, flag_back = False, False
        if mission_page > 0:
            kb_builder.add(InlineKeyboardButton(
                text='<<',
                callback_data=AdminCallbackFactory(
                    page=mission_status,
                    back_page=back_page,
                    mission_page=mission_page - 1
                ).pack()
            ))
            flag_go = True
        if (mission_page + 1) * 8 < mission_count:
            kb_builder.add(InlineKeyboardButton(
                text='>>',
                callback_data=AdminCallbackFactory(
                    page=mission_status,
                    back_page=back_page,
                    mission_page=mission_page + 1
                ).pack()
            ))
            flag_back = True
        if back:
            kb_builder.add(InlineKeyboardButton(
                text=back_name,
                callback_data=AdminCallbackFactory(
                    back_page=back_page,
                    page=back,
                ).pack()
            ))
        if flag_back and flag_go:
            size = [2, 1]
        elif any((flag_back, flag_go)):
            size = [1, 1]
        else:
            size = [1]

        kb_builder.adjust(*[1] * abs(mission_count - (mission_page + 1) * 8),
                          *size).as_markup(resize_keyboard=True)
        return kb_builder.as_markup()

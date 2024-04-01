from typing import Type, Union, Any

from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from factories.factory import (
    UserCallbackFactory,
    AdminCallbackFactory,
    MissionCallbackFactory,
    KYCCallbackFactory,
)
from lexicon.lexicon import backLexicon


class Factories:
    @staticmethod
    async def create_fac_menu(
        callback_factory: Type[Union[AdminCallbackFactory, UserCallbackFactory]],
        width: int = 2,
        back_page: Union[None, str] = None,
        back_name: str = backLexicon["backLexicon"],
        back: Union[bool, str] = False,
        sizes: tuple = None,
        **kwargs: dict[str:str]
    ) -> InlineKeyboardMarkup:
        """
        Create factory menu (inline keyboard) with specified parameters
        :param callback_factory: (Type[Union[AdminCallbackFactory, UserCallbackFactory]])
        :param width: (int) Number of buttons in a row. Default is 2.
        :param back_page: (Union[None, str]) Page to return when back button is clicked. Default is None.
        :param back_name: (str) Text for the back button. Default is 'Назад'.
        :param back: (Union[bool, str]) If True, add a back button to the keyboard. If False, don't add a back button.
        :param sizes: (int) Sizes of the rows in the keyboard. Default is None.
        :param kwargs: (dict[str:str]) Key-value pairs where keys are page and values are button texts.
        :return: InlineKeyboardMarkup object with the created keyboard.
        """
        kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
        kb_builder.row(
            *[
                InlineKeyboardButton(
                    text=text,
                    callback_data=callback_factory(
                        page=data, back_page=back_page
                    ).pack(),
                )
                for data, text in kwargs.items()
            ]
        )

        if back:
            kb_builder.add(
                InlineKeyboardButton(
                    text=back_name,
                    callback_data=callback_factory(
                        page=back, back_page=back_page
                    ).pack(),
                )
            )
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
    async def create_fac_mission(
        callback_factory: Type[MissionCallbackFactory],
        mission_id: int,
        back_name: str = backLexicon["backLexicon"],
        back: Union[bool, str, int] = False,
        back_page: Union[None, str] = None,
        sizes: tuple[Any] = None,
        width: int = 2,
        **kwargs: dict[str:str]
    ) -> InlineKeyboardMarkup:
        """
        Create factory mission (inline keyboard) with specified parameters
        :param callback_factory: (MissionCallbackFactory)
        :param mission_id: (int)
        :param back_name: (str) Text for the back button. Default is 'Вернуться'.
        :param back: (Union[bool, str, int])
        :param back_page: (Union[None, str])
        :param sizes: (tuple[Any]) how many buttons will be on the line
        :param width: (int) how many buttons will be on the line, if you have not specified sizes
        :param kwargs: (dict[str:str]) Key-value pairs where keys are page and values are button texts.
        :return: InlineKeyboardMarkup object with the created keyboard.
        """
        kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

        kb_builder.row(
            *[
                InlineKeyboardButton(
                    text=text,
                    callback_data=callback_factory(
                        mission_id=mission_id,
                        back_page=back_page,
                        page=data,
                    ).pack(),
                )
                for data, text in kwargs.items()
            ]
        )
        if back:
            kb_builder.add(
                InlineKeyboardButton(
                    text=back_name,
                    callback_data=callback_factory(
                        mission_id=mission_id,
                        back_page=back_page,
                        page=back,
                    ).pack(),
                )
            )
        if sizes:
            kb_builder.adjust(*sizes).as_markup(resize_keyboard=True)
        else:
            kb_builder.adjust(*[width] * len(kwargs)).as_markup(resize_keyboard=True)
        return kb_builder.as_markup()

    @staticmethod
    async def create_fac_pagination_missions(
        factory: Union[Type[AdminCallbackFactory], Type[UserCallbackFactory]],
        back: str = None,
        back_page: str = None,
        back_name: str = backLexicon["backLexicon"],
        mission_count: int = 0,
        mission_count_total: int = 0,
        mission_page: int = 0,
        mission_status: str = "wait",
        **kwargs: dict[str:str]
    ) -> InlineKeyboardMarkup:
        """
        Create factory (inline keyboard) with specified parameters and pagination
        :param factory: (Type[Union[AdminCallbackFactory, UserCallbackFactory]])
        :param back: (str)
        :param back_page: (str)
        :param back_name: (str) Text for the back button. Default is 'Вернуться'.
        :param mission_count: (int) of missions in a certain status
        :param mission_count_total: (int) total missions
        :param mission_page: (int)
        :param mission_status: (str)
        :param kwargs: (dict[str:str]) Key-value pairs where keys are page and values are button texts
        :return: InlineKeyboardMarkup object with the created keyboard.
        """
        kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
        kb_builder.row(
            *[
                InlineKeyboardButton(
                    text=text,
                    callback_data=MissionCallbackFactory(
                        mission_id=data,
                        back_page=back_page,
                        page=data,
                    ).pack(),
                )
                for data, text in kwargs.items()
            ]
        )
        flag_go, flag_back = False, False
        if mission_page > 0:
            kb_builder.add(
                InlineKeyboardButton(
                    text="<<",
                    callback_data=factory(
                        page=mission_status,
                        back_page=back_page,
                        mission_page=mission_page - 1,
                    ).pack(),
                )
            )
            flag_go = True
        if (mission_page + 1) * 8 < mission_count_total:
            kb_builder.add(
                InlineKeyboardButton(
                    text=">>",
                    callback_data=factory(
                        page=mission_status,
                        back_page=back_page,
                        mission_page=mission_page + 1,
                    ).pack(),
                )
            )
            flag_back = True
        if back:
            kb_builder.add(
                InlineKeyboardButton(
                    text=back_name,
                    callback_data=factory(
                        back_page=back_page,
                        page=back,
                    ).pack(),
                )
            )
        if flag_back and flag_go:
            size = [2, 1]
        elif any((flag_back, flag_go)):
            size = [1, 1]
        else:
            size = [1]
        kb_builder.adjust(*[1] * mission_count, *size).as_markup(resize_keyboard=True)
        return kb_builder.as_markup()

    @staticmethod
    async def create_kyc_fac(
        user_id: int, verif_number: int, **kwargs: dict[str:str]
    ) -> InlineKeyboardMarkup:
        """
        Returns the keypad for passing KYC
        :param user_id: (int) User id
        :param verif_number: (int) Verification number
        :param kwargs: (dict[str:str]) Key-value pairs where keys are page and values are button texts.
        :return: (InlineKeyboardMarkup) InlineKeyboardMarkup object with the created keyboard.
        """
        kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
        kb_builder.row(
            *[
                InlineKeyboardButton(
                    text=text,
                    callback_data=KYCCallbackFactory(
                        user_id=user_id, verif_number=verif_number, page=data
                    ).pack(),
                )
                for data, text in kwargs.items()
            ]
        )
        kb_builder.adjust(2)
        return kb_builder.as_markup(resize_keyboard=True)

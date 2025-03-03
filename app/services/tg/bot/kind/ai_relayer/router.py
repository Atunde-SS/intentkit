import inspect
import logging

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from epyxid import XID

from app.core.client import execute_agent
from app.services.tg.bot import pool
from app.services.tg.bot.filter.chat_type import GroupOnlyFilter
from app.services.tg.bot.filter.content_type import TextOnlyFilter
from app.services.tg.bot.filter.id import WhitelistedChatIDsFilter
from app.services.tg.bot.filter.no_bot import NoBotFilter
from app.services.tg.utils.cleanup import remove_bot_name
from models.chat import AuthorType, ChatMessageCreate

logger = logging.getLogger(__name__)


def cur_func_name():
    return inspect.stack()[1][3]


def cur_mod_name():
    return inspect.getmodule(inspect.stack()[1][0]).__name__


general_router = Router()


@general_router.message(Command("chat_id"), NoBotFilter(), TextOnlyFilter())
async def command_chat_id(message: Message) -> None:
    try:
        await message.answer(text=str(message.chat.id))
    except Exception as e:
        logger.warning(
            f"error processing in function:{cur_func_name()}, token:{message.bot.token} err: {str(e)}"
        )


## group commands and messages


@general_router.message(
    CommandStart(),
    NoBotFilter(),
    WhitelistedChatIDsFilter(),
    GroupOnlyFilter(),
    TextOnlyFilter(),
)
async def gp_command_start(message: Message):
    try:
        cached_bot_item = pool.bot_by_token(message.bot.token)
        await message.answer(text=cached_bot_item.greeting_group)
    except Exception as e:
        logger.warning(
            f"error processing in function:{cur_func_name()}, token:{message.bot.token} err: {str(e)}"
        )


@general_router.message(
    WhitelistedChatIDsFilter(), NoBotFilter(), GroupOnlyFilter(), TextOnlyFilter()
)
async def gp_process_message(message: Message) -> None:
    bot = await message.bot.get_me()
    if (
        message.reply_to_message
        and message.reply_to_message.from_user.id == message.bot.id
    ) or bot.username in message.text:
        cached_bot_item = pool.bot_by_token(message.bot.token)
        if cached_bot_item is None:
            logger.warning(f"bot with token {message.bot.token} not found in cache.")
            return

        try:
            # remove bot name tag from text
            message_text = remove_bot_name(bot.username, message.text)

            input = ChatMessageCreate(
                id=str(XID()),
                agent_id=cached_bot_item.agent_id,
                chat_id=pool.agent_chat_id(
                    cached_bot_item.is_public_memory, message.chat.id
                ),
                author_id=str(message.from_user.id),
                author_type=AuthorType.TELEGRAM,
                message=message_text,
            )
            response = await execute_agent(input)
            await message.answer(
                text=response[-1].message if response else "Server Error",
                reply_to_message_id=message.message_id,
            )
        except Exception as e:
            logger.warning(
                f"error processing in function:{cur_func_name()}, token:{message.bot.token}, err={str(e)}"
            )


## direct commands and messages


@general_router.message(
    CommandStart(), NoBotFilter(), WhitelistedChatIDsFilter(), TextOnlyFilter()
)
async def command_start(message: Message) -> None:
    try:
        cached_bot_item = pool.bot_by_token(message.bot.token)
        await message.answer(text=cached_bot_item.greeting_user)
    except Exception as e:
        logger.warning(
            f"error processing in function:{cur_func_name()}, token:{message.bot.token} err: {str(e)}"
        )


@general_router.message(
    TextOnlyFilter(),
    NoBotFilter(),
    WhitelistedChatIDsFilter(),
)
async def process_message(message: Message) -> None:
    cached_bot_item = pool.bot_by_token(message.bot.token)
    if cached_bot_item is None:
        logger.warning(f"bot with token {message.bot.token} not found in cache.")
        return

    try:
        input = ChatMessageCreate(
            id=str(XID()),
            agent_id=cached_bot_item.agent_id,
            chat_id=pool.agent_chat_id(False, message.chat.id),
            author_id=str(message.from_user.id),
            author_type=AuthorType.TELEGRAM,
            message=message.text,
        )
        response = await execute_agent(input)
        await message.answer(
            text=response[-1].message if response else "Server Error",
            reply_to_message_id=message.message_id,
        )
    except Exception as e:
        logger.warning(
            f"error processing in function:{cur_func_name()}, token:{message.bot.token} err:{str(e)}"
        )

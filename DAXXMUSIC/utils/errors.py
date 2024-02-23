import sys
import traceback
from functools import wraps

from pyrogram.errors.exceptions.forbidden_403 import ChatWriteForbidden
from DAXXMUSIC import app
from DAXXMUSIC.logging import LOGGER

LOG_CHANNEL = ("LOG_CHANNEL", "https://t.me/ToXiC_BoY_OFFICIAL")



def split_limits(text):
    if len(text) < 2048:
        return [text]

    lines = text.splitlines(True)
    small_msg = ""
    result = []
    for line in lines:
        if len(small_msg) + len(line) < 2048:
            small_msg += line
        else:
            result.append(small_msg)
            small_msg = line

    result.append(small_msg)

    return result


def capture_err(func):
    @wraps(func)
    async def capture(client, message, *args, **kwargs):
        if isinstance(message, CallbackQuery):
            sender = message.message.reply
            chat = message.message.chat
            msg = message.message.text or message.message.caption
        else:
            sender = message.reply
            chat = message.chat
            msg = message.text or message.caption
        try:
            return await func(client, message, *args, **kwargs)
        except ChatWriteForbidden:
            return await client.leave_chat(message.chat.id)
        except Exception as err:
            exc = traceback.format_exc()
            error_feedback = "ERROR | {} | {}\n\n{}\n\n{}\n".format(
                message.from_user.id if message.from_user else 0,
                chat.id if chat else 0,
                msg,
                exc,
            )
            day = datetime.now()
            tgl_now = datetime.now()

            cap_day = f"{day.strftime('%A')}, {tgl_now.strftime('%d %B %Y %H:%M:%S')}"
            await sender(
                "😭 An Internal Error Occurred while processing your Command, the Logs have been sent to the Owners of this Bot. Sorry for Inconvenience..."
            )
            with open(
                f"crash_{tgl_now.strftime('%d %B %Y')}.txt", "w+", encoding="utf-8"
            ) as log:
                log.write(error_feedback)
                log.close()
            await client.send_document(
                LOG_CHANNEL,
                f"crash_{tgl_now.strftime('%d %B %Y')}.txt",
                caption=f"Crash Report of this Bot\n{cap_day}",
            )
            os.remove(f"crash_{tgl_now.strftime('%d %B %Y')}.txt")
            raise err

    return capture

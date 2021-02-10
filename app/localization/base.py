from abc import ABC


class BaseLocalization(ABC):  # == English
    # ---- WELCOME ----
    def help_message(self):
        return (
            f"Command list:\n"
            f"/help – this help page\n"
            f"/start – start/restart the bot\n"
        )

    TEXT_WELCOME = ''

    BUTTON_ENG = 'English'

    BUTTON_MM_MAKE_AVATAR = 'Make me an avatar!'

    def unknown_command(self):
        return (
            "🙄 Sorry, I didn't understand that command.\n"
            "Use /help to see available commands."
        )

    # ------- AVATAR -------

    LOADING_STICKER = 'CAACAgIAAxkBAAIRx1--Tia-m6DNRIApk3yqmNWvap_sAALcAAP3AsgPUNi8Bnu98HweBA'

    TEXT_AVA_WELCOME = "🖼️ Drop me a picture and I'll make your Alpha-branded avatar. " \
                       "I can also download an image from your profile."

    TEXT_AVA_ERR_INVALID = '⚠️ Your picture has invalid format!'
    TEXT_AVA_ERR_SIZE = '🖼️ Your picture must be from 64x64 to 4096x4096'
    TEXT_AVA_ERR_NO_PIC = '⚠️ You have no user pic...'
    TEXT_AVA_READY = '🥳 <b>Your THORChain avatar is ready!</b> Download this image and set it as a profile picture' \
                     ' at Telegram and other social networks.'

    TEXT_AVA_READY_FROM_USERPIC = ''

    BUTTON_AVA_FROM_MY_USERPIC = '😀 From my userpic'
    BUTTON_SM_BACK_MM = 'Back'

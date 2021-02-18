from abc import ABC

from lib.datetime import format_time_ago
from lib.texts import code, link, pre, calc_percent_change, adaptive_round_to_str, emoji_for_percent_change, \
    pretty_dollar, pretty_money, bold
from models.models import PriceReport


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
                       "I can use the image from your profile."

    TEXT_AVA_ERR_INVALID = '⚠️ Your picture has invalid format!'
    TEXT_AVA_ERR_SIZE = '🖼️ Your picture must be from 64x64 to 4096x4096'
    TEXT_AVA_ERR_NO_PIC = '⚠️ You have no user pic...'
    TEXT_AVA_READY = '🥳 <b>Your Alpha avatar is ready!</b> Download this image and set it as a profile picture' \
                     ' at Telegram and other social networks.'

    TEXT_AVA_READY_FROM_USERPIC = ''

    BUTTON_AVA_FROM_MY_USERPIC = '😀 From my profile picture'

    # ----------- PRICE NOTIFICATION ------------

    ALPHA_GECKO_URL = 'https://www.coingecko.com/en/coins/alpha-finance'
    ALPHA = 'ALPHA'

    def notification_text_price_update(self, p: PriceReport):
        title = bold('Price update') if not p.is_ath else bold('🚀 A new all-time high has been achieved!')

        c_gecko_link = link(self.ALPHA_GECKO_URL, self.ALPHA)

        message = f"{title} | {c_gecko_link}\n\n"
        price = p.price_and_cap.usd

        pr_text = f"${price:.3f}"
        btc_price = f"₿ {p.price_and_cap.btc:.8f}"
        message += f"<b>{self.ALPHA}</b> price is {code(pr_text)} ({btc_price}) now.\n"

        last_ath = p.price_ath
        if last_ath is not None and p.is_ath:
            last_ath_pr = f'{last_ath.ath_price:.2f}'
            message += f"Last ATH was ${pre(last_ath_pr)} ({format_time_ago(last_ath.ath_date)}).\n"

        # time_combos = zip(
        #     ('1h', '24h', '7d'),
        #     (p.price_1h, p.price_24h, p.price_7d)
        # )
        time_combos = [('24h', p.price_and_cap.usd_24h_change)]
        for title, old_price in time_combos:
            if old_price:
                pc = calc_percent_change(old_price, price)
                message += pre(f"{title.rjust(4)}:{adaptive_round_to_str(pc, True).rjust(8)} % "
                               f"{emoji_for_percent_change(pc).ljust(4).rjust(6)}") + "\n"

        # TODO: TLV and defipulse rank (+ TLV ATH)

        # fp = p.fair_price
        # if fp.rank >= 1:
        #     message += f"Coin market cap is {bold(pretty_dollar(fp.market_cap))} (#{bold(fp.rank)})\n"
        #
        # if fp.tlv_usd >= 1:
        #     message += (f"TVL of non-RUNE assets: ${pre(pretty_money(fp.tlv_usd))}\n"
        #                 f"So of RUNE is {code(pretty_money(fp.fair_price, prefix='$'))}")
        #
        return message.rstrip()

import re
from datetime import timezone
import pandas as pd
from DiscordAlertsTrader.message_parser import parse_trade_alert
from DiscordAlertsTrader.configurator import channel_ids


async def msg_custom_formated2(message):
    """Dummy function to allow bot to import custom format module."""
    pass


def msg_custom_formated(message, *args, **kwargs):
    "Example of custom message format, adds exits to BTOs, qty for SPX trades, closes BTOs for tracker"
    time_strf = "%Y-%m-%d %H:%M:%S.%f"
    
    # Enhanced, scale qty
    if message.channel.id == 1126325195301462117:
        
        avg_trade_val = 24000
        user_trade_val = 500
        ratio = user_trade_val/avg_trade_val
        
        # get qty
        pattern = r"(BTO|STC) (\d+)"
        match = re.search(pattern, message.content)
        if match is not None:
            action = match.group(1)
            qty = int(match.group(2))
            new_qty = max(int(qty*ratio), 1)
            alert =  message.content.replace(match.group(0), f"{action} {new_qty}")
        else:
            alert =  message.content

        msg = pd.Series({'AuthorID': message.author.id,
                'Author': message.author.name,
                'Date': message.created_at.replace(tzinfo=timezone.utc).astimezone(tz=None), 
                'Content': alert,
                'Channel': message.channel.name
                    })
        return [msg]
    
    # change strike format of the alert example
    elif message.channel.id == 993892865554542820:
        
        msg_date = message.created_at.replace(tzinfo=timezone.utc).astimezone(tz=None)
        msg_date_f = msg_date.strftime(time_strf) 
        author = message.author.name
        alert = message.content
        if len(alert) > 0:
            _, order = parse_trade_alert(alert.replace("@bid", "@1"))
            alert = f"{order['action']} {order['Symbol'].split('_')[0]} {int(float(order['strike'][:-1]))}{order['strike'][-1]} {order['expDate']} @{order['price']}"
        
            
        msg = pd.Series({'AuthorID': 0,
            'Author': author,
            'Date': msg_date_f, 
            'Content': alert,
            'Channel': "roybot"
            })
        return [msg]

    # Support for 'PLTR Jun 6 2025 $118.00 Put' format
    elif message.channel.id == 1381800568611147846:
        alert = message.content
        # Regex to capture: PLTR Jun 6 2025 $118.00 Put
        pattern = r"([A-Z]+)\s+([A-Za-z]+)\s+(\d{1,2})\s+(\d{4})\s+\$\s*(\d+(?:\.\d+)?)\s+(Put|Call)"
        match = re.search(pattern, alert, re.IGNORECASE)

        if match:
            ticker, month_str, day, year, strike, option_type = match.groups()

            # Convert month name to number
            months = {
                "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "May": "05", "Jun": "06",
                "Jul": "07", "Aug": "08", "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"
            }
            month_abbr = month_str.capitalize()[:3]
            month = months.get(month_abbr)

            if month:
                # Format for parser: BTO PLTR 06/06/25 118.00P @0
                exp_date = f"{month}/{int(day):02d}/{year[-2:]}"
                option_char = 'P' if option_type.lower() == 'put' else 'C'
                new_alert = f"BTO {ticker} {exp_date} {strike}{option_char} @0"

                msg_date = message.created_at.replace(tzinfo=timezone.utc).astimezone(tz=None)
                msg_date_f = msg_date.strftime(time_strf)

                # Look up channel name from ID
                channel_name = "Unknown"
                if message.channel.id in channel_ids.values():
                    chn_ix = list(channel_ids.values()).index(message.channel.id)
                    channel_name = list(channel_ids.keys())[chn_ix]

                msg = pd.Series({
                    'AuthorID': message.author.id,
                    'Author': message.author.name,
                    'Date': msg_date_f,
                    'Content': new_alert,
                    'Channel': channel_name
                })
                return [msg]
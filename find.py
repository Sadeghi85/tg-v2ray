import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone, timedelta
import re
import json
import base64
import html
import traceback
import random


def json_load(path):
    # Open and read the json file
    with open(path, "r") as file:
        # Load json file content into list
        list_content = json.load(file)
    # Return list of json content
    return list_content


def tg_message_time(div_message):
    try:
        # Retrieve channel message info
        div_message_info = div_message.find("div", class_="tgme_widget_message_info")
        # Retrieve channel message datetime
        message_datetime_tag = div_message_info.find("time")
        message_datetime = message_datetime_tag.get("datetime")

        # Change message datetime type into object and convert into Iran datetime
        datetime_object = datetime.fromisoformat(message_datetime)
        datetime_object = datetime.astimezone(
            datetime_object, tz=timezone(timedelta(hours=3, minutes=30))
        )

        # Retrieve now datetime based on Iran timezone
        datetime_now = datetime.now(tz=timezone(timedelta(hours=3, minutes=30)))

        # Return datetime object, current datetime based on Iran datetime and delta datetime
        return datetime_object, datetime_now, datetime_now - datetime_object
    except Exception as exc:
        pass


def tg_channel_messages(channel_user):
    try:
        # Retrieve channels messages
        response = requests.get(url=f"https://t.me/s/{channel_user}", timeout=5)
        soup = BeautifulSoup(response.text, "html.parser")
        # Find all telegram widget messages
        div_messages = soup.find_all("div", class_="tgme_widget_message")
        # Return list of all messages in channel
        return div_messages
    except Exception as exc:
        pass


def tg_message_text(div_message):
    try:
        # Retrieve message text class from telegram messages widget
        div_message_text = div_message.find("div", class_="tgme_widget_message_text")
        text_content = div_message_text.prettify()
        text_content = re.sub(
            r"<code>([^<>]+)</code>",
            r"\1",
            re.sub(r"\s*", "", text_content),
        )

        # Return text content
        return text_content
    except Exception as exc:
        pass


def tg_username_extract(url):
    telegram_pattern = r"((http|Http|HTTP)://|(https|Https|HTTPS)://|(www|Www|WWW)\.|https://www\.|)(?P<telegram_domain>(t|T)\.(me|Me|ME)|(telegram|Telegram|TELEGRAM)\.(me|Me|ME)|(telegram|Telegram|TELEGRAM).(org|Org|ORG)|telesco.pe|(tg|Tg|TG).(dev|Dev|DEV)|(telegram|Telegram|TELEGRAM).(dog|Dog|DOG))/(?P<username>[a-zA-Z0-9_+-]+)"
    matches_url = re.match(telegram_pattern, url)
    return matches_url.group("username")


def find_matches(text_content):
    try:
        # Initialize configuration type patterns
        pattern_telegram_user = r"(?:@)(\w{4,})"
        pattern_url = r'(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))'
        pattern_shadowsocks = r"(?<![\w-])(ss://[^\s<>#]+)"
        pattern_trojan = r"(?<![\w-])(trojan://[^\s<>#]+)"
        pattern_vmess = r"(?<![\w-])(vmess://[^\s<>#]+)"
        pattern_vless = r"(?<![\w-])(vless://(?:(?!=reality)[^\s<>#])+(?=[\s<>#]))"
        pattern_reality = r"(?<![\w-])(vless://[^\s<>#]+?security=reality[^\s<>#]*)"

        # Find all matches of patterns in text
        matches_usersname = re.findall(pattern_telegram_user, text_content)
        matches_url = re.findall(pattern_url, text_content)
        matches_shadowsocks = re.findall(pattern_shadowsocks, text_content)
        matches_trojan = re.findall(pattern_trojan, text_content)
        matches_vmess = re.findall(pattern_vmess, text_content)
        matches_vless = re.findall(pattern_vless, text_content)
        matches_reality = re.findall(pattern_reality, text_content)

        matches_usersname = [x for x in matches_usersname if "…" not in x]
        matches_url = [x for x in matches_url if "…" not in x]
        matches_shadowsocks = [x for x in matches_shadowsocks if "…" not in x]
        matches_trojan = [x for x in matches_trojan if "…" not in x]
        matches_vmess = [x for x in matches_vmess if "…" not in x]
        matches_vless = [x for x in matches_vless if "…" not in x]
        matches_reality = [x for x in matches_reality if "…" not in x]

        return (
            matches_usersname,
            matches_url,
            matches_shadowsocks,
            matches_trojan,
            matches_vmess,
            matches_vless,
            matches_reality,
        )

    except Exception as exc:
        pass


# Load and read last date and time update
with open("./last_update", "r") as file:
    last_update_datetime = file.readline()
    last_update_datetime = datetime.strptime(
        last_update_datetime, "%Y-%m-%d %H:%M:%S.%f%z"
    )

current_datetime_update = datetime.now(tz=timezone(timedelta(hours=3, minutes=30)))


# main_channels = [item.lower() for item in json_load("v2ray_channels.json")]
found_channels = [item.lower() for item in json_load("found_channels.json")]

# all_channels = list(set(main_channels) | set(found_channels))
found_channels = list(set(found_channels))

# Initial channels messages array
channel_messages_array = list()

# Iterate over all public telegram chanels and store twenty latest messages
for channel_user in found_channels:
    try:
        print(f"{channel_user}")
        # Iterate over Telegram channels to Retrieve channel messages and extend to array
        div_messages = tg_channel_messages(channel_user)
        for div_message in div_messages:
            datetime_object, datetime_now, delta_datetime_now = tg_message_time(
                div_message
            )
            if datetime_object > last_update_datetime:
                print(f"\t{datetime_object.strftime('%a, %d %b %Y %X %Z')}")
                channel_messages_array.append((channel_user, div_message))
    except Exception as exc:
        continue

# Print out total new messages counter
print(
    f"\nTotal New Messages From {last_update_datetime.strftime('%a, %d %b %Y %X %Z')} To {current_datetime_update.strftime('%a, %d %b %Y %X %Z')} : {len(channel_messages_array)}\n"
)

# Initial arrays for protocols
array_usernames = list()
array_url = list()

for channel_user, message in channel_messages_array:
    try:
        # Iterate over channel messages to extract text content
        text_content = tg_message_text(message)
        # Iterate over each message to extract configuration protocol types and subscription links
        (
            matches_usersname,
            matches_url,
            matches_shadowsocks,
            matches_trojan,
            matches_vmess,
            matches_vless,
            matches_reality,
        ) = find_matches(text_content)

        # Extend protocol type arrays and subscription link array
        array_usernames.extend([element.lower() for element in matches_usersname])
        array_url.extend(matches_url)

    except Exception as exc:
        continue


# Split Telegram usernames and subscription url links
tg_username_list = set()
url_subscription_links = set()

for url in array_url:
    try:
        tg_user = tg_username_extract(url)
        if tg_user not in ["proxy", "img", "emoji", "joinchat"]:
            tg_username_list.add(tg_user.lower())
    except:
        url_subscription_links.add(url.split('"')[0])
        continue

tg_username_list.update(array_usernames)

# Subtract and get new telegram channels
new_telegram_channels = tg_username_list.difference(found_channels)

# Initial channels messages array
new_channel_messages = list()

# Iterate over all public telegram chanels and store twenty latest messages
for channel_user in new_telegram_channels:
    try:
        print(f"{channel_user}")
        # Iterate over Telegram channels to Retrieve channel messages and extend to array
        div_messages = tg_channel_messages(channel_user)
        channel_messages = list()
        for div_message in div_messages:
            datetime_object, datetime_now, delta_datetime_now = tg_message_time(
                div_message
            )
            print(f"\t{datetime_object.strftime('%a, %d %b %Y %X %Z')}")
            channel_messages.append(div_message)
        new_channel_messages.append((channel_user, channel_messages))
    except:
        continue

# Messages Counter
print(
    f"\nTotal New Messages From New Channels {last_update_datetime.strftime('%a, %d %b %Y %X %Z')} To {current_datetime_update.strftime('%a, %d %b %Y %X %Z')} : {len(new_channel_messages)}\n"
)


# Initialize array for channelswith configuration contents
new_array_channels = list()

for channel, messages in new_channel_messages:
    # Set Iterator to estimate each channel configurations
    total_config = 0

    for message in messages:
        try:
            # Iterate over channel messages to extract text content
            text_content = tg_message_text(message)
            # Iterate over each message to extract configuration protocol types and subscription links
            (
                matches_username,
                matches_url,
                matches_shadowsocks,
                matches_trojan,
                matches_vmess,
                matches_vless,
                matches_reality,
            ) = find_matches(text_content)
            total_config = (
                total_config
                + len(matches_shadowsocks)
                + len(matches_trojan)
                + len(matches_vmess)
                + len(matches_vless)
                + len(matches_reality)
            )

        except Exception as exc:
            continue

    # Append to channels that conatins configurations
    if total_config != 0:
        new_array_channels.append(channel)


print("New Configuration Telegram Channels Found:")
for channel in new_array_channels:
    print("\t{value}".format(value=channel))

# Extend new channels into previous channels
found_channels.extend(new_array_channels)
found_channels = list(set(found_channels))
found_channels = sorted(found_channels)

with open("./found_channels.json", "w") as telegram_channels_file:
    json.dump(found_channels, telegram_channels_file, indent=4)


# Write the current date and time update
with open("./last_update", "w") as file:
    file.write(f"{current_datetime_update}")

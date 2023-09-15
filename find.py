import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone, timedelta
import re
import json


def json_load(path):
    try:
        with open(path, "r") as file:
            list_content = json.load(file)

        return list_content
    except:
        return []


def tg_message_time(div_message):
    try:
        div_message_info = div_message.find("div", class_="tgme_widget_message_info")

        message_datetime_tag = div_message_info.find("time")
        message_datetime = message_datetime_tag.get("datetime")

        datetime_object = datetime.fromisoformat(message_datetime)
        datetime_object = datetime.astimezone(
            datetime_object, tz=timezone(timedelta(hours=3, minutes=30))
        )

        datetime_now = datetime.now(tz=timezone(timedelta(hours=3, minutes=30)))

        return datetime_object, datetime_now, datetime_now - datetime_object
    except:
        return (None, None, None)


def tg_channel_messages(channel, wanted_date=None, before=None, results=None):
    if results is None:
        results = []

    if len(results) > 100:
        return results

    if before is None:
        url = f"https://t.me/s/{channel}"
    else:
        url = f"https://t.me/s/{channel}?before={before}"

    try:
        response = requests.get(url=url, timeout=5)
        response.raise_for_status()

        doc = BeautifulSoup(response.text, "html.parser")

        prevPage = doc.find(
            "a", attrs={"class": "tme_messages_more", "data-before": True}
        )

        if before and prevPage:
            if int(prevPage["data-before"]) < int(before):
                before = prevPage["data-before"]
            else:
                before = None
        elif prevPage:
            before = prevPage["data-before"]
        else:
            before = None

        div_messages = doc.find_all("div", class_="tgme_widget_message")

        if div_messages:
            results += div_messages
            found_date = None
            for div_message in div_messages:
                try:
                    div_message_info = div_message.find(
                        "div", class_="tgme_widget_message_info"
                    )
                    time_tag = div_message_info.find("time")
                    datetime_attribute = time_tag["datetime"]
                    datetime_object = datetime.fromisoformat(datetime_attribute)

                    if found_date is None:
                        found_date = datetime_object
                        break

                except:
                    pass

            if before and found_date and wanted_date and found_date > wanted_date:
                return tg_channel_messages(channel, wanted_date, before, results)

    except Exception as ex:
        print(ex)
        pass

    return results
    # try:
    #     response = requests.get(url=f"https://t.me/s/{channel_user}", timeout=5)
    #     soup = BeautifulSoup(response.text, "html.parser")

    #     div_messages = soup.find_all("div", class_="tgme_widget_message")

    #     return div_messages
    # except:
    #     return None


def tg_message_text(div_message, keepUrl=False):
    try:
        div_message_text = div_message.find("div", class_="tgme_widget_message_text")
        text_content = div_message_text.prettify()

        if not keepUrl:
            text_content = re.sub(
                r"<code>([^<>]+)</code>",
                r"\1",
                re.sub(
                    r"<a[^<>]+>([^<>]+)</a>",
                    r"\1",
                    re.sub(r"\s*", "", text_content),
                ),
            )

        return text_content
    except:
        return None


def tg_username_extract(url):
    try:
        telegram_pattern = r"(?:https?://)?(?P<telegram_domain>t\.me|tx\.me|telegram\.me|telegram\.org|telesco\.pe|tg\.dev|telegram\.dog|telegram\.space|telega\.one)/(?P<username>[a-zA-Z0-9_]+)"
        matches_url = re.match(telegram_pattern, url, re.IGNORECASE)
        if matches_url is None:
            return None

        return str(matches_url.group("username"))
    except:
        return None


def find_matches(text_content):
    try:
        pattern_telegram_user = r"(?<![\w-])(?:@)([a-zA-Z0-9_]+)"
        pattern_url = r'(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))'
        pattern_shadowsocks = r"(?<![\w-])(ss://[^\s<>#]+)"
        pattern_trojan = r"(?<![\w-])(trojan://[^\s<>#]+)"
        pattern_vmess = r"(?<![\w-])(vmess://[^\s<>#]+)"
        pattern_vless = r"(?<![\w-])(vless://(?:(?!=reality)[^\s<>#])+(?=[\s<>#]))"
        pattern_reality = r"(?<![\w-])(vless://[^\s<>#]+?security=reality[^\s<>#]*)"

        matches_usersname = re.findall(
            pattern_telegram_user, text_content, re.IGNORECASE
        )
        matches_url = re.findall(pattern_url, text_content, re.IGNORECASE)
        matches_shadowsocks = re.findall(
            pattern_shadowsocks, text_content, re.IGNORECASE
        )
        matches_trojan = re.findall(pattern_trojan, text_content, re.IGNORECASE)
        matches_vmess = re.findall(pattern_vmess, text_content, re.IGNORECASE)
        matches_vless = re.findall(pattern_vless, text_content, re.IGNORECASE)
        matches_reality = re.findall(pattern_reality, text_content, re.IGNORECASE)

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

    except:
        return ([], [], [], [], [], [], [])


found_channels = [item.lower() for item in json_load("found_channels.json")]
found_channels = list(set(found_channels))

now = datetime.now(timezone.utc)
midnight_utc = datetime(now.year, now.month, now.day, 0, 0, 0, tzinfo=timezone.utc)
x_days = 7
x_days_ago = midnight_utc - timedelta(days=x_days)

channel_messages_array = list()

for channel_user in found_channels:
    try:
        div_messages = tg_channel_messages(channel=channel_user, wanted_date=x_days_ago)

        # print(div_messages)
        # exit(0)

        if div_messages is None:
            continue

        print(f"{channel_user}\n")

        for div_message in div_messages:
            datetime_object, datetime_now, delta_datetime_now = tg_message_time(
                div_message
            )

            if datetime_object is None:
                continue

            if datetime_object > x_days_ago:
                # print(
                #     datetime_object.strftime("%Y-%m-%d %H:%M:%S")
                #     + ": \n"
                #     + str(tg_message_text(div_message))
                # )
                channel_messages_array.append((channel_user, div_message))
    except:
        continue

array_username = set()
array_url = set()

for channel_user, message in channel_messages_array:
    try:
        text_content = tg_message_text(div_message=message, keepUrl=True)

        if text_content is None:
            continue

        (
            matches_username,
            matches_url,
            _,
            _,
            _,
            _,
            _,
        ) = find_matches(text_content)

        array_username.update(
            [element.lower() for element in matches_username if len(element) >= 5]
        )
        array_url.update(matches_url)

    except:
        continue

tg_username_list = set()

for url in array_url:
    try:
        tg_user = tg_username_extract(url)

        if tg_user is None or len(tg_user) < 5:
            continue

        # print(tg_user + "\n")
        if tg_user not in ["proxy", "img", "emoji", "joinchat"]:
            tg_username_list.add(tg_user.lower())
    except Exception as ex:
        print(ex)
        continue

tg_username_list.update(array_username)

tg_username_list.update(found_channels)

print(f"\n======new channels: {len(tg_username_list)}============\n")

new_telegram_channels = tg_username_list

new_channel_messages = list()

for channel_user in new_telegram_channels:
    try:
        div_messages = tg_channel_messages(channel=channel_user, wanted_date=x_days_ago)

        if div_messages is None:
            continue

        print(f"{channel_user}\n")

        for div_message in div_messages:
            datetime_object, datetime_now, delta_datetime_now = tg_message_time(
                div_message
            )

            if datetime_object is None:
                continue

            if datetime_object > x_days_ago:
                new_channel_messages.append((channel_user, div_message))
    except:
        continue

new_array_channels = set()

for channel, messages in new_channel_messages:
    for message in messages:
        total_config = 0

        try:
            text_content = tg_message_text(message)

            if text_content is None:
                continue

            (
                _,
                _,
                matches_shadowsocks,
                matches_trojan,
                matches_vmess,
                matches_vless,
                matches_reality,
            ) = find_matches(text_content)

            total_config = (
                len(matches_shadowsocks)
                + len(matches_trojan)
                + len(matches_vmess)
                + len(matches_vless)
                + len(matches_reality)
            )

        except:
            continue

        # print(total_config)
        if total_config > 0:
            new_array_channels.add(channel)

found_channels = sorted(list(new_array_channels))

print(f"\ngood channels found:\n{found_channels}\n")

with open("./found_channels.json", "w") as telegram_channels_file:
    json.dump(found_channels, telegram_channels_file, indent=4)

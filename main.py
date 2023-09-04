import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone, timedelta
import re
import json
import base64
from urllib.parse import urlparse
import html
import traceback
import random
from title import make_title


def download_and_parse(channel, wanted_date=None, before=None, results=None):
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
        else:
            before = None

        div_messages = doc.find_all("div", class_="tgme_widget_message")

        if div_messages:
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

                    div_message_text = div_message.find(
                        "div", class_="tgme_widget_message_text"
                    )
                    text_content = div_message_text.prettify()
                    message_dict = {"text": text_content, "date": datetime_object}

                    results.append(message_dict)
                except:
                    pass

            if before and found_date and wanted_date and found_date > wanted_date:
                return download_and_parse(channel, wanted_date, before, results)

    except:
        pass

    return results


pattern_ss = r"(?<![\w-])(ss://[^\s<>#]+)"
pattern_trojan = r"(?<![\w-])(trojan://[^\s<>#]+)"
pattern_vmess = r"(?<![\w-])(vmess://[^\s<>#]+)"
pattern_vless = r"(?<![\w-])(vless://(?:(?!=reality)[^\s<>#])+(?=[\s<>#]))"
pattern_reality = r"(?<![\w-])(vless://[^\s<>#]+?security=reality[^\s<>#]*)"

array_ss = []
array_trojan = []
array_vmess = []
array_vless = []
array_reality = []

with open("./generated/nomatch.txt", "w", encoding="utf-8") as file:
    file.write("")

with open("found_channels.json") as file:
    found_channels = json.load(file)

found_channels = list(set(found_channels))

for channel in found_channels:
    try:
        # url = "https://t.me/s/" + channel
        # response = requests.get(url=url, timeout=5)
        # html_content = response.text

        # soup = BeautifulSoup(html_content, "html.parser")

        # div_messages = soup.find_all("div", class_="tgme_widget_message")

        # text_messages = []

        # for div_message in div_messages:
        #     try:
        #         div_message_info = div_message.find(
        #             "div", class_="tgme_widget_message_info"
        #         )
        #         time_tag = div_message_info.find("time")
        #         datetime_attribute = time_tag["datetime"]

        #         datetime_object = datetime.fromisoformat(datetime_attribute)

        #         div_message_text = div_message.find(
        #             "div", class_="tgme_widget_message_text"
        #         )

        #         text_content = div_message_text.prettify()

        #         message_dict = {"text": text_content, "date": datetime_object}
        #         text_messages.append(message_dict)
        #     except:
        #         pass

        now = datetime.now(timezone.utc)
        midnight_utc = datetime(
            now.year, now.month, now.day, 0, 0, 0, tzinfo=timezone.utc
        )

        x_days = 7
        x_days_ago = midnight_utc - timedelta(days=x_days)

        text_messages = download_and_parse(channel=channel, wanted_date=x_days_ago)

        text_messages = sorted(text_messages, key=lambda x: x["date"], reverse=True)

        # print(text_messages)
        # exit(0)

        # counter = 0

        for text_message in text_messages:
            # if counter > 20 or
            if midnight_utc - text_message["date"] > timedelta(days=x_days):
                break

            print(f"{channel} | {text_message['date']}\n")

            text_content = text_message["text"]

            text_content = re.sub(
                r"<code>([^<>]+)</code>",
                r"\1",
                re.sub(
                    r"<a[^<>]+>([^<>]+)</a>",
                    r"\1",
                    re.sub(r"\s*", "", text_content),
                ),
            )

            # print(text_content + "\n")

            matches_ss = re.findall(pattern_ss, text_content, re.IGNORECASE)
            matches_trojan = re.findall(pattern_trojan, text_content, re.IGNORECASE)
            matches_vmess = re.findall(pattern_vmess, text_content, re.IGNORECASE)
            matches_vless = re.findall(pattern_vless, text_content, re.IGNORECASE)
            matches_reality = re.findall(pattern_reality, text_content, re.IGNORECASE)

            for index, element in enumerate(matches_vmess):
                matches_vmess[index] = (
                    re.sub(r"#[^#]+$", "", html.unescape(element)) + f"#{channel}"
                )

            for index, element in enumerate(matches_ss):
                matches_ss[index] = (
                    re.sub(r"#[^#]+$", "", html.unescape(element)) + f"#{channel}"
                )

            for index, element in enumerate(matches_trojan):
                matches_trojan[index] = (
                    re.sub(r"#[^#]+$", "", html.unescape(element)) + f"#{channel}"
                )

            for index, element in enumerate(matches_vless):
                matches_vless[index] = (
                    re.sub(r"#[^#]+$", "", html.unescape(element)) + f"#{channel}"
                )

            for index, element in enumerate(matches_reality):
                matches_reality[index] = (
                    re.sub(r"#[^#]+$", "", html.unescape(element)) + f"#{channel}"
                )

            # matches_subscribe = [x for x in matches_subscribe if "…" not in x]
            matches_ss = [x for x in matches_ss if "…" not in x]
            matches_trojan = [x for x in matches_trojan if "…" not in x]
            matches_vmess = [x for x in matches_vmess if "…" not in x]
            matches_vless = [x for x in matches_vless if "…" not in x]
            matches_reality = [x for x in matches_reality if "…" not in x]

            # array_subscribe.extend(matches_subscribe)
            array_ss.extend(
                [{"url": u, "date": text_message["date"]} for u in matches_ss]
            )
            array_trojan.extend(
                [{"url": u, "date": text_message["date"]} for u in matches_trojan]
            )
            array_vmess.extend(
                [{"url": u, "date": text_message["date"]} for u in matches_vmess]
            )
            array_vless.extend(
                [{"url": u, "date": text_message["date"]} for u in matches_vless]
            )
            array_reality.extend(
                [{"url": u, "date": text_message["date"]} for u in matches_reality]
            )

            # counter += len(
            #     matches_ss
            #     + matches_trojan
            #     + matches_vmess
            #     + matches_vless
            #     + matches_reality
            # )

    except Exception as e:
        print("An exception occurred:", e)
        traceback.print_exc()

result_vmess, result_sazman_vmess = make_title(array_input=array_vmess, type="vmess")
result_ss, result_sazman_ss = make_title(array_input=array_ss, type="ss")
result_trojan, result_sazman_trojan = make_title(
    array_input=array_trojan, type="trojan"
)
result_vless, result_sazman_vless = make_title(array_input=array_vless, type="vless")
result_reality, result_sazman_reality = make_title(
    array_input=array_reality, type="reality"
)

result_all = result_ss + result_trojan + result_vmess + result_vless + result_reality
result_sazman_all = (
    result_sazman_ss
    + result_sazman_trojan
    + result_sazman_vmess
    + result_sazman_vless
    + result_sazman_reality
)

random.shuffle(result_all)
random.shuffle(result_sazman_all)

chunk_size = 100  # maximum size of each chunk
chunks = []

for i in range(0, len(result_all), chunk_size):
    chunk = result_all[i : i + chunk_size]
    chunks.append(chunk)

for i in range(0, 10, 1):
    if i < len(chunks):
        with open(f"./generated/subs/all-{i+1}", "w", encoding="utf-8") as file:
            file.write(
                base64.b64encode("\n".join(chunks[i]).encode("utf-8")).decode("utf-8")
            )
    else:
        with open(f"./generated/subs/all-{i+1}", "w", encoding="utf-8") as file:
            file.write("")

with open("./generated/subs/all", "w", encoding="utf-8") as file:
    file.write(base64.b64encode("\n".join(result_all).encode("utf-8")).decode("utf-8"))

with open("./generated/subs/all_sazman", "w", encoding="utf-8") as file:
    file.write(
        base64.b64encode("\n".join(result_sazman_all).encode("utf-8")).decode("utf-8")
    )

with open("./generated/subs/ss", "w", encoding="utf-8") as file:
    file.write(base64.b64encode("\n".join(result_ss).encode("utf-8")).decode("utf-8"))
with open("./generated/subs/trojan", "w", encoding="utf-8") as file:
    file.write(
        base64.b64encode("\n".join(result_trojan).encode("utf-8")).decode("utf-8")
    )
with open("./generated/subs/vmess", "w", encoding="utf-8") as file:
    file.write(
        base64.b64encode("\n".join(result_vmess).encode("utf-8")).decode("utf-8")
    )
with open("./generated/subs/vless", "w", encoding="utf-8") as file:
    file.write(
        base64.b64encode("\n".join(result_vless).encode("utf-8")).decode("utf-8")
    )
with open("./generated/subs/reality", "w", encoding="utf-8") as file:
    file.write(
        base64.b64encode("\n".join(result_reality).encode("utf-8")).decode("utf-8")
    )

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


pattern_subscribe = (
    r"(?<!\w)(https?://(?:(?!://)[^\s<>])+?subscribe\?token=(?:(?!://)[^\s<>])+)"
)
pattern_ss = r"(?<!\w)(ss://[^\s<>#]+)"
pattern_trojan = r"(?<!\w)(trojan://[^\s<>#]+)"
pattern_vmess = r"(?<!\w)(vmess://[^\s<>#]+)"
pattern_vless = r"(?<!\w)(vless://(?:(?!=reality)[^\s<>#])+(?=[\s<>#]))"
pattern_reality = r"(?<!\w)(vless://[^\s<>#]+?security=reality[^\s<>#]*)"

array_subscribe = []
array_subscribe_decoded = []
array_all = []
array_ss = []
array_trojan = []
array_vmess = []
array_vless = []
array_reality = []

with open("./generated/nomatch.txt", "w") as file:
    file.write("")

with open("v2ray_channels.json") as file:
    v2ray_channels = json.load(file)

for channel in v2ray_channels:
    try:
        url = "https://t.me/s/" + channel
        response = requests.get(url)
        html_content = response.text

        soup = BeautifulSoup(html_content, "html.parser")

        div_messages = soup.find_all("div", class_="tgme_widget_message")

        text_messages = []

        for div_message in div_messages:
            try:
                div_message_info = div_message.find(
                    "div", class_="tgme_widget_message_info"
                )
                time_tag = div_message_info.find("time")
                datetime_attribute = time_tag["datetime"]

                datetime_object = datetime.fromisoformat(datetime_attribute)

                div_message_text = div_message.find(
                    "div", class_="tgme_widget_message_text"
                )

                text_content = div_message_text.prettify()

                message_dict = {"text": text_content, "date": datetime_object}
                text_messages.append(message_dict)
            except:
                pass

        text_messages = sorted(text_messages, key=lambda x: x["date"], reverse=True)
        counter = 0

        for text_message in text_messages:
            print(f"{channel} | {text_message['date']}\n")

            if counter > 20 or (
                datetime.now(timezone.utc) - text_message["date"] > timedelta(days=14)
            ):
                break

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

            # matches_subscribe = re.findall(pattern_subscribe, text_content)
            matches_ss = re.findall(pattern_ss, text_content)
            matches_trojan = re.findall(pattern_trojan, text_content)
            matches_vmess = re.findall(pattern_vmess, text_content)
            matches_vless = re.findall(pattern_vless, text_content)
            matches_reality = re.findall(pattern_reality, text_content)

            for index, element in enumerate(matches_vmess):
                matches_vmess[index] = re.sub(r"#[^#]+$", "", html.unescape(element))

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

            counter += len(
                matches_ss
                + matches_trojan
                + matches_vmess
                + matches_vless
                + matches_reality
            )

    except Exception as e:
        print("An exception occurred:", e)
        traceback.print_exc()

""" for subscribe in array_subscribe:
    try:
        response = requests.get(url=subscribe, timeout=1)
        text_content = response.text

        try:
            text_content += "=" * ((4 - len(text_content) % 4) % 4)
            decoded = base64.b64decode(text_content).decode("utf-8")

            matches_subscribe_decoded = decoded.splitlines()

            for index, element in enumerate(matches_subscribe_decoded):
                matches_subscribe_decoded[index] = re.sub(r"#[^#]+$", "", element)

            array_subscribe_decoded.extend(matches_subscribe_decoded)
        except Exception as e:
            print("An exception occurred:", e)
            traceback.print_exc()
    except Exception as e:
        print("An exception occurred:", e)
        traceback.print_exc() """

""" try:
    text_content = "\n".join(array_subscribe_decoded)

    matches_ss = re.findall(pattern_ss, text_content)
    matches_trojan = re.findall(pattern_trojan, text_content)
    # matches_vmess = re.findall(pattern_vmess, text_content)
    matches_vless = re.findall(pattern_vless, text_content)
    matches_reality = re.findall(pattern_reality, text_content)

    # for index, element in enumerate(matches_vmess):
    #     matches_vmess[index] = re.sub(
    #         r"#[^#]+$", "", html.unescape(element)
    #     )

    for index, element in enumerate(matches_ss):
        matches_ss[index] = (
            re.sub(r"#[^#]+$", "", html.unescape(element)) + f"#Subscribe"
        )

    for index, element in enumerate(matches_trojan):
        matches_trojan[index] = (
            re.sub(r"#[^#]+$", "", html.unescape(element)) + f"#Subscribe"
        )

    for index, element in enumerate(matches_vless):
        matches_vless[index] = (
            re.sub(r"#[^#]+$", "", html.unescape(element)) + f"#Subscribe"
        )

    for index, element in enumerate(matches_reality):
        matches_reality[index] = (
            re.sub(r"#[^#]+$", "", html.unescape(element)) + f"#Subscribe"
        )

    array_ss.extend(matches_ss)
    array_trojan.extend(matches_trojan)
    array_vmess.extend(matches_vmess)
    array_vless.extend(matches_vless)
    array_reality.extend(matches_reality)

except Exception as e:
    print("An exception occurred:", e)
    traceback.print_exc() """

# array_subscribe_decoded = list(set(array_subscribe_decoded))
# array_ss = list(set(array_ss))
# array_trojan = list(set(array_trojan))
# array_vmess = list(set(array_vmess))
# array_vless = list(set(array_vless))
# array_reality = list(set(array_reality))

result_vmess = [d["url"] for d in array_vmess]

result_ss = make_title(array_input=array_ss, type="ss")
result_trojan = make_title(array_input=array_trojan, type="trojan")
result_vless = make_title(array_input=array_vless, type="vless")
result_reality = make_title(array_input=array_reality, type="reality")

# array_all = array_ss + array_trojan + array_vmess + array_vless + array_reality
result_all = result_ss + result_trojan + result_vless + result_reality

random.shuffle(result_all)

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

""" with open("./generated/subs/subscribe", "w", encoding="utf-8") as file:
    file.write(
        base64.b64encode("\n".join(array_subscribe_decoded).encode("utf-8")).decode(
            "utf-8"
        )
    ) """

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


""" 

with open("./generated/v2ray_all_base64.txt", "w", encoding="utf-8") as file:
    file.write(base64.b64encode("\n".join(array_all).encode("utf-8")).decode("utf-8"))

with open("./generated/v2ray_subscribe_decoded_base64.txt", "w", encoding="utf-8") as file:
    file.write(
        base64.b64encode("\n".join(array_subscribe_decoded).encode("utf-8")).decode(
            "utf-8"
        )
    )
with open("./generated/v2ray_ss_base64.txt", "w", encoding="utf-8") as file:
    file.write(base64.b64encode("\n".join(array_ss).encode("utf-8")).decode("utf-8"))
with open("./generated/v2ray_trojan_base64.txt", "w", encoding="utf-8") as file:
    file.write(
        base64.b64encode("\n".join(array_trojan).encode("utf-8")).decode("utf-8")
    )
with open("./generated/v2ray_vmess_base64.txt", "w", encoding="utf-8") as file:
    file.write(base64.b64encode("\n".join(array_vmess).encode("utf-8")).decode("utf-8"))
with open("./generated/v2ray_vless_base64.txt", "w", encoding="utf-8") as file:
    file.write(base64.b64encode("\n".join(array_vless).encode("utf-8")).decode("utf-8"))
with open("./generated/v2ray_reality_base64.txt", "w", encoding="utf-8") as file:
    file.write(
        base64.b64encode("\n".join(array_reality).encode("utf-8")).decode("utf-8")
    )
 """

""" with open("./generated/v2ray_all.txt", "w", encoding="utf-8") as file:
    file.writelines(f"{element}\n" for element in array_all)
with open("./generated/v2ray_subscribe_decoded.txt", "w", encoding="utf-8") as file:
    file.writelines(f"{element}\n" for element in array_subscribe_decoded)
with open("./generated/v2ray_subscribe.txt", "w", encoding="utf-8") as file:
    file.writelines(f"{element}\n" for element in array_subscribe)
with open("./generated/v2ray_ss.txt", "w", encoding="utf-8") as file:
    file.writelines(f"{element}\n" for element in array_ss)
with open("./generated/v2ray_trojan.txt", "w", encoding="utf-8") as file:
    file.writelines(f"{element}\n" for element in array_trojan)
with open("./generated/v2ray_vmess.txt", "w", encoding="utf-8") as file:
    file.writelines(f"{element}\n" for element in array_vmess)
with open("./generated/v2ray_vless.txt", "w", encoding="utf-8") as file:
    file.writelines(f"{element}\n" for element in array_vless)
with open("./generated/v2ray_reality.txt", "w", encoding="utf-8") as file:
    file.writelines(f"{element}\n" for element in array_reality)
 """

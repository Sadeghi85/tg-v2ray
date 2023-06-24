import requests
import re
import json
import base64
from urllib.parse import urlparse


pattern_subscribe = r"(?<=(?:[\s]|[<>]))(https?://[^\s<>]+?subscribe\?token=[^\s<>]+)"
pattern_ss = r"(?<=(?:[\s]|[<>]))(ss://[^\s<>]+)"
pattern_trojan = r"(?<=(?:[\s]|[<>]))(trojan://[^\s<>]+)"
pattern_vmess = r"(?<=(?:[\s]|[<>]))(vmess://[^\s<>]+)"
pattern_vless = r"(?<=(?:[\s]|[<>]))(vless://[^\s<>]+?security=(?!reality)[^\s<>]+)"
pattern_reality = r"(?<=(?:[\s]|[<>]))(vless://[^\s<>]+?security=reality[^\s<>]+)"

array_subscribe = []
array_subscribe_decoded = []
array_all = []
array_ss = []
array_trojan = []
array_vmess = []
array_vless = []
array_reality = []

with open("v2ray_channels.json") as file:
    v2ray_channels = json.load(file)

for channel in v2ray_channels:
    try:
        url = "https://t.me/s/" + channel
        response = requests.get(url)
        text_content = response.text

        matches_subscribe = re.findall(pattern_subscribe, text_content)
        matches_ss = re.findall(pattern_ss, text_content)
        matches_trojan = re.findall(pattern_trojan, text_content)
        matches_vmess = re.findall(pattern_vmess, text_content)
        matches_vless = re.findall(pattern_vless, text_content)
        matches_reality = re.findall(pattern_reality, text_content)

        for index, element in enumerate(matches_ss):
            matches_ss[index] = re.sub(r"#[^#]+$", "", element) + "#" + channel
        for index, element in enumerate(matches_trojan):
            matches_trojan[index] = re.sub(r"#[^#]+$", "", element) + "#" + channel
        for index, element in enumerate(matches_vmess):
            matches_vmess[index] = re.sub(r"#[^#]+$", "", element) + "#" + channel
        for index, element in enumerate(matches_vless):
            matches_vless[index] = re.sub(r"#[^#]+$", "", element) + "#" + channel
        for index, element in enumerate(matches_reality):
            matches_reality[index] = re.sub(r"#[^#]+$", "", element) + "#" + channel

        array_subscribe.extend(matches_subscribe)
        array_ss.extend(matches_ss)
        array_trojan.extend(matches_trojan)
        array_vmess.extend(matches_vmess)
        array_vless.extend(matches_vless)
        array_reality.extend(matches_reality)
    except:
        pass

for subscribe in array_subscribe:
    try:
        response = requests.get(subscribe)
        text_content = response.text

        parsed_url = urlparse(subscribe)
        hostname = parsed_url.hostname

        try:
            decoded = base64.b64decode(text_content).decode("utf-8")

            matches_subscribe_decoded = decoded.splitlines()

            for index, element in enumerate(matches_subscribe_decoded):
                matches_subscribe_decoded[index] = (
                    re.sub(r"#[^#]+$", "", element) + "#" + hostname
                )

            array_subscribe_decoded.extend(matches_subscribe_decoded)
        except:
            pass
    except:
        pass

array_all = array_ss + array_trojan + array_vmess + array_vless + array_reality

with open("v2ray_all_base64.txt", "w", encoding="utf-8") as file:
    file.write(base64.b64encode("\n".join(array_all).encode("utf-8")).decode("utf-8"))

with open("v2ray_subscribe_decoded_base64.txt", "w", encoding="utf-8") as file:
    file.write(
        base64.b64encode("\n".join(array_subscribe_decoded).encode("utf-8")).decode(
            "utf-8"
        )
    )
with open("v2ray_ss_base64.txt", "w", encoding="utf-8") as file:
    file.write(base64.b64encode("\n".join(array_ss).encode("utf-8")).decode("utf-8"))
with open("v2ray_trojan_base64.txt", "w", encoding="utf-8") as file:
    file.write(
        base64.b64encode("\n".join(array_trojan).encode("utf-8")).decode("utf-8")
    )
with open("v2ray_vmess_base64.txt", "w", encoding="utf-8") as file:
    file.write(base64.b64encode("\n".join(array_vmess).encode("utf-8")).decode("utf-8"))
with open("v2ray_vless_base64.txt", "w", encoding="utf-8") as file:
    file.write(base64.b64encode("\n".join(array_vless).encode("utf-8")).decode("utf-8"))
with open("v2ray_reality_base64.txt", "w", encoding="utf-8") as file:
    file.write(
        base64.b64encode("\n".join(array_reality).encode("utf-8")).decode("utf-8")
    )


with open("v2ray_all.txt", "w", encoding="utf-8") as file:
    file.writelines(f"{element}\n" for element in array_all)

with open("v2ray_subscribe_decoded.txt", "w", encoding="utf-8") as file:
    file.writelines(f"{element}\n" for element in array_subscribe_decoded)
with open("v2ray_subscribe.txt", "w", encoding="utf-8") as file:
    file.writelines(f"{element}\n" for element in array_subscribe)
with open("v2ray_ss.txt", "w", encoding="utf-8") as file:
    file.writelines(f"{element}\n" for element in array_ss)
with open("v2ray_trojan.txt", "w", encoding="utf-8") as file:
    file.writelines(f"{element}\n" for element in array_trojan)
with open("v2ray_vmess.txt", "w", encoding="utf-8") as file:
    file.writelines(f"{element}\n" for element in array_vmess)
with open("v2ray_vless.txt", "w", encoding="utf-8") as file:
    file.writelines(f"{element}\n" for element in array_vless)
with open("v2ray_reality.txt", "w", encoding="utf-8") as file:
    file.writelines(f"{element}\n" for element in array_reality)

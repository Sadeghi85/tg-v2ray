import ipaddress
import re
import socket
import requests
import json
import html


def is_valid_ip_address(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


def is_ipv6(ip):
    try:
        ipaddress.ip_address(ip)
        if ":" in ip:
            return True
        else:
            return False
    except ValueError:
        return False


def get_ip(node):
    try:
        return socket.gethostbyname(node)
    except Exception:
        return node


def get_country_flag(country_code):
    if country_code == "":
        return html.unescape("&#127988;&#8205;&#9760;&#65039;")

    base = 127397  # Base value for regional indicator symbol letters
    codepoints = [ord(c) + base for c in country_code.upper()]
    return html.unescape("".join(["&#x{:X};".format(c) for c in codepoints]))


def get_country_from_ip(ip):
    api = f"https://ipapi.co/{ip}/country/"

    try:
        # json_dict = json.loads(requests.get(api).text)
        # return json_dict["country"]
        return requests.get(api).text
    except Exception:
        return ""


def make_title(array_input, type):
    result = []

    if type == "reality":
        pattern = r"vless://(?P<id>[^@]+)@\[?(?P<ip>[a-zA-Z0-9\.:-]+?)\]?:(?P<port>[0-9]+)/?\?(?P<params>[^#]+)#?(?P<channel>(?<=#).*)"

        for element in array_input:
            print(element + "\n")

            match = re.match(pattern, element)

            config = {
                "id": match.group("id"),
                "ip": match.group("ip"),
                "port": match.group("port"),
                "params": match.group("params"),
                "channel": match.group("channel"),
            }

            if not is_valid_ip_address(config["ip"]):
                config["ip"] = get_ip(config["ip"])

            flag = get_country_flag(get_country_from_ip(config["ip"]))

            config["title"] = f"Reality|@{config['channel']}|{flag}"

            if is_ipv6(config["ip"]):
                config["ip"] = f"[{config['ip']}]"

            if any(
                f"vless://{config['id']}@{config['ip']}:{config['port']}?{config['params']}"
                in s
                for s in result
            ):
                continue

            result.append(
                f"vless://{config['id']}@{config['ip']}:{config['port']}?{config['params']}#{config['title']}"
            )

    else:
        result = array_input

    return result

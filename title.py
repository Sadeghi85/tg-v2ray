import ipaddress
import re
import socket
import ssl
import requests
import json
import html
import random
import tldextract
import base64


def is_valid_base64(s):
    try:
        # Decode the string using base64
        b = base64.b64decode(s)
        # Encode the decoded bytes back to base64 and compare to the original string
        return base64.b64encode(b).decode("utf-8") == s
    except:
        # If an exception is raised during decoding, the string is not valid base64
        return False


def is_valid_domain(hostname):
    # Extract the TLD, domain, and subdomain from the hostname
    ext = tldextract.extract(hostname)
    # Check if the domain and TLD are not empty
    return ext.domain != "" and ext.suffix != ""


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


def get_ips(node):
    try:
        results = socket.getaddrinfo(node, None, socket.AF_UNSPEC)

        ips = set()

        for result in results:
            ip = result[4][0]
            ips.add(ip)

        return ips
    except:
        return None


def get_ip(node):
    try:
        return socket.gethostbyname(node)
    except Exception:
        return None


def get_country_flag(country_code):
    if country_code is None:
        return html.unescape("&#127988;&#8205;&#9760;&#65039;")

    base = 127397  # Base value for regional indicator symbol letters
    codepoints = [ord(c) + base for c in country_code.upper()]
    return html.unescape("".join(["&#x{:X};".format(c) for c in codepoints]))


def get_country_from_ip(ip):
    api = f"https://api.country.is/{ip}"

    try:
        json_dict = json.loads(requests.get(api).text)
        return json_dict["country"]

    except Exception:
        return None


def check_port(ip, port, timeout=1):
    """
    Check if a port is open on a given IP address.

    Args:
    ip (str): The IP address.
    port (int): The port number.
    timeout (int, optional): The timeout in seconds. Defaults to 5.

    Returns:
    bool: True if the port is open, False otherwise.
    """
    try:
        sock = socket.create_connection(address=(ip, port), timeout=timeout)
        sock.close()
        print("port is open\n")
        return True
    except:
        print("port is closed\n")
        return False


def make_title(array_input, type):
    result = []

    random.shuffle(array_input)

    if type == "reality" or type == "vless":
        for element in array_input:
            pattern = r"vless://(?P<id>[^@]+)@\[?(?P<ip>[a-zA-Z0-9\.:-]+?)\]?:(?P<port>[0-9]+)/?\?(?P<params>[^#]+)#?(?P<channel>(?<=#).*)?"

            print(element + "\n")

            match = re.match(pattern, element, flags=re.IGNORECASE)

            if match is None:
                print("no match\n")
                continue

            config = {
                "id": match.group("id"),
                "ip": match.group("ip"),
                "host": match.group("ip"),
                "port": match.group("port"),
                "params": match.group("params"),
                "channel": match.group("channel"),
            }

            """ if not is_valid_ip_address(config["ip"]):
                config["ip"] = get_ip(config["ip"])

            if config["ip"] is None:
                print("no ip\n")
                continue """

            ips = {config["ip"]}
            if not is_valid_ip_address(config["ip"]):
                ips = get_ips(config["ip"])

            if ips is None:
                print("no ip\n")
                continue

            array_params_input = config["params"].split("&")
            dict_params = {}

            for pair in array_params_input:
                try:
                    key, value = pair.split("=")
                    key = re.sub(
                        r"servicename",
                        "serviceName",
                        re.sub(
                            r"headertype",
                            "headerType",
                            re.sub(r"allowinsecure", "allowInsecure", key.lower()),
                        ),
                    )
                    dict_params[key] = value
                except:
                    pass

            for ip in ips:
                config["ip"] = ip

                # if not check_port(config["ip"], int(config["port"])):
                #     continue

                flag = get_country_flag(get_country_from_ip(config["ip"]))

                if is_ipv6(config["ip"]):
                    config["ip"] = f"[{config['ip']}]"

                if (
                    dict_params.get("security", "") in ["reality", "tls"]
                    and dict_params.get("sni", "") == ""
                    and is_valid_domain(config["host"])
                ):
                    dict_params["sni"] = config["host"]
                    dict_params["allowInsecure"] = 1

                config[
                    "params"
                ] = f"security={dict_params.get('security', '')}&flow={dict_params.get('flow', '')}&sni={dict_params.get('sni', '')}&encryption={dict_params.get('encryption', '')}&type={dict_params.get('type', '')}&serviceName={dict_params.get('serviceName', '')}&host={dict_params.get('host', '')}&path={dict_params.get('path', '')}&headerType={dict_params.get('headerType', '')}&fp={dict_params.get('fp', '')}&pbk={dict_params.get('pbk', '')}&sid={dict_params.get('sid', '')}&alpn={dict_params.get('alpn', '')}&allowInsecure={dict_params.get('allowInsecure', '')}&"

                config["params"] = re.sub(r"\w+=&", "", config["params"])
                config["params"] = re.sub(
                    r"(?:encryption=none&)|(?:headerType=none&)",
                    "",
                    config["params"],
                    flags=re.IGNORECASE,
                )
                config["params"] = config["params"].strip("&")

                if any(
                    f"vless://{config['id']}@{config['ip']}:{config['port']}?{config['params']}"
                    in s
                    for s in result
                ):
                    continue

                if type == "reality":
                    config[
                        "title"
                    ] = f"Reality | {dict_params.get('sni', '')} | @{config['channel']} | {flag}"
                else:
                    config["title"] = f"Vless | @{config['channel']} | {flag}"

                result.append(
                    f"vless://{config['id']}@{config['ip']}:{config['port']}?{config['params']}#{config['title']}"
                )
    elif type == "trojan":
        for element in array_input:
            pattern = r"trojan://(?P<id>[^@]+)@\[?(?P<ip>[a-zA-Z0-9\.:-]+?)\]?:(?P<port>[0-9]+)/?\??(?P<params>[^#]+)?#?(?P<channel>(?<=#).*)?"

            print(element + "\n")

            match = re.match(pattern, element, flags=re.IGNORECASE)

            if match is None:
                print("no match\n")
                continue

            config = {
                "id": match.group("id"),
                "ip": match.group("ip"),
                "host": match.group("ip"),
                "port": match.group("port"),
                "params": match.group("params") or "",
                "channel": match.group("channel"),
            }

            """ if not is_valid_ip_address(config["ip"]):
                config["ip"] = get_ip(config["ip"])

            if config["ip"] is None:
                print("no ip\n")
                continue """

            ips = {config["ip"]}
            if not is_valid_ip_address(config["ip"]):
                ips = get_ips(config["ip"])

            if ips is None:
                print("no ip\n")
                continue

            array_params_input = config["params"].split("&")
            dict_params = {}

            for pair in array_params_input:
                try:
                    key, value = pair.split("=")
                    key = re.sub(
                        r"servicename",
                        "serviceName",
                        re.sub(
                            r"headertype",
                            "headerType",
                            re.sub(r"allowinsecure", "allowInsecure", key.lower()),
                        ),
                    )
                    dict_params[key] = value
                except:
                    pass

            for ip in ips:
                config["ip"] = ip

                # if not check_port(config["ip"], int(config["port"])):
                #     continue

                flag = get_country_flag(get_country_from_ip(config["ip"]))

                if is_ipv6(config["ip"]):
                    config["ip"] = f"[{config['ip']}]"

                if (
                    dict_params.get("security", "") in ["reality", "tls"]
                    and dict_params.get("sni", "") == ""
                    and is_valid_domain(config["host"])
                ):
                    dict_params["sni"] = config["host"]
                    dict_params["allowInsecure"] = 1

                config[
                    "params"
                ] = f"security={dict_params.get('security', '')}&flow={dict_params.get('flow', '')}&sni={dict_params.get('sni', '')}&encryption={dict_params.get('encryption', '')}&type={dict_params.get('type', '')}&serviceName={dict_params.get('serviceName', '')}&host={dict_params.get('host', '')}&path={dict_params.get('path', '')}&headerType={dict_params.get('headerType', '')}&fp={dict_params.get('fp', '')}&pbk={dict_params.get('pbk', '')}&sid={dict_params.get('sid', '')}&alpn={dict_params.get('alpn', '')}&allowInsecure={dict_params.get('allowInsecure', '')}&"

                config["params"] = re.sub(r"\w+=&", "", config["params"])
                config["params"] = re.sub(
                    r"(?:encryption=none&)|(?:headerType=none&)",
                    "",
                    config["params"],
                    flags=re.IGNORECASE,
                )
                config["params"] = config["params"].strip("&")

                if any(
                    f"trojan://{config['id']}@{config['ip']}:{config['port']}?{config['params']}"
                    in s
                    for s in result
                ):
                    continue

                config["title"] = f"Trojan | @{config['channel']} | {flag}"

                result.append(
                    f"trojan://{config['id']}@{config['ip']}:{config['port']}?{config['params']}#{config['title']}"
                )
    elif type == "ss":
        for element in array_input:
            pattern = r"ss://(?P<id>[^@]+)@\[?(?P<ip>[a-zA-Z0-9\.:-]+?)\]?:(?P<port>[0-9]+)/?#?(?P<channel>(?<=#).*)?"

            print(element + "\n")

            match = re.match(pattern, element, flags=re.IGNORECASE)

            if match is None:
                pattern = r"ss://(?P<id>[^#]+)#?(?P<channel>(?<=#).*)?(?P<ip>(?:))(?P<port>(?:))"

                match = re.match(pattern, element, flags=re.IGNORECASE)

                if match is None:
                    print("no match\n")
                    continue

            config = {
                "id": match.group("id"),
                "ip": match.group("ip"),
                "port": match.group("port"),
                "channel": match.group("channel"),
            }

            config["id"] += "=" * ((4 - len(config["id"]) % 4) % 4)

            if not is_valid_base64(config["id"]):
                print(f"invalid base64 string: {config['id']}\n")
                continue

            if config["ip"] == "":
                pattern = (
                    r"(?P<id>[^@]+)@\[?(?P<ip>[a-zA-Z0-9\.:-]+?)\]?:(?P<port>[0-9]+)"
                )

                match = re.match(
                    pattern,
                    base64.b64decode(config["id"]).decode("utf-8"),
                    flags=re.IGNORECASE,
                )

                if match is None:
                    print("no match\n")
                    continue

                config = {
                    "id": base64.b64encode(match.group("id").encode("utf-8")).decode(
                        "utf-8"
                    ),
                    "ip": match.group("ip"),
                    "port": match.group("port"),
                    "channel": config["channel"],
                }

            """ if not is_valid_ip_address(config["ip"]):
                config["ip"] = get_ip(config["ip"])

            if config["ip"] is None:
                print("no ip\n")
                continue """

            ips = {config["ip"]}
            if not is_valid_ip_address(config["ip"]):
                ips = get_ips(config["ip"])

            if ips is None:
                print("no ip\n")
                continue

            for ip in ips:
                config["ip"] = ip

                # if not check_port(config["ip"], int(config["port"])):
                #     continue

                flag = get_country_flag(get_country_from_ip(config["ip"]))

                if is_ipv6(config["ip"]):
                    config["ip"] = f"[{config['ip']}]"

                if any(
                    f"ss://{config['id']}@{config['ip']}:{config['port']}" in s
                    for s in result
                ):
                    continue

                config["title"] = f"ShadowSocks | @{config['channel']} | {flag}"

                result.append(
                    f"ss://{config['id']}@{config['ip']}:{config['port']}#{config['title']}"
                )
    else:
        result = array_input

    return result

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
import geoip2.database
import json
from dns import resolver, rdatatype
import binascii
import ast


def superscript_string(input_string):
    # Define a dictionary mapping regular characters to their superscript equivalents
    superscript_chars = {
        "0": "⁰",
        "1": "¹",
        "2": "²",
        "3": "³",
        "4": "⁴",
        "5": "⁵",
        "6": "⁶",
        "7": "⁷",
        "8": "⁸",
        "9": "⁹",
        "a": "ᵃ",
        "b": "ᵇ",
        "c": "ᶜ",
        "d": "ᵈ",
        "e": "ᵉ",
        "f": "ᶠ",
        # Add more characters as needed
    }

    # Convert the input string to its superscript representation
    superscript_text = "".join(
        superscript_chars.get(char, char) for char in input_string
    )

    return superscript_text


def generate_crc32(input_string):
    # Calculate the CRC32 checksum of the input string
    crc32_value = binascii.crc32(input_string.encode("utf-8"))

    # Ensure the result is a positive integer
    if crc32_value < 0:
        crc32_value += 2**32

    # Convert the integer to a hexadecimal string
    crc32_hex = format(
        crc32_value, "08x"
    )  # '08x' ensures the result is 8 characters long

    return crc32_hex


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
    try:
        # Extract the TLD, domain, and subdomain from the hostname
        ext = tldextract.extract(hostname)
        # Check if the domain and TLD are not empty
        return (
            ext.domain != ""
            and ext.suffix != ""
            and hostname == ".".join(part for part in ext[:3] if part)
        )
    except Exception as e:
        print("An exception occurred:", e)
        return False


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


""" def get_ips(node):
    try:
        results = socket.getaddrinfo(node, None, socket.AF_UNSPEC)

        ips = set()

        for result in results:
            ip = result[4][0]
            ips.add(ip)

        return ips
    except:
        return None """


def get_ips(node):
    try:
        res = resolver.Resolver()
        res.nameservers = ["8.8.8.8"]

        answers_ipv4 = res.resolve(node, rdatatype.A, raise_on_no_answer=False)
        answers_ipv6 = res.resolve(node, rdatatype.AAAA, raise_on_no_answer=False)

        ips = set()

        for rdata in answers_ipv4:
            ips.add(rdata.address)

        for rdata in answers_ipv6:
            ips.add(rdata.address)

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


""" def get_country_from_ip(ip):
    api = f"https://api.country.is/{ip}"

    try:
        json_dict = json.loads(requests.get(api).text)
        return json_dict["country"]

    except Exception:
        return None """


def get_country_from_ip(ip):
    try:
        with geoip2.database.Reader("./geoip2/GeoLite2-Country.mmdb") as reader:
            response = reader.country(ip)
            cc = response.country.iso_code
            print(f"{cc}\n")
            return cc
    except:
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
    result_sazman = []

    if type == "vmess":
        for dict in array_input:
            pattern = r"vmess://(?P<json>[^#]+)#?(?P<channel>(?<=#).*)?"

            url = dict["url"]
            date = dict["date"]

            print(url + "\n")

            match = re.match(pattern, url, flags=re.IGNORECASE)

            if match is None:
                with open("./generated/nomatch.txt", "a", encoding="utf-8") as file:
                    file.write(f"{url}\n")
                print("no match\n")
                continue

            json_string = match.group("json")
            json_string += "=" * ((4 - len(json_string) % 4) % 4)

            if not is_valid_base64(json_string):
                with open("./generated/nomatch.txt", "a", encoding="utf-8") as file:
                    file.write(f"{url}\n")
                print(f"invalid base64 string: {json_string}\n")
                continue

            json_string = base64.b64decode(json_string).decode(
                encoding="utf-8", errors="ignore"
            )

            dict_params = {}

            try:
                # json_params = json.loads(json_string)
                json_params = json.JSONDecoder(strict=False).decode(
                    json.dumps(
                        ast.literal_eval(
                            re.sub(
                                r"(?<=[{,\r\n])(\s*['\"][^'\"]+['\"]\s*:\s*)([^'\"\r\n,}]+)(?=[,\r\n}])",
                                r"\1'\2'",
                                json_string,
                            )
                        )
                    )
                )

                for k, v in json_params.items():
                    key = re.sub(
                        r"servicename",
                        "serviceName",
                        re.sub(
                            r"headertype",
                            "headerType",
                            re.sub(r"allowinsecure", "allowInsecure", k.lower()),
                        ),
                    )
                    dict_params[key] = v

                # dict_params = {k.lower(): v for k, v in json_params.items()}
            except:
                with open("./generated/nomatch.txt", "a", encoding="utf-8") as file:
                    file.write(f"{url}\n")
                print(f"invalid json string: {json_string}\n")
                continue

            config = {
                "id": dict_params.get("id", ""),
                "ip": dict_params.get("add", ""),
                "host": dict_params.get("add", ""),
                "port": dict_params.get("port", ""),
                "params": "",
                "channel": match.group("channel"),
            }

            ips = {config["ip"]}
            if not is_valid_ip_address(config["ip"]):
                ips = get_ips(config["ip"])

            if ips is None:
                print("no ip\n")
                continue

            if dict_params.get("allowInsecure", "0") != "0":
                continue

            if dict_params.get("sni", "") != "":
                if not is_valid_domain(dict_params["sni"]):
                    dict_params["sni"] = ""
                    print(f"invalid sni: {dict_params.get('sni', '')}\n")
                else:
                    dict_params["sni"] = str(dict_params["sni"]).lower()

            if dict_params.get("sni", "") == "":
                continue

            for ip in ips:
                config["ip"] = ip

                if not check_port(config["ip"], int(config["port"])):
                    continue

                flag = get_country_flag(get_country_from_ip(config["ip"]))

                """ if is_ipv6(config["ip"]):
                    config["ip"] = f"[{config['ip']}]" """

                config[
                    "params"
                ] = f"tls={dict_params.get('tls', '')}&sni={dict_params.get('sni', '')}&scy={dict_params.get('scy', '')}&net={dict_params.get('net', '')}&host={dict_params.get('host', '')}&path={dict_params.get('path', '')}&type={dict_params.get('type', '')}&fp={dict_params.get('fp', '')}&alpn={dict_params.get('alpn', '')}&aid={dict_params.get('aid', '')}&v={dict_params.get('v', '')}&allowInsecure={dict_params.get('allowInsecure', '')}&"

                config["params"] = re.sub(r"\w+=&", "", config["params"])
                config["params"] = re.sub(
                    r"(?:tls=none&)|(?:type=none&)|(?:scy=none&)|(?:scy=auto&)",
                    "",
                    config["params"],
                    flags=re.IGNORECASE,
                )
                config["params"] = config["params"].strip("&")

                # def check_duplicate():
                #     for i, d in enumerate(result):
                #         if (
                #             f"vmess://{config['id']}@{config['ip']}:{config['port']}?{config['params']}"
                #             in d["raw"]
                #         ):
                #             if date < d["date"]:
                #                 del result[i]
                #                 return False
                #             else:
                #                 return True

                #     return False

                # if check_duplicate() == True:
                #     continue

                config["title"] = (
                    f"Vmess | @{config['channel']} | {flag}"
                    + "   "
                    + superscript_string(
                        generate_crc32(
                            f"vmess://{config['id']}@{config['ip']}:{config['port']}?{config['params']}"
                        )
                    )
                )

                dict_params["add"] = config["ip"]
                dict_params["ps"] = config["title"]

                result.append(
                    {
                        "raw": f"vmess://{config['id']}@{config['ip']}:{config['port']}?{config['params']}#{config['title']}",
                        "url": f"vmess://{base64.b64encode(json.dumps(dict_params).encode('utf-8')).decode('utf-8')}",
                        "date": date,
                        "sort-string": f"vmess://{config['id']}@{config['ip']}:{config['port']}?{config['params']}",
                    }
                )

                if config["port"] in ["80", "8080", "443"]:
                    result_sazman.append(
                        {
                            "raw": f"vmess://{config['id']}@{config['ip']}:{config['port']}?{config['params']}#{config['title']}",
                            "url": f"vmess://{base64.b64encode(json.dumps(dict_params).encode('utf-8')).decode('utf-8')}",
                            "date": date,
                            "sort-string": f"vmess://{config['id']}@{config['ip']}:{config['port']}?{config['params']}",
                        }
                    )

    elif type == "reality" or type == "vless":
        for dict in array_input:
            pattern = r"vless://(?P<id>[^@]+)@\[?(?P<ip>[a-zA-Z0-9\.:_-]+?)\]?:(?P<port>[0-9]+)/?\?(?P<params>[^#]+)#?(?P<channel>(?<=#).*)?"

            url = dict["url"]
            date = dict["date"]

            print(url + "\n")

            match = re.match(pattern, url, flags=re.IGNORECASE)

            if match is None:
                with open("./generated/nomatch.txt", "a", encoding="utf-8") as file:
                    file.write(f"{url}\n")
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

            if dict_params.get("allowInsecure", "0") != "0":
                continue

            if dict_params.get("sni", "") != "":
                if not is_valid_domain(dict_params["sni"]):
                    dict_params["sni"] = ""
                    print(f"invalid sni: {dict_params.get('sni', '')}\n")
                else:
                    dict_params["sni"] = str(dict_params["sni"]).lower()

            if dict_params.get("sni", "") == "":
                continue

            for ip in ips:
                config["ip"] = ip

                if not check_port(config["ip"], int(config["port"])):
                    continue

                flag = get_country_flag(get_country_from_ip(config["ip"]))

                if is_ipv6(config["ip"]):
                    config["ip"] = f"[{config['ip']}]"

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

                # def check_duplicate():
                #     for i, d in enumerate(result):
                #         if (
                #             f"vless://{config['id']}@{config['ip']}:{config['port']}?{config['params']}"
                #             in d["url"]
                #         ):
                #             if date < d["date"]:
                #                 del result[i]
                #                 return False
                #             else:
                #                 return True

                #     return False

                # if check_duplicate() == True:
                #     continue

                if type == "reality":
                    config["title"] = (
                        f"Reality | {dict_params.get('sni', '')} | @{config['channel']} | {flag}"
                        + "   "
                        + superscript_string(
                            generate_crc32(
                                f"vless://{config['id']}@{config['ip']}:{config['port']}?{config['params']}"
                            )
                        )
                    )
                else:
                    config["title"] = (
                        f"Vless | @{config['channel']} | {flag}"
                        + "   "
                        + superscript_string(
                            generate_crc32(
                                f"vless://{config['id']}@{config['ip']}:{config['port']}?{config['params']}"
                            )
                        )
                    )

                result.append(
                    {
                        "url": f"vless://{config['id']}@{config['ip']}:{config['port']}?{config['params']}#{config['title']}",
                        "date": date,
                        "sort-string": f"vless://{config['id']}@{config['ip']}:{config['port']}?{config['params']}",
                    }
                )

                if config["port"] in ["80", "8080", "443"]:
                    result_sazman.append(
                        {
                            "url": f"vless://{config['id']}@{config['ip']}:{config['port']}?{config['params']}#{config['title']}",
                            "date": date,
                            "sort-string": f"vless://{config['id']}@{config['ip']}:{config['port']}?{config['params']}",
                        }
                    )
    elif type == "trojan":
        for dict in array_input:
            pattern = r"trojan://(?P<id>[^@]+)@\[?(?P<ip>[a-zA-Z0-9\.:_-]+?)\]?:(?P<port>[0-9]+)/?\??(?P<params>[^#]+)?#?(?P<channel>(?<=#).*)?"

            url = dict["url"]
            date = dict["date"]

            print(url + "\n")

            match = re.match(pattern, url, flags=re.IGNORECASE)

            if match is None:
                with open("./generated/nomatch.txt", "a", encoding="utf-8") as file:
                    file.write(f"{url}\n")
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

            if dict_params.get("allowInsecure", "0") != "0":
                continue

            if dict_params.get("sni", "") != "":
                if not is_valid_domain(dict_params["sni"]):
                    dict_params["sni"] = ""
                    print(f"invalid sni: {dict_params.get('sni', '')}\n")
                else:
                    dict_params["sni"] = str(dict_params["sni"]).lower()

            if dict_params.get("sni", "") == "":
                continue

            for ip in ips:
                config["ip"] = ip

                if not check_port(config["ip"], int(config["port"])):
                    continue

                flag = get_country_flag(get_country_from_ip(config["ip"]))

                if is_ipv6(config["ip"]):
                    config["ip"] = f"[{config['ip']}]"

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

                # def check_duplicate():
                #     for i, d in enumerate(result):
                #         if (
                #             f"trojan://{config['id']}@{config['ip']}:{config['port']}?{config['params']}"
                #             in d["url"]
                #         ):
                #             if date < d["date"]:
                #                 del result[i]
                #                 return False
                #             else:
                #                 return True

                #     return False

                # if check_duplicate() == True:
                #     continue

                config["title"] = (
                    f"Trojan | @{config['channel']} | {flag}"
                    + "   "
                    + superscript_string(
                        generate_crc32(
                            f"trojan://{config['id']}@{config['ip']}:{config['port']}?{config['params']}"
                        )
                    )
                )

                result.append(
                    {
                        "url": f"trojan://{config['id']}@{config['ip']}:{config['port']}?{config['params']}#{config['title']}",
                        "date": date,
                        "sort-string": f"trojan://{config['id']}@{config['ip']}:{config['port']}?{config['params']}",
                    }
                )

                if config["port"] in ["80", "8080", "443"]:
                    result_sazman.append(
                        {
                            "url": f"trojan://{config['id']}@{config['ip']}:{config['port']}?{config['params']}#{config['title']}",
                            "date": date,
                            "sort-string": f"trojan://{config['id']}@{config['ip']}:{config['port']}?{config['params']}",
                        }
                    )
    elif type == "ss":
        for dict in array_input:
            pattern = r"ss://(?P<id>[^@]+)@\[?(?P<ip>[a-zA-Z0-9\.:_-]+?)\]?:(?P<port>[0-9]+)/?#?(?P<channel>(?<=#).*)?"

            url = dict["url"]
            date = dict["date"]

            print(url + "\n")

            match = re.match(pattern, url, flags=re.IGNORECASE)

            if match is None:
                pattern = r"ss://(?P<id>[^#]+)#?(?P<channel>(?<=#).*)?(?P<ip>(?:))(?P<port>(?:))"

                match = re.match(pattern, url, flags=re.IGNORECASE)

                if match is None:
                    with open("./generated/nomatch.txt", "a", encoding="utf-8") as file:
                        file.write(f"{url}\n")
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
                with open("./generated/nomatch.txt", "a", encoding="utf-8") as file:
                    file.write(f"{url}\n")
                print(f"invalid base64 string: {config['id']}\n")
                continue

            if config["ip"] == "":
                pattern = (
                    r"(?P<id>[^@]+)@\[?(?P<ip>[a-zA-Z0-9\.:_-]+?)\]?:(?P<port>[0-9]+)"
                )

                match = re.match(
                    pattern,
                    base64.b64decode(config["id"]).decode(
                        encoding="utf-8", errors="ignore"
                    ),
                    flags=re.IGNORECASE,
                )

                if match is None:
                    with open("./generated/nomatch.txt", "a", encoding="utf-8") as file:
                        file.write(f"{url}\n")
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

            ips = {config["ip"]}
            if not is_valid_ip_address(config["ip"]):
                ips = get_ips(config["ip"])

            if ips is None:
                print("no ip\n")
                continue

            for ip in ips:
                config["ip"] = ip

                if not check_port(config["ip"], int(config["port"])):
                    continue

                flag = get_country_flag(get_country_from_ip(config["ip"]))

                if is_ipv6(config["ip"]):
                    config["ip"] = f"[{config['ip']}]"

                # def check_duplicate():
                #     for i, d in enumerate(result):
                #         if (
                #             f"ss://{config['id']}@{config['ip']}:{config['port']}"
                #             in d["url"]
                #         ):
                #             if date < d["date"]:
                #                 del result[i]
                #                 return False
                #             else:
                #                 return True

                #     return False

                # if check_duplicate() == True:
                #     continue

                config["title"] = (
                    f"ShadowSocks | @{config['channel']} | {flag}"
                    + "   "
                    + superscript_string(
                        generate_crc32(
                            f"ss://{config['id']}@{config['ip']}:{config['port']}"
                        )
                    )
                )

                result.append(
                    {
                        "url": f"ss://{config['id']}@{config['ip']}:{config['port']}#{config['title']}",
                        "date": date,
                        "sort-string": f"ss://{config['id']}@{config['ip']}:{config['port']}",
                    }
                )

                if config["port"] in ["80", "8080", "443"]:
                    result_sazman.append(
                        {
                            "url": f"ss://{config['id']}@{config['ip']}:{config['port']}#{config['title']}",
                            "date": date,
                            "sort-string": f"ss://{config['id']}@{config['ip']}:{config['port']}",
                        }
                    )
    else:
        return ([], [])

    result = sorted(result, key=lambda x: x["date"], reverse=False)
    seen_urls = {}
    result = [
        seen_urls.setdefault(item["sort-string"], item)
        for item in result
        if item["sort-string"] not in seen_urls
    ]
    # result = sorted(result, key=lambda x: x["date"], reverse=True)

    result_sazman = sorted(result_sazman, key=lambda x: x["date"], reverse=False)
    seen_urls = {}
    result_sazman = [
        seen_urls.setdefault(item["sort-string"], item)
        for item in result_sazman
        if item["sort-string"] not in seen_urls
    ]
    # result_sazman = sorted(result_sazman, key=lambda x: x["date"], reverse=True)

    # return ([d["url"] for d in result], [d["url"] for d in result_sazman])
    return (result, result_sazman)

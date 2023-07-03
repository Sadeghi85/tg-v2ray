import ipaddress
import re
import socket
import ssl
import requests
import json
import html
import random


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
        return None


def get_country_flag(country_code):
    if country_code == None:
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


def check_connection(ip: str, port: int, sni: str, security: str):
    if is_ipv6(ip):
        server_address = (ip, port, 0, 0)
    else:
        server_address = (ip, port)

    print(f"{ip}:{port}->{sni}\n")

    try:
        if is_ipv6(ip):
            client_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM, 0)
        else:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        client_socket.settimeout(1)
        client_socket.connect(server_address)
    except Exception as e:
        print(f"{ip}:{port} not responding -> '{e}'\n")
        return False

    data = "Hello, server!"
    received_data = ""

    if security == "reality" or security == "tls":
        try:
            ssl_context = ssl.create_default_context()
            ssl_socket = ssl_context.wrap_socket(client_socket, server_hostname=sni)

            ssl_socket.sendall(data.encode())

            received_data = ssl_socket.recv(1024)
            print(f"length: {len(received_data)}\n")
            # print(f"data:\n{received_data.decode()}\n")

            ssl_socket.close()
        except ssl.SSLCertVerificationError:
            return True
        except Exception as e:
            print(f"Exception ({type(e).__name__}) -> '{e}'\n")
            return False
    else:
        try:
            client_socket.sendall(data.encode())

            received_data = client_socket.recv(1024)
            print(f"length: {len(received_data)}\n")
            # print(f"data:\n{received_data.decode()}\n")

            client_socket.close()

        except Exception as e:
            print(f"Exception ({type(e).__name__}) -> '{e}'\n")
            return False

    if len(received_data) > 0 or not (security == "reality" or security == "tls"):
        return True

    return False


def make_title(array_input, type):
    result = []

    random.shuffle(array_input)

    if type == "reality" or type == "vless":
        pattern = r"vless://(?P<id>[^@]+)@\[?(?P<ip>[a-zA-Z0-9\.:-]+?)\]?:(?P<port>[0-9]+)/?\?(?P<params>[^#]+)#?(?P<channel>(?<=#).*)"

        for element in array_input:
            print(element + "\n")

            match = re.match(pattern, element, flags=re.IGNORECASE)

            if match == None:
                continue

            config = {
                "id": match.group("id"),
                "ip": match.group("ip"),
                "host": match.group("ip"),
                "port": match.group("port"),
                "params": match.group("params"),
                "channel": match.group("channel"),
            }

            if not is_valid_ip_address(config["ip"]):
                config["ip"] = get_ip(config["ip"])

            if config["ip"] == None:
                continue

            array_params_input = config["params"].split("&")
            dict_params = {}
            try:
                for pair in array_params_input:
                    key, value = pair.split("=")
                    key = re.sub(r"headertype", "headerType", key.lower())
                    dict_params[key] = value
            except:
                continue

            if (
                check_connection(
                    config["ip"],
                    int(config["port"]),
                    (
                        dict_params.get("sni", config["host"])
                        if is_valid_ip_address(config["host"])
                        else config["host"]
                    )
                    if dict_params.get("security", "none") == "tls"
                    else dict_params.get("sni", config["host"]),
                    dict_params.get("security", "none"),
                )
                == False
            ):
                continue

            flag = get_country_flag(get_country_from_ip(config["ip"]))

            if is_ipv6(config["ip"]):
                config["ip"] = f"[{config['ip']}]"

            config[
                "params"
            ] = f"security={dict_params.get('security', '')}&flow={dict_params.get('flow', '')}&sni={dict_params.get('sni', '')}&encryption={dict_params.get('encryption', '')}&type={dict_params.get('type', '')}&host={dict_params.get('host', '')}&path={dict_params.get('path', '')}&headerType={dict_params.get('headerType', '')}&fp={dict_params.get('fp', '')}&pbk={dict_params.get('pbk', '')}&sid={dict_params.get('sid', '')}&alpn={dict_params.get('alpn', '')}&"

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

    else:
        result = array_input

    return result

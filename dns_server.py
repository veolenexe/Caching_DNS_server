from socket import *
import datetime
import json
import os

HOST = 'localhost'
PORT = 53
ADDR = (HOST, PORT)
CACHE_FILE = 'cache.txt'


def send_udp_message(message, address="8.8.8.8"):
    server_address = (address, PORT)
    sock = socket(AF_INET, SOCK_DGRAM)
    try:
        sock.sendto(message, server_address)
        data, _ = sock.recvfrom(4096)
    finally:
        sock.close()
    return data


def build_name(data, offset):
    """
    :param data: пакет
    :param offset: смещение с которого начинается чтения name поля
    :return: name,смещение в котором закачиватеся чтения поля
    """
    name = ''
    while 1:
        count = int(data[offset:offset + 1].hex(), 16)
        if count == 0:
            name = name[1:]
            offset += 1
            break
        name += f".{data[offset + 1:offset + count + 1].decode(encoding='ascii', errors='ignore')}"
        offset += count + 1
    return name, offset


def parse_answer(data):
    """

    :param data: пакет ответа
    :return: данные, ttl
    """
    try:
        _, offset = build_name(data, 12)
        offset += 10
        ttl = (datetime.datetime.now() + datetime.timedelta(
            seconds=int(data[offset:offset + 4].hex(), 16))).strftime(
            '%Y-%B-%d %H:%M:%S')
        return data[2:], ttl
    except Exception:
        return b'', 0


class DNSServer:
    def __init__(self):
        self.cache = dict()
        if os.path.exists(CACHE_FILE):
            try:
                self.cache = json.load(open(CACHE_FILE))
            except Exception:
                pass

    def start(self):
        with socket(AF_INET, SOCK_DGRAM) as udp_socket:
            udp_socket.bind(ADDR)
            while 1:
                conn, addr = udp_socket.recvfrom(1024)
                answer = self.parse_query(conn)
                if answer:
                    udp_socket.sendto(answer, addr)

    def parse_query(self, data):
        try:
            qname, offset = build_name(data, 12)
            qtype = data[offset:offset + 2].hex()
            answer = ''
            if qtype == '0001' or qtype == '0002':
                key = f'{qname} {qtype}'
                if key in self.cache:
                    answer, ttl = self.cache[key]
                    answer = data[:2] + bytes(bytearray.fromhex(answer))
                    if datetime.datetime.strptime(ttl,
                                                  '%Y-%B-%d %H:%M:%S') \
                            < datetime.datetime.now():
                        answer = None
                        self.cache.pop(key, None)
                        self.save_cache()
                if not answer:
                    answer, ttl = parse_answer(send_udp_message(data))
                    if answer:
                        self.cache[key] = (answer.hex(), ttl)
                        self.save_cache()
                        answer = data[:2] + answer
            return answer
        except Exception:
            return b''

    def save_cache(self):
        with open(CACHE_FILE, 'w', encoding='utf-8') as fp:
            json.dump(self.cache, fp)


if __name__ == '__main__':
    server = DNSServer()
    server.start()

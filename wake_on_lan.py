import socket
import re
from conf import MAC_ADDRESS, BROADCAST_IP

def send_wol(mac_address, broadcast_ip=BROADCAST_IP, port=9):
    # Удаляем разделители и проверяем MAC-адрес
    mac_clean = re.sub(r'[^0-9A-Fa-f]', '', mac_address)
    if len(mac_clean) != 12:
        raise ValueError('Неверный MAC-адрес')

    # Формируем magic packet
    mac_bytes = bytes.fromhex(mac_clean)
    magic_packet = b'\xff' * 6 + mac_bytes * 16

    # Отправляем через UDP broadcast
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(magic_packet, (broadcast_ip, port))
        print(f"Magic packet отправлен на {mac_address} через {broadcast_ip}:{port}")

if __name__ == '__main__':
    send_wol(MAC_ADDRESS)
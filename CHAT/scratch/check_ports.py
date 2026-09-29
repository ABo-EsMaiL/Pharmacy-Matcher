import socket

for port in [8000, 8001]:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        res = s.connect_ex(('127.0.0.1', port))
        print(f"Port {port} status: {'IN USE / LISTENING' if res == 0 else 'FREE'}")

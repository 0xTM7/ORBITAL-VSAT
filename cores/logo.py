#!/usr/bin/python3
from config.color import Color

xbanner = f"""
{Color.bold}{Color.red}
________ ____________________.___________________  .____      ____   _____________   ________________
\\_____  \\\\______   \\______   \\   \\__    ___/  _  \\ |    |     \\   \\ /   /   _____/  /  _  \\__    ___/
 /   |   \\|       _/|    |  _/   | |    | /  /_\\  \\|    |      \\   Y   /\\_____  \\  /  /_\\  \\|    |   
/    |    \\    |   \\|    |   \\   | |    |/    |    \\    |___    \\     / /        \\/    |    \\    |   
\\_______  /____|_  /|______  /___| |____|\\____|__  /_______ \\    \\___/ /_______  /\\____|__  /____|   
        \\/       \\/        \\/                    \\/        \\/                  \\/         \\/         
{Color.reset}
"""

xhelper = f"""
    {Color.white}[{Color.red}M{Color.white}]: {Color.cyan} Available Methods:
        {Color.white}[{Color.red}+{Color.white}] {Color.white} LAYER 7: {Color.orange} APPLICATION
            {Color.white}     ->{Color.orange} GET                   \t: {Color.orange} HTTP GET Flood With Cache Bypass
            {Color.white}     ->{Color.orange} POST                  \t: {Color.orange} HTTP POST Flood [ 64KB Payloads ]
            {Color.white}     ->{Color.orange} PUT                   \t: {Color.orange} HTTP PUT Flood
            {Color.white}     ->{Color.orange} HEAD                  \t: {Color.orange} HTTP HEAD Flood
            {Color.white}     ->{Color.orange} DELETE                   \t: {Color.orange} HTTP DELETE Flood
            {Color.white}     ->{Color.orange} PATCH                 \t: {Color.orange} HTTP PATCH Flood
            {Color.white}     ->{Color.orange} OPTIONS                   \t: {Color.orange} HTTP OPTIONS Flood

        {Color.white}[{Color.red}+{Color.white}]{Color.white} LAYER 7: {Color.orange} ADVANCED METHODS
            {Color.white}     ->{Color.orange} XMLRPC                    \t: {Color.orange} XML-RPC Pingback attack
            {Color.white}     ->{Color.orange} RANDOM                    \t: {Color.orange} Random HTTP Methods Flood
            {Color.white}     ->{Color.orange} SLOWLORIS                 \t: {Color.orange} Slowloris Attack [ Keep Alive ]
            {Color.white}     ->{Color.orange} SLOW-POST                 \t: {Color.orange} Slow-POST Body Attack
            {Color.white}     ->{Color.orange} CACHE                 \t: {Color.orange} Cache Bypass Flood
            {Color.white}     ->{Color.orange} BYPASS                    \t: {Color.orange} WAF Bypass Techniques
            {Color.white}     ->{Color.orange} CONNECT                   \t: {Color.orange} HTTP CONNECT Flood
            {Color.white}     ->{Color.orange} TRACE                 \t: {Color.orange} HTTP TRACE Flood
            {Color.white}     ->{Color.orange} SLOW-READ                 \t: {Color.orange} Slow-READ Body Attack
            {Color.white}     ->{Color.orange} RUDY                  \t: {Color.orange} ARE-YOU-DEAD-YET Attack

        {Color.white}[{Color.red}+{Color.white}]{Color.white} LAYER 7: {Color.orange} HTTP/2 | HTTP/3
            {Color.white}     ->{Color.orange} H2-GET                    \t: {Color.orange} HTTP/2 GET With Priority
            {Color.white}     ->{Color.orange} H2-POST                   \t: {Color.orange} HTTP/2 POST With Multiplexing
            {Color.white}     ->{Color.orange} H2-RAPID                  \t: {Color.orange} HTTP/2 RAPID reset
            {Color.white}     ->{Color.orange} H2-PING                   \t: {Color.orange} HTTP/2 PING Flood
            {Color.white}     ->{Color.orange} H3-GET                    \t: {Color.orange} HTTP/3 QUIC GET
            {Color.white}     ->{Color.orange} H3-POST                   \t: {Color.orange} HTTP/3 QUIC POST

        {Color.white}[{Color.red}+{Color.white}]{Color.white} LAYER 4: {Color.orange} TRANSPORT
            {Color.white}     ->{Color.orange} TCP                   \t: {Color.orange} TCP Connection Flood
            {Color.white}     ->{Color.orange} UDP                   \t: {Color.orange} UDP Packet Flood [ 64KB Payloads ]
            {Color.white}     ->{Color.orange} SYN                   \t: {Color.orange} TCP SYN Flood {Color.white} [{Color.orange} REQUIRES ROOT {Color.white}]
            {Color.white}     ->{Color.orange} ACK                   \t: {Color.orange} TCP ACK Flood {Color.white} [{Color.orange} REQUIRES ROOT {Color.white}]
            {Color.white}     ->{Color.orange} RST                   \t: {Color.orange} TCP RST Flood {Color.white} [{Color.orange} REQUIRES ROOT {Color.white}]
            {Color.white}     ->{Color.orange} FIN                   \t: {Color.orange} TCP FIN Flood {Color.white} [{Color.orange} REQUIRES ROOT {Color.white}]
            {Color.white}     ->{Color.orange} SYNACK                    \t: {Color.orange} TCP SYN-ACK Reflection
            {Color.white}     ->{Color.orange} PSH                   \t: {Color.orange} TCP PSH + ACK Flood
            {Color.white}     ->{Color.orange} URG                   \t: {Color.orange} TCP URG Flood
            {Color.white}     ->{Color.orange} XMAS                  \t: {Color.orange} TCP XMAS SCAN Flood
            {Color.white}     ->{Color.orange} NULL                  \t: {Color.orange} TCP NULL SCAN Flood

        {Color.white}[{Color.red}+{Color.white}]{Color.white} LAYER 4: {Color.orange} AMPLIFICATIONS
            {Color.white}     ->{Color.orange} UDP-FRAG                  \t: {Color.orange} UDP FRAGMENTATION Flood
            {Color.white}     ->{Color.orange} DNS-AMP                   \t: {Color.orange} DNS AMPLIFICATION
            {Color.white}     ->{Color.orange} NTP-AMP                   \t: {Color.orange} NTP AMPLIFICATION
            {Color.white}     ->{Color.orange} SSDP-AMP                  \t: {Color.orange} SSDP AMPLIFICATION
            {Color.white}     ->{Color.orange} MEMCACHED                 \t: {Color.orange} MEMCACHED AMPLIFICATION
            {Color.white}     ->{Color.orange} CHARGEN                   \t: {Color.orange} CHARGEN AMPLIFICATION

        {Color.white}[{Color.red}+{Color.white}]{Color.white} LAYER 3: {Color.orange} NETWORKS
            {Color.white}     ->{Color.orange} ICMP                  \t: {Color.orange} ICMP Ping Flood {Color.white} [{Color.orange} REQUIRES ROOT {Color.white}]
            {Color.white}     ->{Color.orange} PING                  \t: {Color.orange} PING Flood
            {Color.white}     ->{Color.orange} SMURF                 \t: {Color.orange} SMURF Attack
            {Color.white}     ->{Color.orange} FRAGGLE                   \t: {Color.orange} FRAGGLE Attack [ UDP + ECHO ]

    {Color.white}[{Color.red}C{Color.white}]: {Color.cyan} Configuration Supports:
            {Color.white}[{Color.red}+{Color.white}]: {Color.white} User-Agent Headers Randomization
            {Color.white}[{Color.red}+{Color.white}]: {Color.white} Proxy Address Randomization/Proxychaining
            {Color.white}[{Color.red}+{Color.white}]: {Color.white} Referers Randomization/Requests Sources Randomization
            {Color.white}[{Color.red}+{Color.white}]: {Color.white} HTTP1 | HTTP2 | HTTP3 Configurations Support
            {Color.white}[{Color.red}+{Color.white}]: {Color.white} Autofingerprinting JA3, TLS, Browser Like Requests [ chrome | firefox | safari ]

    {Color.white}[{Color.red}EXIT{Color.white}]: {Color.red} CTRL + C To Stop.

{Color.reset}
"""


def Banner():
    print(xbanner)


def Helper():
    print(xhelper)

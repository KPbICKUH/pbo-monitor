import os
import platform
import socket
import subprocess
import psutil
import requests
import shutil
import re
from datetime import datetime
import json

# Telegram
BOT_TOKEN = "7925447298:AAE222NvzyGD_z52S4VY3wxY2dWhY13PUbk"
ALLOWED_CHAT_IDS = [499724678, 282311671, 6754531334, 350846940]

DOMAIN = "pbo.kz"
SERVER_IP = "109.233.109.158"
GOOGLE_DNS = "8.8.8.8"

os.chdir(os.path.dirname(os.path.abspath(__file__)))

def ping_stats(host, count=2):
    try:
        ip = socket.gethostbyname(host)
    except:
        return "❌ DNS ошибка", host, "100%"

    system = platform.system().lower()
    count_flag = "-n" if system == "windows" else "-c"
    
    try:
        cmd = ["ping", count_flag, str(count), host]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=5)
        output = result.stdout

        if system == "windows":
            # Ищем хотя бы один ответ
            if "TTL=" in output or "время=" in output or "time=" in output:
                # Есть ответ — ищем среднее
                avg_match = re.search(r"Average = (\d+)ms", output)
                avg = avg_match.group(1) + " ms" if avg_match else "OK"
                return f"{avg}, потери: 0%", ip, "0%"
            else:
                return "ICMP заблокирован", ip, "100%"
        else:
            if "bytes from" in output:
                avg_match = re.search(r"rtt min/avg/max/mdev = .*?/([\d\.]+)/", output)
                avg = avg_match.group(1) + " ms" if avg_match else "OK"
                return f"{avg}, потери: 0%", ip, "0%"
            else:
                return "ICMP заблокирован", ip, "100%"

    except subprocess.TimeoutExpired:
        return "ICMP заблокирован", ip, "100%"
    except Exception:
        return "❌ ошибка", ip, "100%"

def check_http_status(url, timeout=5):
    try:
        response = requests.get(url, timeout=timeout)
        return f"✅ HTTP {response.status_code}"
    except requests.exceptions.Timeout:
        return "❌ Таймаут HTTP"
    except requests.exceptions.ConnectionError:
        return "❌ Не удаётся подключиться"
    except Exception as e:
        return f"❌ Ошибка: {type(e).__name__}"

def get_system_info():
    pc_name = platform.node()
    cpu_usage = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory()
    disk_path = "C:\\" if platform.system() == "Windows" else "/"
    disk = psutil.disk_usage(disk_path)
    system = f"{platform.system()} {platform.release()}"
    return {
        "pc_name": pc_name,
        "os": system,
        "cpu": cpu_usage,
        "ram_used": round(ram.used / (1024**3), 2),
        "ram_total": round(ram.total / (1024**3), 2),
        "disk_used": round(disk.used / (1024**3), 2),
        "disk_total": round(disk.total / (1024**3), 2),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def run_speedtest():
    speedtest_path = shutil.which("speedtest")
    if not speedtest_path and os.path.exists("speedtest.exe"):
        speedtest_path = os.path.abspath("speedtest.exe")
    if not speedtest_path:
        return "Speedtest недоступен", None
    try:
        result = subprocess.run([speedtest_path, "-f", "json"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30)
        data = json.loads(result.stdout)
        dl = round(data["download"]["bandwidth"] * 8 / 1e6, 2)
        ul = round(data["upload"]["bandwidth"] * 8 / 1e6, 2)
        ping = round(data["ping"]["latency"], 2)
        return f"⬇️ {dl} Mbps | ⬆️ {ul} Mbps | ⏱ {ping} ms", {"dl": dl, "ul": ul, "ping": ping}
    except Exception:
        return "Speedtest error", None

def send_report():
    sysinfo = get_system_info()

    # DNS
    try:
        domain_ip = socket.gethostbyname(DOMAIN)
        dns_status = f"✅ {DOMAIN} → {domain_ip}"
        dns_ok = True
    except:
        dns_status = "❌ DNS ошибка"
        dns_ok = False

    # Пинги
    domain_ping, domain_ip_resolved, loss1 = ping_stats(DOMAIN)
    server_ping, _, loss2 = ping_stats(SERVER_IP)
    google_ping, google_ip, loss3 = ping_stats(GOOGLE_DNS)

    # HTTP-статус
    http_status = check_http_status(f"http://{DOMAIN}")

    # Speedtest
    speedtest_res, spd_data = run_speedtest()

    # Анализ проблем
    problems = []
    if not dns_ok:
        problems.append("❌ DNS не резолвится")
    if "100%" in loss1 or "100%" in loss2:
        problems.append("❌ Потери пакетов до серверов")
    if spd_data and (spd_data["dl"] < 10 or spd_data["ul"] < 5):
        problems.append("❌ Низкая скорость")
    if "❌" in http_status:
        problems.append("❌ Сайт не отвечает (HTTP)")

    final_status = "✅ Всё ОК" if not problems else "\n".join(problems)

    msg = (
        f"🖥 Отчёт с ПК\n\n"
        f"📌 Время: {sysinfo['timestamp']}\n"
        f"💻 Компьютер: {sysinfo['pc_name']}\n"
        f"🖥 ОС: {sysinfo['os']}\n\n"
        f"⚡ CPU: {sysinfo['cpu']}%\n"
        f"💾 RAM: {sysinfo['ram_used']} / {sysinfo['ram_total']} GB\n"
        f"📂 SSD: {sysinfo['disk_used']} / {sysinfo['disk_total']} GB\n\n"
        f"🌍 Интернет:\n{speedtest_res}\n\n"
        f"🌐 HTTP: {http_status}\n"
        f"📡 Пинг:\n"
        f"   🌍 {DOMAIN} → {domain_ping} ({domain_ip_resolved})\n"
        f"   🖥 {SERVER_IP} → {server_ping}\n"
        f"   🌐 {GOOGLE_DNS} → {google_ping} ({google_ip})\n\n"
        f"🔎 DNS: {dns_status}\n\n"
        f"📊 Итог: {final_status}"
    )

    # Исправленный URL без пробелов
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    for chat_id in ALLOWED_CHAT_IDS:
        try:
            requests.post(url, data={"chat_id": chat_id, "text": msg}, timeout=10)
        except Exception:
            pass

if __name__ == "__main__":
    send_report()
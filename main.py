import asyncio
import random
import hashlib
import base64
import uuid
import time
import os

import aiohttp
from playwright.async_api import async_playwright
from playwright_stealth import Stealth
from cryptography.hazmat.primitives import padding, serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding as rsa_padding
import aiofiles

WORKING_PROXIES = []

async def captcha(browser):
    html_content = """
    <!DOCTYPE html>
    <html>
    <head><meta charset="UTF-8"></head>
    <body>
        <div id="captcha-container"></div>
        <p id="result"></p>
        <script src="https://ca.turing.captcha.qcloud.com/TSDKCaptcha-global.js"></script>
        <script>
            const container = document.getElementById('captcha-container');
            const resultContainer = document.getElementById('result');
            const appId = '189951227';
            const callback = (response) => {
                if (response.ret === 0) {
                    resultContainer.textContent = response.ticket + ':' + response.randstr;
                } else {
                    resultContainer.textContent = 'Error';
                }
            };
            try {
                new TencentCaptcha(container, appId, callback, {}).show();
            } catch (e) {
                resultContainer.textContent = 'Init Error';
            }
        </script>
    </body>
    </html>
    """
    
    p = "p"
    if p == "p":
        page = await browser.new_page()
        
        try:
            await page.set_content(html_content, wait_until="domcontentloaded")
            result_selector = '#result:has-text(":")'
            await page.wait_for_selector(result_selector, timeout=15000)
            
            combined_result = await page.inner_text('#result')
            await page.close()
            
            return combined_result.strip()
        except TimeoutError:
            await page.close()
            print("Timeout: Не удалось получить ticket:randstr за 15 сек.")
        except Exception as e:
            await page.close()
            print(f"Непредвиденная ошибка: {e}")

def enc_token(token):
    key = hashlib.md5(b"9EuDKGtoWAOWoQH1cRng-d5ihNN60hkGLaRiaZTk-6s").hexdigest()
    padder = padding.PKCS7(128).padder()
    encryptor = Cipher(algorithms.AES(key[:16].encode()), modes.ECB(), backend=default_backend()).encryptor()
    return base64.b64encode(encryptor.update(padder.update(bytes(b ^ 0x73 for b in token.encode())) + padder.finalize()) + encryptor.finalize()).decode()

def enc_device_id(device_id):
    padder = padding.PKCS7(128).padder()
    encryptor = Cipher(algorithms.AES(b"MFwwDQYJKoZIhvcN"), modes.ECB(), backend=default_backend()).encryptor()
    return base64.b64encode(encryptor.update(padder.update(bytes(b ^ 0x73 for b in device_id.encode())) + padder.finalize()) + encryptor.finalize()).decode()

def enc_q(device_id, x_nonce):
    key = serialization.load_der_public_key(base64.b64decode("MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCLzlsA+3wXCAph80r/xs1bWhVrsJSOQmSBTA0GaBpVIzXqFBaibDmYA3WJDM9rcQ7KpYSyrJ02iFlsN43RnizrHfS+xPtdwuxBQ2Clow5cYPZucqQYL9HIlbBLoighH2eGQqGlVadL7r384iKTz9mmckSUa8hhJzS+WwUAqVO3DwIDAQAB"))
    text = f"0\n{device_id}\n{x_nonce}".encode()
    encrypted = b""
    for i in range(0, len(text), 117):
        encrypted += key.encrypt(text[i:i+117], rsa_padding.PKCS1v15())
    return base64.b64encode(encrypted).decode()

async def auth_token(proxy, lock, sem, browser):
    async with sem:
        async with aiohttp.ClientSession() as session:
            try:
                device_id = "".join(random.choices("0123456789abcdef", k=16))
                ad = str(uuid.uuid4())
                x_nonce = str(uuid.uuid4())
                x_time = str(int(time.time()))
                q = enc_q(device_id, x_nonce)

                ticket, randstr = (await captcha(browser)).split(":")
                print(ticket)

                async with session.get(
                    "http://gw.sandboxol.com/user/api/v5/account/auth-token",
                    params={"q":q,"randomstr":randstr,"ticket":ticket},
                    headers={
                        "bmg-user-id": "0",
                        "bmg-device-id": device_id,
                        "bmg-sign": enc_device_id(device_id),
                        "bmg-adid-sign": hashlib.sha1(ad.encode()).hexdigest(),
                        "package-name": "com.sandboxol.blockymods",
                        "userId": "0",
                        "packageName": "blockymods",
                        "packageNameFull": "com.sandboxol.blockymods",
                        "androidVersion": "36",
                        "OS": "android",
                        "appType": "android",
                        "appLanguage": "en",
                        "appVersion": "5531",
                        "appVersionName": "3.7.1",
                        "channel": "sandbox",
                        "uid_register_ts": "0",
                        "device_register_ts": "0",
                        "eventType": "app",
                        "userDeviceId": device_id,
                        "userLanguage": "en_US",
                        "region": "",
                        "clientType": "client",
                        "env": "prd",
                        "package_name_en": "com.sandboxol.blockymods",
                        "md5": "5d0de77b0f4b93b44669f146e54b49d9",
                        "adid": ad,
                        "telecomOper": "unknown",
                        "manufacturer": "POCO_2412DPC0AG",
                        "network": "wifi",
                        "brand": "POCO",
                        "model": "2412DPC0AG",
                        "device": "rodin",
                        "deviceModel": "2412DPC0AG",
                        "board": "rodin",
                        "cpu": "CPU architecture: 8",
                        "cpuFrequency": "2581250",
                        "dpi": "3.25",
                        "screenHeight": "2712",
                        "screenWidth": "1220",
                        "ram_memory": "11312",
                        "rom_memory": "490898",
                        "open_id": "",
                        "open_id_type": "0",
                        "client_ip": "",
                        "apps_flyer_gaid": ad,
                        "X-ApiKey": "6aDtpIdzQdgGwrpP6HzuPA",
                        "X-Nonce": x_nonce,
                        "X-Time": x_time,
                        "X-Sign": hashlib.md5(f"6aDtpIdzQdgGwrpP6HzuPA/user/api/v5/account/auth-token{x_nonce}{x_time}q={q}&randomstr={randstr}&ticket={ticket}9EuDKGtoWAOWoQH1cRng-d5ihNN60hkGLaRiaZTk-6s".encode()).hexdigest(),
                        "X-UrlPath": "/user/api/v5/account/auth-token",
                        "Access-Token": "",
                        "Connection": "Keep-Alive",
                        "Accept-Encoding": "gzip",
                        "User-Agent": "okhttp/4.12.0"
                    },
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    result = await response.json(content_type=None)
                    print(result)
                if result["code"] != 1:
                    os._exit(0)

                elif result["code"] == 1:
                    userId = str(int(result["data"]["userId"]))
                    accessToken = result["data"]["accessToken"]
                    registerTime = str(int(result["data"]["registerTime"]))
                    deviceRegisterTime = str(int(result["data"]["deviceRegisterTime"]))

                    async with lock:
                        async with aiofiles.open("result.txt", mode="a") as f:
                            res = f"{userId},{accessToken},{registerTime},{deviceRegisterTime},{device_id}"
                            print(res)
                            await f.write(f"{res}\n")

                    x_nonce = str(uuid.uuid4())
                    x_time = str(int(time.time()))

                    async with session.get(
                        f"http://gw.sandboxol.com/user/api/v1/user/random/nickname",
                        headers={
                            "language": "en_US",
                            "userId": "0",
                            "packageName": "blockymods",
                            "packageNameFull": "com.sandboxol.blockymods",
                            "androidVersion": "36",
                            "OS": "android",
                            "appType": "android",
                            "appLanguage": "en",
                            "appVersion": "5531",
                            "appVersionName": "3.7.1",
                            "channel": "sandbox",
                            "uid_register_ts": "0",
                            "device_register_ts": "0",
                            "eventType": "app",
                            "userDeviceId": device_id,
                            "userLanguage": "en_US",
                            "region": "",
                            "clientType": "client",
                            "env": "prd",
                            "package_name_en": "com.sandboxol.blockymods",
                            "md5": "5d0de77b0f4b93b44669f146e54b49d9",
                            "X-ApiKey": "6aDtpIdzQdgGwrpP6HzuPA",
                            "X-Nonce": x_nonce,
                            "X-Time": x_time,
                            "X-Sign": hashlib.md5(f"6aDtpIdzQdgGwrpP6HzuPA/user/api/v1/user/random/nickname{x_nonce}{x_time}9EuDKGtoWAOWoQH1cRng-d5ihNN60hkGLaRiaZTk-6s".encode()).hexdigest(),
                            "X-UrlPath": "/user/api/v1/user/random/nickname",
                            "Access-Token": "",
                            "Connection": "Keep-Alive",
                            "Accept-Encoding": "gzip",
                            "User-Agent": "okhttp/4.12.0"
                        },
                        timeout=aiohttp.ClientTimeout(total=5)
                    ) as response:
                        result = await response.json(content_type=None)
                        print(result)

                    if result["code"] == 1:
                        nickname = result["data"]
                        x_nonce = str(uuid.uuid4())
                        x_time = str(int(time.time()))

                        sex = random.choice([1, 2])
                        if sex == 1:
                            data = "{" + f'"decorationPicUrl":"http://static.sandboxol.com/sandbox/avatar/male.png","inviteCode":"","nickName":"{nickname}","picType":1,"sex":1' + "}"
                        else:
                            data = "{" + f'"decorationPicUrl":"http://static.sandboxol.com/sandbox/avatar/female.png","inviteCode":"","nickName":"{nickname}","picType":1,"sex":2' + "}"

                        md5 = hashlib.md5(f"6aDtpIdzQdgGwrpP6HzuPA/user/api/v1/user/register{x_nonce}{x_time}{data}9EuDKGtoWAOWoQH1cRng-d5ihNN60hkGLaRiaZTk-6s".encode()).hexdigest()

                        async with session.post(
                            f"http://gw.sandboxol.com/user/api/v1/user/register",
                            data=data,
                            headers={
                                "bmg-device-id": device_id,
                                "userId": userId,
                                "packageName": "blockymods",
                                "packageNameFull": "com.sandboxol.blockymods",
                                "androidVersion": "36",
                                "OS": "android",
                                "appType": "android",
                                "appLanguage": "en",
                                "appVersion": "5531",
                                "appVersionName": "3.7.1",
                                "channel": "sandbox",
                                "uid_register_ts": registerTime,
                                "device_register_ts": deviceRegisterTime,
                                "eventType": "app",
                                "userDeviceId": device_id,
                                "userLanguage": "en_US",
                                "region": "RU",
                                "clientType": "client",
                                "env": "prd",
                                "package_name_en": "com.sandboxol.blockymods",
                                "md5": "5d0de77b0f4b93b44669f146e54b49d9",
                                "adid": ad,
                                "telecomOper": "unknown",
                                "manufacturer": "POCO_2412DPC0AG",
                                "network": "wifi",
                                "brand": "POCO",
                                "model": "2412DPC0AG",
                                "device": "rodin",
                                "deviceModel": "2412DPC0AG",
                                "board": "rodin",
                                "cpu": "CPU architecture: 8",
                                "cpuFrequency": "2581250",
                                "dpi": "3.25",
                                "screenHeight": "2712",
                                "screenWidth": "1220",
                                "ram_memory": "11312",
                                "rom_memory": "490898",
                                "open_id": "",
                                "open_id_type": "0",
                                "client_ip": "",
                                "apps_flyer_gaid": ad,
                                "X-ApiKey": "6aDtpIdzQdgGwrpP6HzuPA",
                                "X-Nonce": x_nonce,
                                "X-Time": x_time,
                                "X-Sign": hashlib.md5(f"{md5}{device_id}".encode()).hexdigest(),
                                "X-UrlPath": "/user/api/v1/user/register",
                                "Access-Token": enc_token(accessToken + x_nonce),
                                "Content-Type": "application/json; charset=UTF-8",
                                "Connection": "Keep-Alive",
                                "Accept-Encoding": "gzip",
                                "User-Agent": "okhttp/4.12.0"
                            },
                            timeout=aiohttp.ClientTimeout(total=5)
                        ) as response:
                            result = await response.json(content_type=None)
                            print(result)
            except Exception as e:
                print(e)

async def main():
    async with Stealth().use_async(async_playwright()) as p:
        browser = await p.chromium.launch(
            headless=True, 
            args=["--disable-blink-features=AutomationControlled"]
        )
        lock = asyncio.Lock()
        sem = asyncio.Semaphore(5)
        while True:
            await auth_token("h", lock, sem, browser)

asyncio.run(main()) 

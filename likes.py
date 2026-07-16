import asyncio
import random
import uuid
import time
import hashlib
import base64

import aiohttp
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

TARGET_ACCOUNT_ID = "6970935870" # Тут твой айди аккаунта.
TARGET_DEVICE_ID = "d7c12aa755064b45" # Тут твой идентификатор устройства. Пример: 284f9e92693da75d
TARGET_ACCOUNT_REGISTER_TS = "0" # Оставить как есть.
TARGET_DEVICE_REGISTER_TS = "0" # Оставить как есть.
TARGET_ACCOUNT_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJqdGkiOiI2OTcwOTM1ODcwIiwiaWF0IjoxNzg0MjIzNDM3LCJzdWIiOiIyMDI2MDcxNiAxNzM3MTczNTIiLCJpc3MiOiJTYW5kYm94LVNlY3VyaXR5LUJhc2ljIiwiZXhwIjoxNzg1NDMzMDM3fQ.D_atz6xeJYwFdOs4t1f2bPNPAIPtUYwMwlfX2Frfc2Y" # Тут твой временный токен аккаунта. Пример: eyJhbGciOiJIUzI1NiJ9.eyJqdGkiOiIzMjY5MzA4Mjg4IiwiaWF0IjoxNzcyNzI5MjgwLCJzdWIiOiIyMDI2MDMwNSAxNjQ4MDA3NzMiLCJpc3MiOiJTYW5kYm94LVNlY3VyaXR5LUJhc2ljIiwiZXhwIjoxNzczOTM4ODgwfQ.Nfth3u6qdUV3Oo5TsmmXEY2zHI218XSx9M_E5spit9k

def enc_token(data):
    key = hashlib.md5(b"9EuDKGtoWAOWoQH1cRng-d5ihNN60hkGLaRiaZTk-6s").hexdigest()
    padder = padding.PKCS7(128).padder()
    encryptor = Cipher(algorithms.AES(key[:16].encode()), modes.ECB(), backend=default_backend()).encryptor()
    return base64.b64encode(encryptor.update(padder.update(bytes(b ^ 0x73 for b in data.encode())) + padder.finalize()) + encryptor.finalize()).decode()

async def like(account, semaphore, session, progress, total):
    async with semaphore:
        account_id, account_token, account_register_ts, device_register_ts, device_id = account.rstrip().split(",")

        data = '{' + f'"channel":1,"friendId":{TARGET_ACCOUNT_ID},"gameId":"","msg":"Let\'s be friends!","type":1' + '}'

        x_nonce = str(uuid.uuid4())
        x_time = str(int(time.time()))
        x_sign = hashlib.md5(f"6aDtpIdzQdgGwrpP6HzuPA/friend/api/v1/friends{x_nonce}{x_time}{data}9EuDKGtoWAOWoQH1cRng-d5ihNN60hkGLaRiaZTk-6s".encode()).hexdigest()

        subdomain = random.choice(["gw", "gwbyte"])
        async with session.post(
            f"http://{subdomain}.sandboxol.com/friend/api/v1/friends",
            data=data,
            headers={
                "userId": account_id,
                "packageName": "blockymods",
                "packageNameFull": "com.sandboxol.blockymods",
                "androidVersion": "36",
                "OS": "android",
                "appType": "android",
                "appLanguage": "en",
                "appVersion": "5544",
                "appVersionName": "3.8.4",
                "channel": "sandbox",
                "uid_register_ts": account_register_ts,
                "device_register_ts": device_register_ts,
                "eventType": "app",
                "userDeviceId": device_id,
                "userLanguage": "en_US",
                "region": "RU",
                "clientType": "client",
                "env": "prd",
                "package_name_en": "com.sandboxol.blockymods",
                "md5": "5d0de77b0f4b93b44669f146e54b49d9",
                "X-ApiKey": "6aDtpIdzQdgGwrpP6HzuPA",
                "X-Nonce": x_nonce,
                "X-Time": x_time,
                "X-Sign": hashlib.md5((x_sign + device_id).encode()).hexdigest(),
                "X-UrlPath": "/friend/api/v1/friends",
                "Access-Token": enc_token(account_token + x_nonce),
                "Content-Type": "application/json; charset=UTF-8",
                "Connection": "Keep-Alive",
                "Accept-Encoding": "gzip",
                "User-Agent": "okhttp/4.12.0"
            }
        ) as response:
            pass

        x_nonce = str(uuid.uuid4())
        x_time = str(int(time.time()))
        x_sign = hashlib.md5(f"6aDtpIdzQdgGwrpP6HzuPA/friend/api/v1/friends/{account_id}/agreement{x_nonce}{x_time}channel=1&gameId=&source=19EuDKGtoWAOWoQH1cRng-d5ihNN60hkGLaRiaZTk-6s".encode()).hexdigest()

        async with session.put(
            f"http://{subdomain}.sandboxol.com/friend/api/v1/friends/{account_id}/agreement?source=1&gameId=&channel=1",
            headers={
                "userId": TARGET_ACCOUNT_ID,
                "packageName": "blockymods",
                "packageNameFull": "com.sandboxol.blockymods",
                "androidVersion": "36",
                "OS": "android",
                "appType": "android",
                "appLanguage": "en",
                "appVersion": "5544",
                "appVersionName": "3.8.4",
                "channel": "sandbox",
                "uid_register_ts": TARGET_ACCOUNT_REGISTER_TS,
                "device_register_ts": TARGET_DEVICE_REGISTER_TS,
                "eventType": "app",
                "userDeviceId": TARGET_DEVICE_ID,
                "userLanguage": "en_US",
                "region": "RU",
                "clientType": "client",
                "env": "prd",
                "package_name_en": "com.sandboxol.blockymods",
                "md5": "5d0de77b0f4b93b44669f146e54b49d9",
                "X-ApiKey": "6aDtpIdzQdgGwrpP6HzuPA",
                "X-Nonce": x_nonce,
                "X-Time": x_time,
                "X-Sign": hashlib.md5((x_sign + TARGET_DEVICE_ID).encode()).hexdigest(),
                "X-UrlPath": f"/friend/api/v1/friends/{account_id}/agreement",
                "Access-Token": enc_token(TARGET_ACCOUNT_TOKEN + x_nonce),
                "Connection": "Keep-Alive",
                "Accept-Encoding": "gzip",
                "User-Agent": "okhttp/4.12.0"
            }
        ) as response:
            pass

        x_nonce = str(uuid.uuid4())
        x_time = str(int(time.time()))
        x_sign = hashlib.md5(f"6aDtpIdzQdgGwrpP6HzuPA/friend/api/v1/popularity{x_nonce}{x_time}friendId={TARGET_ACCOUNT_ID}9EuDKGtoWAOWoQH1cRng-d5ihNN60hkGLaRiaZTk-6s".encode()).hexdigest()

        async with session.post(
            f"http://{subdomain}.sandboxol.com/friend/api/v1/popularity?friendId={TARGET_ACCOUNT_ID}",
            headers={
                "userId": account_id,
                "packageName": "blockymods",
                "packageNameFull": "com.sandboxol.blockymods",
                "androidVersion": "36",
                "OS": "android",
                "appType": "android",
                "appLanguage": "en",
                "appVersion": "5544",
                "appVersionName": "3.8.4",
                "channel": "sandbox",
                "uid_register_ts": account_register_ts,
                "device_register_ts": device_register_ts,
                "eventType": "app",
                "userDeviceId": device_id,
                "userLanguage": "en_US",
                "region": "RU",
                "clientType": "client",
                "env": "prd",
                "package_name_en": "com.sandboxol.blockymods",
                "md5": "5d0de77b0f4b93b44669f146e54b49d9",
                "X-ApiKey": "6aDtpIdzQdgGwrpP6HzuPA",
                "X-Nonce": x_nonce,
                "X-Time": x_time,
                "X-Sign": hashlib.md5((x_sign + device_id).encode()).hexdigest(),
                "X-UrlPath": "/friend/api/v1/popularity",
                "Access-Token": enc_token(account_token + x_nonce),
                "Connection": "Keep-Alive",
                "Accept-Encoding": "gzip",
                "User-Agent": "okhttp/4.12.0"
            }
        ) as response:
            progress[0] += 1
            print(f"[{progress[0]}/{total}] {await response.text()}")

        x_nonce = str(uuid.uuid4())
        x_time = str(int(time.time()))
        x_sign = hashlib.md5(f"6aDtpIdzQdgGwrpP6HzuPA/friend/api/v1/friends{x_nonce}{x_time}friendId={TARGET_ACCOUNT_ID}9EuDKGtoWAOWoQH1cRng-d5ihNN60hkGLaRiaZTk-6s".encode()).hexdigest()

        async with session.delete(
            f"http://{subdomain}.sandboxol.com/friend/api/v1/friends?friendId={TARGET_ACCOUNT_ID}",
            headers={
                "userId": account_id,
                "packageName": "blockymods",
                "packageNameFull": "com.sandboxol.blockymods",
                "androidVersion": "36",
                "OS": "android",
                "appType": "android",
                "appLanguage": "en",
                "appVersion": "5544",
                "appVersionName": "3.8.4",
                "channel": "sandbox",
                "uid_register_ts": account_register_ts,
                "device_register_ts": device_register_ts,
                "eventType": "app",
                "userDeviceId": device_id,
                "userLanguage": "en_US",
                "region": "RU",
                "clientType": "client",
                "env": "prd",
                "package_name_en": "com.sandboxol.blockymods",
                "md5": "5d0de77b0f4b93b44669f146e54b49d9",
                "X-ApiKey": "6aDtpIdzQdgGwrpP6HzuPA",
                "X-Nonce": x_nonce,
                "X-Time": x_time,
                "X-Sign": hashlib.md5((x_sign + device_id).encode()).hexdigest(),
                "X-UrlPath": "/friend/api/v1/friends",
                "Access-Token": enc_token(account_token + x_nonce),
                "Connection": "Keep-Alive",
                "Accept-Encoding": "gzip",
                "User-Agent": "okhttp/4.12.0"
            }
        ) as response:
            pass

async def main():
    with open("results.txt") as f:
        accounts = f.readlines()

    total = len(accounts)
    progress = [0]

    async with aiohttp.ClientSession() as session:
        async with asyncio.TaskGroup() as tg:
            semaphore = asyncio.Semaphore(25)

            for account in accounts:
                tg.create_task(like(account, semaphore, session, progress, total))

asyncio.run(main()) 

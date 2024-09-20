from selenium.webdriver.common.by import By
from selenium import webdriver
from time import sleep
import json
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from queue import Queue
import asyncio
from concurrent.futures import ThreadPoolExecutor


data_queue = Queue()


def get_info(url, mode, driver):
    try:
        driver = driver

        computers = []
        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "product-picture__img"))
        )
        sleep(2)
        pixels = 700
        for i in range(10):
            driver.execute_script(f"window.scrollTo(0, {pixels});")
            sleep(0.1)
            pixels += 700

        elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "product-card--list"))
        )

        for element in elements:

            title = element.find_element(By.TAG_NAME, "mvid-plp-product-title").text
            descr = element.find_elements(By.CLASS_NAME, "product-feature-list__item")[1:3]

            desc = ''
            for d in descr:
                desc += d.text + '\n'
            desc = desc.replace("Процессор", "Процессор: ")
            desc = desc.replace("SSD", "SSD: ")
            desc = desc.replace("экран", "экран: ")
            desc = desc.replace("память", "память: ")

            try:
                price = element.find_element(By.CLASS_NAME, "price__main-value").text

            except:
                price = "нет в наличии"

            link = element.find_element(By.TAG_NAME, "a").get_attribute("href")
            pict = element.find_element(By.TAG_NAME, "img").get_attribute("src")
            computers.append({"title": title, "price": price, "desc": desc, "link": link, "pict": pict})

        if mode == 'w':
            with open('computers.json', 'w', encoding='utf-8') as f:
                json.dump(computers, f, ensure_ascii=False, indent=4)

        elif mode == 'a':
            with open('computers.json', 'r', encoding='utf-8') as f:
                existing_computers = json.load(f)

            existing_computers.extend(computers)

            with open('computers.json', 'w', encoding='utf-8') as file:
                json.dump(existing_computers, file, ensure_ascii=False, indent=4)

        driver.quit()
    except:

        driver.quit()


async def threads(x, y):
    urls = [f"https://www.mvideo.ru/noutbuki-planshety-komputery-8/noutbuki-118?f_tolko-v-nalichii=da&page={page}" for page in range(x, y)]
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [loop.run_in_executor(executor, get_info, url, "a" if page > 1 else "w", webdriver.Chrome()) for page, url in enumerate(urls, start=1)]
        for future in asyncio.as_completed(futures):
            await future



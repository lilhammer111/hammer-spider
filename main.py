import base64
import os
import time
import uuid

import requests
from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By


class GoogleBrowser:
    def __init__(self, query: str, url="https://www.google.com/search?tbm=isch&q="):
        self.url = url
        self.query = query
        self.driver = self.init_driver()

    def init_driver(self, *args) -> Chrome:
        options = webdriver.ChromeOptions()
        # options.add_argument("--disable-infobars")
        options.add_argument("--proxy-server=socks5://127.0.0.1:7890")
        for arg in args:
            options.add_argument(arg)

        driver = webdriver.Chrome(options=options)

        # process keyword, which format in google query string was like: 'women+in+pantyhose'
        # instead of 'women in pantyhose'
        word_list: list = self.query.split(" ", -1)
        driver.get(self.url + "+".join(word_list))

        driver.maximize_window()

        return driver

    @staticmethod
    def unique_image_name(prefix: str) -> str:
        unique_id = uuid.uuid4()
        image_name = f"{prefix}-{unique_id}.jpg"
        return image_name

    @staticmethod
    def save_base64_image(img_data, file_path):
        # 分割数据URL获取纯Base64字符串部分
        header, encoded = img_data.split(",", 1)

        # 解码Base64字符串
        image_data = base64.b64decode(encoded)

        # 将解码后的图片数据保存到文件
        with open(file_path, 'wb') as file:
            file.write(image_data)
        print(f"Image saved to {file_path}\n")

    def download_images(self, save_dir: str, image_name_prefix: str, count: int) -> int:
        # make sure the dir exists
        os.makedirs(save_dir, exist_ok=True)
        seen_image_src = set()
        # scroll pos
        for idx in range(count):
            print(f"Round: {idx + 1}")
            js = f'document.documentElement.scrollTop={(idx + 1) * 500};'
            self.driver.execute_script(js)
            # wait for loading page
            time.sleep(1)

            # Determine if it is bottom of page
            img_elem_list = self.driver.find_elements(
                by=By.TAG_NAME,
                value='img'
            )

            print("list len: ", len(img_elem_list))

            for elem in img_elem_list:
                img_src: str = elem.get_attribute('src')
                print(f"cur img src: {img_src} \n")
                if not img_src or (img_src in seen_image_src):
                    continue

                file_path = os.path.join(
                    save_dir,
                    self.unique_image_name(image_name_prefix)
                )

                if img_src.startswith("data:"):
                    self.save_base64_image(
                        img_src,
                        file_path
                    )

                if img_src.startswith("https://"):
                    try:
                        proxies = {
                            "https": "http://127.0.0.1:7890",
                            "http": "http://127.0.0.1:7890"
                        }
                        resp = requests.get(
                            img_src,
                            stream=True,
                            proxies=proxies,
                            timeout=3
                        )
                        resp.raise_for_status()
                        with open(file_path, 'wb') as f:
                            f.write(resp.content)
                            print(f"Image saved to {file_path} from internet\n")
                    except Exception as e:
                        print(f"network error: {e}")
                    time.sleep(0.2)

                seen_image_src.add(img_src)
        return len(seen_image_src)


if __name__ == '__main__':
    # gb = GoogleBrowser(query="women in pantyhose")
    # total = gb.download_images(
    #     "./data/",
    #     "pantyhose",
    #     500
    # )
    #
    # print("total images downloaded: ", total)


    images = os.listdir("data")
    print(len(images))
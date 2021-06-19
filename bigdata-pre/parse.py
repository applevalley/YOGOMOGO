import json
import pandas as pd
import numpy as np
import os
import shutil
from datetime import datetime
from django.utils.dateformat import DateFormat

DATA_DIR = "../data"
DATA_FILE = os.path.join(DATA_DIR, "data.json")
DUMP_FILE = os.path.join(DATA_DIR, "dump.pkl")
year = datetime.today().year
        
store_columns = (
    "id",  # 음식점 고유번호
    "store_name",  # 음식점 이름
    "branch",  # 음식점 지점 여부
    "area",  # 음식점 위치
    "tel",  # 음식점 번호
    "address",  # 음식점 주소
    "latitude",  # 음식점 위도
    "longitude",  # 음식점 경도
    "review_cnt", #리뷰 숫자
    "category",  # 음식점 카테고리
)

review_columns = (
    "id",  # 리뷰 고유번호
    "store",  # 음식점 고유번호
    "user",  # 유저 고유번호
    "score",  # 평점
    "content",  # 리뷰 내용
    "reg_time",  # 리뷰 등록 시간
)

menu_columns = (
    "id",  
    "store",
    "menu_name",
    "price",
)

user_columns = (
    "id",
    "gender",
    "age",
    "user_review_count",
 )


def import_data(data_path=DATA_FILE):
    """
    Req. 1-1-1 음식점 데이터 파일을 읽어서 Pandas DataFrame 형태로 저장합니다
    """

    try:
        with open(data_path, encoding="utf-8") as f:
            data = json.loads(f.read())
    except FileNotFoundError as e:
        print(f"`{data_path}` 가 존재하지 않습니다.")
        exit(1)

    stores = []  # 음식점 테이블
    reviews = []  # 리뷰 테이블
    menus = [] # 메뉴 테이블
    users = [] # 유저 테이블

    for d in data:

        # 데이터 전처리
        if not d["category_list"]:
            continue
            
        if d["category_list"] == [{'category': ''}]:
            continue
        
        if not d["menu_list"]:
            continue
            
        # reviews
        review_count = 0
        user_review_count = 1
        for review in d["review_list"]:
            r = review["review_info"]
            u = review["writer_info"]
    
            reviews.append(
                [r["id"], d["id"], u["id"], r["score"], r["content"], r["reg_time"]]
            )
        
        # stores
        categories = [c["category"] for c in d["category_list"]]
        
        stores.append(
            [
                d["id"],
                d["name"],
                d["branch"],
                d["area"],
                d["tel"],
                d["address"],
                d["latitude"],
                d["longitude"],
                d["review_cnt"],
                "|".join(categories),
            ]
        )
        
        # menu에 고유의 id가 없음!!
        for index in range(len(d['menu_list'])):
            menu = d['menu_list'][index]
            menus.append([index, d["id"], menu["menu"], menu["price"]])

        # user
        for user in d["review_list"]:
            r = review["review_info"]
            u = review["writer_info"]

            # 유저의 리뷰 개수 저장
            # for li in users:
            #     if u["id"] == li[0]:        
            #         user_review_count = li[3] + 1
            #         users.remove(li)
            #         break
           
            age = int(year) - int(u["born_year"]) + 1
            users.append(
                [u["id"], u["gender"], age, user_review_count]
            )

    store_frame = pd.DataFrame(data=stores, columns=store_columns)
    review_frame = pd.DataFrame(data=reviews, columns=review_columns)
    menu_frame = pd.DataFrame(data=menus, columns=menu_columns)
    user_frame = pd.DataFrame(data=users, columns=user_columns)
    return {"stores": store_frame, "reviews": review_frame, "menus": menu_frame, "users": user_frame}
    
def dump_dataframes(dataframes):
    pd.to_pickle(dataframes, DUMP_FILE)


def load_dataframes():
    return pd.read_pickle(DUMP_FILE)


def main():

    print("[*] Parsing data...")
    data = import_data()
    print("[+] Done")

    print("[*] Dumping data...")
    dump_dataframes(data)
    print("[+] Done\n")

    data = load_dataframes()
    term_w = shutil.get_terminal_size()[0] - 1
    separater = "-" * term_w

    print("[음식점]")
    print(f"{separater}\n")
    print(data["stores"].head())
    print(f"\n{separater}\n\n")
    print(data["stores"].count())

    print("[리뷰]")
    print(f"{separater}\n")
    print(data["reviews"].head())
    print(f"\n{separater}\n\n")
    print(data["reviews"].count())
    
    print("[메뉴]")
    print(f"{separater}\n")
    print(data["menus"].head())
    print(f"\n{separater}\n\n")
    print(data["menus"].count())
    
    print("[유저]")
    print(f"{separater}\n")
    print(data["users"].head())
    print(f"\n{separater}\n\n")
    print(data["users"].count())
    
if __name__ == "__main__":
    main()

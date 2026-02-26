from ninjemail import Ninjemail
from ninjemail.utils import generate_missing_info
import os
import csv
import multiprocessing

CSV_FILE = "accounts.csv"

def init_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Username", "Password", "Status"])

def append_to_csv(username, password, status):
    with open(CSV_FILE, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([username, password, status])

def update_csv_status(username, password, status):
    rows = []
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, mode='r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
    
    for i in range(1, len(rows)):
        if rows[i][0] == username and rows[i][1] == password:
            rows[i][2] = status
            break
            
    with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(rows)

if __name__ == '__main__':
    multiprocessing.freeze_support()
    init_csv()
    
    # 1. Tạo ngẫu nhiên temp username và password bằng thư viện của Ninjemail
    temp_username, temp_password, _, _, _, _ = generate_missing_info("", "", "", "", "", "")
    
    # 2. Lưu vào file CSV với trạng thái Pending (Đang chờ)
    append_to_csv(temp_username, temp_password, "Pending")
    
    print("="*50)
    print(f">> CẬP NHẬT CSV: Lưu nháp tài khoản: [{temp_username}] | Pass: [{temp_password}]")
    print("="*50)

    print("Đang khởi tạo Ninjemail...")
    ninja = Ninjemail(
        browser="undetected-chrome",
        sms_keys={"5sim": {"token": "dummy_token"}}
    )

    print("\nBắt đầu khởi chạy trình duyệt tạo Gmail (Không dùng Proxy)...")
    try:
        # 3. Truyền tài khoản temp vào hàm tạo account
        account = ninja.create_gmail_account(
            username=temp_username,
            password=temp_password,
            use_proxy=False
        )
        
        print("\n------------------------------")
        print("Mọi tiến trình đã hoàn tất!")
        print(f"Kết quả thu được: {account}")
        
        # 4A. Cập nhật trạng thái thành công
        update_csv_status(temp_username, temp_password, "Success")
        print(f">> Đã cập nhật trạng thái [Success] vào file {CSV_FILE}")

    except Exception as e:
        print(f"\n[LỖI]: Có lỗi xảy ra trong quá trình chạy automation: {e}")
        # 4B. Cập nhật trạng thái thất bại
        update_csv_status(temp_username, temp_password, "Failed")
        print(f">> Đã cập nhật trạng thái [Failed] vào file {CSV_FILE}")

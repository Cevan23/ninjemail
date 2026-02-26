from ninjemail import Ninjemail
import os

import multiprocessing

if __name__ == '__main__':
    multiprocessing.freeze_support()
    
    print("Đang khởi tạo Ninjemail...")
    # 1. Khởi tạo Ninjemail (Sử dụng Undetected Chrome đã fix, Tắt Proxy)
    ninja = Ninjemail(
        browser="undetected-chrome",
        sms_keys={"5sim": {"token": "dummy_token"}}  # Truyền tạm chuỗi giả để vượt qua bước kiểm tra
    )

    print("\nBắt đầu khởi chạy trình duyệt tạo Gmail (Không dùng Proxy)...")
    print("Hãy theo dõi cửa sổ Terminal. Khi nào tool yêu cầu nhập Số Điện Thoại / OTP, hãy gõ tay vào nhé!")

    try:
        # 2. Gọi hàm tạo Gmail (Tắt proxy)
        account = ninja.create_gmail_account(
            username="AnhBakhiamientay72",
            use_proxy=False  # TẮT PROXY Ở ĐÂY CHÍNH LÀ CHÌA KHÓA
        )
        
        print("\n------------------------------")
        print("Mọi tiến trình đã hoàn tất!")
        print(f"Kết quả thu được: {account}")

    except Exception as e:
        print(f"\n[LỖI]: Có lỗi xảy ra trong quá trình chạy automation: {e}")
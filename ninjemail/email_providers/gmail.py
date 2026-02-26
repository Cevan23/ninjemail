import logging
import time
from typing import Optional, Tuple
from utils.web_helpers import wait_and_click, set_input_value, type_into, action_chain_click
from selenium.common.exceptions import TimeoutException, NoSuchElementException, NoAlertPresentException, ElementClickInterceptedException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from utils import get_month_by_number

# 1. CẤU HÌNH LOGGING (Thêm phần này để đảm bảo log in ra màn hình)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# Centralized selector configuration
SELECTORS = {
    "first_name": (By.ID, 'firstName'),
    "last_name": (By.ID, 'lastName'),
    "month": (By.ID, 'month'),
    "day": (By.XPATH, '//input[@name="day"]'),
    "year": (By.ID, 'year'),
    "gender": (By.ID, 'gender'),
    "how_to_set_username": (By.ID, 'selectionc3'),
    "username": (By.NAME, 'Username'),
    "password": (By.NAME, 'Passwd'),
    "password_confirm": (By.NAME, 'PasswdAgain'),
    "phone_input": (By.ID, 'phoneNumberId'),
    "verification_code": (By.ID, 'code'),
    "error_message": (By.XPATH, "//div[contains(text(), 'Sorry, we could not create your Google Account.')]"),
    "phone_error": (By.XPATH, "//div[@class='Ekjuhf Jj6Lae']"),
    "final_buttons": (By.TAG_NAME, 'button')
}

NEXT_BUTTON_SELECTORS = [
    (By.XPATH, "//span[contains(text(),'Skip')]"),
    (By.CSS_SELECTOR, "div.VfPpkd-RLmnJb"),
    (By.CSS_SELECTOR, "div.VfPpkd-Jh9lGc"),
    (By.CSS_SELECTOR, "span.VfPpkd-vQzf8d"),
    (By.XPATH, "//span[contains(text(), 'Next')]"),
    (By.XPATH, "//span[contains(text(),'I agree')]"),
    (By.XPATH, "//div[contains(text(),'I agree')]"),
    (By.CLASS_NAME, "VfPpkd-LgbsSe"),
    (By.XPATH, "//button[contains(text(),'Next')]"),
    (By.XPATH, "//button[contains(text(),'I agree')]"),
]

WAIT_TIMEOUT = 10
RETRY_ATTEMPTS = 3

class AccountCreationError(Exception):
    """Base exception for account creation failures"""
    pass

def next_button(driver: WebDriver) -> None:
    """Click the next button with improved reliability"""
    logger.info("--> Đang tìm và ấn nút Next...")
    for selector in NEXT_BUTTON_SELECTORS:
        try:
            current_page = driver.current_url
            wait_and_click(driver, selector, timeout=5)
            time.sleep(1)  # Brief pause for page transition
            if current_page != driver.current_url:
                logger.info("    Đã chuyển trang thành công!")
                return
        except (TimeoutException, NoSuchElementException):
            continue
    raise AccountCreationError("Failed to find next button")

def set_how_to_set_username(driver: WebDriver) -> None:
    """Set how to set username"""
    try:
        how_to_set_username = WebDriverWait(driver, WAIT_TIMEOUT).until(EC.element_to_be_clickable((By.ID, 'selectionc22')))
        how_to_set_username.click()
        logger.info("--> Đã chọn chế độ 'Tạo địa chỉ Gmail của riêng bạn'")
    except:
        pass

def handle_errors(driver: WebDriver) -> None:
    """Check for common error conditions"""
    try:
        error_element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(SELECTORS["error_message"])
        )
        logger.error("Google account creation failed: %s", error_element.text)
        raise AccountCreationError(f"Google error: {error_element.text}")
    except TimeoutException:
        pass

def fill_personal_info(driver: WebDriver, first_name: str, last_name: str) -> None:
    """Fill in personal information section"""
    logger.info(f"--> Bắt đầu điền Họ Tên: {first_name} {last_name}")
    try:
        set_input_value(driver, SELECTORS["first_name"], first_name)
        set_input_value(driver, SELECTORS["last_name"], last_name)
        next_button(driver)
    except TimeoutException as e:
        logger.error("Failed to fill personal info")
        raise AccountCreationError("Personal info section timed out") from e

def fill_birthdate(driver: WebDriver, month, day, year) -> None:
    """Fill in birthdate information"""
    logger.info(f"--> Bắt đầu điền Ngày sinh: {month}-{day}-{year} và Giới tính")
    try:
        # Set day and year
        type_into(driver, SELECTORS["day"], day)
        type_into(driver, SELECTORS["year"], year)

        # Select month from dropdown
        month_select = WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.element_to_be_clickable(SELECTORS["month"])
        )
        action_chain_click(driver, month_select)

        month_element = month_select.find_element(By.XPATH, f"//span[text()='{get_month_by_number(month)}']")
        driver.execute_script("arguments[0].scrollIntoView(true);", month_element)
        action_chain_click(driver, month_element)
        
        # Select gender (index 3 = 'Rather not say')
        gender_select = WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.element_to_be_clickable(SELECTORS["gender"])
        )
        action_chain_click(driver, gender_select)
        gender_element = gender_select.find_element(By.XPATH, "//span[text()='Rather not say']")
        action_chain_click(driver, gender_element)
        
        next_button(driver)
    except (NoSuchElementException, TimeoutException, ElementClickInterceptedException) as e:
        logger.error("Failed to fill birthdate info")
        raise AccountCreationError("Birthdate section failed") from e

def handle_phone_verification_manual(driver: WebDriver) -> None:
    """Handle phone number verification manually via terminal input"""
    try:
        # In ra Terminal yêu cầu người dùng nhập số
        print("\n" + "="*50)
        phone = input("[THỦ CÔNG] Vui lòng nhập số điện thoại của bạn (VD: 0912345678): ")
        logger.info(f"Đang gửi số điện thoại {phone} lên trình duyệt...")
        print("="*50 + "\n")
        
        phone_input = WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.element_to_be_clickable(SELECTORS["phone_input"])
        )
        phone_input.clear()
        phone_input.send_keys(str(phone) + Keys.ENTER)
        
        # Check for phone number rejection
        try:
            error_element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located(SELECTORS["phone_error"])
            )
            logger.error("Phone number rejected: %s", error_element.text)
            raise AccountCreationError(f"Phone rejected: {error_element.text}")
        except TimeoutException:
            logger.info("Số điện thoại hợp lệ, chờ nhập mã OTP...")
            pass # Không có lỗi, tiếp tục
            
    except Exception as e:
        logger.error("Phone verification failed: %s", str(e))
        raise AccountCreationError("Phone verification step failed") from e

def handle_sms_code_manual(driver: WebDriver) -> None:
    """Handle SMS code entry manually via terminal input"""
    try:
        # In ra Terminal yêu cầu người dùng nhập OTP
        print("\n" + "="*50)
        code = input("[THỦ CÔNG] Vui lòng nhập mã OTP 6 số Google gửi về điện thoại: ")
        logger.info("Đang điền mã OTP vào trình duyệt...")
        print("="*50 + "\n")
        
        code_input = WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.element_to_be_clickable(SELECTORS["verification_code"])
        )
        code_input.clear()
        code_input.send_keys(str(code) + Keys.ENTER)
        time.sleep(2)  # Allow time for code verification
    except Exception as e:
        logger.error("SMS code entry failed: %s", str(e))
        raise AccountCreationError("SMS verification failed") from e

def handle_qr_verification_manual(driver: WebDriver) -> bool:
    """Check if Google shows the QR code verification page and pause for manual scanning"""
    try:
        # Check for the QR verification header or text quickly
        qr_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Verify some info before creating an account') or contains(text(), 'Scan the QR code')]")
        if qr_elements:
            logger.info("!!! CẢNH BÁO: Google yêu cầu xác minh bằng MÃ QR !!!")
            print("\n" + "="*50)
            print("[THỦ CÔNG] Google đang yêu cầu quét mã QR xác thực.")
            print("1. Hãy mở ứng dụng Camera/Google Lens trên điện thoại của bạn.")
            print("2. Quét mã QR đang hiển thị trên trình duyệt laptop.")
            print("3. Làm theo hướng dẫn trên điện thoại.")
            input("4. SAU KHI XONG xác thực trên điện thoại và trình duyệt đã tự chuyển trang, hãy NHẤN ENTER TẠI ĐÂY để tool chạy tiếp... ")
            print("="*50 + "\n")
            return True
        return False
    except Exception as e:
        return False

def confirm_alert(driver: WebDriver) -> None:
    """Confirm the alert popup"""
    try:
        WebDriverWait(driver, 10).until(EC.alert_is_present())
        alert = driver.switch_to.alert
        alert.accept()
    except NoAlertPresentException:
        pass # Đoạn này không cần log nữa để tránh rác màn hình

def create_account(
    driver,
    sms_key, # Vẫn giữ tham số này để không làm hỏng hàm gọi từ bên ngoài
    username,
    password,
    first_name,
    last_name,
    month,
    day,
    year
) -> Tuple[Optional[str], Optional[str]]:
    """
    Create a new Gmail account using manual phone verification
    """
    try:
        logger.info('================ BẮT ĐẦU LUỒNG GOOGLE ================')
        logger.info('--> Đang mở trang đăng ký Google...')
        driver.get('https://accounts.google.com/signup/v2/createaccount?flowName=GlifWebSignIn&flowEntry=SignUp')
        
        # Initial information
        fill_personal_info(driver, first_name, last_name)
        fill_birthdate(driver, month, day, year)
        
        # Username and password
        logger.info(f"--> Bắt đầu điền Username: {username}")
        set_how_to_set_username(driver)
        set_input_value(driver, SELECTORS["username"], username)
        next_button(driver)

        logger.info("--> Bắt đầu điền Mật khẩu...")
        type_into(driver, SELECTORS["password"], password)
        type_into(driver, SELECTORS["password_confirm"], password)
        next_button(driver)

        logger.info("--> Đang kiểm tra lỗi sau khi điền thông tin cơ bản...")
        handle_errors(driver)
        
        time.sleep(2)
        
        # Kiểm tra QR code xác minh thiết bị
        if handle_qr_verification_manual(driver):
            pass # Đã xử lý thủ công xong, trình duyệt sẽ tự nhảy trang
        # Nếu không có QR, kiểm tra xem có bị bắt xác minh SĐT không
        elif driver.find_elements(By.ID, "phoneNumberId"):
            logger.info("!!! CẢNH BÁO: Google yêu cầu xác minh số điện thoại !!!")
            # Gọi 2 hàm nhập tay
            handle_phone_verification_manual(driver)
            handle_sms_code_manual(driver)
        else:
            logger.info("--> May mắn! Google KHÔNG yêu cầu xác minh SĐT lúc này.")
        
        logger.info("--> Đang xử lý các trang cuối (Recovery Email, Terms...)")
        for _ in range(3):
            next_button(driver)
            time.sleep(2)

        confirm_alert(driver)
        
        # Agree to terms
        try:
            logger.info("--> Đang tìm nút 'I agree' (Đồng ý điều khoản)...")
            agree_button = WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "button span.VfPpkd-vQzf8d")))
            agree_button.click()
            logger.info("--> Đã click 'I agree'!")
        except:
            logger.info("--> Không tìm thấy nút 'I agree', có thể đã lướt qua.")
            pass

        # Log successful creation
        logger.info("================ TẠO TÀI KHOẢN THÀNH CÔNG ================")
        logger.info(f"Tài khoản: {username}@gmail.com")
        return f"{username}@gmail.com", password

    except Exception as e:
        logger.error("!!! LUỒNG TẠO TÀI KHOẢN THẤT BẠI !!!")
        logger.error(f"Chi tiết lỗi: {str(e)}")
        raise AccountCreationError("Account creation process failed") from e
    finally:
        logger.info("--> Đang đóng trình duyệt và dọn dẹp...")
        driver.quit()
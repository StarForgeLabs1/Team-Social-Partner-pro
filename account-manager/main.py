import asyncio
import json
import random
import os
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent
import undetected_chromedriver as uc
from pymongo import MongoClient
import redis
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@dataclass
class AccountProfile:
    """账号配置文件"""
    account_id: str
    user_id: str
    proxy_config: Dict
    browser_fingerprint: Dict
    language: str
    timezone: str
    device_info: Dict
    created_at: datetime
    last_active: datetime
    status: str

class AccountIsolationManager:
    """账号隔离管理器"""
    
    def __init__(self):
        self.mongo = MongoClient(os.getenv('MONGODB_URL'))
        self.db = self.mongo.tiktok_accounts # Using a specific DB for TikTok accounts
        self.redis_client = redis.from_url(os.getenv('REDIS_URL'))
        self.ua = UserAgent()
        
        # Supported language configurations
        self.supported_languages = {
            'en': {'name': 'English', 'locale': 'en-US'},
            'zh': {'name': 'Chinese', 'locale': 'zh-CN'},
            'ja': {'name': 'Japanese', 'locale': 'ja-JP'},
            'ko': {'name': 'Korean', 'locale': 'ko-KR'},
            'es': {'name': 'Spanish', 'locale': 'es-ES'},
            'fr': {'name': 'French', 'locale': 'fr-FR'},
            'de': {'name': 'German', 'locale': 'de-DE'},
            'it': {'name': 'Italian', 'locale': 'it-IT'},
            'pt': {'name': 'Portuguese', 'locale': 'pt-BR'},
            'ru': {'name': 'Russian', 'locale': 'ru-RU'},
            'ar': {'name': 'Arabic', 'locale': 'ar-SA'},
            'hi': {'name': 'Hindi', 'locale': 'hi-IN'},
            'th': {'name': 'Thai', 'locale': 'th-TH'}
        }

    async def create_isolated_account(self, user_id: str, account_config: Dict) -> str:
        """创建隔离的账号环境"""
        account_id = f"tiktok_{user_id}_{random.randint(10000, 99999)}"
        
        # Generate independent browser fingerprint
        fingerprint = self._generate_browser_fingerprint()
        
        # Assign independent proxy
        proxy_config = await self._assign_proxy()
        
        # Create account profile
        profile = AccountProfile(
            account_id=account_id,
            user_id=user_id,
            proxy_config=proxy_config,
            browser_fingerprint=fingerprint,
            language=account_config.get('language', 'en'),
            timezone=account_config.get('timezone', 'UTC'),
            device_info=self._generate_device_info(),
            created_at=datetime.now(),
            last_active=datetime.now(),
            status='active'
        )
        
        # Save to database
        await self._save_account_profile(profile)
        
        # Initialization of browser environment might not be done here directly, but when `get_browser_instance` is called
        
        return account_id

    def _generate_browser_fingerprint(self) -> Dict:
        """生成唯一的浏览器指纹"""
        return {
            'user_agent': self.ua.random,
            'screen_resolution': random.choice(['1920x1080', '1366x768', '1440x900', '1536x864']),
            'viewport_size': random.choice(['1200x800', '1366x768', '1440x900']),
            'color_depth': random.choice([24, 32]),
            'pixel_ratio': random.choice([1, 1.25, 1.5, 2]),
            'timezone_offset': random.randint(-12, 12),
            'language': random.choice(list(self.supported_languages.keys())),
            'platform': random.choice(['Win32', 'MacIntel', 'Linux x86_64']),
            'webgl_vendor': random.choice(['NVIDIA Corporation', 'AMD', 'Intel Inc.']),
            'canvas_fingerprint': self._generate_canvas_fingerprint()
        }

    def _generate_canvas_fingerprint(self) -> str:
        """生成Canvas指纹"""
        import hashlib
        seed = f"{random.random()}{datetime.now().timestamp()}"
        return hashlib.md5(seed.encode()).hexdigest()

    def _generate_device_info(self) -> Dict:
        """生成模拟的设备信息"""
        return {
            'device_model': random.choice(['iPhone 13', 'Samsung Galaxy S22', 'Google Pixel 7']),
            'os_version': random.choice(['iOS 16', 'Android 13']),
            'gpu': random.choice(['Apple A15 Bionic', 'Adreno 730', 'Mali-G710 MP10'])
        }

    async def _assign_proxy(self) -> Dict:
        """分配独立代理"""
        # In a real system, this would interact with the proxy-manager service
        # For now, a placeholder assuming proxies are available
        proxy_list = [
            {'type': 'http', 'ip': '1.2.3.4', 'port': '8080', 'user': 'user1', 'password': 'password1'},
            {'type': 'socks5', 'ip': '5.6.7.8', 'port': '1080', 'user': 'user2', 'password': 'password2'}
        ]
        if not proxy_list:
            raise Exception("No available proxies")
        
        proxy = random.choice(proxy_list)
        
        # This part assumes Redis is accessible and correctly configured to manage proxy usage
        # await self.redis_client.setex(f"proxy_usage:{proxy['ip']}", 3600, "in_use")
        
        return proxy

    async def _save_account_profile(self, profile: AccountProfile):
        """保存账号配置文件到MongoDB"""
        await self.db.profiles.insert_one(profile.__dict__)
        logging.info(f"Account profile {profile.account_id} saved to MongoDB.")

    async def _get_account_profile(self, account_id: str) -> Optional[Dict]:
        """从MongoDB获取账号配置文件"""
        return await self.db.profiles.find_one({'account_id': account_id})

    async def get_browser_instance(self, account_id: str) -> webdriver.Chrome:
        """获取账号专用浏览器实例"""
        profile = await self._get_account_profile(account_id)
        if not profile:
            raise Exception(f"Account {account_id} not found")
        
        # Configure Chrome options
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Set proxy
        if profile.get('proxy_config'):
            proxy = profile['proxy_config']
            proxy_string = f"{proxy['ip']}:{proxy['port']}"
            if proxy.get('user') and proxy.get('password'):
                # This setup is more complex and typically requires a proxy extension or
                # setting up the proxy with authentication programmatically.
                # For simplicity here, just the IP:PORT is used, assuming proxy-manager handles auth.
                options.add_argument(f"--proxy-server={proxy['type']}://{proxy_string}")
            else:
                options.add_argument(f"--proxy-server={proxy['type']}://{proxy_string}")
        
        # Set user agent
        options.add_argument(f"--user-agent={profile['browser_fingerprint']['user_agent']}")
        
        # Set window size
        resolution = profile['browser_fingerprint']['screen_resolution']
        options.add_argument(f"--window-size={resolution.replace('x', ',')}")
        
        # Set language
        lang = self.supported_languages[profile['language']]['locale']
        options.add_argument(f"--lang={lang}")
        
        # Create isolated user data directory
        user_data_dir = f"/tmp/chrome_profiles/{account_id}"
        options.add_argument(f"--user-data-dir={user_data_dir}")
        
        # Use undetected_chromedriver to avoid detection
        driver = uc.Chrome(options=options)
        
        # Apply anti-detection scripts
        await self._apply_anti_detection(driver, profile['browser_fingerprint'])
        
        return driver

    async def _apply_anti_detection(self, driver: webdriver.Chrome, fingerprint: Dict):
        """应用反检测措施"""
        # Remove webdriver property
        driver.execute_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
        """)
        
        # Modify navigator properties
        driver.execute_script(f"""
            Object.defineProperty(navigator, 'userAgent', {{
                get: () => '{fingerprint['user_agent']}',
            }});
            Object.defineProperty(navigator, 'platform', {{
                get: () => '{fingerprint['platform']}',
            }});
            Object.defineProperty(navigator, 'language', {{
                get: () => '{fingerprint['language']}',
            }});
        """)
        
        # Modify screen properties
        driver.execute_script(f"""
            Object.defineProperty(screen, 'width', {{
                get: () => {fingerprint['screen_resolution'].split('x')[0]},
            }});
            Object.defineProperty(screen, 'height', {{
                get: () => {fingerprint['screen_resolution'].split('x')[1]},
            }});
            Object.defineProperty(screen, 'colorDepth', {{
                get: () => {fingerprint['color_depth']},
            }});
        """)
        
        # Simulate plugin and mimeType arrays
        driver.execute_script("""
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5], // Simulate some plugins
            });
            Object.defineProperty(navigator, 'mimeTypes', {
                get: () => [1, 2, 3, 4, 5], // Simulate some mime types
            });
        """)

class TikTokAccountManager:
    """TikTok账号管理"""
    
    def __init__(self):
        self.isolation_manager = AccountIsolationManager()
        self.mongo = MongoClient(os.getenv('MONGODB_URL'))
        self.db = self.mongo.tiktok_accounts # Using a specific DB for TikTok accounts
        
    async def create_tiktok_account(self, user_id: str, account_config: Dict) -> Dict:
        """创建TikTok账号"""
        try:
            # Create isolated environment
            account_id = await self.isolation_manager.create_isolated_account(
                user_id, account_config
            )
            
            # Get browser instance
            driver = await self.isolation_manager.get_browser_instance(account_id)
            
            # Execute TikTok registration process
            tiktok_profile = await self._register_tiktok_account(
                driver, account_config
            )
            
            # Save TikTok account information
            await self._save_tiktok_profile(account_id, tiktok_profile)
            
            driver.quit()
            
            return {
                'account_id': account_id,
                'status': 'created',
                'tiktok_username': tiktok_profile['username']
            }
            
        except Exception as e:
            logging.error(f"Failed to create TikTok account: {e}")
            return {'status': 'error', 'message': str(e)}

    async def _register_tiktok_account(self, driver: webdriver.Chrome, config: Dict) -> Dict:
        """执行TikTok注册流程"""
        try:
            # Visit TikTok registration page
            driver.get('https://www.tiktok.com/signup')
            
            # Wait for page to load (adjust as needed)
            await asyncio.sleep(5)
            
            # Try to click on "Use phone or email" if present
            try:
                phone_email_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Use phone or email')]"))
                )
                phone_email_button.click()
                await asyncio.sleep(2)
            except Exception as e:
                logging.info(f"Phone or email button not found or not clickable immediately, proceeding. {e}")

            # Fill in birthdate - TikTok often asks for this early
            # This is a common hurdle, so make sure to handle it robustly
            # Example: Find month, day, year dropdowns and select
            # This part will require more specific XPATHs based on actual TikTok signup page
            # For demonstration, using placeholders:
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//select[@name='month']"))
                ).send_keys(random.choice(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']))
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//select[@name='day']"))
                ).send_keys(str(random.randint(1, 28)))
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//select[@name='year']"))
                ).send_keys(str(random.randint(1990, 2000))) # Ensure age is above 18
                
                # Click next/submit after birthdate
                WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Next') or contains(text(), 'Sign up')]"))
                ).click()
                await asyncio.sleep(3)

            except Exception as e:
                logging.warning(f"Could not fill birthdate, might not be prompted or XPATHs changed: {e}")
            
            # Select phone number registration
            # The XPATH might change; this is a generic attempt
            try:
                phone_tab_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'tab-item') and contains(text(), 'Phone')]"))
                )
                phone_tab_button.click()
                await asyncio.sleep(2)
            except Exception as e:
                logging.info(f"Phone tab not found or not clickable, assuming direct input. {e}")

            # Generate virtual phone number (placeholder)
            phone_number = self._generate_virtual_phone() # Make this non-async for simple generation

            # Input phone number
            # TikTok often has country code selector, ensure to handle it if needed
            try:
                phone_input = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//input[@type='tel' or @name='phone_number' or @data-tt='phone-number-input']"))
                )
                phone_input.send_keys(phone_number)
                await asyncio.sleep(1) # Small delay for UI to react
            except Exception as e:
                logging.error(f"Could not find or input phone number: {e}")
                raise

            # Generate username
            username = self._generate_username(config.get('preferred_username'))
            
            # Input password (TikTok might ask for password after phone number or separately)
            try:
                password_input = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//input[@type='password' or @name='password']"))
                )
                password = self._generate_secure_password()
                password_input.send_keys(password)
                await asyncio.sleep(1)
            except Exception as e:
                logging.warning(f"Could not find or input password field: {e}")
                password = None # Set to None if field not found


            # Click the 'Send Code' or 'Next' button related to phone/email
            try:
                send_code_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Send code') or contains(text(), 'Next') or @type='submit']"))
                )
                send_code_button.click()
                await asyncio.sleep(5) # Wait for code to be sent and potential captcha
            except Exception as e:
                logging.error(f"Could not click 'Send code'/'Next' button: {e}")
                raise

            # Handle CAPTCHA if it appears
            await self._handle_captcha(driver)

            # Input verification code (this part needs integration with an SMS/email verification service)
            # For demonstration, this is a placeholder. In a real system, you'd fetch the code.
            try:
                verification_code_input = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, "//input[@name='code' or @data-tt='verification-code-input']"))
                )
                # This is where you'd integrate with an SMS/email verification service
                # For now, a placeholder code
                fake_code = "123456" 
                verification_code_input.send_keys(fake_code)
                await asyncio.sleep(2)
            except Exception as e:
                logging.warning(f"Verification code input not found or cannot be filled: {e}")
                # If no verification code is requested, this might pass without error

            # Attempt to click final sign-up/next button if not already done
            try:
                final_signup_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Sign up') or contains(text(), 'Next') or @type='submit']"))
                )
                final_signup_button.click()
                await asyncio.sleep(5)
            except Exception as e:
                logging.info(f"Final signup button not found or already clicked. {e}")
                # This can happen if the previous step already completed registration

            # Attempt to input username if it's a separate step after registration
            try:
                username_input_after_reg = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Username' or @name='unique_id']"))
                )
                username_input_after_reg.clear() # Clear any pre-filled value
                username_input_after_reg.send_keys(username)
                
                # Click confirm for username
                WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Confirm') or @type='submit']"))
                ).click()
                await asyncio.sleep(2)
            except Exception as e:
                logging.info(f"Username input after registration not found or handled earlier: {e}")

            # Complete profile setup (e.g., profile picture, bio)
            await self._setup_profile(driver, config)
            
            return {
                'username': username,
                'password': password,
                'phone': phone_number,
                'status': 'active',
                'created_at': datetime.now()
            }
            
        except Exception as e:
            logging.error(f"TikTok registration failed: {e}")
            driver.save_screenshot(f"registration_error_{datetime.now().strftime('%Y%m%d%H%M%S')}.png")
            raise

    def _generate_virtual_phone(self) -> str:
        """生成虚拟手机号 (placeholder)"""
        # In a real system, this would integrate with a virtual phone number service
        return f"1{random.randint(200, 999)}{random.randint(200, 999)}{random.randint(1000, 9999)}"

    def _generate_username(self, preferred: Optional[str]) -> str:
        """生成TikTok用户名"""
        if preferred:
            return f"{preferred}_{random.randint(100, 999)}"
        return f"user_{datetime.now().strftime('%Y%m%d%H%M%S')}_{random.randint(100, 999)}"

    def _generate_secure_password(self) -> str:
        """生成安全密码"""
        chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()"
        return "".join(random.choice(chars) for i in range(12))

    async def _handle_captcha(self, driver: webdriver.Chrome):
        """处理验证码 (placeholder)"""
        # This is a complex part. It typically requires:
        # 1. CAPTCHA detection (e.g., check for specific elements, image recognition)
        # 2. Integration with a CAPTCHA solving service (e.g., 2Captcha, Anti-Captcha)
        # 3. Selenium interaction to input the solved CAPTCHA
        logging.info("Checking for CAPTCHA...")
        # Example: look for a common CAPTCHA element (this will vary greatly)
        try:
            captcha_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(@class, 'captcha') or contains(@id, 'captcha')]"))
            )
            logging.warning("CAPTCHA detected! Manual intervention or CAPTCHA solving service required.")
            # Here you would typically send the image to a solving service and wait for result
            # For now, it will just pause or raise an error
            raise Exception("CAPTCHA detected, cannot proceed automatically.")
        except:
            logging.info("No CAPTCHA detected or element not found, proceeding.")
            pass # No CAPTCHA or element not found

    async def _setup_profile(self, driver: webdriver.Chrome, config: Dict):
        """完成个人资料设置 (placeholder)"""
        logging.info("Setting up TikTok profile...")
        # Example: try to add a profile picture or bio if prompts appear
        # This is highly dependent on TikTok's UI flows after registration
        try:
            # Check for profile picture upload prompt
            upload_photo_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Upload photo') or contains(text(), 'Add profile picture')]"))
            )
            # You would programmatically upload an image here
            logging.info("Found profile photo upload prompt.")
            # Example: upload a dummy image if available
            # upload_photo_button.send_keys("/path/to/dummy_image.png")
            # await asyncio.sleep(2)
        except:
            logging.info("No profile photo upload prompt found.")

        try:
            # Check for bio input
            bio_input = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//textarea[@placeholder='Add a bio']"))
            )
            bio_input.send_keys(config.get('bio', 'Automated content creator.'))
            logging.info("Filled bio.")
            await asyncio.sleep(1)
            # Click save/confirm if available
            save_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Save') or contains(text(), 'Confirm')]"))
            )
            save_button.click()
            await asyncio.sleep(2)
        except:
            logging.info("No bio input or save button found.")

    async def _save_tiktok_profile(self, account_id: str, tiktok_profile: Dict):
        """保存TikTok账号信息到MongoDB"""
        await self.db.tiktok_accounts.update_one(
            {'account_id': account_id},
            {'$set': {'tiktok_profile': tiktok_profile, 'status': 'registered'}},
            upsert=True
        )
        logging.info(f"TikTok profile for account {account_id} saved/updated.")

if __name__ == "__main__":
    # Example usage - in a real system, this would be triggered by an API call
    # Ensure MongoDB and Redis are running and .env is configured
    import os
    from dotenv import load_dotenv
    load_dotenv() # Load environment variables

    async def test_account_creation():
        manager = TikTokAccountManager()
        user_id = "test_user_123"
        account_config = {
            'language': 'en',
            'timezone': 'America/New_York',
            'preferred_username': 'ai_creator_bot'
        }
        logging.info(f"Attempting to create TikTok account for user {user_id}")
        result = await manager.create_tiktok_account(user_id, account_config)
        logging.info(f"TikTok account creation result: {result}")

    # Run the test
    asyncio.run(test_account_creation())

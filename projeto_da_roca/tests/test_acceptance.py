import environ
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver

from products.models import Category
from users.models import User, DeliveryTime, ServiceAddress

env = environ.Env()

TEST_ON_CHROME = True if env('TEST_ON_CHROME') == 'on' else False
TEST_ON_FIREFOX = True if env('TEST_ON_FIREFOX') == 'on' else False


class UsersTest(StaticLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        cls.selenium = None
        if TEST_ON_CHROME:
            cls.selenium = webdriver.Chrome(executable_path=env('CHROMEDRIVER_PATH'))
        elif TEST_ON_FIREFOX:
            cls.selenium = webdriver.Firefox(executable_path=env('FIREFOXDRIVER_PATH'))

        #Choose your url to visit
        cls.selenium.get('http://127.0.0.1:8000')

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_login(self, user=False):
        user = User.objects.create(
            first_name = 'User',
            email = 'user@gmail.com',
            cpf = '11111111111',
            password='pbkdf2_sha256$260000$TuHWxP0N32cFSfqCkGVVvl$33dSJ0TKPHQev0weDFHu97mPz8oIPAAdphqDLvo1A3U=',
            is_admin = True
        ) if not user else user

        driver = self.selenium
        driver.get('%s%s' % (self.live_server_url, '/login/'))
        username_input = driver.find_element_by_name("username")
        username_input.send_keys(user.email)
        password_input = driver.find_element_by_name("password")
        password_input.send_keys('abcde123456')
        driver.find_element_by_xpath('//input[@value="Entrar"]').click()
        assert 'email ou senha estão incorretos' not in driver.page_source

    def test_admin_search_user_with_cpf(self):
        user = User.objects.create(
            first_name = 'Iris Viana',
            email = 'iris@gmail.com',
            cpf = '22222222222',
            password = 'pbkdf2_sha256$260000$TuHWxP0N32cFSfqCkGVVvl$33dSJ0TKPHQev0weDFHu97mPz8oIPAAdphqDLvo1A3U=',
        )

        driver = self.selenium
        self.test_login()
        driver.get('%s%s' % (self.live_server_url, '/user/admin/users/all'))
        search_input = driver.find_element_by_id('custom_table-search')
        search_input.send_keys(user.cpf)
        assert user.cpf in driver.page_source

    def test_admin_search_user_with_name(self):
        user = User.objects.create(
            first_name = 'Iris Viana',
            email = 'iris@gmail.com',
            cpf = '22222222222',
            password = 'pbkdf2_sha256$260000$TuHWxP0N32cFSfqCkGVVvl$33dSJ0TKPHQev0weDFHu97mPz8oIPAAdphqDLvo1A3U=',
        )

        driver = self.selenium
        self.test_login()
        driver.get('%s%s' % (self.live_server_url, '/user/admin/users/all'))
        search_input = driver.find_element_by_id('custom_table-search')
        search_input.send_keys(user.first_name)
        assert user.first_name in driver.page_source

    def test_admin_search_user_with_error(self):
        driver = self.selenium
        self.test_login()
        driver.get('%s%s' % (self.live_server_url, '/user/admin/users/all'))
        search_input = driver.find_element_by_id('custom_table-search')
        search_input.send_keys('Luana')
        assert 'Luana' not in driver.page_source

    def test_admin_remove_user(self):
        user = User.objects.create(
            first_name = 'Iris Viana',
            email = 'iris@gmail.com',
            cpf = '22222222222',
            password = 'pbkdf2_sha256$260000$TuHWxP0N32cFSfqCkGVVvl$33dSJ0TKPHQev0weDFHu97mPz8oIPAAdphqDLvo1A3U=',
        )

        driver = self.selenium
        self.test_login()
        driver.get('%s%s' % (self.live_server_url, '/user/admin/users/all'))
        driver.find_element_by_xpath(f"//button[@data-query=\"user_id={user.id},user_type=all\"]").click()
        driver.find_element_by_xpath("//button[@class=\"btn btn-danger btn-confirm\"]").click()
        assert user.first_name not in driver.page_source

    def test_admin_self_remove(self):
        user = User.objects.create(
            first_name = 'Iris Viana',
            email = 'iris@gmail.com',
            cpf = '22222222222',
            password = 'pbkdf2_sha256$260000$TuHWxP0N32cFSfqCkGVVvl$33dSJ0TKPHQev0weDFHu97mPz8oIPAAdphqDLvo1A3U=',
        )

        driver = self.selenium
        self.test_login(user)
        driver = self.selenium
        driver.get('%s%s' % (self.live_server_url, "/user/update"))
        driver.find_element_by_xpath("//button[@class=\"btn btn-danger\"]").click()
        driver.find_element_by_xpath("//button[@class=\"btn btn-danger btn-confirm\"]").click()
        assert 'Acesso' not in driver.page_source

    def test_user_self_edit(self):
        user = User.objects.create(
            first_name = 'Iris Viana',
            email = 'iris@gmail.com',
            cpf = '22222222222',
            password = 'pbkdf2_sha256$260000$TuHWxP0N32cFSfqCkGVVvl$33dSJ0TKPHQev0weDFHu97mPz8oIPAAdphqDLvo1A3U=',
        )
        driver = self.selenium
        self.test_login(user)
        driver.get('%s%s' % (self.live_server_url, "/user/update"))
        first_name_input = driver.find_element_by_name("first_name")
        first_name_input.send_keys('Iris')
        last_name_input = driver.find_element_by_name("last_name")
        last_name_input.send_keys('Viana')
        driver.find_element_by_xpath("//input[@name=\"save\"]").click()
        assert 'Atualizado com sucesso.' in driver.page_source

    def test_update_store_status(self):
        user = User.objects.create(
            first_name='Iris Viana',
            email='iris@gmail.com',
            cpf='22222222222',
            password='pbkdf2_sha256$260000$TuHWxP0N32cFSfqCkGVVvl$33dSJ0TKPHQev0weDFHu97mPz8oIPAAdphqDLvo1A3U=',
            is_seller=True
        )

        driver = self.selenium
        self.test_login(user)
        driver.get('%s%s' % (self.live_server_url, "/user/seller/"))
        status_old = driver.find_element_by_name("status").get_attribute('value')
        driver.find_element_by_xpath("//a[@href=\"/user/seller/updateStoreStatus\"]").click()

        assert status_old not in driver.page_source

    def test_user_self_edit_without_name(self):
        user = User.objects.create(
            first_name = 'Iris Viana',
            email = 'iris@gmail.com',
            cpf = '22222222222',
            password = 'pbkdf2_sha256$260000$TuHWxP0N32cFSfqCkGVVvl$33dSJ0TKPHQev0weDFHu97mPz8oIPAAdphqDLvo1A3U=',
        )

        driver = self.selenium
        self.test_login(user)
        driver.get('%s%s' % (self.live_server_url, "/user/update"))
        first_name_input = driver.find_element_by_name("first_name")
        first_name_input.clear()
        last_name_input = driver.find_element_by_name("last_name")
        last_name_input.send_keys('Viana')
        driver.find_element_by_xpath("//input[@name=\"save\"]").click()
        assert 'Atualizado com sucesso.' not in driver.page_source

    def test_request_reset_password(self):
        driver = self.selenium
        driver.get('%s%s' % (self.live_server_url, "/reset_password"))
        email_input = driver.find_element_by_id("id_email")
        email_input.send_keys('email@dominio.com')
        driver.find_element_by_xpath("//input[@value=\"Recuperar\"]").click()
        assert 'Confirmação de redefinição de senha' in driver.page_source

    def test_update_exists_user_email(self):
        user = User.objects.create(
            first_name='Iris Viana',
            email='iris@gmail.com',
            cpf='22222222222',
            password='pbkdf2_sha256$260000$TuHWxP0N32cFSfqCkGVVvl$33dSJ0TKPHQev0weDFHu97mPz8oIPAAdphqDLvo1A3U=',
        )
        User.objects.create(
            first_name='User',
            email='user@gmail.com',
            cpf='11111111111',
            password='pbkdf2_sha256$260000$TuHWxP0N32cFSfqCkGVVvl$33dSJ0TKPHQev0weDFHu97mPz8oIPAAdphqDLvo1A3U=',
            is_admin=True
        )
        driver = self.selenium
        self.test_login(user)
        driver.get('%s%s' % (self.live_server_url, "/user/update"))
        driver.find_element_by_id('update-email-button').click()
        new_email_input = driver.find_element_by_id("id_email")
        new_email_input.send_keys('user@gmail.com')
        confirm_new_email_input = driver.find_element_by_id("id_confirm_email")
        confirm_new_email_input.send_keys('user@gmail.com')
        password_confirm_input = driver.find_element_by_id("id_confirm_password")
        password_confirm_input.send_keys('abcde123456')
        driver.find_element_by_id("update-email-modal-button").click()

        assert 'O e-mail já está sendo usado' in driver.page_source

    def test_update_user_password(self):
        user = User.objects.create(
            first_name='Iris Viana',
            email='iris@gmail.com',
            cpf='22222222222',
            password='pbkdf2_sha256$260000$TuHWxP0N32cFSfqCkGVVvl$33dSJ0TKPHQev0weDFHu97mPz8oIPAAdphqDLvo1A3U=',
        )
        driver = self.selenium
        self.test_login(user)
        driver.get('%s%s' % (self.live_server_url, "/user/update"))
        driver.find_element_by_id('update-password-button').click()
        old_password_input = driver.find_element_by_id("id_old_password")
        old_password_input.send_keys('abcde123456')
        new_password_input = driver.find_element_by_id("id_new_password")
        new_password_input.send_keys('123456abcde')
        password_confirm_input = driver.find_element_by_id("id_confirm_new_password")
        password_confirm_input.send_keys('123456abcde')
        driver.find_element_by_id("update-password-modal-button").click()

        assert 'Entrar' in driver.page_source

    def test_update_user_incorrect_confirm_password(self):
        user = User.objects.create(
            first_name='Iris Viana',
            email='iris@gmail.com',
            cpf='22222222222',
            password='pbkdf2_sha256$260000$TuHWxP0N32cFSfqCkGVVvl$33dSJ0TKPHQev0weDFHu97mPz8oIPAAdphqDLvo1A3U=',
        )
        driver = self.selenium
        self.test_login(user)
        driver.get('%s%s' % (self.live_server_url, "/user/update"))
        driver.find_element_by_id('update-password-button').click()
        old_password_input = driver.find_element_by_id("id_old_password")
        old_password_input.send_keys('abcde123456')
        new_password_input = driver.find_element_by_id("id_new_password")
        new_password_input.send_keys('123456abcde574')
        password_confirm_input = driver.find_element_by_id("id_confirm_new_password")
        password_confirm_input.send_keys('123456abcde')
        driver.find_element_by_id("update-password-modal-button").click()

        assert 'As senhas precisam ser iguais' in driver.page_source

    def test_admin_remove_admin_permissions(self):
        user = User.objects.create(
            first_name='Iris Viana',
            email='iris@gmail.com',
            cpf='22222222222',
            password='pbkdf2_sha256$260000$TuHWxP0N32cFSfqCkGVVvl$33dSJ0TKPHQev0weDFHu97mPz8oIPAAdphqDLvo1A3U=',
            is_admin=True
        )

        user_to_remove = User.objects.create(
            first_name='Vinicius',
            email='vinicius@gmail.com',
            cpf='33333333333',
            password='pbkdf2_sha256$260000$TuHWxP0N32cFSfqCkGVVvl$33dSJ0TKPHQev0weDFHu97mPz8oIPAAdphqDLvo1A3U=',
            is_admin=True
        )
        driver = self.selenium
        self.test_login(user)
        driver.get('%s%s' % (self.live_server_url, "/user/admin/users/admin"))
        driver.find_element_by_xpath(f"//button[@data-query=\"admin_id={user_to_remove.id},user_type=admin\"]").click()
        driver.find_element_by_xpath("//*[text()='Remover administrador']").click()
        assert user_to_remove.first_name not in driver.page_source

    def test_admin_cancel_remove_admin_permissions(self):
        user = User.objects.create(
            first_name='Iris Viana',
            email='iris@gmail.com',
            cpf='22222222222',
            password='pbkdf2_sha256$260000$TuHWxP0N32cFSfqCkGVVvl$33dSJ0TKPHQev0weDFHu97mPz8oIPAAdphqDLvo1A3U=',
            is_admin=True
        )

        user_to_remove = User.objects.create(
            first_name='Vinicius',
            email='vinicius@gmail.com',
            cpf='33333333333',
            password='pbkdf2_sha256$260000$TuHWxP0N32cFSfqCkGVVvl$33dSJ0TKPHQev0weDFHu97mPz8oIPAAdphqDLvo1A3U=',
            is_admin=True
        )
        driver = self.selenium
        self.test_login(user)
        driver.get('%s%s' % (self.live_server_url, "/user/admin/users/admin"))
        driver.find_element_by_xpath(f"//button[@data-query=\"admin_id={user_to_remove.id},user_type=admin\"]").click()
        driver.find_element_by_xpath("//div[@id=\"includedModalRemoveAdmin\"]/div/div/div/button[@class=\"btn btn-primary w-50\"]").click()
        assert user_to_remove.first_name in driver.page_source

    def test_admin_remove_producer_permissions(self):
        user = User.objects.create(
            first_name='Iris Viana',
            email='iris@gmail.com',
            cpf='22222222222',
            password='pbkdf2_sha256$260000$TuHWxP0N32cFSfqCkGVVvl$33dSJ0TKPHQev0weDFHu97mPz8oIPAAdphqDLvo1A3U=',
            is_admin=True,
            is_seller=True
        )

        user_to_remove = User.objects.create(
            first_name='Vinicius',
            email='vinicius@gmail.com',
            cpf='33333333333',
            password='pbkdf2_sha256$260000$TuHWxP0N32cFSfqCkGVVvl$33dSJ0TKPHQev0weDFHu97mPz8oIPAAdphqDLvo1A3U=',
            is_seller=True
        )
        driver = self.selenium
        self.test_login(user)
        driver.get('%s%s' % (self.live_server_url, "/user/admin/users/producer"))
        driver.find_element_by_xpath(f"//button[@title=\"Tirar privilégios de vendedor\" and @data-query=\"user_id={user_to_remove.id},user_type=producer\"]").click()
        driver.find_element_by_xpath("//*[text()='Remover produtor']").click()
        assert user_to_remove.first_name not in driver.page_source

    def test_admin_cancel_remove_producer_permissions(self):
        user = User.objects.create(
            first_name='Iris Viana',
            email='iris@gmail.com',
            cpf='22222222222',
            password='pbkdf2_sha256$260000$TuHWxP0N32cFSfqCkGVVvl$33dSJ0TKPHQev0weDFHu97mPz8oIPAAdphqDLvo1A3U=',
            is_admin=True,
            is_seller=True
        )

        user_to_remove = User.objects.create(
            first_name='Vinicius',
            email='vinicius@gmail.com',
            cpf='33333333333',
            password='pbkdf2_sha256$260000$TuHWxP0N32cFSfqCkGVVvl$33dSJ0TKPHQev0weDFHu97mPz8oIPAAdphqDLvo1A3U=',
            is_seller=True
        )
        driver = self.selenium
        self.test_login(user)
        driver.get('%s%s' % (self.live_server_url, "/user/admin/users/producer"))
        driver.find_element_by_xpath(f"//button[@title=\"Tirar privilégios de vendedor\" and @data-query=\"user_id={user_to_remove.id},user_type=producer\"]").click()
        driver.find_element_by_xpath("//div[@id=\"includedModalRemoveProducer\"]/div/div/div/button[@class=\"btn btn-primary w-50\"]").click()
        assert user_to_remove.first_name in driver.page_source


class DeliveryTimeTest(StaticLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.selenium = None
        if TEST_ON_CHROME:
            cls.selenium = webdriver.Chrome(executable_path = env('CHROMEDRIVER_PATH'))
        elif TEST_ON_FIREFOX:
            cls.selenium = webdriver.Firefox(executable_path = env('FIREFOXDRIVER_PATH'))

        #Choose your url to visit
        cls.selenium.get('http://127.0.0.1:8000')

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_login(self, user=False):
        user = User.objects.create(
            first_name = 'User',
            email = 'user@gmail.com',
            cpf = '11111111111',
            password = 'pbkdf2_sha256$260000$TuHWxP0N32cFSfqCkGVVvl$33dSJ0TKPHQev0weDFHu97mPz8oIPAAdphqDLvo1A3U=',
            is_admin = True
        ) if not user else user

        driver = self.selenium
        driver.get('%s%s' % (self.live_server_url, '/login/'))
        username_input = driver.find_element_by_name("username")
        username_input.send_keys(user.email)
        password_input = driver.find_element_by_name("password")
        password_input.send_keys('abcde123456')
        driver.find_element_by_xpath('//input[@value="Entrar"]').click()
        assert 'email ou senha estão incorretos' not in driver.page_source

    def test_create_delivery_time(self):
        user = User.objects.create(
            first_name = 'Iris Viana',
            email = 'iris@gmail.com',
            cpf = '22222222222',
            password = 'pbkdf2_sha256$260000$TuHWxP0N32cFSfqCkGVVvl$33dSJ0TKPHQev0weDFHu97mPz8oIPAAdphqDLvo1A3U=',
            is_seller = True
        )
        self.test_login(user)

        service_address = ServiceAddress.objects.create(
            user = user,
            city = 'Garanhuns',
            state = 'PE'
        )

        driver = self.selenium
        driver.get('%s%s' % (self.live_server_url, f"/user/delivery_time/list/{service_address.id}"))
        driver.find_element_by_xpath(f"//a[@href=\"/user/delivery_time/create/{service_address.id}\"]").click()
        time_input = driver.find_element_by_name("time")
        time_input.send_keys('13:00')
        driver.find_element_by_xpath("//select[@name='day']/option[text()='Quinta-feira']").click()
        driver.find_element_by_xpath("//input[@type=\"submit\"]").click()
        search_input = driver.find_element_by_id('custom_table-search')
        search_input.send_keys('quinta')
        assert '13:00' in driver.page_source and 'Quinta-feira' in driver.page_source

    def test_create_delivery_time_with_error(self):
        user = User.objects.create(
            first_name = 'Iris Viana',
            email = 'iris@gmail.com',
            cpf = '22222222222',
            password = 'pbkdf2_sha256$260000$TuHWxP0N32cFSfqCkGVVvl$33dSJ0TKPHQev0weDFHu97mPz8oIPAAdphqDLvo1A3U=',
            is_seller = True
        )
        self.test_login(user)

        service_address = ServiceAddress.objects.create(
            user = user,
            city = 'Garanhuns',
            state = 'PE'
        )

        driver = self.selenium
        driver.get('%s%s' % (self.live_server_url, f"/user/delivery_time/list/{service_address.id}"))
        driver.find_element_by_xpath(f"//a[@href=\"/user/delivery_time/create/{service_address.id}\"]").click()
        driver.find_element_by_xpath("//select[@name='day']/option[text()='Quinta-feira']").click()
        driver.find_element_by_xpath("//input[@type=\"submit\"]").click()
        
        assert 'Quando você irá atender?' == driver.title

    def test_update_delivery_time(self):
        # Use already created delivery time
        user = User.objects.create(
            first_name = 'Iris Viana',
            email = 'iris@gmail.com',
            cpf = '22222222222',
            password = 'pbkdf2_sha256$260000$TuHWxP0N32cFSfqCkGVVvl$33dSJ0TKPHQev0weDFHu97mPz8oIPAAdphqDLvo1A3U=',
            is_seller = True
        )
        self.test_login(user)

        service_address = ServiceAddress.objects.create(
            user = user,
            city = 'Garanhuns',
            state = 'PE'
        )

        delivery_time = DeliveryTime.objects.create(
            service_address=service_address,
            time='13:00',
            day='thursday'
        )

        # Find created delivery time
        driver = self.selenium
        driver.get('%s%s' % (self.live_server_url, f"/user/delivery_time/list/{service_address.id}"))
        search_input = driver.find_element_by_id('custom_table-search')
        search_input.send_keys('quinta')

        # Click edit button to start editing delivery time
        driver.find_element_by_xpath(f"//a[@href=\"/user/delivery_time/update/{delivery_time.id}\"]").click()
        
        # Update fields
        driver.find_element_by_xpath("//select[@name='day']/option[text()='Sexta-feira']").click()
        driver.find_element_by_xpath("//input[@type=\"submit\"]").click()
        
        assert '13:00' in driver.page_source and 'Sexta-feira' in driver.page_source

    def test_update_delivery_time_with_error(self):
        # Use already created delivery time
        user = User.objects.create(
            first_name = 'Iris Viana',
            email = 'iris@gmail.com',
            cpf = '22222222222',
            password = 'pbkdf2_sha256$260000$TuHWxP0N32cFSfqCkGVVvl$33dSJ0TKPHQev0weDFHu97mPz8oIPAAdphqDLvo1A3U=',
            is_seller = True
        )
        self.test_login(user)

        service_address = ServiceAddress.objects.create(
            user = user,
            city = 'Garanhuns',
            state = 'PE'
        )

        delivery_time = DeliveryTime.objects.create(
            service_address=service_address,
            time='13:00',
            day='thursday'
        )

        # Find created delivery time
        driver = self.selenium
        driver.get('%s%s' % (self.live_server_url, f"/user/delivery_time/list/{service_address.id}"))
        search_input = driver.find_element_by_id('custom_table-search')
        search_input.send_keys('quinta')

        # Click edit button to start editing delivery time
        driver.find_element_by_xpath(f"//a[@href=\"/user/delivery_time/update/{delivery_time.id}\"]").click()
        
        # Update fields
        time_input = driver.find_element_by_name("time")
        time_input.send_keys('')
        driver.find_element_by_xpath("//select[@name='day']/option[text()='Sexta-feira']").click()
        driver.find_element_by_xpath("//input[@type=\"submit\"]").click()
        
        assert 'Quando você irá atender?' == driver.title

    def test_delete_delivery_time(self):
        # Use already created delivery time
        user = User.objects.create(
            first_name = 'Iris Viana',
            email = 'iris@gmail.com',
            cpf = '22222222222',
            password = 'pbkdf2_sha256$260000$TuHWxP0N32cFSfqCkGVVvl$33dSJ0TKPHQev0weDFHu97mPz8oIPAAdphqDLvo1A3U=',
            is_seller = True
        )
        self.test_login(user)

        service_address = ServiceAddress.objects.create(
            user = user,
            city = 'Garanhuns',
            state = 'PE'
        )

        delivery_time = DeliveryTime.objects.create(
            service_address = service_address,
            time='13:00',
            day='thursday'
        )

        # Find created delivery time
        driver = self.selenium
        driver.get('%s%s' % (self.live_server_url, f"/user/delivery_time/list/{service_address.id}"))
        search_input = driver.find_element_by_id('custom_table-search')
        search_input.send_keys('quinta')

        driver.find_element_by_xpath(f"//button[@data-query=\"delivery_time_id={delivery_time.id}\"]").click()
        driver.find_element_by_xpath("//button[@class=\"btn btn-danger btn-confirm\"]").click()

        search_input = driver.find_element_by_id('custom_table-search')
        search_input.send_keys('quinta')
        assert '13:00' not in driver.page_source and 'Quinta-feira' not in driver.page_source


class CategoryTest(StaticLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.selenium = None

        if TEST_ON_CHROME:
            cls.selenium = webdriver.Chrome(executable_path = env('CHROMEDRIVER_PATH'))
        elif TEST_ON_FIREFOX:
            cls.selenium = webdriver.Firefox(executable_path = env('FIREFOXDRIVER_PATH'))

        cls.selenium.get('http://127.0.0.1:8000')
    
    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_login(self, user=False):
        user = User.objects.create(
            first_name = 'Usuario',
            email = 'usuario@gmail.com',
            cpf = '44455544455',
            password = 'pbkdf2_sha256$260000$TuHWxP0N32cFSfqCkGVVvl$33dSJ0TKPHQev0weDFHu97mPz8oIPAAdphqDLvo1A3U=',
            is_admin = True
        ) if not user else user

        driver = self.selenium
        driver.get('%s%s' % (self.live_server_url, '/login/'))
        username_input = driver.find_element_by_name("username")
        username_input.send_keys(user.email)
        password_input = driver.find_element_by_name("password")
        password_input.send_keys('abcde123456')
        driver.find_element_by_xpath('//input[@value="Entrar"]').click()
        assert 'email ou senha estão incorretos' not in driver.page_source

    def test_create_category(self):
        user = User.objects.create(
            first_name = 'Raquel Vieira',
            email = 'raquel@gmail.com',
            cpf = '99999999999',
            password = 'pbkdf2_sha256$260000$TuHWxP0N32cFSfqCkGVVvl$33dSJ0TKPHQev0weDFHu97mPz8oIPAAdphqDLvo1A3U=',
            is_seller = True
        )
        self.test_login(user)

        driver = self.selenium
        driver.get('%s%s' % (self.live_server_url, "/user/admin"))
        driver.find_element_by_xpath("//a[@href=\"/product/categories/create\"]").click()
        search_input = driver.find_element_by_name('name')
        search_input.send_keys('Frutas')
        driver.find_element_by_xpath("//input[@type=\"submit\"]").click()
        assert 'Frutas' in driver.page_source
    
    def test_create_category_with_error_name(self):
        user = User.objects.create(
            first_name = 'Raquel Vieira',
            email = 'raquel@gmail.com',
            cpf = '99999999999',
            password = 'pbkdf2_sha256$260000$TuHWxP0N32cFSfqCkGVVvl$33dSJ0TKPHQev0weDFHu97mPz8oIPAAdphqDLvo1A3U=',
            is_seller = True
        )
        self.test_login(user)

        driver = self.selenium
        driver.get('%s%s' % (self.live_server_url, "/user/admin"))
        driver.find_element_by_xpath("//a[@href=\"/product/categories/create\"]").click()
        search_input = driver.find_element_by_name('name')
        search_input.send_keys('Frutas')
        driver.find_element_by_xpath("//input[@type=\"submit\"]").click()
        assert 'Frutas' in driver.page_source
        driver.find_element_by_xpath("//a[@href=\"/product/categories/create\"]").click()
        search_input = driver.find_element_by_name('name')
        search_input.send_keys('Frutas')
        assert 'Cadastre sua categoria' in driver.page_source

    def test_create_category_empty(self):
        user = User.objects.create(
            first_name = 'Raquel Vieira',
            email = 'raquel@gmail.com',
            cpf = '99999999999',
            password = 'pbkdf2_sha256$260000$TuHWxP0N32cFSfqCkGVVvl$33dSJ0TKPHQev0weDFHu97mPz8oIPAAdphqDLvo1A3U=',
            is_seller = True
        )
        self.test_login(user)

        driver = self.selenium
        driver.get('%s%s' % (self.live_server_url, "/user/admin"))
        driver.find_element_by_xpath("//a[@href=\"/product/categories/create\"]").click()
        search_input = driver.find_element_by_name('name')
        search_input.send_keys('')
        driver.find_element_by_xpath("//input[@type=\"submit\"]").click()
        assert 'Cadastre sua categoria' in driver.page_source

    def test_delete_category(self):
        user = User.objects.create(
            first_name = 'Raquel Vieira',
            email = 'raquel@gmail.com',
            cpf = '99999999999',
            password = 'pbkdf2_sha256$260000$TuHWxP0N32cFSfqCkGVVvl$33dSJ0TKPHQev0weDFHu97mPz8oIPAAdphqDLvo1A3U=',
            is_seller = True
        )
        self.test_login(user)
        category = Category.objects.create(
            name='Verdura'
        )

        driver = self.selenium
        driver.get('%s%s' % (self.live_server_url, "/user/admin"))
        driver.find_element_by_xpath("//a[@href=\"/product/categories/list\"]").click()
        
        driver.find_element_by_xpath(f"//button[@data-query=\"category_id={category.id}\"]").click()
        driver.find_element_by_xpath("//button[@class=\"btn btn-danger btn-confirm\"]").click()

        assert 'Verdura' not in driver.page_source

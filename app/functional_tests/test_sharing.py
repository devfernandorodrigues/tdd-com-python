from selenium import webdriver
from .base import FunctionalTest

def quit_if_possible(browser):
    try:
        browser.quit()
    except Exception as e:
        print(e)


class SharingTest(FunctionalTest):

    def test_can_share_a_list_with_another_user(self):
        # Edith é uma usuária logada
        self.create_pre_authenticated_session('edith@example.com')
        edith_browser = self.browser
        self.addCleanup(lambda: quit_if_possible(edith_browser))

        # Seu amigo Oniciferous também está no site de listas
        oni_browser = self.new_browser()
        self.addCleanup(lambda: quit_if_possible(oni_browser))
        self.browser = oni_browser
        self.create_pre_authenticated_session('oniciferous@example.com')

        # Edith acessa a página inicial e começa uma lista
        self.browser = edith_browser
        self.browser.get(self.live_server_url)
        self.add_list_item('Get help')

        # Ela percebe que há uma opção "Share this list" (Compartilhar essa lista)
        share_box = self.browser.find_element_by_css_selector(
            'input[name="sharee"]'
        )
        self.assertEqual(
            share_box.get_attribute('placeholder'),
            'your-friend@example.com'
        )

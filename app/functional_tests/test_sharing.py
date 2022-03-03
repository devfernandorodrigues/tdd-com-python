from .list_page import ListPage
from .base import FunctionalTest
from .my_lists_page import MyListsPage

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
        list_page = ListPage(self).add_list_item('Get help')

        # Ela percebe que há uma opção "Share this list" (Compartilhar essa lista)
        share_box = list_page.get_share_box()
        self.assertEqual(
            share_box.get_attribute('placeholder'),
            'your-friend@example.com'
        )

        # Ela compartilha sua lista.
        # A página é atualizada para informar que a lista foi compartilhada
        # com Oniciferous:
        list_page.share_list_with('oniciferous@example.com')

        # Oniciferous agora acessa a página de listas com o seu navegador
        self.browser = oni_browser
        MyListsPage(self).go_to_my_lists_page()

        # Ele vê ai a lista de Edith!
        self.browser.find_element_by_link_text('Get help').click()

        # Na página de lista, Oniciferous pode ver que a lista é de Edith
        self.wait_for(lambda: self.assertEqual(
            list_page.get_list_owner(),
            'edith@example.com'
        ))

        # Ele adiciona um item na lista
        list_page.add_list_item('Hi Edith!')

        # Quando Edith atualiza a página, ela vê o acréscimo feito por Oniciferous
        self.browser = edith_browser
        self.browser.refresh()
        list_page.wait_for_row_in_list_table('Hi Edith!', 2)

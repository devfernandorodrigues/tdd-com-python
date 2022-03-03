import os
import poplib
import time
import re

from django.core import mail
from selenium.webdriver.common.keys import Keys

from .base import FunctionalTest

SUBJECT = 'Your login link for Superlists'


class LoginTest(FunctionalTest):

    def test_can_get_email_link_to_log_in(self):
        # Edith acessa o incrível site de superlistas
        # e, pela primeira vez, percebe que há uma seção de "Log in" na barra
        # de navegação. Essa seção está lhe dizendo para inserir o seu endereço
        # de email, portanto ela faz isso
        if self.staging_server:
            test_email = 'tddcompython@gmail.com'
        else:
            test_email = 'edith@example.com'
        self.browser.get(self.live_server_url)
        self.browser.find_element_by_name('email').send_keys(test_email)
        self.browser.find_element_by_name('email').send_keys(Keys.ENTER)

        # Uma mensagem aparece informando-lhe que um email foi enviado
        self.wait_for(lambda: self.assertIn(
            'Check your email',
            self.browser.find_element_by_tag_name('body').text
        ))

        # Ela verifica seu email e encontra uma mensagem
        body = self.wait_for_email(test_email, SUBJECT)

        # A mensagem contém um link com url
        self.assertIn('Use this link to log in', body)
        url_search = re.search(r'http://.+/.+$', body)
        if not url_search:
            self.fail(f'Could not find url in email body:\n{body}')
        url = url_search.group(0)
        self.assertIn(self.live_server_url, url)

        # Ela clica no url
        self.browser.get(url)

        # Ela está logada
        self.wait_to_be_logged_in(email=test_email)

        # Agora ela faz logout
        self.browser.find_element_by_link_text('Log out').click()

        # Ela não está mais logada!
        self.wait_to_be_logged_out(email=test_email)

    def wait_for_email(self, test_email, subject):
        if not self.staging_server:
            email = mail.outbox[0]
            self.assertIn(test_email, email.to)
            self.assertEqual(email.subject, subject)
            return email.body

        email_id = None
        start = time.time()
        inbox = poplib.POP3_SSL('pop.gmail.com')
        try:
            inbox.user(test_email)
            inbox.pass_(os.environ.get('EMAIL_PASSWORD'))
            while time.time() - start < 60:
                # obtém as 10 mensagens mais recentes
                count, _ = inbox.stat()
                for i in reversed(range(max(1, count - 10), count + 1)):
                    print('getting msg', i)
                    _, lines, _ = inbox.retr(i)
                    lines = [l.decode('utf-8') for l in lines]
                    print(lines)
                    if f'Subject: {subject}' in lines:
                        email_id = i
                        body = '\n'.join(lines)
                        return body
        finally:
            if email_id:
                inbox.dele(email_id)
            inbox.quit()

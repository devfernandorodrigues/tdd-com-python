from unittest import skip
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils.html import escape
from lists.forms import ExistingListItemForm
from lists.forms import DUPLICATE_ITEM_ERROR
from lists.forms import EMPTY_ITEM_ERROR
from lists.forms import ItemForm
from lists.models import Item, List


User = get_user_model()

class HomePageTest(TestCase):

    def test_uses_home_template(self):
        response = self.client.get('/')

        self.assertTemplateUsed(response, 'home.html')

    def test_home_page_uses_item_form(self):
        response = self.client.get('/')

        self.assertIsInstance(response.context["form"], ItemForm)

class ListViewTests(TestCase):

    def post_invalid_input(self):
        list_ = List.objects.create()

        return self.client.post(
            f'/lists/{list_.id}/',
            data={'text': ''}
        )

    def test_uses_list_template(self):
        list_ = List.objects.create()
        response = self.client.get(f'/lists/{list_.id}/')

        self.assertTemplateUsed(response, 'list.html')


    def test_passes_correct_list_to_template(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()

        response = self.client.get(f'/lists/{correct_list.id}/')

        self.assertEqual(response.context['list'], correct_list)

    def test_can_save_a_POST_request_to_an_existing_list(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()

        self.client.post(
            f'/lists/{correct_list.id}/',
            data={'text': 'A new item for an existing list'}
        )

        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, 'A new item for an existing list')
        self.assertEqual(new_item.list, correct_list)

    def test_POST_redirects_to_list_view(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()

        response = self.client.post(
            f'/lists/{correct_list.id}/',
            data={'text': 'A new item for an existing list'}
        )

        self.assertRedirects(response, f'/lists/{correct_list.id}/')

    def test_validation_errors_end_up_on_lists_page(self):
        list_ = List.objects.create()

        response = self.client.post(
            f'/lists/{list_.id}/',
            data={'text': ''}
        )

        expected_error = escape("You can't have an empty list item")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'list.html')
        self.assertContains(response, expected_error)

    def test_displays_item_form(self):
        list_ = List.objects.create()

        response = self.client.get(f'/lists/{list_.id}/')

        self.assertIsInstance(response.context["form"], ExistingListItemForm)
        self.assertContains(response, 'name="text')

    def test_for_invalid_input_nohting_saved_to_db(self):
        self.post_invalid_input()

        self.assertEqual(Item.objects.count(), 0)

    def test_for_invalid_input_renders_list_template(self):
        response = self.post_invalid_input()

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'list.html')

    def test_for_invalid_input_passes_form_to_template(self):
        response = self.post_invalid_input()

        self.assertIsInstance(response.context["form"], ExistingListItemForm)

    def test_for_invalid_input_shows_error_on_page(self):
        response = self.post_invalid_input()

        self.assertContains(response, escape(EMPTY_ITEM_ERROR))

    def test_duplicate_item_validation_errors_end_up_on_list_pages(self):
        list1 = List.objects.create()
        item1 = Item.objects.create(list=list1, text='textey')

        response = self.client.post(
            f'/lists/{list1.id}/',
            data={'text': 'textey'}
        )

        expected_error = escape(DUPLICATE_ITEM_ERROR)
        self.assertContains(response, expected_error)
        self.assertTemplateUsed(response, 'list.html')
        self.assertEqual(Item.objects.count(), 1)

class NewListTestCase(TestCase):
    def test_can_save_a_POST_request(self):
        self.client.post('/lists/new', data={'text': 'A new list item'})

        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, 'A new list item')


    def test_redirects_after_POST(self):
        response = self.client.post('/lists/new', data={'text': 'A new list item'})

        new_list = List.objects.first()

        self.assertRedirects(response, f'/lists/{new_list.id}/')


    def test_invalid_list_items_arent_saved(self):
        self.client.post('/lists/new', data={'text': ''})

        self.assertEqual(List.objects.count(), 0)
        self.assertEqual(Item.objects.count(), 0)

    def test_for_invalid_input_renders_home_template(self):
        response = self.client.post('/lists/new', data={'text': ''})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_validation_errors_are_shown_on_home_page(self):
        response = self.client.post('/lists/new', data={'text': ''})

        self.assertContains(response, escape(EMPTY_ITEM_ERROR))

    def test_for_invalid_input_passes_form_to_template(self):
        response = self.client.post('/lists/new', data={'text': ''})

        self.assertIsInstance(response.context['form'], ItemForm)

    def test_list_owner_is_saved_if_user_is_authenticated(self):
        user = User.objects.create(email='a@b.com')
        self.client.force_login(user)

        self.client.post('/lists/new', data={'text': 'new item'})

        list_ = List.objects.first()
        self.assertEqual(list_.owner, user)

    def test_list_owner_is_saved_if_user_is_not_authenticated(self):
        self.client.post('/lists/new', data={'text': 'new item'})

        list_ = List.objects.first()
        self.assertEqual(list_.owner, None)

class MyListsTest(TestCase):

    def test_my_lists_url_renders_my_lists_template(self):
        User.objects.create(email='a@b.com')

        response = self.client.get('/lists/users/a@b.com/')

        self.assertTemplateUsed(response, 'my_lists.html')

    def test_passes_correct_owner_to_template(self):
        User.objects.create(email='wrong@owner.com')
        correct_user = User.objects.create(email='a@b.com')

        response = self.client.get('/lists/users/a@b.com/')

        self.assertEqual(response.context['owner'], correct_user)


class ShareList(TestCase):

    def test_redirects_after_POST(self):
        list_ = List.objects.create()

        response = self.client.post(f'/lists/{list_.id}/share', data={
            'sharee': 'a@b.com',
        })

        self.assertRedirects(response, f'/lists/{list_.id}/')

    def test_add_users_on_share(self):
        list_ = List.objects.create()

        self.client.post(f'/lists/{list_.id}/share', data={
            'sharee': 'a@b.com',
        })

        list_.refresh_from_db()
        self.assertEqual(list_.shared_with.count(), 1)



    def test_uses_form_to_valid_data(self):
        list_ = List.objects.create()

        self.client.post(f'/lists/{list_.id}/share', data={
            'sharee': 'wrongemail',
        })

        list_.refresh_from_db()
        self.assertEqual(list_.shared_with.count(), 0)

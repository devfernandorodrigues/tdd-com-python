from django.test import TestCase

from lists.forms import DUPLICATE_ITEM_ERROR
from lists.forms import EMPTY_ITEM_ERROR
from lists.models import List, Item


class ListAPITest(TestCase):
    base_url = '/api/lists'

    def post_empty_input(self):
        list_ = List.objects.create()
        return self.client.post(
            f"{self.base_url}/{list_.id}/"
        )

    def test_get_returns_json_200(self):
        list_ = List.objects.create()

        response = self.client.get(f'{self.base_url}/{list_.id}/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/json')

    def test_get_returns_items_for_correct_list(self):
        other_list = List.objects.create()
        Item.objects.create(list=other_list, text='item1')
        our_list = List.objects.create()
        item1 = Item.objects.create(list=our_list, text='item 1')
        item2 = Item.objects.create(list=our_list, text='item 2')

        response = self.client.get(f'{self.base_url}/{our_list.id}/')

        self.assertEqual(
            response.json(),
            [
                {'id': item1.id, 'text': item1.text},
                {'id': item2.id, 'text': item2.text}
            ]
        )

    def test_POSTing_a_new_item(self):
        list_ = List.objects.create()

        response = self.client.post(
            f"{self.base_url}/{list_.id}/",
            {'text': 'new item'}
        )

        new_item = list_.item_set.first()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(new_item.text, 'new item')



    def test_for_invalid_input_nothing_saved_to_db(self):
        self.post_empty_input()
        self.assertEqual(Item.objects.count(), 0)

    def test_for_invalid_input_returns_error_code(self):
        response = self.post_empty_input()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": EMPTY_ITEM_ERROR})

    def test_duplicate_items_error(self):
        list_ = List.objects.create()

        self.client.post(
            f"{self.base_url}/{list_.id}/",
            data={"text": "thing"}
        )
        response = self.client.post(
            f"{self.base_url}/{list_.id}/",
            data={"text": "thing"}
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": DUPLICATE_ITEM_ERROR})


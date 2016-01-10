import django
django.setup()

import unittest
from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from nose.tools import raises
from restapi.models import Chat

class ChatTests(APITestCase):
    def test_create_message(self):
        """
        Ensure we can create a new chat message
        """
        url = reverse('create_message')
        data = {"username": "kiran",
               "text": "This is a test message",
               "timeout": 300}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertGreaterEqual(Chat.objects.count(), 1)
        pk = response.data['id']
        self.assertEqual(Chat.objects.get(id=pk).username, 'kiran')


    def test_create_message_invalid_timeout(self):
        """
        Ensure we fail if we pass invalid data
        """
        url = reverse('create_message')
        data = {"username": "kiran",
               "text": "This is a test message",
               "timeout": ''}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_long_message_(self):
        """
        Ensure we fail if we pass message > 512
        """
        msg = "blah "*150
        url = reverse('create_message')
        data = {"username": "kiran",
               "text": msg,
               "timeout": 90}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.data['text'],
                         ['Ensure this field has no more than 512 characters.'])

    def test_get_message(self):
        """
        If we create a message, get the Id and do a get request,
        ensure we get the text message we just passed.
        """
        url = reverse('create_message')
        data = {"username": "kiran",
               "text": "This is a test message",
               "timeout": 300}
        test_response = self.client.post(url, data, format='json')
        pk = test_response.data['id']
        response = self.client.get('/chat/%s' %(pk))
        self.assertEqual(response.data['text'], "This is a test message")


    @raises(AssertionError)
    def test_get_invalid_message(self):
        """
        Raise error if chatId doesn't exist
        """
        response = self.client.get('/chat/999')
        self.assertEqual(response.data, {
            "username": "kiran",
            "text": "Redis 1",
            "expiration_date": "2016-01-10 01:12:49"
        })

    def test_get_user_message(self):
        """
        Ensure we can get all messages for a given user
        """
        url = reverse('create_message')
        data = {"username": "kiran",
               "text": "This is a test message",
               "timeout": 300}
        self.client.post(url, data, format='json')
        response = self.client.get('/chats/kiran')
        self.assertEqual(dict(response.data[-1])['text'], "This is a test message")

if __name__ == '__main__':
    unittest.main()

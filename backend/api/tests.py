from rest_framework import status
from rest_framework.test import APITestCase

from .models import Document


class ApiTests(APITestCase):
    def test_hello_endpoint(self):
        response = self.client.get('/api/hello/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            {'message': 'Olá do backend Django! A comunicação está funcionando.'},
        )

    def test_document_crud(self):
        create_response = self.client.post(
            '/api/documents/',
            {'title': 'Guia interno', 'content': 'Conteúdo inicial'},
            format='json',
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        document_id = create_response.data['id']

        update_response = self.client.patch(
            f'/api/documents/{document_id}/',
            {'title': 'Guia atualizado'},
            format='json',
        )

        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_response.data['title'], 'Guia atualizado')

        delete_response = self.client.delete(f'/api/documents/{document_id}/')

        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Document.objects.filter(id=document_id).exists())

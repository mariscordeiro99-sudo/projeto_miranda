from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets

from .models import Document
from .serializers import DocumentSerializer


class HelloView(APIView):
    def get(self, request):
        return Response({
            'message': 'Olá do backend Django! A comunicação está funcionando.',
        })


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

from rest_framework.views import APIView
from rest_framework.response import Response


class HelloView(APIView):
    def get(self, request):
        return Response({
            'message': 'Olá do backend Django! A comunicação está funcionando.',
        })

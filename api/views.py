from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from api.components.element_location import process_data

def index(request):
    return HttpResponse("API Endpoint")

class ElementLocation(APIView):
    """
    View to return element location based on grid and element coordinates.
    """

    def get(self, request, format=None):
        """
        Return a list of
        """
        if not request.content_type == 'application/json':
            return Response({'error': 'Request must contain JSON data'}, status=status.HTTP_400_BAD_REQUEST)

        processed_data = process_data(request.data)
        
        return Response({"elements": [[x[0][0], x[1], x[2][0]] for x in processed_data]}, status=status.HTTP_200_OK)
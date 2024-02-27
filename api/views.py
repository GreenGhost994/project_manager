from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from api.components.element_location import process_data
from management.models import Element, Project
from management.serializers import ElementSerializer, ProjectSerializer

def index(request):
    return HttpResponse("API Endpoint")

class ElementLocation(APIView):
    """
    Endpoint to return element location based on grid and element coordinates.
    """

    def get(self, request, format=None):
        """
        Return a list of elements with axis zone based of building grid.
        """
        if not request.content_type == 'application/json':
            return Response({'error': 'Request must contain JSON data'}, status=status.HTTP_400_BAD_REQUEST)

        processed_data = process_data(request.data)
        
        return Response({"elements": [[x[0][0], x[1], x[2][0]] for x in processed_data]}, status=status.HTTP_200_OK)
    

class ElementInstance(APIView):
    """
    Endpoint to create or update element.
    """
    def post(self, request, format=None):
        data = request.data
        elements_data = data.get('elements', [])
        project_index = data.get('index')

        try:
            project = Project.objects.get(index=project_index)
        except Project.DoesNotExist:
            project_serializer = ProjectSerializer(data={'index': project_index})
            if project_serializer.is_valid():
                project = project_serializer.save()
            else:
                return Response(project_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        for element_data in elements_data:
            element_identify = {
                "element_name": element_data["element_name"],
                "coord_x": element_data["coord_x"],
                "coord_y": element_data["coord_y"],
                "coord_z": element_data["coord_z"],
                "rotation": element_data["rotation"],
                "project": project.id
            }
            try:
                element = Element.objects.get(**element_identify)
                for key, value in element_data.items():
                    setattr(element, key, value)
                element.save()
            except Element.DoesNotExist:
                element_serializer = ElementSerializer(data=element_identify)
                if element_serializer.is_valid():
                    element, created = Element.objects.update_or_create(
                        project=project,
                        element_name=element_data['element_name'],
                        defaults=element_data
                    )
                else:
                    return Response(element_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': 'Elements created/updated successfully'}, status=status.HTTP_201_CREATED)
    
    """
    Endpoint to delete element.
    """
    def delete(self, request, format=None):
        data = request.data
        elements_data = data.get('elements', [])
        project_index = data.get('index')

        try:
            project = Project.objects.get(index=project_index)
        except Project.DoesNotExist:
            project_serializer = ProjectSerializer(data={'index': project_index})
            if project_serializer.is_valid():
                project = project_serializer.save()
            else:
                return Response(project_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        for element_data in elements_data:
            element_identify = {
                "element_name": element_data["element_name"],
                "coord_x": element_data["coord_x"],
                "coord_y": element_data["coord_y"],
                "coord_z": element_data["coord_z"],
                "rotation": element_data["rotation"],
                "project": project.id
            }
            try:
                element = Element.objects.get(**element_identify)
                element.delete()
                return Response({'message': 'Element deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
            except Element.DoesNotExist:
                return Response({'error': 'Element does not exist'}, status=status.HTTP_404_NOT_FOUND)
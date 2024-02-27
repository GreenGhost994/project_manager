import unittest
from datetime import datetime
import os
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assembly_manager.settings')
import django
django.setup()

from rest_framework.test import APIClient
from rest_framework import status
from management.models import Element, Project


class Test_ElementInstance(unittest.TestCase):
    def setUp(self):
        self.client = APIClient()
        self.project_index = 'ABCD'
        self.elements_data = [{
            "element_name": "W_123",
            "coord_x": 123,
            "coord_y": 223,
            "coord_z": 124,
            "rotation": 90,
            "assembly_status": True
        }]

    def test_element_instance(self):
        # Create instance
        response = self.client.post('/api/element_instance/', {
            'elements': self.elements_data,
            'index': self.project_index
        }, format='json')
        self.assertTrue(Project.objects.filter(index=self.project_index).exists())


        self.assertTrue(Element.objects.filter(
            element_name=self.elements_data[0]['element_name']
        ).exists())


        # Modify instance
        updated_assembly_date = datetime.strptime('2024-02-01', '%Y-%m-%d').date()
        self.elements_data[0]['assembly_date'] = updated_assembly_date

        response = self.client.post('/api/element_instance/', {
            'elements': self.elements_data,
            'index': self.project_index
        }, format='json')
        self.assertEqual(response.status_code, 201)
        element = Element.objects.get(element_name=self.elements_data[0]['element_name'])
        self.assertEqual(element.assembly_date, updated_assembly_date)

        # Delete instance
        del self.elements_data[0]['assembly_status']
        response = self.client.delete('/api/element_instance/', {
            'elements': self.elements_data,
            'index': self.project_index
        }, format='json')

        self.assertFalse(Element.objects.filter(
            element_name=self.elements_data[0]['element_name']
        ).exists())
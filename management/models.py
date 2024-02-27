from django.db import models


class Project(models.Model):
    id = models.AutoField(primary_key=True)
    index = models.CharField(max_length=100)
    name = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"[{self.id}] {self.index} - {self.name}"


class Element(models.Model):
    id = models.AutoField(primary_key=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    element_name = models.CharField(max_length=255)
    coord_x = models.FloatField(null=True, blank=True)
    coord_y = models.FloatField(null=True, blank=True)
    coord_z = models.FloatField(null=True, blank=True)
    rotation = models.FloatField(null=True, blank=True)
    production_date = models.DateField(null=True, blank=True)
    production_status = models.CharField(max_length=100, null=True, blank=True)
    transport_date = models.DateField(null=True, blank=True)
    transport_status = models.CharField(max_length=100, null=True, blank=True)
    planned_assembly_date = models.DateField(null=True, blank=True)
    assembly_date = models.DateField(null=True, blank=True)
    assembly_status = models.CharField(max_length=100, null=True, blank=True)
    created_by = models.CharField(max_length=100, null=True, blank=True)
    modified_by = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.element_name} ({self.id})"


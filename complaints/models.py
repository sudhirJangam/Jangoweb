from django.db import models


class Complaints(models.Model):
    complaintId=models.IntegerField(blank=False)
    company = models.CharField (max_length=50)
    product  = models.CharField(max_length= 50)
    subproduct = models.CharField(max_length=50)
    issue = models.CharField(max_length=50)
    subIssue = models.CharField(max_length=50)
    repoDt = models.DateField(blank=False)
    complaint = models.TextField(blank=False)
    cluster = models.IntegerField(blank=False)


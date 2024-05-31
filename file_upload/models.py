
from django.db import models

class UploadFile(models.Model):
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class UploadedData(models.Model):
    date = models.DateField()
    acc_no = models.CharField(max_length=50)
    cust_state = models.CharField(max_length=50)
    cust_pin = models.CharField(max_length=6)
    dpd = models.IntegerField()

    def __str__(self):
        return self.acc_no

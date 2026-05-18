from django.db import models

class Medicine(models.Model):
    name = models.CharField(max_length=100)
    batch_number = models.CharField(max_length=50)
    supplier = models.CharField(max_length=100)
    quantity = models.IntegerField()
    minimum_stock = models.IntegerField(default=10)  # alert if below this
    expiry_date = models.DateField()
    added_at = models.DateTimeField(auto_now_add=True)

    @property
    def is_low_stock(self):
        return self.quantity < self.minimum_stock

    def __str__(self):
        return f"{self.name} (Qty: {self.quantity})"


class Prescription(models.Model):
    resident = models.ForeignKey('residents.ResidentProfile', on_delete=models.CASCADE, related_name='prescriptions')
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    dosage = models.CharField(max_length=50)       # e.g. "1 tablet"
    frequency = models.CharField(max_length=50)    # e.g. "twice a day"
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    prescribed_by = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.medicine.name} for {self.resident.full_name}"
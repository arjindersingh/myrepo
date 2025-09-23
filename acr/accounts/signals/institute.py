from django.db.models.signals import post_migrate
from django.dispatch import receiver
from accounts.models.institute import Institute  # Adjust import based on your app structure
import logging

logger = logging.getLogger(__name__)

@receiver(post_migrate)
def populate_institutes(sender, **kwargs):
    if sender.name == "accounts":  # Ensure it runs only for the 'accounts' app
        institute_data = [
            {
                "institute_name": "Bowry Memorial Educational and Medical Trust",
                "short_name": "BMEMT",
                "address": "Green Model Town, Jalandhar",
                "pincode": "144003",
                "phone": "0181-XXX-XXXX",
                "email": "bmemt@innocenthearts.in",
            },
            {
                "institute_name": "Innocent Hearts School",
                "short_name": "IHS GMT",
                "address": "Green Model Town, Jalandhar",
                "pincode": "144003",
                "phone": "0181-XXX-XXXX",
                "email": "gmt@innocenthearts.in",
            },
            {
                "institute_name": "Innocent Hearts School",
                "short_name": "IHS Loharan",
                "address": "Loharan, Jalandhar",
                "pincode": "144002",
                "phone": "0181-XXX-XXXX",
                "email": "loharan@innocenthearts.in",
            },
            {
                "institute_name": "Innocent Hearts School",
                "short_name": "IHS CJR",
                "address": "Cantt-Jandiala Road, Jalandhar",
                "pincode": "144004",
                "phone": "0181-XXX-XXXX",
                "email": "cantt@innocenthearts.in",
            },
            {
                "institute_name": "Innocent Hearts School",
                "short_name": "IHS Kapurthala",
                "address": "Kapurthala Road, Jalandhar",
                "pincode": "144005",
                "phone": "0181-XXX-XXXX",
                "email": "kapurthala@innocenthearts.in",
            },
            {
                "institute_name": "Innocent Hearts School",
                "short_name": "IHS Noorpur",
                "address": "Noorpur, Jalandhar",
                "pincode": "144006",
                "phone": "0181-XXX-XXXX",
                "email": "noorpur@innocenthearts.in",
            },
        ]

        for data in institute_data:
            obj, created = Institute.objects.update_or_create(
                institute_name=data["institute_name"],  # Ensuring the record is updated if found
                short_name=data["short_name"],  # Ensuring uniqueness
                defaults={
                    "address": data["address"],
                    "pincode": data["pincode"],
                    "phone": data["phone"],
                    "email": data["email"],
                }
            )
            if created:
                logger.info(f"Added new institute: {data['short_name']}")
            else:
                logger.info(f"Updated existing institute: {data['short_name']}")

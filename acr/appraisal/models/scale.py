from django.db import models
from django.db.models import Max

class Scale(models.Model):
    """A scale consisting of multiple dimensions and an overall remark."""
    name = models.CharField(max_length=30, unique=True, verbose_name="Scale Name")
    description = models.TextField(blank=True, verbose_name="Scale Description")
    
    """     def get_items_with_options(self, scale_id):
        ""Returns all items under the specified scale along with their associated dimensions and options.""
        data = {}
        items = self.items.filter(scale_id=scale_id)  # Get items linked to the given scale
        
        for item in items:
            dimension_name = item.dimension.name if item.dimension else "Uncategorized"
            option_set = item.option_set  # Get OptionSet for the item
            options = option_set.options.all() if option_set else []
            
            if dimension_name not in data:
                data[dimension_name] = []  # Initialize a list for this dimension
            
            data[dimension_name].append({
                "item_id": item.id,
                "item_statement": item.statement,
                "options": [{"text": opt.text, "value": opt.value} for opt in options]
            }) """
        
        #return data  # Returns a dictionary grouped by dimension

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Scale"
        verbose_name_plural = "Scales"


class OptionSet(models.Model):
    """A collection of options assigned to an item."""
    name = models.CharField(max_length=30, verbose_name="Option Set Name")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Option Set"
        verbose_name_plural = "Option Sets"

class Option(models.Model):
    """Options within an option set, each having a value and text."""
    option_set = models.ForeignKey(OptionSet, on_delete=models.CASCADE, related_name="options")
    text = models.CharField(max_length=100, verbose_name="Option Text")
    value = models.IntegerField(verbose_name="Option Value")

    def __str__(self):
        return f"{self.option_set.name} - {self.text} ({self.value})"

    class Meta:
        verbose_name = "Option"
        verbose_name_plural = "Options"
        ordering = ["option_set", "value"]

class Item(models.Model):
    """An item within a scale, linked to an option set."""
    scale = models.ForeignKey(Scale, on_delete=models.CASCADE, related_name="items")  # One-to-many relationship
    statement = models.TextField(verbose_name="Item Question", default="Default item question.")
    option_set = models.ForeignKey(OptionSet, on_delete=models.CASCADE, related_name="items")  # Many-to-one with OptionSet

    def __str__(self):
        return f"{self.dimension.name} - {self.statement[:30]}"

    class Meta:
        verbose_name = "Item"
        verbose_name_plural = "Items"
    @property
    def max_option_value(self):
        """Return maximum option value for this item."""
        return self.option_set.options.aggregate(Max("value"))["value__max"]
    @classmethod
    def get_max_value_of_option(cls, item_id):
        """Returns the maximum option value for the given item."""
        try:
            item = cls.objects.get(id=item_id)
            max_option = item.option_set.options.order_by("-value").first()
            return max_option.value if max_option else None
        except cls.DoesNotExist:
            return None  # Return None if the item does not exist
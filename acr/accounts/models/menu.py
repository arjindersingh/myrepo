from django.db import models
from django.contrib.auth.models import Group, User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse
from django.core.exceptions import ImproperlyConfigured

class Menu(models.Model):
    """Model to store menu items for a dynamic navigation system."""
    
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE,
        related_name="submenus", verbose_name="Parent Menu",
        help_text="Select a parent menu for submenus (leave blank for main menus)."
    )
    Command_No = models.PositiveSmallIntegerField(
        default=100,
        validators=[
            MinValueValidator(100, message="The Command Number must be between 100 and 999."),
            MaxValueValidator(999, message="The Command Number must be between 100 and 999."),
        ],
        verbose_name="Command Number",
        help_text="A unique three-digit identifier for this command."
    )
    Command_Depth = models.PositiveSmallIntegerField(
        default=1,
        validators=[
            MinValueValidator(1, message="The Command Depth must be between 1 and 9."),
            MaxValueValidator(9, message="The Command Depth must be between 1 and 9."),
        ],
        verbose_name="Command Depth",
        help_text="Defines the depth level in the hierarchy (1 for top-level menus)."
    )
    Command_Sequence = models.PositiveSmallIntegerField(
        default=1,
        validators=[
            MinValueValidator(1, message="The Command Sequence must be between 1 and 9."),
            MaxValueValidator(9, message="The Command Sequence must be between 1 and 9."),
        ],
        verbose_name="Command Sequence",
        help_text="Defines the order of display at the same level."
    )
    UrlPath = models.CharField(
        max_length=200,
        unique=True,
        verbose_name="Command URL Path",
        help_text="Unique URL path for this command."
    )
    UrlName = models.CharField(
        max_length=200,
        unique=True,
        verbose_name="URL Name",
        help_text="Enter the Django URL name used for reversing."
    )
    Display_Menu_Text = models.CharField(
        max_length=50,
        verbose_name="Menu Display Text",
        help_text="Text displayed in the menu.",
        default="Menu Name"
    )
    icon_class = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Icon Class",
        help_text="CSS class for menu icons (e.g., Bootstrap icons)."
    )
    default_permission = models.BooleanField(
        default=True,
        verbose_name="Is Active",
        help_text="Assign default menu permission to group."
    )
    default_display = models.BooleanField(
        default=True,
        verbose_name="Dsiplay in Menu list",
        help_text="Whether to display menu item in Menu permission Assignment."
    )
    @classmethod
    def get_menus_with_display_permission(cls):
        """Returns all menu items where default_display is True, ordered by ID."""
        return cls.objects.filter(default_display=True).order_by("id")
    class Meta:
        ordering = ["Command_Depth", "Command_Sequence"]
        verbose_name = "Menu"
        verbose_name_plural = "Menus"

    def __str__(self):
        """Return menu item with hierarchical structure."""
        return f"{'—' * (self.Command_Depth - 1)} {self.Display_Menu_Text}"

    def get_absolute_url(self):
        """Returns the URL for this menu item, handling required parameters."""
        try:
            if '<int:pk>' in self.UrlPath:  # Check if the URL pattern expects 'pk'
                return reverse(self.UrlName, kwargs={'pk': 1})  # Provide a dummy pk
            return reverse(self.UrlName)
        except Exception as e:
            raise ImproperlyConfigured(f"Error generating URL for {self.UrlName}: {e}")

    def get_submenus(self):
        """Returns active submenus for this menu item."""
        return self.submenus.filter(is_active=True).order_by("Command_Sequence")


class UserGroupMenuPermission(models.Model): 
    """Defines which user groups have access to which menu items."""
    
    group = models.ForeignKey(
        Group, on_delete=models.CASCADE,
        verbose_name="User Group",
        help_text="Select the user group."
    )
    menu = models.ForeignKey(
        Menu, on_delete=models.CASCADE,
        verbose_name="Menu Item",
        help_text="Select the menu item the group can access."
    )
    can_access = models.BooleanField(
        default=True,
        verbose_name="Has Access",
        help_text="Determines if the group can access this menu."
    )
    
    class Meta:
        unique_together = ("group", "menu")  # ✅ Prevents duplicate entries
        verbose_name = "User Group Menu Permission"
        verbose_name_plural = "User Group Menu Permissions"

    def __str__(self):
        return f"{self.group.name} → {self.menu.Display_Menu_Text}"

class UserMenuPermission(models.Model): 
    """Defines which user groups have access to which menu items."""
    
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name="User ",
        help_text="Select the user."
    )
    menu = models.ForeignKey(
        Menu, on_delete=models.CASCADE,
        verbose_name="Menu Item",
        help_text="Select the menu item the User can access."
    )
    can_access = models.BooleanField(
        default=True,
        verbose_name="Has Access",
        help_text="Determines if the User can access this menu."
    )
    
    class Meta:
        unique_together = ("user", "menu")  # ✅ Prevents duplicate entries
        verbose_name = "User Menu Permission"
        verbose_name_plural = "User Menu Permissions"

    def __str__(self):
        return f"{self.user.name} → {self.menu.Display_Menu_Text}"

from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin, GroupAdmin as BaseGroupAdmin
from unfold.admin import ModelAdmin, StackedInline
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
from unfold.decorators import display
from unfold.contrib.filters.admin import ChoicesDropdownFilter, DropdownFilter
from .models import UserProfile

admin.site.unregister(User)
admin.site.unregister(Group)


class UserProfileInline(StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Officer Security Profile'
    tab = True
    fields = ('role', 'badge_number', 'sector_assignment', 'phone')


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    inlines = (UserProfileInline,)
    
    list_display = ('username', 'get_officer_name', 'get_role_badge', 'get_badge_number', 'get_sector', 'is_active', 'is_staff')
    list_filter = ('is_active', 'is_staff', 'is_superuser', ('profile__role', ChoicesDropdownFilter))
    search_fields = ('username', 'first_name', 'last_name', 'email', 'profile__badge_number', 'profile__sector_assignment')
    ordering = ('username',)

    @display(description='Officer Name')
    def get_officer_name(self, obj):
        full_name = obj.get_full_name()
        return full_name if full_name else '—'

    @display(
        description='Role',
        label={
            'ADMIN': 'danger',
            'OFFICER': 'info',
        }
    )
    def get_role_badge(self, obj):
        if hasattr(obj, 'profile'):
            return obj.profile.role
        return 'OFFICER'

    @display(description='Badge Number')
    def get_badge_number(self, obj):
        if hasattr(obj, 'profile'):
            return obj.profile.badge_number
        return '—'

    @display(description='Sector Assignment')
    def get_sector(self, obj):
        if hasattr(obj, 'profile'):
            return obj.profile.sector_assignment
        return '—'


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass


@admin.register(UserProfile)
class UserProfileAdmin(ModelAdmin):
    list_display = ('user', 'get_role_badge', 'badge_number', 'sector_assignment', 'phone', 'created_at')
    list_filter = (('role', ChoicesDropdownFilter),)
    search_fields = ('user__username', 'badge_number', 'sector_assignment', 'phone')
    ordering = ('-created_at',)

    @display(
        description='Operational Role',
        label={
            'ADMIN': 'danger',
            'OFFICER': 'info',
        }
    )
    def get_role_badge(self, obj):
        return obj.role

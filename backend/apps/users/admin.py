"""
Admin configuration for Users app.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import User, UserProfile, UserSettings, Subscription, Achievement, UserAchievement


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User admin with extended fields."""
    
    list_display = [
        'username', 'email', 'full_name', 'current_level', 
        'xp_points', 'streak_days', 'is_active', 'is_staff', 'date_joined'
    ]
    list_filter = [
        'is_staff', 'is_superuser', 'is_active', 
        'current_level', 'date_joined'
    ]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-date_joined']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        (_('Learning Progress'), {
            'fields': (
                'current_level', 'xp_points', 'streak_days', 
                'longest_streak', 'last_study_date'
            )
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (_('Learning Progress'), {
            'fields': ('current_level',)
        }),
    )
    
    readonly_fields = ['xp_points', 'streak_days', 'longest_streak', 'last_study_date']
    
    def full_name(self, obj):
        return obj.get_full_name() or '-'
    full_name.short_description = 'Họ tên'


class UserProfileInline(admin.StackedInline):
    """Inline for UserProfile in User admin."""
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'


class UserSettingsInline(admin.StackedInline):
    """Inline for UserSettings in User admin."""
    model = UserSettings
    can_delete = False
    verbose_name_plural = 'Settings'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin for UserProfile."""
    
    list_display = ['user', 'country', 'city', 'onboarding_completed', 'created_at']
    list_filter = ['onboarding_completed', 'country', 'created_at']
    search_fields = ['user__username', 'user__email', 'bio']
    raw_id_fields = ['user']


@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    """Admin for UserSettings."""
    
    list_display = [
        'user', 'email_notifications', 'push_notifications',
        'study_reminders', 'dark_mode', 'updated_at'
    ]
    list_filter = [
        'email_notifications', 'push_notifications',
        'sound_effects', 'dark_mode'
    ]
    search_fields = ['user__username', 'user__email']
    raw_id_fields = ['user']


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Admin for Subscription."""
    
    list_display = [
        'user', 'plan', 'status', 'starts_at', 'expires_at', 
        'is_auto_renew', 'is_active_display'
    ]
    list_filter = ['plan', 'status', 'is_auto_renew', 'starts_at']
    search_fields = ['user__username', 'user__email']
    raw_id_fields = ['user']
    date_hierarchy = 'starts_at'
    
    def is_active_display(self, obj):
        return obj.is_active
    is_active_display.boolean = True
    is_active_display.short_description = 'Đang hoạt động'


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    """Admin for Achievement."""
    
    list_display = [
        'name', 'category', 'xp_reward', 'is_secret', 
        'is_active', 'order', 'created_at'
    ]
    list_filter = ['category', 'is_secret', 'is_active']
    search_fields = ['name', 'description', 'code']
    prepopulated_fields = {'code': ('name',)}
    ordering = ['category', 'order', 'name']
    
    fieldsets = (
        (None, {
            'fields': ('name', 'code', 'description', 'icon')
        }),
        (_('Requirements'), {
            'fields': ('category', 'requirement_type', 'requirement_value', 'requirement_config')
        }),
        (_('Rewards'), {
            'fields': ('xp_reward', 'badge_image')
        }),
        (_('Settings'), {
            'fields': ('is_secret', 'is_active', 'order')
        }),
    )


@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    """Admin for UserAchievement."""
    
    list_display = ['user', 'achievement', 'progress_percent', 'is_unlocked', 'unlocked_at']
    list_filter = ['is_unlocked', 'unlocked_at', 'achievement__category']
    search_fields = ['user__username', 'achievement__name']
    raw_id_fields = ['user', 'achievement']
    date_hierarchy = 'unlocked_at'
    
    def progress_percent(self, obj):
        return f"{obj.progress}%"
    progress_percent.short_description = 'Tiến độ'

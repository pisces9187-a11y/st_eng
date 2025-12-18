# 🎵 AUDIO VERSIONING SYSTEM - Technical Design

**Ngày tạo:** 17/12/2025  
**Mục đích:** Giải quyết vấn đề không thể quay lại audio cũ và quản lý phiên bản audio theo thời gian

---

## 🎯 PROBLEM STATEMENT

### Vấn đề hiện tại:
```
❌ Upload audio native ngày 15/12 → Xóa test TTS → KHÔNG thể quay lại audio 15/12
❌ Không biết đang dùng audio phiên bản nào
❌ Không so sánh được chất lượng giữa các version
❌ Rủi ro mất dữ liệu khi tạo lại audio
```

### Solution:
```
✅ Mọi audio đều có version number
✅ Có thể activate/deactivate version bất kỳ
✅ Track history đầy đủ (who, when, why)
✅ Compare versions side-by-side
✅ A/B testing support
```

---

## 📊 DATABASE DESIGN

### 1. New Model: AudioVersion

```python
# backend/apps/curriculum/models.py

class AudioVersion(models.Model):
    """
    Tracks all versions of audio for a phoneme over time.
    
    Example:
        Phoneme /p/:
        - Version 1: Native audio (ngày 15/12) - ACTIVE
        - Version 2: TTS test (ngày 17/12) - INACTIVE
        - Version 3: Native improved (ngày 20/12) - INACTIVE
        
    Use case:
        # Activate version 2
        v2 = AudioVersion.objects.get(phoneme=p, version_number=2)
        v2.activate()  # v1 becomes inactive automatically
    """
    
    # Core fields
    phoneme = models.ForeignKey(
        Phoneme,
        on_delete=models.CASCADE,
        related_name='audio_versions',
        verbose_name='Âm vị'
    )
    
    audio_source = models.ForeignKey(
        AudioSource,
        on_delete=models.PROTECT,  # PROTECT: không xóa audio nếu có version
        related_name='versions',
        verbose_name='Audio Source'
    )
    
    # Version tracking
    version_number = models.PositiveIntegerField(
        verbose_name='Số phiên bản',
        help_text='Auto-increment cho mỗi phoneme'
    )
    
    # Activation status
    is_active = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name='Đang sử dụng',
        help_text='Chỉ có 1 version active cho mỗi phoneme'
    )
    
    # Time tracking
    effective_from = models.DateTimeField(
        default=timezone.now,
        verbose_name='Có hiệu lực từ',
        help_text='Thời điểm version này được activate'
    )
    
    effective_until = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Hết hiệu lực',
        help_text='Thời điểm version này bị deactivate (None = vẫn active)'
    )
    
    # Metadata
    uploaded_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_audio_versions',
        verbose_name='Người upload'
    )
    
    upload_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Ngày upload'
    )
    
    change_reason = models.TextField(
        blank=True,
        verbose_name='Lý do thay đổi',
        help_text='Ví dụ: "Giọng rõ hơn", "Fix background noise"'
    )
    
    # Analytics for A/B testing
    usage_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Số lần phát',
        help_text='Đếm số lần audio được phát'
    )
    
    avg_user_rating = models.FloatField(
        null=True,
        blank=True,
        verbose_name='Đánh giá TB',
        help_text='Rating trung bình từ users (1-5 sao)'
    )
    
    user_rating_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Số lượt đánh giá'
    )
    
    class Meta:
        db_table = 'curriculum_audio_version'
        ordering = ['phoneme', '-version_number']
        verbose_name = 'Audio Version'
        verbose_name_plural = 'Audio Versions'
        unique_together = [['phoneme', 'version_number']]
        indexes = [
            models.Index(fields=['phoneme', 'is_active']),
            models.Index(fields=['effective_from']),
            models.Index(fields=['-version_number']),
        ]
    
    def __str__(self):
        status = "✓ ACTIVE" if self.is_active else "✗ INACTIVE"
        return f"/{self.phoneme.ipa_symbol}/ v{self.version_number} ({status})"
    
    def save(self, *args, **kwargs):
        """Auto-increment version_number for phoneme"""
        if not self.version_number:
            last_version = AudioVersion.objects.filter(
                phoneme=self.phoneme
            ).aggregate(models.Max('version_number'))['version_number__max']
            
            self.version_number = (last_version or 0) + 1
        
        super().save(*args, **kwargs)
    
    def activate(self, user=None, reason=''):
        """
        Activate this version and deactivate all others for this phoneme.
        
        Args:
            user: User who activated (for audit trail)
            reason: Reason for activation
        
        Example:
            v2.activate(user=request.user, reason="Better quality")
        """
        from django.db import transaction
        
        with transaction.atomic():
            # Deactivate all other versions
            AudioVersion.objects.filter(
                phoneme=self.phoneme,
                is_active=True
            ).exclude(
                pk=self.pk
            ).update(
                is_active=False,
                effective_until=timezone.now()
            )
            
            # Activate this version
            self.is_active = True
            self.effective_from = timezone.now()
            self.effective_until = None
            
            if reason:
                self.change_reason = reason
            
            self.save(update_fields=[
                'is_active', 
                'effective_from', 
                'effective_until',
                'change_reason'
            ])
            
            # Update phoneme's preferred_audio_source
            self.phoneme.preferred_audio_source = self.audio_source
            self.phoneme.save(update_fields=['preferred_audio_source'])
    
    def get_duration_text(self):
        """Get human-readable duration"""
        if not self.effective_until:
            days = (timezone.now() - self.effective_from).days
            return f"Active for {days} days"
        else:
            days = (self.effective_until - self.effective_from).days
            return f"Was active for {days} days"
    
    def increment_usage(self):
        """Increment usage counter (called when audio is played)"""
        self.usage_count = models.F('usage_count') + 1
        self.save(update_fields=['usage_count'])
    
    def add_rating(self, rating):
        """
        Add user rating (1-5 stars).
        
        Args:
            rating: Integer 1-5
        """
        if not 1 <= rating <= 5:
            raise ValueError("Rating must be between 1 and 5")
        
        total = (self.avg_user_rating or 0) * self.user_rating_count
        total += rating
        self.user_rating_count += 1
        self.avg_user_rating = total / self.user_rating_count
        
        self.save(update_fields=['avg_user_rating', 'user_rating_count'])
```

### 2. Migration Strategy

```python
# backend/apps/curriculum/migrations/0XXX_add_audio_versioning.py

from django.db import migrations, models
import django.utils.timezone

def migrate_existing_audio_to_versions(apps, schema_editor):
    """
    Migrate existing AudioSource records to AudioVersion.
    Each AudioSource becomes Version 1 and is activated.
    """
    AudioSource = apps.get_model('curriculum', 'AudioSource')
    AudioVersion = apps.get_model('curriculum', 'AudioVersion')
    
    for audio in AudioSource.objects.all():
        # Create version 1 for this audio
        AudioVersion.objects.create(
            phoneme=audio.phoneme,
            audio_source=audio,
            version_number=1,
            is_active=True,
            effective_from=audio.created_at,
            change_reason='Migrated from existing AudioSource',
            usage_count=0
        )
    
    print(f"✅ Migrated {AudioSource.objects.count()} audio sources to versions")

class Migration(migrations.Migration):
    dependencies = [
        ('curriculum', '0XXX_previous_migration'),
    ]
    
    operations = [
        migrations.CreateModel(
            name='AudioVersion',
            fields=[
                ('id', models.BigAutoField(primary_key=True)),
                ('version_number', models.PositiveIntegerField()),
                ('is_active', models.BooleanField(default=False, db_index=True)),
                ('effective_from', models.DateTimeField(default=django.utils.timezone.now)),
                ('effective_until', models.DateTimeField(null=True, blank=True)),
                ('change_reason', models.TextField(blank=True)),
                ('usage_count', models.PositiveIntegerField(default=0)),
                ('avg_user_rating', models.FloatField(null=True, blank=True)),
                ('user_rating_count', models.PositiveIntegerField(default=0)),
                ('upload_date', models.DateTimeField(auto_now_add=True)),
                ('phoneme', models.ForeignKey(...)),
                ('audio_source', models.ForeignKey(...)),
                ('uploaded_by', models.ForeignKey(...)),
            ],
        ),
        migrations.RunPython(migrate_existing_audio_to_versions),
    ]
```

---

## 🎨 ADMIN INTERFACE

### Enhanced AudioVersionAdmin

```python
# backend/apps/curriculum/admin.py

from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.urls import reverse
from django.shortcuts import redirect

@admin.register(AudioVersion)
class AudioVersionAdmin(admin.ModelAdmin):
    """
    Admin interface for managing audio versions.
    
    Features:
    - View version history
    - Activate/deactivate versions
    - Compare versions side-by-side
    - A/B testing metrics
    """
    
    list_display = [
        'version_display',
        'phoneme_link',
        'audio_preview',
        'status_badge',
        'quality_badge',
        'usage_stats',
        'rating_display',
        'duration_text',
        'uploaded_info'
    ]
    
    list_filter = [
        'is_active',
        'audio_source__source_type',
        'audio_source__voice_id',
        'effective_from',
        'phoneme__category'
    ]
    
    search_fields = [
        'phoneme__ipa_symbol',
        'phoneme__vietnamese_approx',
        'change_reason',
        'uploaded_by__email'
    ]
    
    readonly_fields = [
        'version_number',
        'upload_date',
        'usage_count',
        'audio_player_full',
        'version_history_table',
        'comparison_link'
    ]
    
    fieldsets = (
        ('Version Info', {
            'fields': (
                'phoneme',
                'audio_source',
                'version_number',
                'is_active'
            )
        }),
        ('Audio Player', {
            'fields': ('audio_player_full',)
        }),
        ('Time Tracking', {
            'fields': (
                'effective_from',
                'effective_until',
                'upload_date'
            )
        }),
        ('Metadata', {
            'fields': (
                'uploaded_by',
                'change_reason'
            )
        }),
        ('Analytics', {
            'fields': (
                'usage_count',
                'avg_user_rating',
                'user_rating_count'
            ),
            'classes': ('collapse',)
        }),
        ('Version History', {
            'fields': ('version_history_table',),
            'classes': ('collapse',)
        })
    )
    
    actions = [
        'activate_selected_versions',
        'deactivate_selected_versions',
        'compare_versions',
        'export_analytics'
    ]
    
    # Custom displays
    
    def version_display(self, obj):
        """Show version with icon"""
        icon = '🎯' if obj.is_active else '📦'
        return format_html(
            '{} <strong>v{}</strong>',
            icon, obj.version_number
        )
    version_display.short_description = 'Version'
    version_display.admin_order_field = 'version_number'
    
    def phoneme_link(self, obj):
        """Link to phoneme detail"""
        url = reverse('admin:curriculum_phoneme_change', args=[obj.phoneme.pk])
        return format_html(
            '<a href="{}" style="font-size: 18px;">/{}/</a><br>'
            '<small style="color: #666;">{}</small>',
            url,
            obj.phoneme.ipa_symbol,
            obj.phoneme.vietnamese_approx
        )
    phoneme_link.short_description = 'Phoneme'
    
    def audio_preview(self, obj):
        """Compact audio player"""
        if obj.audio_source and obj.audio_source.audio_file:
            return format_html(
                '<audio controls preload="none" style="width: 200px; height: 32px;">'
                '<source src="{}" type="audio/mpeg"></audio>',
                obj.audio_source.audio_file.url
            )
        return format_html('<span style="color: #999;">No audio</span>')
    audio_preview.short_description = 'Audio'
    
    def status_badge(self, obj):
        """Active/Inactive badge"""
        if obj.is_active:
            return format_html(
                '<span style="background: #10b981; color: white; '
                'padding: 4px 12px; border-radius: 12px; font-weight: 600;">'
                '✓ ACTIVE</span>'
            )
        else:
            return format_html(
                '<span style="background: #6b7280; color: white; '
                'padding: 4px 12px; border-radius: 12px;">'
                '✗ INACTIVE</span>'
            )
    status_badge.short_description = 'Status'
    
    def quality_badge(self, obj):
        """Quality score from AudioSource"""
        score = obj.audio_source.get_quality_score()
        source_type = obj.audio_source.get_source_type_display()
        
        if score >= 95:
            color = '#10b981'
            icon = '⭐'
        elif score >= 85:
            color = '#f59e0b'
            icon = '✓'
        else:
            color = '#ef4444'
            icon = '⚠'
        
        return format_html(
            '<span style="display: inline-flex; align-items: center; gap: 4px; '
            'background: {}; color: white; padding: 4px 10px; border-radius: 12px; '
            'font-size: 12px; font-weight: 600;">{} {}%</span><br>'
            '<small style="color: #666;">{}</small>',
            color, icon, score, source_type
        )
    quality_badge.short_description = 'Quality'
    
    def usage_stats(self, obj):
        """Usage statistics"""
        count = obj.usage_count
        
        if count > 1000:
            color = '#10b981'
            label = 'Very Popular'
        elif count > 100:
            color = '#f59e0b'
            label = 'Popular'
        else:
            color = '#6b7280'
            label = 'New'
        
        return format_html(
            '<div style="text-align: center;">'
            '<div style="font-size: 20px; font-weight: bold; color: {};">{}</div>'
            '<small style="color: #666;">{} plays</small>'
            '</div>',
            color, count, label
        )
    usage_stats.short_description = 'Usage'
    
    def rating_display(self, obj):
        """User rating"""
        if obj.avg_user_rating:
            stars = '⭐' * round(obj.avg_user_rating)
            return format_html(
                '<div>{}</div><small>({:.1f}/5.0 from {} users)</small>',
                stars,
                obj.avg_user_rating,
                obj.user_rating_count
            )
        return format_html('<span style="color: #999;">No ratings</span>')
    rating_display.short_description = 'Rating'
    
    def duration_text(self, obj):
        """How long active"""
        return obj.get_duration_text()
    duration_text.short_description = 'Duration'
    
    def uploaded_info(self, obj):
        """Who uploaded and when"""
        if obj.uploaded_by:
            user_name = obj.uploaded_by.get_full_name() or obj.uploaded_by.email
        else:
            user_name = 'System'
        
        return format_html(
            '<div><strong>{}</strong></div>'
            '<small style="color: #666;">{}</small>',
            user_name,
            obj.upload_date.strftime('%Y-%m-%d %H:%M')
        )
    uploaded_info.short_description = 'Uploaded By'
    
    # Readonly field displays
    
    def audio_player_full(self, obj):
        """Full-width audio player"""
        if obj.audio_source and obj.audio_source.audio_file:
            return format_html(
                '<audio controls preload="metadata" style="width: 100%; max-width: 600px;">'
                '<source src="{}" type="audio/mpeg">'
                'Your browser does not support audio.</audio>'
                '<div style="margin-top: 8px; color: #666; font-size: 13px;">'
                'File: {}<br>'
                'Duration: {:.1f}s | Size: {}</div>',
                obj.audio_source.audio_file.url,
                obj.audio_source.audio_file.name,
                obj.audio_source.audio_duration,
                self._format_file_size(obj.audio_source.audio_file.size)
            )
        return format_html('<p style="color: #999;">No audio file</p>')
    audio_player_full.short_description = 'Audio Player'
    
    def version_history_table(self, obj):
        """Show all versions for this phoneme"""
        versions = AudioVersion.objects.filter(
            phoneme=obj.phoneme
        ).select_related('audio_source', 'uploaded_by').order_by('-version_number')
        
        if not versions:
            return 'No version history'
        
        html = '<table style="width: 100%; border-collapse: collapse;">'
        html += '''
        <thead style="background: #f3f4f6;">
            <tr>
                <th style="padding: 8px; text-align: left;">Version</th>
                <th style="padding: 8px; text-align: left;">Status</th>
                <th style="padding: 8px; text-align: left;">Quality</th>
                <th style="padding: 8px; text-align: left;">Usage</th>
                <th style="padding: 8px; text-align: left;">Uploaded</th>
                <th style="padding: 8px; text-align: left;">Action</th>
            </tr>
        </thead>
        <tbody>
        '''
        
        for v in versions:
            status_badge = '✓ Active' if v.is_active else '✗ Inactive'
            status_color = '#10b981' if v.is_active else '#6b7280'
            
            quality = v.audio_source.get_quality_score()
            
            action = ''
            if not v.is_active:
                action = f'<a href="?activate={v.pk}">Activate</a>'
            
            html += f'''
            <tr style="border-bottom: 1px solid #e5e7eb;">
                <td style="padding: 8px;"><strong>v{v.version_number}</strong></td>
                <td style="padding: 8px;">
                    <span style="color: {status_color};">{status_badge}</span>
                </td>
                <td style="padding: 8px;">{quality}%</td>
                <td style="padding: 8px;">{v.usage_count}</td>
                <td style="padding: 8px;">{v.upload_date.strftime("%Y-%m-%d")}</td>
                <td style="padding: 8px;">{action}</td>
            </tr>
            '''
        
        html += '</tbody></table>'
        
        return format_html(html)
    version_history_table.short_description = 'Version History'
    
    def comparison_link(self, obj):
        """Link to compare versions page"""
        url = reverse('admin:curriculum_audioversion_compare', args=[obj.phoneme.pk])
        return format_html(
            '<a href="{}" class="button" target="_blank">'
            'Compare All Versions →</a>',
            url
        )
    comparison_link.short_description = 'Comparison'
    
    # Actions
    
    def activate_selected_versions(self, request, queryset):
        """Activate selected versions"""
        for version in queryset:
            version.activate(
                user=request.user,
                reason=f"Activated by admin via bulk action"
            )
        
        self.message_user(
            request,
            f"Successfully activated {queryset.count()} version(s)"
        )
    activate_selected_versions.short_description = "✓ Activate selected versions"
    
    def deactivate_selected_versions(self, request, queryset):
        """Deactivate selected versions"""
        queryset.update(
            is_active=False,
            effective_until=timezone.now()
        )
        
        self.message_user(
            request,
            f"Successfully deactivated {queryset.count()} version(s)"
        )
    deactivate_selected_versions.short_description = "✗ Deactivate selected versions"
    
    def compare_versions(self, request, queryset):
        """Redirect to comparison page"""
        if queryset.count() < 2:
            self.message_user(
                request,
                "Please select at least 2 versions to compare",
                level='warning'
            )
            return
        
        # Get unique phonemes
        phonemes = queryset.values_list('phoneme_id', flat=True).distinct()
        
        if len(phonemes) > 1:
            self.message_user(
                request,
                "Please select versions from the same phoneme",
                level='warning'
            )
            return
        
        # Redirect to comparison view
        phoneme_id = phonemes[0]
        version_ids = ','.join(str(v.pk) for v in queryset)
        url = f"{reverse('admin:curriculum_audioversion_compare', args=[phoneme_id])}?versions={version_ids}"
        
        return redirect(url)
    compare_versions.short_description = "⚖ Compare selected versions"
    
    def export_analytics(self, request, queryset):
        """Export analytics to CSV"""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="audio_versions_analytics.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Phoneme', 'Version', 'Status', 'Quality', 
            'Usage Count', 'Avg Rating', 'Rating Count',
            'Uploaded By', 'Upload Date', 'Change Reason'
        ])
        
        for v in queryset:
            writer.writerow([
                v.phoneme.ipa_symbol,
                v.version_number,
                'Active' if v.is_active else 'Inactive',
                v.audio_source.get_quality_score(),
                v.usage_count,
                v.avg_user_rating or '',
                v.user_rating_count,
                v.uploaded_by.email if v.uploaded_by else '',
                v.upload_date.strftime('%Y-%m-%d %H:%M'),
                v.change_reason
            ])
        
        return response
    export_analytics.short_description = "📊 Export analytics to CSV"
    
    # Helpers
    
    @staticmethod
    def _format_file_size(size):
        """Format file size in human-readable format"""
        if size < 1024:
            return f"{size} bytes"
        elif size < 1024 * 1024:
            return f"{size / 1024:.2f} KB"
        else:
            return f"{size / (1024 * 1024):.2f} MB"
```

---

## 🔌 API ENDPOINTS

### 1. Get Audio Versions for Phoneme

```python
# backend/apps/curriculum/api/audio_version_api.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

class AudioVersionListAPIView(APIView):
    """
    GET /api/v1/audio-versions/<phoneme_id>/
    
    Get all audio versions for a phoneme.
    """
    
    def get(self, request, phoneme_id):
        phoneme = get_object_or_404(Phoneme, pk=phoneme_id)
        versions = AudioVersion.objects.filter(
            phoneme=phoneme
        ).select_related('audio_source', 'uploaded_by').order_by('-version_number')
        
        data = []
        for v in versions:
            data.append({
                'id': v.id,
                'version_number': v.version_number,
                'is_active': v.is_active,
                'audio_url': v.audio_source.audio_file.url if v.audio_source.audio_file else None,
                'quality_score': v.audio_source.get_quality_score(),
                'source_type': v.audio_source.source_type,
                'voice_id': v.audio_source.voice_id,
                'usage_count': v.usage_count,
                'avg_rating': v.avg_user_rating,
                'rating_count': v.user_rating_count,
                'effective_from': v.effective_from.isoformat(),
                'effective_until': v.effective_until.isoformat() if v.effective_until else None,
                'change_reason': v.change_reason,
                'uploaded_by': v.uploaded_by.email if v.uploaded_by else None,
                'upload_date': v.upload_date.isoformat()
            })
        
        return Response({
            'success': True,
            'phoneme': {
                'id': phoneme.id,
                'ipa_symbol': phoneme.ipa_symbol,
                'vietnamese_approx': phoneme.vietnamese_approx
            },
            'versions': data,
            'total_versions': len(data)
        })
```

### 2. Activate Version

```python
class AudioVersionActivateAPIView(APIView):
    """
    POST /api/v1/audio-versions/<version_id>/activate/
    
    Activate a specific version.
    """
    permission_classes = [IsAdminUser]
    
    def post(self, request, version_id):
        version = get_object_or_404(AudioVersion, pk=version_id)
        
        reason = request.data.get('reason', 'Activated via API')
        version.activate(user=request.user, reason=reason)
        
        return Response({
            'success': True,
            'message': f'Version {version.version_number} activated',
            'version': {
                'id': version.id,
                'version_number': version.version_number,
                'is_active': version.is_active,
                'effective_from': version.effective_from.isoformat()
            }
        })
```

### 3. Add Rating

```python
class AudioVersionRatingAPIView(APIView):
    """
    POST /api/v1/audio-versions/<version_id>/rate/
    
    Rate an audio version (1-5 stars).
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, version_id):
        version = get_object_or_404(AudioVersion, pk=version_id)
        
        rating = request.data.get('rating')
        
        if not rating or not isinstance(rating, int) or not 1 <= rating <= 5:
            return Response({
                'success': False,
                'error': 'Rating must be an integer between 1 and 5'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        version.add_rating(rating)
        
        return Response({
            'success': True,
            'message': 'Rating added successfully',
            'avg_rating': version.avg_user_rating,
            'rating_count': version.user_rating_count
        })
```

---

## 🎬 USE CASES

### Use Case 1: Admin quay lại audio cũ

```python
# Admin interface workflow:

1. Vào admin panel: /admin/curriculum/audioversion/
2. Filter by phoneme: /p/
3. See list:
   - v3 (ACTIVE) - TTS Generated - 90% quality
   - v2 (INACTIVE) - Native upload - 100% quality 
   - v1 (INACTIVE) - TTS test - 80% quality

4. Click "Activate" trên v2 (native audio ngày 15/12)
5. v2 becomes ACTIVE, v3 becomes INACTIVE
6. Users immediately get v2 audio
```

### Use Case 2: A/B Testing

```python
# Test which version performs better

# Week 1: Use v1 (US voice)
v1.activate()

# After 7 days, check analytics:
v1.usage_count  # 5000 plays
v1.avg_user_rating  # 4.2 stars

# Week 2: Use v2 (GB voice)
v2.activate()

# After 7 days:
v2.usage_count  # 4800 plays
v2.avg_user_rating  # 4.7 stars  ← Better!

# Decision: Keep v2 active
```

### Use Case 3: Bulk version management

```python
# Management command to create versions for all phonemes

python manage.py create_audio_versions_bulk \
    --source-type tts \
    --voice en-US-AriaNeural \
    --reason "Initial TTS generation"

# Output:
Creating audio versions...
✓ /p/ → v2 created
✓ /b/ → v2 created
✓ /t/ → v2 created
...
✅ Created 46 new versions
```

---

## 📈 BENEFITS

### For Admins:
✅ Không bao giờ mất audio  
✅ Dễ dàng quay lại version cũ (2 clicks)  
✅ So sánh chất lượng giữa các version  
✅ Track performance với analytics  
✅ A/B test different voices  

### For Developers:
✅ Clear audit trail  
✅ Safe to experiment với TTS  
✅ Easy rollback  
✅ Analytics for optimization  

### For Users:
✅ Luôn có audio tốt nhất  
✅ Có thể rate audio quality  
✅ System learns từ feedback  

---

## 🚀 IMPLEMENTATION PLAN

### Week 1: Core Model
- [ ] Create AudioVersion model
- [ ] Write migration
- [ ] Test on dev database
- [ ] Create sample data

### Week 2: Admin Interface
- [ ] AudioVersionAdmin with custom displays
- [ ] Admin actions (activate/deactivate)
- [ ] Version history view
- [ ] Comparison view

### Week 3: API & Integration
- [ ] API endpoints
- [ ] Frontend integration
- [ ] User rating system
- [ ] Analytics dashboard

---

**Tạo bởi:** GitHub Copilot  
**Status:** Ready for implementation

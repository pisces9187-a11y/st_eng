"""
API Views for Curriculum app.

Handles courses, units, lessons, sentences, flashcards, and grammar rules.
"""

from django.db.models import Count, Prefetch, Q
from django.views.generic import TemplateView
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Course, Unit, Lesson, Sentence, Flashcard, GrammarRule
from .serializers import (
    CourseSerializer, CourseListSerializer,
    UnitSerializer, UnitListSerializer,
    LessonSerializer, LessonListSerializer,
    SentenceSerializer, SentenceMinimalSerializer,
    FlashcardSerializer, FlashcardMinimalSerializer,
    GrammarRuleSerializer, GrammarRuleListSerializer
)


class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API viewset for courses.
    
    GET /api/v1/courses/ - List published courses
    GET /api/v1/courses/{slug}/ - Get course detail with units
    """
    
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'slug'
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CourseListSerializer
        return CourseSerializer
    
    def get_queryset(self):
        queryset = Course.objects.filter(status='published')
        
        # Filter by level
        level = self.request.query_params.get('level')
        if level:
            queryset = queryset.filter(cefr_level=level)
        
        # Filter free/paid
        is_free = self.request.query_params.get('is_free')
        if is_free is not None:
            queryset = queryset.filter(is_free=is_free.lower() == 'true')
        
        # Filter featured
        is_featured = self.request.query_params.get('featured')
        if is_featured is not None:
            queryset = queryset.filter(is_featured=is_featured.lower() == 'true')
        
        # Annotate counts
        queryset = queryset.annotate(
            units_count=Count('units', filter=Q(units__status='published')),
            lessons_count=Count(
                'units__lessons',
                filter=Q(units__lessons__status='published')
            )
        )
        
        return queryset.order_by('cefr_level', 'order', 'title')
    
    @action(detail=True, methods=['get'])
    def units(self, request, slug=None):
        """Get all units for a course."""
        course = self.get_object()
        units = course.units.filter(status='published').order_by('order')
        serializer = UnitListSerializer(units, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def levels(self, request):
        """Get available CEFR levels with course counts."""
        levels = []
        for code, name in Course.CEFR_LEVEL_CHOICES:
            count = Course.objects.filter(
                status='published',
                cefr_level=code
            ).count()
            levels.append({
                'code': code,
                'name': name,
                'course_count': count
            })
        return Response(levels)


class UnitViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API viewset for units.
    
    GET /api/v1/units/{id}/ - Get unit detail with lessons
    """
    
    serializer_class = UnitSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = Unit.objects.filter(
            status='published',
            course__status='published'
        )
        
        # Filter by course
        course_id = self.request.query_params.get('course')
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        
        return queryset.select_related('course').prefetch_related(
            Prefetch(
                'lessons',
                queryset=Lesson.objects.filter(status='published').order_by('order')
            )
        ).order_by('course', 'order')
    
    @action(detail=True, methods=['get'])
    def lessons(self, request, pk=None):
        """Get all lessons for a unit."""
        unit = self.get_object()
        lessons = unit.lessons.filter(status='published').order_by('order')
        serializer = LessonListSerializer(lessons, many=True)
        return Response(serializer.data)


class LessonViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API viewset for lessons.
    
    GET /api/v1/lessons/ - List lessons
    GET /api/v1/lessons/{slug}/ - Get lesson detail with content
    """
    
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'slug'
    
    def get_serializer_class(self):
        if self.action == 'list':
            return LessonListSerializer
        return LessonSerializer
    
    def get_queryset(self):
        queryset = Lesson.objects.filter(
            status='published',
            unit__status='published',
            unit__course__status='published'
        )
        
        # Filter by unit
        unit_id = self.request.query_params.get('unit')
        if unit_id:
            queryset = queryset.filter(unit_id=unit_id)
        
        # Filter by type
        lesson_type = self.request.query_params.get('type')
        if lesson_type:
            queryset = queryset.filter(lesson_type=lesson_type)
        
        # Filter premium
        is_premium = self.request.query_params.get('premium')
        if is_premium is not None:
            queryset = queryset.filter(is_premium=is_premium.lower() == 'true')
        
        return queryset.select_related('unit', 'unit__course').prefetch_related(
            'sentences', 'flashcards'
        ).order_by('unit', 'order')
    
    @action(detail=True, methods=['get'])
    def sentences(self, request, slug=None):
        """Get all sentences for a lesson."""
        lesson = self.get_object()
        sentences = lesson.sentences.order_by('order')
        serializer = SentenceSerializer(sentences, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def flashcards(self, request, slug=None):
        """Get all flashcards for a lesson."""
        lesson = self.get_object()
        flashcards = lesson.flashcards.filter(is_active=True).order_by('order')
        serializer = FlashcardSerializer(flashcards, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def next(self, request, slug=None):
        """Get next lesson in sequence."""
        lesson = self.get_object()
        
        # Try next in same unit
        next_lesson = Lesson.objects.filter(
            unit=lesson.unit,
            status='published',
            order__gt=lesson.order
        ).order_by('order').first()
        
        if not next_lesson:
            # Try first lesson in next unit
            next_unit = Unit.objects.filter(
                course=lesson.unit.course,
                status='published',
                order__gt=lesson.unit.order
            ).order_by('order').first()
            
            if next_unit:
                next_lesson = next_unit.lessons.filter(
                    status='published'
                ).order_by('order').first()
        
        if next_lesson:
            serializer = LessonListSerializer(next_lesson)
            return Response(serializer.data)
        
        return Response({'message': 'Đây là bài học cuối cùng.'}, status=404)
    
    @action(detail=True, methods=['get'])
    def previous(self, request, slug=None):
        """Get previous lesson in sequence."""
        lesson = self.get_object()
        
        # Try previous in same unit
        prev_lesson = Lesson.objects.filter(
            unit=lesson.unit,
            status='published',
            order__lt=lesson.order
        ).order_by('-order').first()
        
        if not prev_lesson:
            # Try last lesson in previous unit
            prev_unit = Unit.objects.filter(
                course=lesson.unit.course,
                status='published',
                order__lt=lesson.unit.order
            ).order_by('-order').first()
            
            if prev_unit:
                prev_lesson = prev_unit.lessons.filter(
                    status='published'
                ).order_by('-order').first()
        
        if prev_lesson:
            serializer = LessonListSerializer(prev_lesson)
            return Response(serializer.data)
        
        return Response({'message': 'Đây là bài học đầu tiên.'}, status=404)


class SentenceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API viewset for sentences.
    
    GET /api/v1/sentences/{id}/ - Get sentence detail
    """
    
    serializer_class = SentenceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = Sentence.objects.filter(
            lesson__status='published'
        )
        
        # Filter by lesson
        lesson_id = self.request.query_params.get('lesson')
        if lesson_id:
            queryset = queryset.filter(lesson_id=lesson_id)
        
        return queryset.select_related('lesson').order_by('lesson', 'order')


class FlashcardViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API viewset for flashcards.
    
    GET /api/v1/flashcards/ - List flashcards
    GET /api/v1/flashcards/{id}/ - Get flashcard detail
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return FlashcardMinimalSerializer
        return FlashcardSerializer
    
    def get_queryset(self):
        queryset = Flashcard.objects.filter(is_active=True)
        
        # Filter by lesson
        lesson_id = self.request.query_params.get('lesson')
        if lesson_id:
            queryset = queryset.filter(lesson_id=lesson_id)
        
        # Filter by type
        card_type = self.request.query_params.get('type')
        if card_type:
            queryset = queryset.filter(card_type=card_type)
        
        # Filter by difficulty
        difficulty = self.request.query_params.get('difficulty')
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
        
        return queryset.select_related('lesson').order_by('lesson', 'order')
    
    @action(detail=False, methods=['get'])
    def random(self, request):
        """Get random flashcards for practice."""
        limit = min(int(request.query_params.get('limit', 10)), 50)
        
        queryset = self.get_queryset().order_by('?')[:limit]
        serializer = FlashcardSerializer(queryset, many=True)
        return Response(serializer.data)


class GrammarRuleViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API viewset for grammar rules.
    
    GET /api/v1/grammar/ - List grammar rules
    GET /api/v1/grammar/{slug}/ - Get grammar rule detail
    """
    
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'slug'
    
    def get_serializer_class(self):
        if self.action == 'list':
            return GrammarRuleListSerializer
        return GrammarRuleSerializer
    
    def get_queryset(self):
        queryset = GrammarRule.objects.filter(is_active=True)
        
        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        # Filter by level
        level = self.request.query_params.get('level')
        if level:
            queryset = queryset.filter(cefr_level=level)
        
        # Search
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(explanation_html__icontains=search) |
                Q(structure__icontains=search)
            )
        
        return queryset.order_by('category', 'cefr_level', 'order')
    
    @action(detail=False, methods=['get'])
    def categories(self, request):
        """Get all grammar categories with counts."""
        categories = GrammarRule.objects.filter(
            is_active=True
        ).values('category').annotate(
            count=Count('id')
        ).order_by('category')
        
        return Response(list(categories))


class TestAudioView(TemplateView):
    """Test page for audio playback."""
    template_name = 'test_audio.html'

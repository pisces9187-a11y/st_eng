"""
Autocomplete views for curriculum app
"""

from dal import autocomplete
from django.db.models import Q

from .models import Phoneme


class PhonemeAutocomplete(autocomplete.Select2QuerySetView):
    """
    Autocomplete view for Phoneme selection in admin.
    
    Shows: /p/ - pờ (không có âm ờ)
    Searchable by: IPA symbol, Vietnamese approximation, example words
    """
    
    def get_queryset(self):
        """Filter phonemes based on search term"""
        # User must be staff
        if not self.request.user.is_staff:
            return Phoneme.objects.none()
        
        qs = Phoneme.objects.all()
        
        if self.q:
            # Search by IPA symbol, Vietnamese approximation, or example words
            qs = qs.filter(
                Q(ipa_symbol__icontains=self.q) |
                Q(vietnamese_approximation__icontains=self.q) |
                Q(example_words__word__icontains=self.q)
            ).distinct()
        
        return qs.order_by('ipa_symbol')
    
    def get_result_label(self, item):
        """
        Custom label format: /p/ - pờ (không có âm ờ)
        """
        label = f"/{item.ipa_symbol}/"
        
        if item.vietnamese_approximation:
            label += f" - {item.vietnamese_approximation}"
        
        if item.pronunciation_tips:
            # Show first 50 chars of tips
            tips = item.pronunciation_tips[:50]
            if len(item.pronunciation_tips) > 50:
                tips += "..."
            label += f" ({tips})"
        
        return label

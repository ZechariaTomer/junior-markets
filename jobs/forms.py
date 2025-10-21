from django import forms
from .models import Job, Application


class JobForm(forms.ModelForm):
    """טופס ליצירת משרה"""
    
    class Meta:
        model = Job
        fields = [
            'title',
            'description',
            'status',
            'difficulty',
            'deadline',
            'max_applicants'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'deadline': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
    
    def clean_title(self):
        """ולידציה לכותרת"""
        title = self.cleaned_data.get('title')
        if len(title) < 5:
            raise forms.ValidationError('כותרת חייבת להיות לפחות 5 תווים')
        return title


class ApplicationForm(forms.ModelForm):
    """טופס להגשת מועמדות"""
    
    class Meta:
        model = Application
        fields = ['cover_letter']
        widgets = {
            'cover_letter': forms.Textarea(attrs={
                'rows': 5,
                'placeholder': 'למה אתה מתאים למשרה?'
            }),
        }
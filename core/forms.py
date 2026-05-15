from django import forms
from .models import Note, Assignment, Submission


class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ('student', 'value', 'comment')
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'student': 'Alumno',
            'value': 'Nota (1-10)',
            'comment': 'Comentario',
        }


class NoteBulkForm(forms.Form):
    student = forms.ModelChoiceField(queryset=None, label='Alumno')
    value = forms.DecimalField(max_digits=4, decimal_places=2, min_value=1, max_value=10, label='Nota')
    comment = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}), required=False, label='Comentario')

    def __init__(self, *args, **kwargs):
        subject = kwargs.pop('subject', None)
        super().__init__(*args, **kwargs)
        if subject:
            self.fields['student'].queryset = subject.school_level.user_set.filter(role='student')


class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ('title', 'description', 'due_date', 'file')
        widgets = {
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'description': forms.Textarea(attrs={'rows': 4}),
        }
        labels = {
            'title': 'Título',
            'description': 'Descripción',
            'due_date': 'Fecha de entrega',
            'file': 'Archivo adjunto',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['due_date'].input_formats = ['%Y-%m-%dT%H:%M']


class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ('file', 'comment')
        labels = {
            'file': 'Archivo',
            'comment': 'Comentario',
        }


class GradeSubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ('grade', 'feedback')
        labels = {
            'grade': 'Calificación (1-10)',
            'feedback': 'Retroalimentación',
        }

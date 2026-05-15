from django.contrib import admin
from .models import SchoolLevel, Subject, Assignment, Submission, Note


@admin.register(SchoolLevel)
class SchoolLevelAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'school_level', 'teacher')
    list_filter = ('school_level', 'teacher')


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'teacher', 'due_date')
    list_filter = ('subject__school_level', 'teacher')


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('student', 'assignment', 'submitted_at', 'grade')
    list_filter = ('assignment__subject',)


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'value', 'date')
    list_filter = ('subject', 'subject__school_level')

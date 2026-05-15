from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg
from django.utils import timezone
from accounts.decorators import student_required, teacher_required
from accounts.models import User
from .models import SchoolLevel, Subject, Assignment, Submission, Note
from .forms import NoteForm, AssignmentForm, SubmissionForm, GradeSubmissionForm


class StudentDashboardView(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.role != User.Role.STUDENT:
            messages.error(request, 'Acceso no autorizado.')
            return redirect('home')
        if not request.user.is_approved:
            return redirect('accounts:pending')

        student = request.user
        notes = Note.objects.filter(student=student).select_related('subject', 'subject__school_level')
        subjects = Subject.objects.filter(school_level__in=SchoolLevel.objects.filter(
            id__in=notes.values_list('subject__school_level', flat=True).distinct()
        ))

        pending_assignments = Assignment.objects.filter(
            subject__school_level__in=notes.values_list('subject__school_level', flat=True)
        ).exclude(
            submissions__student=student
        ).select_related('subject').order_by('due_date')[:5]

        subject_averages = notes.values('subject__name', 'subject_id').annotate(avg=Avg('value'))
        overall_avg = notes.aggregate(Avg('value'))['value__avg']

        context = {
            'student': student,
            'notes': notes.order_by('-date')[:10],
            'subjects': subjects,
            'pending_assignments': pending_assignments,
            'subject_averages': subject_averages,
            'overall_avg': overall_avg,
        }
        return render(request, 'core/student/dashboard.html', context)


class StudentGradesView(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.role != User.Role.STUDENT:
            return redirect('home')
        if not request.user.is_approved:
            return redirect('accounts:pending')

        student = request.user
        subjects = Subject.objects.filter(
            school_level__in=SchoolLevel.objects.filter(
                id__in=Note.objects.filter(student=student).values_list('subject__school_level', flat=True)
            )
        )

        grades_by_subject = {}
        for subject in subjects:
            notes = Note.objects.filter(student=student, subject=subject).order_by('-date')
            avg = notes.aggregate(Avg('value'))['value__avg']
            grades_by_subject[subject] = {
                'notes': notes,
                'average': avg,
            }

        context = {
            'grades_by_subject': grades_by_subject,
        }
        return render(request, 'core/student/grades.html', context)


class StudentAssignmentsView(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.role != User.Role.STUDENT:
            return redirect('home')
        if not request.user.is_approved:
            return redirect('accounts:pending')

        student = request.user
        student_levels = Note.objects.filter(student=student).values_list('subject__school_level', flat=True).distinct()
        subjects = Subject.objects.filter(school_level__in=student_levels)

        pending = Assignment.objects.filter(subject__in=subjects).exclude(
            submissions__student=student
        ).select_related('subject').order_by('due_date')

        submitted = Submission.objects.filter(student=student).select_related(
            'assignment', 'assignment__subject'
        ).order_by('-submitted_at')

        context = {
            'pending_assignments': pending,
            'submitted_assignments': submitted,
        }
        return render(request, 'core/student/assignments.html', context)


class StudentAssignmentDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        if request.user.role != User.Role.STUDENT:
            return redirect('home')

        assignment = get_object_or_404(Assignment, pk=pk)
        submission = Submission.objects.filter(assignment=assignment, student=request.user).first()
        form = SubmissionForm()

        context = {
            'assignment': assignment,
            'submission': submission,
            'form': form,
        }
        return render(request, 'core/student/assignment_detail.html', context)


class SubmitAssignmentView(LoginRequiredMixin, View):
    def post(self, request, pk):
        if request.user.role != User.Role.STUDENT:
            return redirect('home')

        assignment = get_object_or_404(Assignment, pk=pk)
        existing = Submission.objects.filter(assignment=assignment, student=request.user).first()
        if existing:
            messages.warning(request, 'Ya has entregado esta tarea.')
            return redirect('core:student_assignment_detail', pk=pk)

        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.assignment = assignment
            submission.student = request.user
            submission.save()
            messages.success(request, 'Tarea entregada correctamente.')
        else:
            messages.error(request, 'Error al entregar la tarea.')

        return redirect('core:student_assignment_detail', pk=pk)


class TeacherSubjectListView(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.role not in [User.Role.TEACHER, User.Role.ADMIN]:
            return redirect('home')

        if request.user.role == User.Role.ADMIN:
            subjects = Subject.objects.all().select_related('school_level', 'teacher')
        else:
            subjects = Subject.objects.filter(teacher=request.user).select_related('school_level')

        context = {'subjects': subjects}
        return render(request, 'core/teacher/subject_list.html', context)


class TeacherGradeSubjectView(LoginRequiredMixin, View):
    def get(self, request, pk):
        subject = get_object_or_404(Subject, pk=pk)
        if request.user.role != User.Role.ADMIN and subject.teacher != request.user:
            messages.error(request, 'No tienes permiso para gestionar esta materia.')
            return redirect('core:teacher_subject_list')

        students = User.objects.filter(
            role=User.Role.STUDENT, is_approved=True,
            notes__subject=subject
        ).distinct()

        all_students = User.objects.filter(
            role=User.Role.STUDENT, is_approved=True
        ).distinct()

        notes = Note.objects.filter(subject=subject).select_related('student')

        context = {
            'subject': subject,
            'students': all_students,
            'notes': notes,
            'form': NoteForm(),
        }

        return render(request, 'core/teacher/grade_subject.html', context)

    def post(self, request, pk):
        subject = get_object_or_404(Subject, pk=pk)
        if request.user.role != User.Role.ADMIN and subject.teacher != request.user:
            return redirect('core:teacher_subject_list')

        form = NoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.subject = subject
            note.teacher = request.user
            note.save()
            messages.success(request, 'Nota guardada correctamente.')
        else:
            messages.error(request, 'Error al guardar la nota.')

        return redirect('core:teacher_grade_subject', pk=pk)


class TeacherAssignmentListView(LoginRequiredMixin, View):
    def get(self, request, pk):
        subject = get_object_or_404(Subject, pk=pk)
        if request.user.role != User.Role.ADMIN and subject.teacher != request.user:
            return redirect('core:teacher_subject_list')

        assignments = Assignment.objects.filter(subject=subject).order_by('-created_at')
        context = {
            'subject': subject,
            'assignments': assignments,
        }
        return render(request, 'core/teacher/assignment_list.html', context)


class TeacherAssignmentCreateView(LoginRequiredMixin, View):
    def get(self, request, pk):
        subject = get_object_or_404(Subject, pk=pk)
        if request.user.role != User.Role.ADMIN and subject.teacher != request.user:
            return redirect('core:teacher_subject_list')

        form = AssignmentForm()
        context = {'subject': subject, 'form': form}
        return render(request, 'core/teacher/assignment_form.html', context)

    def post(self, request, pk):
        subject = get_object_or_404(Subject, pk=pk)
        if request.user.role != User.Role.ADMIN and subject.teacher != request.user:
            return redirect('core:teacher_subject_list')

        form = AssignmentForm(request.POST, request.FILES)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.subject = subject
            assignment.teacher = request.user
            assignment.save()
            messages.success(request, 'Tarea creada correctamente.')
            return redirect('core:teacher_assignment_list', pk=pk)
        else:
            messages.error(request, 'Error al crear la tarea.')

        context = {'subject': subject, 'form': form}
        return render(request, 'core/teacher/assignment_form.html', context)


class TeacherGradeSubmissionsView(LoginRequiredMixin, View):
    def get(self, request, pk):
        assignment = get_object_or_404(Assignment, pk=pk)
        if request.user.role != User.Role.ADMIN and assignment.teacher != request.user:
            return redirect('core:teacher_subject_list')

        submissions = Submission.objects.filter(assignment=assignment).select_related('student')
        context = {
            'assignment': assignment,
            'submissions': submissions,
        }
        return render(request, 'core/teacher/grade_submissions.html', context)


class TeacherGradeSubmissionView(LoginRequiredMixin, View):
    def get(self, request, pk):
        submission = get_object_or_404(Submission, pk=pk)
        if request.user.role != User.Role.ADMIN and submission.assignment.teacher != request.user:
            return redirect('core:teacher_subject_list')

        form = GradeSubmissionForm(instance=submission)
        context = {
            'submission': submission,
            'form': form,
        }
        return render(request, 'core/teacher/grade_submission_form.html', context)

    def post(self, request, pk):
        submission = get_object_or_404(Submission, pk=pk)
        if request.user.role != User.Role.ADMIN and submission.assignment.teacher != request.user:
            return redirect('core:teacher_subject_list')

        form = GradeSubmissionForm(request.POST, instance=submission)
        if form.is_valid():
            sub = form.save(commit=False)
            sub.graded_at = timezone.now()
            sub.save()
            messages.success(request, 'Entrega calificada correctamente.')
            return redirect('core:teacher_grade_submissions', pk=submission.assignment.pk)
        else:
            messages.error(request, 'Error al calificar.')

        context = {'submission': submission, 'form': form}
        return render(request, 'core/teacher/grade_submission_form.html', context)

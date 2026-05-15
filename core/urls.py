from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('student/dashboard/', views.StudentDashboardView.as_view(), name='student_dashboard'),
    path('student/grades/', views.StudentGradesView.as_view(), name='student_grades'),
    path('student/assignments/', views.StudentAssignmentsView.as_view(), name='student_assignments'),
    path('student/assignment/<int:pk>/', views.StudentAssignmentDetailView.as_view(), name='student_assignment_detail'),
    path('student/assignment/<int:pk>/submit/', views.SubmitAssignmentView.as_view(), name='submit_assignment'),

    path('teacher/subjects/', views.TeacherSubjectListView.as_view(), name='teacher_subject_list'),
    path('teacher/subject/<int:pk>/grades/', views.TeacherGradeSubjectView.as_view(), name='teacher_grade_subject'),
    path('teacher/subject/<int:pk>/assignments/', views.TeacherAssignmentListView.as_view(), name='teacher_assignment_list'),
    path('teacher/subject/<int:pk>/assignments/create/', views.TeacherAssignmentCreateView.as_view(), name='teacher_assignment_create'),
    path('teacher/assignment/<int:pk>/submissions/', views.TeacherGradeSubmissionsView.as_view(), name='teacher_grade_submissions'),
    path('teacher/submission/<int:pk>/grade/', views.TeacherGradeSubmissionView.as_view(), name='teacher_grade_submission'),
]

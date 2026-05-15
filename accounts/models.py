from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = 'student', 'Alumno'
        TEACHER = 'teacher', 'Profesor'
        ADMIN = 'admin', 'Administrativo'

    role = models.CharField(max_length=10, choices=Role.choices, default=Role.STUDENT)
    is_approved = models.BooleanField(default=False, help_text='Indica si un usuario alumno ha sido aprobado por un administrador.')

    def __str__(self):
        return f'{self.get_full_name() or self.username} ({self.get_role_display()})'

    def is_student(self):
        return self.role == self.Role.STUDENT

    def is_teacher(self):
        return self.role == self.Role.TEACHER

    def is_admin_role(self):
        return self.role == self.Role.ADMIN

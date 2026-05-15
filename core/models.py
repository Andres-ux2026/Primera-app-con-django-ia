from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from accounts.models import User


class SchoolLevel(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='Nivel/Año')

    class Meta:
        verbose_name = 'Nivel escolar'
        verbose_name_plural = 'Niveles escolares'
        ordering = ['name']

    def __str__(self):
        return self.name


class Subject(models.Model):
    name = models.CharField(max_length=100, verbose_name='Materia')
    code = models.CharField(max_length=10, unique=True, verbose_name='Código')
    school_level = models.ForeignKey(SchoolLevel, on_delete=models.CASCADE, related_name='subjects', verbose_name='Nivel')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subjects', limit_choices_to={'role': User.Role.TEACHER}, verbose_name='Profesor')

    class Meta:
        verbose_name = 'Materia'
        verbose_name_plural = 'Materias'
        ordering = ['school_level', 'name']
        unique_together = [('name', 'school_level')]

    def __str__(self):
        return f'{self.name} - {self.school_level.name}'


class Assignment(models.Model):
    title = models.CharField(max_length=200, verbose_name='Título')
    description = models.TextField(verbose_name='Descripción')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='assignments', verbose_name='Materia')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_assignments', verbose_name='Profesor')
    due_date = models.DateTimeField(verbose_name='Fecha de entrega')
    file = models.FileField(upload_to='assignments/', blank=True, null=True, verbose_name='Archivo adjunto')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Creado el')

    class Meta:
        verbose_name = 'Tarea'
        verbose_name_plural = 'Tareas'
        ordering = ['-due_date']

    def __str__(self):
        return f'{self.title} - {self.subject.name}'


class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions', verbose_name='Tarea')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions', verbose_name='Alumno')
    file = models.FileField(upload_to='submissions/', blank=True, null=True, verbose_name='Archivo entregado')
    comment = models.TextField(blank=True, verbose_name='Comentario del alumno')
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name='Entregado el')
    grade = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(1), MaxValueValidator(10)], verbose_name='Calificación')
    graded_at = models.DateTimeField(blank=True, null=True, verbose_name='Calificado el')
    feedback = models.TextField(blank=True, verbose_name='Retroalimentación')

    class Meta:
        verbose_name = 'Entrega'
        verbose_name_plural = 'Entregas'
        unique_together = [('assignment', 'student')]
        ordering = ['-submitted_at']

    def __str__(self):
        return f'{self.student.get_full_name()} - {self.assignment.title}'


class Note(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes', limit_choices_to={'role': User.Role.STUDENT}, verbose_name='Alumno')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='notes', verbose_name='Materia')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_notes', verbose_name='Profesor')
    value = models.DecimalField(max_digits=4, decimal_places=2, validators=[MinValueValidator(1), MaxValueValidator(10)], verbose_name='Nota')
    date = models.DateTimeField(auto_now_add=True, verbose_name='Fecha')
    comment = models.TextField(blank=True, verbose_name='Comentario')

    class Meta:
        verbose_name = 'Nota'
        verbose_name_plural = 'Notas'
        ordering = ['-date']

    def __str__(self):
        return f'{self.student.get_full_name()} - {self.subject.name}: {self.value}'

"""
Script para poblar la base de datos con datos de ejemplo.
Ejecutar: python manage.py runscript scripts.seed_data
O desde shell: python manage.py shell < scripts/seed_data.py
"""

import os
import sys
import django
from decimal import Decimal
from datetime import datetime, timedelta
from random import uniform, randint, choice

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.models import SchoolLevel, Subject, Note, Assignment, Submission
from django.utils import timezone

User = get_user_model()


def clean_data():
    print('Limpiando datos existentes...')
    Submission.objects.all().delete()
    Assignment.objects.all().delete()
    Note.objects.all().delete()
    Subject.objects.all().delete()
    SchoolLevel.objects.all().delete()
    User.objects.filter(is_superuser=False).delete()
    print('Datos limpiados.')


def create_users():
    print('Creando usuarios...')

    admin1, _ = User.objects.get_or_create(
        username='admin1',
        defaults={
            'email': 'admin1@colegio.edu',
            'first_name': 'Carlos',
            'last_name': 'Gutiérrez',
            'role': User.Role.ADMIN,
            'is_approved': True,
            'is_staff': True,
        }
    )
    admin1.set_password('admin123')
    admin1.save()

    admin2, _ = User.objects.get_or_create(
        username='admin2',
        defaults={
            'email': 'admin2@colegio.edu',
            'first_name': 'María',
            'last_name': 'Fernández',
            'role': User.Role.ADMIN,
            'is_approved': True,
            'is_staff': True,
        }
    )
    admin2.set_password('admin123')
    admin2.save()

    teachers_data = [
        ('prof1', 'prof1', 'Ricardo', 'García'),
        ('prof2', 'prof2', 'Laura', 'Martínez'),
        ('prof3', 'prof3', 'Pedro', 'López'),
        ('prof4', 'prof4', 'Sofía', 'Rodríguez'),
    ]

    teachers = {}
    for username, password, first, last in teachers_data:
        t, _ = User.objects.get_or_create(
            username=username,
            defaults={
                'email': f'{username}@colegio.edu',
                'first_name': first,
                'last_name': last,
                'role': User.Role.TEACHER,
                'is_approved': True,
            }
        )
        t.set_password(password)
        t.save()
        teachers[username] = t

    niveles_nombres = ['1° Año', '2° Año', '3° Año']
    first_names = [
        'Mateo', 'Valentina', 'Santiago', 'Camila', 'Benjamín',
        'Isabella', 'Sebastián', 'Luciana', 'Joaquín', 'Victoria',
        'Matías', 'Emma', 'Facundo', 'Martina', 'Nicolás',
        'Julieta', 'Gabriel', 'Renata', 'Tomas', 'Lara',
        'Felipe', 'Mía', 'Bruno', 'Sara', 'Agustín',
        'Abril', 'Emilia', 'Lautaro', 'Catalina', 'Thiago',
        'Josefina', 'Lucas', 'Delfina', 'Valentino', 'Pilar',
    ]
    last_names = [
        'González', 'Díaz', 'Pérez', 'Álvarez', 'Romero',
        'Torres', 'Acosta', 'Medina', 'Castillo', 'Ríos',
        'Molina', 'Suárez', 'Ortiz', 'Moreno', 'Navarro',
        'Vega', 'Campos', 'Iglesias', 'Rojas', 'Silva',
        'Paz', 'Cabrera', 'Herrera', 'Flores', 'Pereyra',
        'Méndez', 'Cruz', 'Roldán', 'Sosa', 'Arias',
    ]

    students = []
    for i in range(35):
        first = first_names[i % len(first_names)]
        last = last_names[i % len(last_names)]
        nivel_idx = i // 12
        if nivel_idx >= 3:
            nivel_idx = 2
        username = f'alumno{i+1}'
        s, _ = User.objects.get_or_create(
            username=username,
            defaults={
                'email': f'{username}@colegio.edu',
                'first_name': first,
                'last_name': last,
                'role': User.Role.STUDENT,
                'is_approved': True,
            }
        )
        s.set_password('alumno123')
        s.save()
        students.append(s)

    print(f'  {2} administradores')
    print(f'  {len(teachers)} profesores')
    print(f'  {len(students)} alumnos')
    return teachers, students


def create_levels_subjects(teachers):
    print('Creando niveles y materias...')

    niveles_data = [
        ('1° Año', [
            ('MAT1', 'Matemática', 'prof1'),
            ('LEN1', 'Lengua', 'prof2'),
            ('CIE1', 'Ciencias Naturales', 'prof3'),
        ]),
        ('2° Año', [
            ('MAT2', 'Matemática', 'prof1'),
            ('LEN2', 'Lengua', 'prof2'),
            ('HIS2', 'Historia', 'prof4'),
        ]),
        ('3° Año', [
            ('MAT3', 'Matemática', 'prof1'),
            ('LEN3', 'Lengua', 'prof2'),
            ('ING3', 'Inglés', 'prof4'),
        ]),
    ]

    levels = {}
    subjects = []

    for nivel_name, materia_list in niveles_data:
        level, _ = SchoolLevel.objects.get_or_create(name=nivel_name)
        levels[nivel_name] = level

        for code, name, teacher_key in materia_list:
            subj, _ = Subject.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'school_level': level,
                    'teacher': teachers[teacher_key],
                }
            )
            subjects.append(subj)

    print(f'  {len(levels)} niveles, {len(subjects)} materias')
    return levels, subjects


def assign_students_to_levels(levels, students):
    print('Asignando alumnos a niveles...')
    nivel_list = list(levels.values())
    students_per_level = {}

    for i, student in enumerate(students):
        level = nivel_list[i // 12] if i // 12 < 3 else nivel_list[2]
        if level.name not in students_per_level:
            students_per_level[level.name] = []
        students_per_level[level.name].append(student)

    for level_name, level_students in students_per_level.items():
        print(f'  {level_name}: {len(level_students)} alumnos')

    return students_per_level


def create_notes(levels, subjects, students_per_level):
    print('Creando notas...')

    teachers = {s.teacher.id: s.teacher for s in subjects}
    note_count = 0

    for subject in subjects:
        level_name = subject.school_level.name
        level_students = students_per_level.get(level_name, [])
        teacher = subject.teacher

        for student in level_students:
            for _ in range(randint(2, 4)):
                value = round(uniform(3, 10), 2)
                date = timezone.now() - timedelta(days=randint(1, 90))
                comment = choice([
                    'Buen trabajo', 'Puede mejorar', 'Excelente desempeño',
                    'Regular', 'Muy bien', 'Necesita repasar', '',
                    'Sobresaliente', 'Aprobado', 'Bien'
                ])
                Note.objects.create(
                    student=student,
                    subject=subject,
                    teacher=teacher,
                    value=Decimal(str(value)),
                    date=date,
                    comment=comment,
                )
                note_count += 1

    print(f'  {note_count} notas creadas')
    return note_count


def create_assignments(levels, subjects, students_per_level):
    print('Creando tareas y entregas...')

    assignment_count = 0
    submission_count = 0

    for subject in subjects:
        level_name = subject.school_level.name
        level_students = students_per_level.get(level_name, [])

        for i in range(randint(2, 3)):
            days_offset = randint(1, 30)
            due_date = timezone.now() + timedelta(days=days_offset)

            assignment = Assignment.objects.create(
                title=choice([
                    'Trabajo Práctico',
                    'Ejercicios de repaso',
                    'Investigación',
                    'Proyecto integrador',
                    'Cuestionario',
                ]) + f' {i+1} - {subject.name}',
                description=choice([
                    f'Resolver los ejercicios del capítulo {randint(1, 10)} del libro.',
                    f'Investigar sobre los temas vistos en clase y preparar un resumen.',
                    f'Completar las actividades de la unidad {randint(1, 8)}.',
                    f'Desarrollar un proyecto práctico aplicando los conceptos aprendidos.',
                    f'Responder el cuestionario sobre {subject.name}.',
                ]),
                subject=subject,
                teacher=subject.teacher,
                due_date=due_date,
            )
            assignment_count += 1

            for student in level_students:
                if randint(0, 1):
                    submitted_at = due_date - timedelta(days=randint(0, 5))
                    Submission.objects.create(
                        assignment=assignment,
                        student=student,
                        comment=choice(['Listo', 'Entregado', '', 'Finalizado', 'Completo']),
                        submitted_at=submitted_at,
                        grade=Decimal(str(round(uniform(4, 10), 2))) if randint(0, 1) else None,
                        graded_at=timezone.now() if randint(0, 1) else None,
                        feedback=choice(['Bien hecho', '', 'Corregir algunos puntos', 'Excelente', 'Buen trabajo']) if randint(0, 1) else '',
                    )
                    submission_count += 1

    print(f'  {assignment_count} tareas, {submission_count} entregas')
    return assignment_count, submission_count


def main():
    print('=== INICIANDO CARGA DE DATOS ===\n')

    clean_data()
    teachers, students = create_users()
    levels, subjects = create_levels_subjects(teachers)
    students_per_level = assign_students_to_levels(levels, students)
    create_notes(levels, subjects, students_per_level)
    create_assignments(levels, subjects, students_per_level)

    print('\n=== CARGA DE DATOS COMPLETADA ===')
    print('\nCredenciales de prueba:')
    print('  Administradores: admin1 / admin123 | admin2 / admin123')
    print('  Profesores: prof1 / prof1 | prof2 / prof2 | prof3 / prof3 | prof4 / prof4')
    print('  Alumnos: alumno1 / alumno123 ... alumno35 / alumno123')


if __name__ == '__main__':
    main()

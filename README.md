# Sistema Escolar

Aplicación web Django para gestión escolar con roles de alumno, profesor y administrativo.

## Requisitos

- Python 3.10+
- PostgreSQL 16
- pip

## Instalación

### 1. Clonar el repositorio

```bash
git clone <repo-url>
cd Primera-app-con-django-ia
```

### 2. Crear entorno virtual

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar PostgreSQL 16

```bash
# Acceder a PostgreSQL
sudo -u postgres psql

# Crear base de datos
CREATE DATABASE colegio_db;
CREATE USER postgres WITH PASSWORD 'postgres';
GRANT ALL PRIVILEGES ON DATABASE colegio_db TO postgres;
\q
```

### 5. Configurar variables de entorno

Editar el archivo `.env` si es necesario:

```env
DB_NAME=colegio_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
SECRET_KEY=tu-clave-secreta-aqui
DEBUG=True
```

### 6. Ejecutar migraciones

```bash
python manage.py migrate
```

### 7. Cargar datos de prueba

```bash
python scripts/seed_data.py
```

### 8. Iniciar servidor

```bash
python manage.py runserver
```

Acceder a: http://127.0.0.1:8000

## Credenciales de prueba

| Rol | Usuario | Contraseña |
|-----|---------|------------|
| Administrativo | admin1 | admin123 |
| Administrativo | admin2 | admin123 |
| Profesor | prof1 | prof1 |
| Profesor | prof2 | prof2 |
| Profesor | prof3 | prof3 |
| Profesor | prof4 | prof4 |
| Alumno | alumno1 | alumno123 |
| Alumno | alumno2 | alumno123 |
| ... | alumno35 | alumno123 |

## Estructura del proyecto

```
├── config/              # Configuración Django
│   ├── settings.py
│   └── urls.py
├── accounts/            # Gestión de usuarios y autenticación
│   ├── models.py        # Custom User con roles
│   ├── views.py         # Login, registro, aprobación
│   ├── decorators.py    # Decoradores de permisos
│   └── templates/
├── core/                # Lógica principal del negocio
│   ├── models.py        # SchoolLevel, Subject, Assignment, Submission, Note
│   ├── views.py         # CRUDs por rol
│   └── templates/
│       ├── student/     # Dashboard, notas, tareas (alumno)
│       └── teacher/     # Gestión de materias (profesor/admin)
├── scripts/
│   └── seed_data.py     # Carga de datos de prueba
└── static/              # Archivos estáticos
```

## Modelos de datos

- **User** — Usuario con rol (student/teacher/admin) y estado de aprobación
- **SchoolLevel** — Niveles escolares (1° Año, 2° Año, 3° Año)
- **Subject** — Materias asociadas a un nivel y profesor
- **Assignment** — Tareas creadas por profesores
- **Submission** — Entregas de tareas por alumnos (con calificación)
- **Note** — Notas numéricas (1-10) por alumno y materia

## Roles y permisos

### Alumno
- Dashboard con resumen de notas y tareas pendientes
- Visualización de notas por materia con promedios
- Listado de tareas pendientes y entregadas
- Entrega de tareas con archivos adjuntos

### Profesor
- Panel con sus materias asignadas
- Carga de notas por materia y alumno
- Creación y gestión de tareas
- Calificación de entregas con retroalimentación

### Administrativo
- Acceso a todas las funcionalidades de profesor
- Aprobación de cuentas de alumnos registrados
- Panel de administración de Django completo

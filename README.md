# Plantilla final de proyecto Unidad 1

## Índice
1. [Estructura del Proyecto](#estructura-del-proyecto)
2. [Instalacion y configuración](#instalación-y-configuración)
3. [Introducción a CSRF](#introducción-a-csrf)
4. [¿Qué es un ataque CSRF?](#qué-es-un-ataque-csrf)
5. [Protección CSRF en Django](#protección-csrf-en-django)
6. [Implementación práctica](#implementación-práctica)
7. [Decoradores de seguridad](#decoradores-de-seguridad)
8. [CSRF en peticiones AJAX](#csrf-en-peticiones-ajax)
9. [Buenas prácticas](#buenas-prácticas)
10. [Ejercicios prácticos](#ejercicios-prácticos)
11. [Referencias](#referencias)

---

## Estructura del Proyecto

```
bienvenida/
├── bienvenida/
│   ├── __init__.py
│   ├── settings.py          # Configuración con inventario añadido
│   ├── urls.py              # URLs principales
│   ├── views.py             # Vista de inicio
│   ├── wsgi.py
│   └── templates/
│       └── inicio.html      # Página de bienvenida
├── inventario/
│   ├── __init__.py
│   ├── admin.py             # Configuración del admin
│   ├── apps.py
│   ├── forms.py             # Formularios ModelForm
│   ├── models.py            # Modelo Producto
│   ├── views.py             # Vistas CRUD con formularios
│   ├── urls.py              # URLs del inventario
│   ├── tests.py
│   ├── migrations/
│   │   └── 0001_initial.py  # Migración del modelo
│   └── templates/
│       └── inventario/
│           ├── base.html # 
│           ├── producto_list.html        # Vista de lista estándar
│           ├── producto_detail.html      # Vista de detalle estándar
│           ├── producto_form.html        # Formulario crear/editar
│           ├── producto_confirm_delete.html  # Confirmación eliminar
├── manage.py
├── create_sample_data.py    # Script para datos de ejemplo
└── db.sqlite3              # Base de datos SQLite
```

### URLs del Sistema
- `/` - Página de inicio
- `/inventario/productos/` - Lista de productos
- `/inventario/productos/nuevo/` - Crear nuevo producto
- `/inventario/productos/<id>/` - Detalle del producto
- `/inventario/productos/<id>/editar/` - Editar producto
- `/inventario/productos/<id>/eliminar/` - Eliminar producto
- `/admin/` - Panel de administración

---

## Instalación y Configuración

### 1. Activar el entorno virtual
```cmd
venv\Scripts\activate
```

### 2. Ejecutar migraciones
```cmd
python manage.py makemigrations
python manage.py migrate
```

### 3. Crear superusuario (opcional)
```cmd
python manage.py createsuperuser
```

### 4. Cargar datos de ejemplo
```cmd
python manage.py shell < create_sample_data.py
```

### 5. Iniciar servidor
```cmd
python manage.py runserver
```

---

## Introducción a CSRF

### ¿Qué significa CSRF?
**CSRF (Cross-Site Request Forgery)** es un tipo de ataque donde un sitio web malicioso puede ejecutar acciones no deseadas en nombre de un usuario autenticado en otro sitio web.

### Importancia en aplicaciones web
- Protege contra ataques automatizados
- Garantiza que las peticiones provienen del usuario legítimo
- Mantiene la integridad de los datos
- Es un requisito de seguridad estándar

---

## ¿Qué es un ataque CSRF?

### Escenario típico de ataque
1. **Usuario autenticado**: El usuario inicia sesión en `mibanco.com`
2. **Sitio malicioso**: El usuario visita `sitiomalicioso.com`
3. **Formulario oculto**: El sitio malicioso contiene un formulario que apunta a `mibanco.com`
4. **Ejecución automática**: Se ejecuta una transferencia sin que el usuario lo sepa

### Ejemplo de ataque
```html
<!-- Formulario malicioso en sitiomalicioso.com -->
<form action="https://mibanco.com/transferir" method="POST">
    <input type="hidden" name="cuenta_destino" value="atacante123">
    <input type="hidden" name="monto" value="1000">
    <input type="submit" value="¡Gana dinero fácil!">
</form>
```

### Consecuencias
- Transferencias no autorizadas
- Cambio de configuraciones
- Eliminación de datos
- Modificación de perfiles

---

## Protección CSRF en Django

### Middleware CSRF
Django incluye un middleware que protege automáticamente contra ataques CSRF:

```python
# settings.py
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',  # <- CSRF Middleware
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

### ¿Cómo funciona?
1. **Token único**: Se genera un token único por sesión
2. **Cookie segura**: Se almacena en una cookie
3. **Validación**: Cada petición POST debe incluir el token
4. **Comparación**: Django compara el token del formulario con el de la cookie

---

## Implementación práctica

### 1. Token CSRF en formularios HTML

```html
<!-- Forma básica -->
<form method="post">
    {% csrf_token %}
    <!-- campos del formulario -->
</form>

<!-- Lo que genera Django -->
<form method="post">
    <input type="hidden" name="csrfmiddlewaretoken" 
           value="abc123def456ghi789...">
    <!-- campos del formulario -->
</form>
```

### 2. Ejemplo completo en nuestro sistema de inventario

```html
<!-- producto_form.html -->
{% extends 'inventario/base.html' %}

{% block content %}
<div class="card">
    <div class="card-body">
        <form method="post" class="needs-validation" novalidate>
            {% csrf_token %}  <!-- <- Token CSRF obligatorio -->
            
            <!-- Campo Nombre -->
            <div class="mb-3">
                <label class="form-label">Nombre del Producto</label>
                {{ form.nombre }}
            </div>
            
            <!-- Campo Precio -->
            <div class="mb-3">
                <label class="form-label">Precio</label>
                <div class="input-group">
                    <span class="input-group-text">$</span>
                    {{ form.precio }}
                </div>
            </div>
            
            <button type="submit" class="btn btn-success">
                Guardar Producto
            </button>
        </form>
    </div>
</div>
{% endblock %}
```

### 3. Vista con protección CSRF

```python
# inventario/views.py
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render, redirect
from .forms import ProductoForm

@csrf_protect
def producto_create(request):
    """Vista protegida con CSRF"""
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            producto = form.save()
            messages.success(request, f'Producto "{producto.nombre}" creado exitosamente')
            return redirect('producto_list')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario')
    else:
        form = ProductoForm()
    
    return render(request, 'inventario/producto_form.html', {'form': form})
```

---

## Decoradores de seguridad

### @csrf_protect
Asegura que la vista tenga protección CSRF habilitada:

```python
from django.views.decorators.csrf import csrf_protect

@csrf_protect
def mi_vista(request):
    # Vista protegida contra CSRF
    pass
```

### @csrf_exempt
**USAR CON PRECAUCIÓN** - Deshabilita la protección CSRF:

```python
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def api_endpoint(request):
    # Vista SIN protección CSRF (solo para APIs específicas)
    pass
```

### @require_POST
Combina bien con CSRF para operaciones críticas:

```python
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect

@csrf_protect
@require_POST
def producto_delete(request, pk):
    """Solo acepta POST y con token CSRF válido"""
    producto = get_object_or_404(Producto, pk=pk)
    producto.activo = False
    producto.save()
    return redirect('producto_list')
```

---

## CSRF en peticiones AJAX

### Obtener el token CSRF en JavaScript

```javascript
// Función para obtener el token CSRF
function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}

// Alternativamente, desde las cookies
function getCSRFTokenFromCookie() {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'csrftoken') {
            return value;
        }
    }
    return null;
}
```

### Configurar AJAX con CSRF

```javascript
// Configuración global para fetch()
function setupCSRF() {
    const csrftoken = getCSRFToken();
    
    // Para todas las peticiones fetch
    window.fetch = new Proxy(window.fetch, {
        apply(target, thisArg, argumentsList) {
            const [url, options = {}] = argumentsList;
            
            if (options.method === 'POST') {
                options.headers = {
                    ...options.headers,
                    'X-CSRFToken': csrftoken
                };
            }
            
            return target.apply(thisArg, [url, options]);
        }
    });
}
```

### Ejemplo práctico de eliminación con AJAX

```javascript
// En nuestro sistema de inventario
function eliminarProducto(productId) {
    fetch(`/inventario/productos/${productId}/eliminar/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCSRFToken(),
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Remover el producto de la interfaz
            document.getElementById(`producto-${productId}`).remove();
            mostrarMensaje('Producto eliminado exitosamente', 'success');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        mostrarMensaje('Error al eliminar el producto', 'error');
    });
}
```

---

## Buenas prácticas

### DO - Hacer siempre
1. **Incluir CSRF token en todos los formularios POST**
   ```html
   <form method="post">
       {% csrf_token %}
       <!-- formulario -->
   </form>
   ```

2. **Usar @csrf_protect en vistas críticas**
   ```python
   @csrf_protect
   def vista_importante(request):
       pass
   ```

3. **Configurar AJAX correctamente**
   ```javascript
   headers: {
       'X-CSRFToken': getCSRFToken()
   }
   ```

4. **Validar en el servidor**
   ```python
   if request.method == 'POST':
       # Django valida automáticamente el token CSRF
       form = MiForm(request.POST)
   ```

### DON'T - Evitar siempre
1. **No usar @csrf_exempt sin justificación**
2. **No hacer peticiones POST sin token CSRF**
3. **No desactivar el middleware CSRF**
4. **No confiar solo en validación del cliente**

---

## Ejercicios prácticos

### Ejercicio 1: Implementar CSRF en formulario básico
**Objetivo**: Crear un formulario con protección CSRF completa

```html
<!-- templates/ejercicio1.html -->
{% extends 'base.html' %}

{% block content %}
<form method="post">
    <!-- TODO: Agregar token CSRF -->
    <div class="mb-3">
        <label class="form-label">Nombre:</label>
        <input type="text" name="nombre" class="form-control">
    </div>
    <button type="submit" class="btn btn-primary">Enviar</button>
</form>
{% endblock %}
```

**Solución**:
```html
<form method="post">
    {% csrf_token %}  <!-- <- Solución -->
    <!-- resto del formulario -->
</form>
```

### Ejercicio 2: Vista con decoradores de seguridad
**Objetivo**: Proteger una vista de eliminación

```python
# views.py - Versión inicial (insegura)
def eliminar_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    item.delete()
    return redirect('lista_items')
```

**Solución mejorada**:
```python
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST

@csrf_protect
@require_POST
def eliminar_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    item.delete()
    messages.success(request, 'Item eliminado exitosamente')
    return redirect('lista_items')
```

### Ejercicio 3: AJAX con CSRF
**Objetivo**: Implementar eliminación por AJAX con protección CSRF

```javascript
// Código inicial (inseguro)
function eliminar(id) {
    fetch(`/eliminar/${id}/`, {
        method: 'POST'
    });
}
```

**Solución segura**:
```javascript
function eliminar(id) {
    fetch(`/eliminar/${id}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCSRFToken(),
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        }
    });
}
```

---

## Debugging CSRF

### Errores comunes y soluciones

#### Error: "CSRF token missing or incorrect"
**Causas**:
- Falta `{% csrf_token %}` en el formulario
- Token expirado
- Cookies deshabilitadas

**Soluciones**:
```html
<!-- Verificar que existe el token -->
<form method="post">
    {% csrf_token %}
    <!-- formulario -->
</form>

<!-- Verificar en el HTML generado -->
<input type="hidden" name="csrfmiddlewaretoken" value="...">
```

#### Error en AJAX: "Forbidden (CSRF token missing)"
**Solución**:
```javascript
// Asegurar header correcto
headers: {
    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
}
```

### Herramientas de debugging

```python
# settings.py - Para desarrollo únicamente
if DEBUG:
    CSRF_FAILURE_VIEW = 'myapp.views.csrf_failure'
    
def csrf_failure(request, reason=""):
    """Vista personalizada para errores CSRF"""
    print(f"CSRF Error: {reason}")
    return render(request, 'csrf_error.html', {'reason': reason})
```

---

## Referencias y recursos adicionales

### Documentación oficial
- [Django CSRF Protection](https://docs.djangoproject.com/en/5.2/ref/csrf/)
- [Security in Django](https://docs.djangoproject.com/en/5.2/topics/security/)

### Herramientas útiles
- **DevTools del navegador**: Para verificar headers y cookies

### Lecturas complementarias
- OWASP CSRF Prevention Cheat Sheet
- Mozilla Web Security Guidelines
- Django Security Best Practices

---

## Checklist de seguridad CSRF

### Lista de verificación
- [ ] Middleware CSRF activado en `settings.py`
- [ ] `{% csrf_token %}` en todos los formularios POST
- [ ] Decoradores `@csrf_protect` en vistas críticas
- [ ] Headers CSRF en peticiones AJAX
- [ ] Validación de errores CSRF
- [ ] Tests de seguridad implementados
- [ ] Documentación actualizada

### Objetivos de aprendizaje alcanzados
Al completar esta clase, los estudiantes pueden:
- Explicar qué es CSRF y por qué es importante
- Implementar protección CSRF en formularios Django
- Usar decoradores de seguridad apropiados
- Configurar CSRF para peticiones AJAX
- Debuggear y solucionar errores CSRF
- Aplicar buenas prácticas de seguridad web

---

## Próximos pasos

### Unidad 2. Clase 01: Autenticación y autorización
- Sistema de usuarios de Django
- Login/Logout
- Permisos y grupos
- Decoradores de autenticación

---

**© 2025 - Clase 05: Crud en Django. Parte 2**  
*Programación Back End - INACAP*
*Instructor: SebaMorales74*

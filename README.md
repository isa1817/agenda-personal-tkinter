# 🗓️ Agenda Personal en Tkinter

Aplicación GUI desarrollada en **Python** con **Tkinter** que funciona como una agenda personal.  
Permite agregar, visualizar y eliminar eventos o tareas, incluyendo **fecha**, **hora** y **descripción**.

---

## 🚀 Funcionalidades

- **Interfaz gráfica amigable** con Tkinter.
- **Lista de eventos** en un `TreeView` con columnas: Fecha, Hora, Descripción.
- **Formulario de entrada** con campos para ingresar fecha, hora y descripción.
- **DatePicker integrado**:
  - Usa `tkcalendar.DateEntry` si está instalado.
  - Alternativa con `Combobox` si no se dispone de `tkcalendar`.
- **Botones de acción**:
  - Agregar evento.
  - Eliminar evento seleccionado (con confirmación).
  - Salir de la aplicación.
- **Organización con Frames** para mejor estructura.
- **Validaciones** de fecha (AAAA-MM-DD) y hora (HH:MM, 24h).
- **Persistencia**: guarda automáticamente los eventos en `agenda_data.json`.

---

## 🛠️ Requisitos

- Python 3.10 o superior.
- Tkinter (incluido en la instalación estándar de Python).
- (Opcional) [tkcalendar](https://pypi.org/project/tkcalendar/) para el calendario:

```bash
pip install tkcalendar

## 📸 Capturas de pantalla

### Vista inicial
![Vista inicial](captura1.png)

### Agregando un evento
![Agregando evento](captura2.png)

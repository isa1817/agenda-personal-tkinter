# -*- coding: utf-8 -*-
"""
Aplicación: Agenda Personal con Tkinter
Autoría: CELIA (con asistencia de IA)
Descripción:
    - Interfaz GUI con Tkinter.
    - Lista (Treeview) de eventos: Fecha, Hora, Descripción.
    - Campos de entrada y botones: Agregar, Eliminar seleccionado, Salir.
    - DatePicker:
        * Usa tkcalendar.DateEntry si está disponible.
        * Si no, usa un selector alternativo (Combobox día/mes/año).
    - Confirmación al eliminar (messagebox askyesno).
    - Organización por Frames.
    - Validación de fecha (AAAA-MM-DD) y hora (HH:MM 24h).
    - Persistencia simple en agenda_data.json (carga/guarda automático).

Requisitos opcionales:
    pip install tkcalendar   # Para tener el DatePicker tipo calendario

Ejecución:
    python agenda_personal.py
"""

import json
import os
import re
from datetime import datetime, date

import tkinter as tk
from tkinter import ttk, messagebox

# Intento de importar tkcalendar; si no existe, la app usa un selector alternativo.
try:
    from tkcalendar import DateEntry  # type: ignore
    TKCALENDAR_AVAILABLE = True
except Exception:
    TKCALENDAR_AVAILABLE = False


DATA_FILE = "agenda_data.json"


class AgendaApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Agenda Personal - CELIA")
        self.root.geometry("800x500")
        self.root.minsize(780, 480)

        # ---------- Contenedores (Frames) ----------
        # Frame principal para Treeview (lista de eventos)
        self.frame_lista = ttk.Frame(self.root, padding=(10, 10, 10, 0))
        self.frame_lista.pack(fill="both", expand=True)

        # Frame para entradas (fecha, hora, descripción)
        self.frame_form = ttk.LabelFrame(self.root, text="Nuevo evento", padding=10)
        self.frame_form.pack(fill="x", padx=10, pady=(8, 0))

        # Frame para botones de acción
        self.frame_botones = ttk.Frame(self.root, padding=10)
        self.frame_botones.pack(fill="x")

        # ---------- Treeview + Scrollbar ----------
        columnas = ("fecha", "hora", "descripcion")
        self.tree = ttk.Treeview(self.frame_lista, columns=columnas, show="headings", height=12)
        self.tree.heading("fecha", text="Fecha")
        self.tree.heading("hora", text="Hora")
        self.tree.heading("descripcion", text="Descripción")

        # Anchos relativos
        self.tree.column("fecha", width=120, anchor="center")
        self.tree.column("hora", width=90, anchor="center")
        self.tree.column("descripcion", width=520, anchor="w")

        scroll_y = ttk.Scrollbar(self.frame_lista, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scroll_y.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")

        # Expandir el Treeview cuando se redimensiona
        self.frame_lista.rowconfigure(0, weight=1)
        self.frame_lista.columnconfigure(0, weight=1)

        # ---------- Formulario de entrada ----------
        # Etiquetas
        ttk.Label(self.frame_form, text="Fecha:").grid(row=0, column=0, sticky="w", padx=(0, 8), pady=5)
        ttk.Label(self.frame_form, text="Hora (HH:MM):").grid(row=0, column=2, sticky="w", padx=(20, 8), pady=5)
        ttk.Label(self.frame_form, text="Descripción:").grid(row=1, column=0, sticky="w", padx=(0, 8), pady=5)

        # Selector de fecha (DatePicker con fallback)
        if TKCALENDAR_AVAILABLE:
            self.date_widget = DateEntry(
                self.frame_form,
                date_pattern="yyyy-mm-dd",
                firstweekday="monday",
                showweeknumbers=False,
                width=14
            )
            self.date_widget.set_date(date.today())
            self.date_widget.grid(row=0, column=1, sticky="w", pady=5)
        else:
            # Fallback: Combobox para día/mes/año
            # Año: rango actual +- 5 años (ajustable)
            year_now = date.today().year
            years = [str(y) for y in range(year_now - 5, year_now + 6)]
            months = [f"{m:02d}" for m in range(1, 13)]
            days = [f"{d:02d}" for d in range(1, 32)]

            self.cb_year = ttk.Combobox(self.frame_form, values=years, width=6, state="readonly")
            self.cb_month = ttk.Combobox(self.frame_form, values=months, width=4, state="readonly")
            self.cb_day = ttk.Combobox(self.frame_form, values=days, width=4, state="readonly")

            # Valores por defecto = hoy
            self.cb_year.set(str(year_now))
            self.cb_month.set(f"{date.today().month:02d}")
            self.cb_day.set(f"{date.today().day:02d}")

            # Ubicación en grilla
            self.cb_year.grid(row=0, column=1, sticky="w", pady=5)
            ttk.Label(self.frame_form, text="-").grid(row=0, column=1, sticky="w", padx=(60, 0))
            self.cb_month.grid(row=0, column=1, sticky="w", padx=(70, 0))
            ttk.Label(self.frame_form, text="-").grid(row=0, column=1, sticky="w", padx=(110, 0))
            self.cb_day.grid(row=0, column=1, sticky="w", padx=(120, 0))

        # Entrada de hora
        self.entry_hora = ttk.Entry(self.frame_form, width=12)
        self.entry_hora.insert(0, "08:00")
        self.entry_hora.grid(row=0, column=3, sticky="w", pady=5)

        # Entrada de descripción
        self.entry_desc = ttk.Entry(self.frame_form, width=80)
        self.entry_desc.grid(row=1, column=1, columnspan=3, sticky="we", pady=5)

        # ---------- Botones ----------
        self.btn_agregar = ttk.Button(self.frame_botones, text="Agregar Evento", command=self.agregar_evento)
        self.btn_eliminar = ttk.Button(self.frame_botones, text="Eliminar Evento Seleccionado", command=self.eliminar_evento)
        self.btn_salir = ttk.Button(self.frame_botones, text="Salir", command=self.salir)

        self.btn_agregar.pack(side="left", padx=(0, 10))
        self.btn_eliminar.pack(side="left", padx=10)
        self.btn_salir.pack(side="right")

        # Doble clic para seleccionar (opcional: futuro editar)
        self.tree.bind("<Double-1>", self._on_double_click)

        # Cargar datos previos si existen
        self.eventos = []
        self.cargar_desde_json()
        self.refrescar_tree()

    # ---------- Utilidades de fecha/hora ----------
    def _get_fecha_str(self) -> str:
        """Obtiene la fecha en formato AAAA-MM-DD desde el DatePicker (o fallback)."""
        if TKCALENDAR_AVAILABLE:
            return self.date_widget.get_date().strftime("%Y-%m-%d")
        else:
            y = self.cb_year.get().strip()
            m = self.cb_month.get().strip()
            d = self.cb_day.get().strip()
            return f"{y}-{m}-{d}"

    @staticmethod
    def validar_fecha(fecha_str: str) -> bool:
        """Valida formato y existencia de la fecha AAAA-MM-DD."""
        try:
            datetime.strptime(fecha_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    @staticmethod
    def validar_hora(hora_str: str) -> bool:
        """Valida hora en formato HH:MM (24h)."""
        if not re.match(r"^\d{2}:\d{2}$", hora_str):
            return False
        try:
            datetime.strptime(hora_str, "%H:%M")
            return True
        except ValueError:
            return False

    # ---------- Acciones ----------
    def agregar_evento(self):
        """Agrega un evento validando fecha, hora y descripción; actualiza la vista y guarda."""
        fecha = self._get_fecha_str()
        hora = self.entry_hora.get().strip()
        desc = self.entry_desc.get().strip()

        # Validaciones amigables
        if not self.validar_fecha(fecha):
            messagebox.showerror("Fecha inválida", "Por favor, ingresa una fecha válida en formato AAAA-MM-DD.")
            return

        if not self.validar_hora(hora):
            messagebox.showerror("Hora inválida", "Por favor, ingresa la hora en formato 24h HH:MM (ej. 08:30).")
            return

        if not desc:
            messagebox.showwarning("Descripción vacía", "La descripción no puede estar vacía.")
            return

        # Agregar al modelo en memoria
        self.eventos.append({"fecha": fecha, "hora": hora, "descripcion": desc})

        # Ordenar por fecha y hora para mantener la lista limpia
        self.eventos.sort(key=lambda e: (e["fecha"], e["hora"]))

        # Actualizar vista y limpiar campos
        self.refrescar_tree()
        self.entry_desc.delete(0, tk.END)

        # Guardar en archivo
        self.guardar_en_json()

    def eliminar_evento(self):
        """Elimina el evento seleccionado con diálogo de confirmación."""
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showinfo("Sin selección", "Selecciona un evento para eliminar.")
            return

        # Confirmación
        if not messagebox.askyesno("Confirmar eliminación", "¿Deseas eliminar el evento seleccionado?"):
            return

        # Obtener índices y eliminar del modelo
        indices_a_eliminar = []
        for item_id in seleccion:
            # El Treeview tiene el índice en 'values' o podemos usar .index()
            idx = int(self.tree.item(item_id, "tags")[0])  # Guardamos el índice como tag
            indices_a_eliminar.append(idx)

        # Eliminar de mayor a menor para no desfasar índices
        for idx in sorted(indices_a_eliminar, reverse=True):
            del self.eventos[idx]

        self.refrescar_tree()
        self.guardar_en_json()

    def salir(self):
        """Guarda y cierra la aplicación."""
        self.guardar_en_json()
        self.root.quit()

    def _on_double_click(self, _event):
        """(Opcional) En doble clic se podría prellenar para edición futura."""
        # Aquí podrías implementar edición si te lo piden en otra tarea.
        pass

    # ---------- Persistencia ----------
    def cargar_desde_json(self):
        """Carga eventos desde archivo JSON si existe."""
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        # Validar estructura mínima
                        self.eventos = [
                            e for e in data
                            if isinstance(e, dict) and {"fecha", "hora", "descripcion"} <= set(e.keys())
                        ]
            except Exception as e:
                messagebox.showwarning("Advertencia", f"No se pudo cargar {DATA_FILE}.\nDetalle: {e}")

    def guardar_en_json(self):
        """Guarda eventos al archivo JSON."""
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.eventos, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar {DATA_FILE}.\nDetalle: {e}")

    # ---------- Vista ----------
    def refrescar_tree(self):
        """Refresca la tabla con el contenido actual de eventos."""
        # Limpiar
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Rellenar (guardamos el índice real como 'tag' para ubicarlo luego)
        for idx, e in enumerate(self.eventos):
            self.tree.insert("", "end",
                             values=(e["fecha"], e["hora"], e["descripcion"]),
                             tags=(str(idx),))


def main():
    root = tk.Tk()
    # Tema visual (opcional): usar estilo 'clam' si está disponible
    try:
        style = ttk.Style()
        style.theme_use("clam")
    except Exception:
        pass
    app = AgendaApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

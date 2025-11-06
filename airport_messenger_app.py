import tkinter as tk
from tkinter import ttk, messagebox
from dataclasses import dataclass, asdict
from typing import Dict, Any, List

# ------------------------------
# Domain: rules + templates
# ------------------------------
RULES = {
    "forbidden": ["panic", "blame", "speculation", "jargon for passengers: METAR, TAF, NOTAM"],
    "event_types": {
        "weather": {
            "phrases": {
                "passenger": [
                    "due to adverse weather",
                    "your safety is our priority",
                    "we appreciate your patience",
                ],
                "pilot": [
                    "expect delay due to weather in departure/arrival sector",
                    "monitor ATC advisory",
                ],
                "staff": [
                    "coordinate gate and crew availability",
                    "update displays and inform gate agents",
                ],
            }
        },
        "runway": {
            "phrases": {
                "passenger": ["runway availability constraints"],
                "pilot": ["runway closure/restriction in effect"],
                "staff": ["redirect ground operations"],
            }
        },
        "technical": {
            "phrases": {
                "passenger": ["aircraft requires a technical inspection", "for your safety"],
                "pilot": ["maintenance in progress; stand by for new ETD"],
                "staff": ["dispatch maintenance team and prepare equipment"],
            }
        },
    },
}

SEVERITIES = ["low", "medium", "high", "critical"]
EVENT_TYPES = list(RULES["event_types"].keys())

def _safe(lst: List[str], idx: int, default: str = "") -> str:
    try:
        return lst[idx]
    except Exception:
        return default

def generate_messages(event: Dict[str, Any]) -> Dict[str, str]:
    """
    Deterministic, template-based messages (no API keys needed).
    """
    etype = event.get("event_type", "")
    phrases = RULES["event_types"].get(etype, {}).get("phrases", {})
    passenger_p = phrases.get("passenger", [])
    pilot_p = phrases.get("pilot", [])
    staff_p = phrases.get("staff", [])

    flight_no = event.get("flight_no") or "N/A"
    dest = event.get("destination") or "your destination"
    gate = event.get("gate") or "the assigned gate"
    runway = event.get("runway") or "TBD"
    severity = event.get("severity") or "medium"
    eta = event.get("eta_change_minutes")
    eta_str = f"{eta} minutes" if eta else "TBD"
    notes = event.get("notes") or "N/A"

    passenger_msg = (
        f"Attention passengers: {_safe(passenger_p, 0, 'an operational delay')} "
        f"affecting flight {flight_no} to {dest}. "
        f"Estimated delay: {eta_str}. "
        f"{_safe(passenger_p, 1)}. {_safe(passenger_p, 2)} "
        f"Please remain near gate {gate} for updates. Thank you for your understanding."
    ).strip()

    pilot_msg = (
        f"{_safe(pilot_p, 0, 'operational delay in effect')} for {flight_no}. "
        f"Severity: {severity}. {_safe(pilot_p, 1)} "
        f"Runway: {runway}. Gate: {gate}. ETA change: {eta_str}. "
        f"Notes: {notes}."
    ).strip()

    staff_msg = (
        f"Action required: event={etype}, severity={severity} for flight {flight_no}. "
        f"- Gate: {gate}, Runway: {runway}, ETA change: {eta_str}. "
        f"- Tasks: {_safe(staff_p, 0, 'coordinate impacted teams')}, "
        f"{_safe(staff_p, 1, 'notify affected parties')}. "
        f"- Comms: update FIDS, inform AOCC, and document actions in the log."
    ).strip()

    outputs = {}
    for a in event.get("audiences", ["passenger", "pilot", "staff"]):
        if a == "passenger":
            outputs[a] = passenger_msg
        elif a == "pilot":
            outputs[a] = pilot_msg
        elif a == "staff":
            outputs[a] = staff_msg
    return outputs

# ------------------------------
# UI Helpers
# ------------------------------
def splitflap_animate(widget: tk.Text, text: str, delay_ms: int = 12):
    """
    Cute split-flap style: reveal text char-by-char, with slight stutter on spaces.
    """
    widget.configure(state="normal")
    widget.delete("1.0", tk.END)
    current = []

    def step(i: int):
        if i > len(text):
            widget.configure(state="disabled")
            return
        current_text = text[:i]
        widget.delete("1.0", tk.END)
        widget.insert(tk.END, current_text)
        widget.see(tk.END)
        # Slightly longer pause on whitespace for a 'flip' vibe
        ch = text[i - 1] if i > 0 else ""
        pause = delay_ms * (3 if ch in [" ", "\n", "\t"] else 1)
        widget.after(pause, lambda: step(i + 1))

    step(0)

@dataclass
class EventForm:
    event_type: str
    severity: str
    flight_no: str
    origin: str
    destination: str
    eta_change_minutes: int
    gate: str
    runway: str
    notes: str
    audience_passenger: bool
    audience_pilot: bool
    audience_staff: bool

    def to_event(self) -> Dict[str, Any]:
        audiences = []
        if self.audience_passenger:
            audiences.append("passenger")
        if self.audience_pilot:
            audiences.append("pilot")
        if self.audience_staff:
            audiences.append("staff")
        return {
            "event_type": self.event_type,
            "severity": self.severity,
            "flight_no": self.flight_no or None,
            "origin": self.origin or None,
            "destination": self.destination or None,
            "eta_change_minutes": int(self.eta_change_minutes) if str(self.eta_change_minutes).strip() else 0,
            "gate": self.gate or None,
            "runway": self.runway or None,
            "language": "en",
            "audiences": audiences or ["passenger", "pilot", "staff"],
            "notes": self.notes or None,
        }

# ------------------------------
# Tkinter App
# ------------------------------
class AirportApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Airport Disruption Messenger ✈️")
        self.geometry("1060x720")
        self.configure(bg="#0b1220")  # dark/navy
        self.style = ttk.Style(self)
        try:
            self.style.theme_use("clam")
        except:
            pass

        # Global style tweaks
        self.style.configure("TLabel", foreground="#e6edf3", background="#0b1220")
        self.style.configure("TCheckbutton", foreground="#e6edf3", background="#0b1220")
        self.style.configure("TButton", padding=6)
        self.style.configure("TEntry", fieldbackground="#0f172a")
        self.style.configure("TCombobox", fieldbackground="#0f172a")

        # Header
        header = ttk.Label(self, text="Airport Disruption Messenger",
                           font=("Segoe UI", 20, "bold"))
        header.pack(pady=(16, 10))

        # Controls frame
        frm = ttk.Frame(self)
        frm.pack(fill="x", padx=16)

        # Left column: inputs
        left = ttk.Frame(frm)
        left.grid(row=0, column=0, sticky="nwe", padx=(0, 8))
        right = ttk.Frame(frm)
        right.grid(row=0, column=1, sticky="nwe", padx=(8, 0))

        frm.grid_columnconfigure(0, weight=1)
        frm.grid_columnconfigure(1, weight=1)

        # Inputs
        def labeled(parent, text, row, widget):
            ttk.Label(parent, text=text).grid(row=row, column=0, sticky="w", pady=3)
            widget.grid(row=row, column=1, sticky="we", pady=3, padx=(6,0))
            parent.grid_columnconfigure(1, weight=1)

        self.event_type = tk.StringVar(value=EVENT_TYPES[0])
        self.severity = tk.StringVar(value="medium")
        self.flight_no = tk.StringVar(value="AI-320")
        self.origin = tk.StringVar(value="DEL")
        self.destination = tk.StringVar(value="BOM")
        self.eta_change = tk.StringVar(value="45")
        self.gate = tk.StringVar(value="A7")
        self.runway = tk.StringVar(value="09R")
        self.notes = tk.StringVar(value="Thunderstorm cells near departure path")

        labeled(left, "Event Type", 0, ttk.Combobox(left, textvariable=self.event_type, values=EVENT_TYPES, state="readonly"))
        labeled(left, "Severity", 1, ttk.Combobox(left, textvariable=self.severity, values=SEVERITIES, state="readonly"))
        labeled(left, "Flight No", 2, ttk.Entry(left, textvariable=self.flight_no))
        labeled(left, "Origin", 3, ttk.Entry(left, textvariable=self.origin))
        labeled(left, "Destination", 4, ttk.Entry(left, textvariable=self.destination))
        labeled(left, "ETA Change (min)", 5, ttk.Entry(left, textvariable=self.eta_change))
        labeled(left, "Gate", 6, ttk.Entry(left, textvariable=self.gate))
        labeled(left, "Runway", 7, ttk.Entry(left, textvariable=self.runway))
        labeled(left, "Notes", 8, ttk.Entry(left, textvariable=self.notes))

        # Audiences + behavior toggles
        self.aud_passenger = tk.BooleanVar(value=True)
        self.aud_pilot = tk.BooleanVar(value=True)
        self.aud_staff = tk.BooleanVar(value=True)
        self.instant_mode = tk.BooleanVar(value=True)  # Mode 1
        self.animated_mode = tk.BooleanVar(value=True) # Mode 2

        audience_box = ttk.LabelFrame(left, text="Audiences & Behavior", padding=8)
        audience_box.grid(row=9, column=0, columnspan=2, sticky="we", pady=(8, 0))
        ttk.Checkbutton(audience_box, text="Passenger", variable=self.aud_passenger).grid(row=0, column=0, sticky="w", padx=(0,12))
        ttk.Checkbutton(audience_box, text="Pilot", variable=self.aud_pilot).grid(row=0, column=1, sticky="w", padx=(0,12))
        ttk.Checkbutton(audience_box, text="Staff", variable=self.aud_staff).grid(row=0, column=2, sticky="w", padx=(0,12))

        ttk.Checkbutton(audience_box, text="Instant Generate", variable=self.instant_mode).grid(row=1, column=0, sticky="w", pady=(6,0))
        ttk.Checkbutton(audience_box, text="Animated Flip", variable=self.animated_mode).grid(row=1, column=1, sticky="w", pady=(6,0))

        # Buttons
        btns = ttk.Frame(left)
        btns.grid(row=10, column=0, columnspan=2, sticky="we", pady=10)
        ttk.Button(btns, text="Generate", command=self.on_generate).pack(side="left")
        ttk.Button(btns, text="Clear", command=self.on_clear).pack(side="left", padx=6)

        # Right column: outputs (glass cards)
        def output_panel(parent, title):
            frame = tk.Frame(parent, bg="#0b1220", highlightbackground="#334155", highlightthickness=1)
            frame.pack(fill="both", expand=True, pady=8)
            lbl = tk.Label(frame, text=title, bg="#0b1220", fg="#93c5fd", font=("Segoe UI", 12, "bold"))
            lbl.pack(anchor="w", padx=8, pady=(6,2))
            txt = tk.Text(frame, wrap="word", height=8, bg="#0f172a", fg="#e6edf3", bd=0, insertbackground="#e6edf3")
            txt.pack(fill="both", expand=True, padx=8, pady=8)
            txt.configure(state="disabled")
            return txt

        self.out_passenger = output_panel(right, "Passenger Message")
        self.out_pilot = output_panel(right, "Pilot Message")
        self.out_staff = output_panel(right, "Staff Message")

        # Footer
        footer = tk.Label(self, text="B+C UI — Airport board vibe + modern dashboard • © You, crushing it",
                          bg="#0b1220", fg="#64748b")
        footer.pack(pady=(2, 10))

    def form_data(self) -> EventForm:
        return EventForm(
            event_type=self.event_type.get(),
            severity=self.severity.get(),
            flight_no=self.flight_no.get(),
            origin=self.origin.get(),
            destination=self.destination.get(),
            eta_change_minutes=int(self.eta_change.get() or 0),
            gate=self.gate.get(),
            runway=self.runway.get(),
            notes=self.notes.get(),
            audience_passenger=self.aud_passenger.get(),
            audience_pilot=self.aud_pilot.get(),
            audience_staff=self.aud_staff.get(),
        )

    def on_generate(self):
        event = self.form_data().to_event()
        try:
            msgs = generate_messages(event)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        # Fill outputs
        def set_text(widget: tk.Text, text: str):
            if self.animated_mode.get():
                splitflap_animate(widget, text, delay_ms=10 if self.instant_mode.get() else 25)
            else:
                widget.configure(state="normal")
                widget.delete("1.0", tk.END)
                widget.insert(tk.END, text)
                widget.configure(state="disabled")

        set_text(self.out_passenger, msgs.get("passenger", ""))
        set_text(self.out_pilot, msgs.get("pilot", ""))
        set_text(self.out_staff, msgs.get("staff", ""))

    def on_clear(self):
        for t in (self.out_passenger, self.out_pilot, self.out_staff):
            t.configure(state="normal")
            t.delete("1.0", tk.END)
            t.configure(state="disabled")

if __name__ == "__main__":
    app = AirportApp()
    app.mainloop()

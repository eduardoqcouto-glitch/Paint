"""
ETo Calculator - Reference Evapotranspiration (FAO-56 Penman-Monteith method)
===============================================================================

This program calculates ETo, the amount of water (in millimeters per day)
that a well-watered reference grass surface would lose to the atmosphere
through evaporation and plant transpiration on a given day. It is the
standard starting point for irrigation scheduling in agriculture: the water
needs of a real crop are found by multiplying ETo by a crop-specific factor
(Kc) that depends on the crop and its growth stage.

The math implemented here is the FAO-56 Penman-Monteith equation, which is
the internationally standardized, practical form of the general
Penman-Monteith combination equation:

            0.408 * Delta * (Rn - G) + gamma * [900 / (T + 273)] * u2 * (es - ea)
    ETo = ------------------------------------------------------------------------
                        Delta + gamma * (1 + 0.34 * u2)

All the inputs you type in (temperature, humidity, wind, sunshine, location,
date) are used to work out every term of that formula automatically -
you never need to look up Delta, gamma, Rn, es or ea yourself.

Reference:
Allen, R.G., Pereira, L.S., Raes, D., Smith, M. (1998). Crop
Evapotranspiration - Guidelines for computing crop water requirements.
FAO Irrigation and Drainage Paper 56. Food and Agriculture Organization
of the United Nations, Rome.

Run this file directly to open the calculator window:
    python ETo_Calculator.py
"""

import math
import csv
import os
from datetime import date
import tkinter as tk
from tkinter import ttk, messagebox


# ---------------------------------------------------------------------------
# 1) THE SCIENCE - pure calculation functions (no GUI code in here at all,
#    so these can be tested or reused independently of the window below).
# ---------------------------------------------------------------------------

GSC = 0.0820        # Solar constant, MJ m-2 min-1
SIGMA = 4.903e-9    # Stefan-Boltzmann constant, MJ K-4 m-2 day-1
ALBEDO = 0.23       # Reference crop (grass) albedo


def saturation_vapour_pressure(temp_c):
    """Saturation vapour pressure (kPa) at a given air temperature (deg C)."""
    return 0.6108 * math.exp((17.27 * temp_c) / (temp_c + 237.3))


def slope_of_saturation_curve(temp_mean_c):
    """Delta: slope of the saturation vapour pressure curve, kPa/deg C."""
    es_mean = saturation_vapour_pressure(temp_mean_c)
    return (4098 * es_mean) / ((temp_mean_c + 237.3) ** 2)


def atmospheric_pressure(elevation_m):
    """Atmospheric pressure (kPa) as a function of elevation above sea level."""
    return 101.3 * (((293 - 0.0065 * elevation_m) / 293) ** 5.26)


def psychrometric_constant(pressure_kpa):
    """gamma: psychrometric constant, kPa/deg C."""
    return 0.000665 * pressure_kpa


def wind_speed_at_2m(u_z, z_m):
    """
    Convert a wind speed measured at height z_m (meters) to the equivalent
    speed at the standard 2 m height used by the FAO-56 equation.
    """
    if abs(z_m - 2.0) < 1e-9:
        return u_z
    return u_z * (4.87 / math.log(67.8 * z_m - 5.42))


def day_of_year(day, month, year):
    return date(year, month, day).timetuple().tm_yday


def extraterrestrial_radiation(latitude_deg, doy):
    """
    Ra: extraterrestrial radiation (MJ m-2 day-1) - the solar radiation that
    would reach a horizontal surface at the top of the atmosphere. Also
    returns N, the maximum possible daylight hours for that latitude/date.
    """
    phi = math.radians(latitude_deg)
    dr = 1 + 0.033 * math.cos((2 * math.pi / 365) * doy)
    decl = 0.409 * math.sin((2 * math.pi / 365) * doy - 1.39)

    # Guard against the tan(phi)*tan(decl) argument to arccos drifting just
    # outside [-1, 1] due to floating point error at extreme latitudes.
    x = -math.tan(phi) * math.tan(decl)
    x = max(-1.0, min(1.0, x))
    sunset_hour_angle = math.acos(x)

    ra = ((24 * 60 / math.pi) * GSC * dr *
          (sunset_hour_angle * math.sin(phi) * math.sin(decl) +
           math.cos(phi) * math.cos(decl) * math.sin(sunset_hour_angle)))

    max_daylight_hours = (24 / math.pi) * sunset_hour_angle
    return ra, max_daylight_hours


def solar_radiation_from_sunshine(sunshine_hours, max_daylight_hours, ra):
    """Rs: incoming solar radiation estimated from measured sunshine hours."""
    a_s, b_s = 0.25, 0.50
    return (a_s + b_s * (sunshine_hours / max_daylight_hours)) * ra


def net_radiation(rs, ra, elevation_m, tmax_c, tmin_c, ea_kpa):
    """
    Rn: net radiation (MJ m-2 day-1) = net shortwave (Rns) - net longwave (Rnl).
    """
    rns = (1 - ALBEDO) * rs

    rso = (0.75 + 2e-5 * elevation_m) * ra  # clear-sky radiation
    rso = max(rso, 0.0001)
    rs_rso_ratio = min(rs / rso, 1.0)  # cap at 1.0 (Rs can't exceed clear-sky)

    tmax_k4 = (tmax_c + 273.16) ** 4
    tmin_k4 = (tmin_c + 273.16) ** 4

    rnl = (SIGMA * ((tmax_k4 + tmin_k4) / 2) *
           (0.34 - 0.14 * math.sqrt(max(ea_kpa, 0))) *
           (1.35 * rs_rso_ratio - 0.35))

    return rns - rnl, rns, rnl, rso


def calculate_eto(latitude_deg, elevation_m, day, month, year,
                   tmax_c, tmin_c, rh_max, rh_min,
                   wind_speed, wind_height_m,
                   rs_measured=None, sunshine_hours=None):
    """
    Runs the full FAO-56 Penman-Monteith calculation.

    Provide EITHER rs_measured (directly measured solar radiation, in
    MJ m-2 day-1) OR sunshine_hours (hours of bright sunshine that day) -
    whichever your weather data actually gives you.

    Returns a dictionary with the final ETo plus every intermediate value,
    so the GUI can display the full working, not just the final answer.
    """
    tmean = (tmax_c + tmin_c) / 2.0
    doy = day_of_year(day, month, year)

    # Vapour pressures
    es_tmax = saturation_vapour_pressure(tmax_c)
    es_tmin = saturation_vapour_pressure(tmin_c)
    es = (es_tmax + es_tmin) / 2.0
    ea = (es_tmin * (rh_max / 100.0) + es_tmax * (rh_min / 100.0)) / 2.0

    delta = slope_of_saturation_curve(tmean)
    pressure = atmospheric_pressure(elevation_m)
    gamma = psychrometric_constant(pressure)
    u2 = wind_speed_at_2m(wind_speed, wind_height_m)

    ra, max_daylight = extraterrestrial_radiation(latitude_deg, doy)

    if rs_measured is not None:
        rs = rs_measured
    elif sunshine_hours is not None:
        rs = solar_radiation_from_sunshine(sunshine_hours, max_daylight, ra)
    else:
        raise ValueError("Provide either measured solar radiation or sunshine hours.")

    rn, rns, rnl, rso = net_radiation(rs, ra, elevation_m, tmax_c, tmin_c, ea)
    g = 0.0  # soil heat flux is assumed negligible for daily calculations (FAO-56)

    numerator = 0.408 * delta * (rn - g) + gamma * (900 / (tmean + 273)) * u2 * (es - ea)
    denominator = delta + gamma * (1 + 0.34 * u2)
    eto = numerator / denominator

    return {
        "eto_mm_day": eto,
        "day_of_year": doy,
        "tmean_c": tmean,
        "es_kpa": es,
        "ea_kpa": ea,
        "vpd_kpa": es - ea,
        "delta": delta,
        "pressure_kpa": pressure,
        "gamma": gamma,
        "u2_m_s": u2,
        "ra_mj_m2_day": ra,
        "max_daylight_hours": max_daylight,
        "rs_mj_m2_day": rs,
        "rso_mj_m2_day": rso,
        "rns_mj_m2_day": rns,
        "rnl_mj_m2_day": rnl,
        "rn_mj_m2_day": rn,
        "g_mj_m2_day": g,
    }


# ---------------------------------------------------------------------------
# 2) THE WINDOW - the part your grandpa actually sees and uses.
# ---------------------------------------------------------------------------

class EToApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ETo Calculator - Crop Water Use (FAO-56 Penman-Monteith)")
        self.resizable(True, True)

        # Cap the initial window height to the screen, so it never opens
        # taller than the user's monitor - the content inside still scrolls.
        width = 600
        height = min(760, self.winfo_screenheight() - 100)
        self.geometry(f"{width}x{height}")
        self.minsize(480, 300)

        self.log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                      "ETo_results_log.csv")

        self.rs_mode = tk.StringVar(value="sunshine")  # "sunshine" or "measured"

        self._build_layout()
        self._load_example_values()

    # -- scrollable layout ------------------------------------------------
    def _build_layout(self):
        # Everything is placed inside a scrollable canvas so the window can
        # be resized freely, or the mouse wheel used, without ever hiding
        # the result at the bottom.
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)

        canvas = tk.Canvas(container, borderwidth=0, highlightthickness=0)
        vscroll = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vscroll.set)
        vscroll.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        pad = {"padx": 6, "pady": 4}
        main = ttk.Frame(canvas, padding=12)
        main_window = canvas.create_window((0, 0), window=main, anchor="nw")

        def _on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        main.bind("<Configure>", _on_frame_configure)

        def _on_canvas_configure(event):
            canvas.itemconfig(main_window, width=event.width)
        canvas.bind("<Configure>", _on_canvas_configure)

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def _bind_mousewheel(_event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)

        def _unbind_mousewheel(_event):
            canvas.unbind_all("<MouseWheel>")

        # Only scroll with the wheel while the pointer is actually over this
        # window's canvas, so it doesn't hijack scrolling elsewhere.
        canvas.bind("<Enter>", _bind_mousewheel)
        canvas.bind("<Leave>", _unbind_mousewheel)

        title = ttk.Label(main, text="Reference Evapotranspiration (ETo) Calculator",
                           font=("Segoe UI", 13, "bold"))
        title.grid(row=0, column=0, columnspan=4, pady=(0, 2), sticky="w")
        subtitle = ttk.Label(
            main,
            text="Enter today's weather and field location below, then press Calculate.",
            font=("Segoe UI", 9))
        subtitle.grid(row=1, column=0, columnspan=4, pady=(0, 10), sticky="w")

        r = 2
        r = self._section(main, r, "Field Location & Date")
        self.lat = self._entry(main, r, "Latitude (degrees, negative = South)")
        self.elev = self._entry(main, r + 1, "Elevation above sea level (m)")
        r += 2

        date_frame = ttk.Frame(main)
        date_frame.grid(row=r, column=0, columnspan=4, sticky="w", **pad)
        ttk.Label(date_frame, text="Date:").pack(side="left")
        self.day = tk.StringVar()
        self.month = tk.StringVar()
        self.year = tk.StringVar()
        ttk.Entry(date_frame, width=4, textvariable=self.day).pack(side="left", padx=(6, 2))
        ttk.Label(date_frame, text="/").pack(side="left")
        ttk.Entry(date_frame, width=4, textvariable=self.month).pack(side="left", padx=2)
        ttk.Label(date_frame, text="/").pack(side="left")
        ttk.Entry(date_frame, width=6, textvariable=self.year).pack(side="left", padx=(2, 6))
        ttk.Label(date_frame, text="(Day / Month / Year)").pack(side="left")
        r += 1

        r = self._section(main, r, "Temperature")
        self.tmax = self._entry(main, r, "Maximum temperature today (deg C)")
        self.tmin = self._entry(main, r + 1, "Minimum temperature today (deg C)")
        r += 2

        r = self._section(main, r, "Humidity")
        self.rhmax = self._entry(main, r, "Maximum relative humidity (%)")
        self.rhmin = self._entry(main, r + 1,
                                  "Minimum relative humidity (%)  -  if you only have one "
                                  "humidity reading, enter it in both boxes")
        r += 2

        r = self._section(main, r, "Wind")
        self.wind = self._entry(main, r, "Wind speed (m/s)")
        self.wind_height = self._entry(main, r + 1, "Height of wind measurement above ground (m)")
        r += 2

        r = self._section(main, r, "Sunlight")
        radio_frame = ttk.Frame(main)
        radio_frame.grid(row=r, column=0, columnspan=4, sticky="w", **pad)
        ttk.Radiobutton(radio_frame, text="I know the hours of bright sunshine today",
                         variable=self.rs_mode, value="sunshine",
                         command=self._toggle_rs_mode).pack(anchor="w")
        ttk.Radiobutton(radio_frame, text="I know the measured solar radiation directly",
                         variable=self.rs_mode, value="measured",
                         command=self._toggle_rs_mode).pack(anchor="w")
        r += 1
        self.sunshine = self._entry(main, r, "Hours of bright sunshine today (hours)")
        self.rs_measured = self._entry(main, r + 1,
                                        "Measured solar radiation (MJ per m2 per day)")
        r += 2

        btn_frame = ttk.Frame(main)
        btn_frame.grid(row=r, column=0, columnspan=4, pady=(10, 6))
        ttk.Button(btn_frame, text="Calculate", command=self._on_calculate).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Load example", command=self._load_example_values).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Clear all", command=self._clear_all).pack(side="left", padx=4)
        r += 1

        result_frame = ttk.LabelFrame(main, text="Result", padding=10)
        result_frame.grid(row=r, column=0, columnspan=4, sticky="ew", pady=(4, 0))
        self.result_headline = ttk.Label(result_frame, text="",
                                          font=("Segoe UI", 14, "bold"))
        self.result_headline.pack(anchor="w")
        self.result_detail = tk.Text(result_frame, width=70, height=10,
                                      font=("Consolas", 9), state="disabled",
                                      relief="flat", background=self.cget("background"))
        self.result_detail.pack(fill="x", pady=(6, 6))
        ttk.Button(result_frame, text="Save this result to log file (CSV)",
                   command=self._save_to_log).pack(anchor="w")

        self._toggle_rs_mode()

    def _section(self, parent, row, text):
        ttk.Separator(parent, orient="horizontal").grid(
            row=row, column=0, columnspan=4, sticky="ew", pady=(10, 2))
        ttk.Label(parent, text=text, font=("Segoe UI", 10, "bold")).grid(
            row=row + 1, column=0, columnspan=4, sticky="w", pady=(0, 4))
        return row + 2

    def _entry(self, parent, row, label_text):
        ttk.Label(parent, text=label_text).grid(row=row, column=0, sticky="w",
                                                  padx=6, pady=3)
        var = tk.StringVar()
        ttk.Entry(parent, textvariable=var, width=14).grid(
            row=row, column=1, sticky="w", padx=6, pady=3)
        return var

    def _toggle_rs_mode(self):
        # Nothing to enable/disable structurally; just a visual hint via
        # focus. Kept simple - both fields stay visible, only the selected
        # one needs to be filled in.
        pass

    # -- example / clear ------------------------------------------------
    def _load_example_values(self):
        today = date.today()
        self.lat.set("-23.5")
        self.elev.set("760")
        self.day.set(str(today.day))
        self.month.set(str(today.month))
        self.year.set(str(today.year))
        self.tmax.set("29.0")
        self.tmin.set("18.0")
        self.rhmax.set("82")
        self.rhmin.set("45")
        self.wind.set("2.0")
        self.wind_height.set("2")
        self.rs_mode.set("sunshine")
        self.sunshine.set("8.5")
        self.rs_measured.set("")

    def _clear_all(self):
        for var in (self.lat, self.elev, self.day, self.month, self.year,
                    self.tmax, self.tmin, self.rhmax, self.rhmin,
                    self.wind, self.wind_height, self.sunshine, self.rs_measured):
            var.set("")

    # -- calculate --------------------------------------------------------
    def _on_calculate(self):
        try:
            latitude = float(self.lat.get())
            elevation = float(self.elev.get())
            day = int(self.day.get())
            month = int(self.month.get())
            year = int(self.year.get())
            tmax = float(self.tmax.get())
            tmin = float(self.tmin.get())
            rhmax = float(self.rhmax.get())
            rhmin = float(self.rhmin.get())
            wind = float(self.wind.get())
            wind_height = float(self.wind_height.get())

            rs_measured = None
            sunshine = None
            if self.rs_mode.get() == "measured":
                rs_measured = float(self.rs_measured.get())
            else:
                sunshine = float(self.sunshine.get())

            if tmin > tmax:
                raise ValueError("Minimum temperature is higher than maximum temperature.")
            if not (-90 <= latitude <= 90):
                raise ValueError("Latitude must be between -90 and 90 degrees.")

        except ValueError as exc:
            messagebox.showerror("Check your inputs", f"There's a problem with the "
                                  f"values entered:\n\n{exc}\n\nPlease make sure every "
                                  f"box has a valid number.")
            return
        except Exception:
            messagebox.showerror("Check your inputs",
                                  "Please make sure every box has a valid number, "
                                  "and the date is a real calendar date.")
            return

        try:
            self.last_result = calculate_eto(
                latitude_deg=latitude, elevation_m=elevation,
                day=day, month=month, year=year,
                tmax_c=tmax, tmin_c=tmin, rh_max=rhmax, rh_min=rhmin,
                wind_speed=wind, wind_height_m=wind_height,
                rs_measured=rs_measured, sunshine_hours=sunshine,
            )
        except Exception as exc:
            messagebox.showerror("Calculation error", str(exc))
            return

        res = self.last_result
        self.result_headline.config(
            text=f"ETo = {res['eto_mm_day']:.2f} mm/day  "
                 f"(reference crop water use for this day)")

        detail_lines = [
            f"Day of year:                    {res['day_of_year']}",
            f"Mean temperature:               {res['tmean_c']:.2f} deg C",
            f"Saturation vapour pressure (es): {res['es_kpa']:.3f} kPa",
            f"Actual vapour pressure (ea):     {res['ea_kpa']:.3f} kPa",
            f"Vapour pressure deficit:         {res['vpd_kpa']:.3f} kPa",
            f"Slope of vapour curve (Delta):   {res['delta']:.4f} kPa/degC",
            f"Atmospheric pressure:            {res['pressure_kpa']:.2f} kPa",
            f"Psychrometric constant (gamma):  {res['gamma']:.5f} kPa/degC",
            f"Wind speed at 2m (u2):           {res['u2_m_s']:.2f} m/s",
            f"Extraterrestrial radiation (Ra): {res['ra_mj_m2_day']:.2f} MJ/m2/day",
            f"Max possible daylight hours:     {res['max_daylight_hours']:.2f} hours",
            f"Solar radiation used (Rs):       {res['rs_mj_m2_day']:.2f} MJ/m2/day",
            f"Clear-sky radiation (Rso):       {res['rso_mj_m2_day']:.2f} MJ/m2/day",
            f"Net shortwave radiation (Rns):   {res['rns_mj_m2_day']:.2f} MJ/m2/day",
            f"Net longwave radiation (Rnl):    {res['rnl_mj_m2_day']:.2f} MJ/m2/day",
            f"Net radiation (Rn):              {res['rn_mj_m2_day']:.2f} MJ/m2/day",
            f"Soil heat flux (G, assumed):     {res['g_mj_m2_day']:.2f} MJ/m2/day",
        ]
        self.result_detail.config(state="normal")
        self.result_detail.delete("1.0", "end")
        self.result_detail.insert("1.0", "\n".join(detail_lines))
        self.result_detail.config(state="disabled")

    # -- logging ----------------------------------------------------------
    def _save_to_log(self):
        if not hasattr(self, "last_result"):
            messagebox.showinfo("Nothing to save", "Press Calculate first.")
            return

        res = self.last_result
        file_exists = os.path.isfile(self.log_path)
        try:
            with open(self.log_path, "a", newline="") as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(["date_entered", "latitude", "elevation_m",
                                      "day", "month", "year", "tmax_c", "tmin_c",
                                      "rh_max", "rh_min", "wind_m_s", "eto_mm_day"])
                writer.writerow([
                    date.today().isoformat(), self.lat.get(), self.elev.get(),
                    self.day.get(), self.month.get(), self.year.get(),
                    self.tmax.get(), self.tmin.get(), self.rhmax.get(),
                    self.rhmin.get(), self.wind.get(), f"{res['eto_mm_day']:.2f}",
                ])
            messagebox.showinfo("Saved", f"Result appended to:\n{self.log_path}")
        except Exception as exc:
            messagebox.showerror("Could not save", str(exc))


if __name__ == "__main__":
    app = EToApp()
    app.mainloop()

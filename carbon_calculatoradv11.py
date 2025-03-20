import flet as ft
import json
import logging
import os
from datetime import datetime
import csv
from fpdf import FPDF  # For PDF export
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Language dictionaries (with Telugu and Tamil)
LANGUAGES = {
    "en": {
        "title": "Carbon Footprint Calculator",
        "electricity": "Monthly Electricity Usage",
        "gas": "Monthly Natural Gas Usage",
        "water": "Monthly Water Usage",
        "kilometers": "Monthly Kilometers Driven",
        "flights": "Number of Flights per Year",
        "food": "Monthly Meat Consumption",
        "calculate": "Calculate",
        "reset": "Reset",
        "save": "Save",
        "load": "Load",
        "export_csv": "Export CSV",
        "export_pdf": "Export PDF",
        "total": "Total Carbon Footprint",
        "about": "About",
        "theme": "Switch Theme",
        "language": "Language",
        "region": "Region",
        "offset": "Carbon Offset Suggestion"
    },
    "hi": {
        "title": "कार्बन फुटप्रिंट कैलकुलेटर",
        "electricity": "मासिक बिजली उपयोग",
        "gas": "मासिक प्राकृतिक गैस उपयोग",
        "water": "मासिक पानी उपयोग",
        "kilometers": "मासिक किलोमीटर ड्राइव",
        "flights": "प्रति वर्ष उड़ानों की संख्या",
        "food": "मासिक मांस खपत",
        "calculate": "गणना करें",
        "reset": "रीसेट करें",
        "save": "सहेजें",
        "load": "लोड करें",
        "export_csv": "CSV निर्यात करें",
        "export_pdf": "PDF निर्यात करें",
        "total": "कुल कार्बन फुटप्रिंट",
        "about": "के बारे में",
        "theme": "थीम बदलें",
        "language": "भाषा",
        "region": "क्षेत्र",
        "offset": "कार्बन ऑफसेट सुझाव"
    },
    "es": {
        "title": "Calculadora de Huella de Carbono",
        "electricity": "Uso Mensual de Electricidad",
        "gas": "Uso Mensual de Gas Natural",
        "water": "Uso Mensual de Agua",
        "kilometers": "Kilómetros Conducidos al Mes",
        "flights": "Número de Vuelos por Año",
        "food": "Consumo Mensual de Carne",
        "calculate": "Calcular",
        "reset": "Reiniciar",
        "save": "Guardar",
        "load": "Cargar",
        "export_csv": "Exportar CSV",
        "export_pdf": "Exportar PDF",
        "total": "Huella de Carbono Total",
        "about": "Acerca de",
        "theme": "Cambiar Tema",
        "language": "Idioma",
        "region": "Región",
        "offset": "Sugerencia de Compensación de Carbono"
    },
    "te": {  # Telugu
        "title": "కార్బన్ ఫుట్‌ప్రింట్ కాలిక్యులేటర్",
        "electricity": "నెలవారీ విద్యుత్ వినియోగం",
        "gas": "నెలవారీ సహజ వాయు వినియోగం",
        "water": "నెలవారీ నీటి వినియోగం",
        "kilometers": "నెలవారీ కిలోమీటర్లు డ్రైవ్ చేయబడ్డాయి",
        "flights": "సంవత్సరానికి విమానాల సంఖ్య",
        "food": "నెలవారీ మాంసం వినియోగం",
        "calculate": "లెక్కించు",
        "reset": "రీసెట్",
        "save": "సేవ్",
        "load": "లోడ్",
        "export_csv": "CSV ఎగుమతి",
        "export_pdf": "PDF ఎగుమతి",
        "total": "మొత్తం కార్బన్ ఫుట్‌ప్రింట్",
        "about": "గురించి",
        "theme": "థీమ్ మార్చు",
        "language": "భాష",
        "region": "ప్రాంతం",
        "offset": "కార్బన్ ఆఫ్‌సెట్ సూచన"
    },
    "ta": {  # Tamil
        "title": "கார்பன் பாதச்சுவடு கால்குலேட்டர்",
        "electricity": "மாதாந்திர மின்சார பயன்பாடு",
        "gas": "மாதாந்திர இயற்கை எரிவாயு பயன்பாடு",
        "water": "மாதாந்திர நீர் பயன்பாடு",
        "kilometers": "மாதாந்திர கிலோமீட்டர் ஓட்டப்பட்டது",
        "flights": "ஆண்டுக்கு விமானங்களின் எண்ணிக்கை",
        "food": "மாதாந்திர இறைச்சி உட்கொள்ளல்",
        "calculate": "கணக்கிடு",
        "reset": "மீட்டமை",
        "save": "சேமி",
        "load": "ஏற்று",
        "export_csv": "CSV ஏற்றுமதி",
        "export_pdf": "PDF ஏற்றுமதி",
        "total": "மொத்த கார்பன் பாதச்சுவடு",
        "about": "பற்றி",
        "theme": "தீம் மாற்று",
        "language": "மொழி",
        "region": "பிராந்தியம்",
        "offset": "கார்பன் ஆஃப்செட் பரிந்துரை"
    }
}

# Regional emission factors
REGIONAL_FACTORS = {
    "US": {"electricity": 0.92, "gas": 5.3, "water": 0.00007, "kilometers": 0.245, "flights": 900, "food": 2.5},
    "EU": {"electricity": 0.60, "gas": 4.8, "water": 0.00005, "kilometers": 0.200, "flights": 850, "food": 2.0},
    "IN": {"electricity": 1.20, "gas": 5.5, "water": 0.00008, "kilometers": 0.280, "flights": 950, "food": 2.8}
}

async def main(page: ft.Page):
    # Initial setup
    current_lang = "en"
    current_region = "US"
    history = []  # For historical data tracking

    # Dynamic color scheme based on theme
    def get_colors(theme_mode):
        return {
            "background": ft.Colors.GREY_900 if theme_mode == ft.ThemeMode.DARK else ft.Colors.GREY_100,
            "container_bg": ft.Colors.GREY_800 if theme_mode == ft.ThemeMode.DARK else ft.Colors.GREY_200,
            "text": ft.Colors.WHITE if theme_mode == ft.ThemeMode.DARK else ft.Colors.BLACK,
            "label": ft.Colors.GREY_300 if theme_mode == ft.ThemeMode.DARK else ft.Colors.GREY_700,
            "hint": ft.Colors.GREY_500 if theme_mode == ft.ThemeMode.DARK else ft.Colors.GREY_400,
            "progress_bg": ft.Colors.GREY_800 if theme_mode == ft.ThemeMode.DARK else ft.Colors.GREY_300
        }

    colors = get_colors(page.theme_mode)

    # Page setup
    page.title = LANGUAGES[current_lang]["title"]
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 900
    page.window_height = 700
    page.window_min_width = 600
    page.window_min_height = 500
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 20
    page.bgcolor = colors["background"]

    # Custom theme
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=ft.Colors.TEAL_700,
            on_primary=ft.Colors.WHITE,
            secondary=ft.Colors.AMBER_700,
            background=colors["background"]
        )
    )

    # Header with language and theme switch
    header = ft.Row([
        ft.Icon(ft.Icons.ECO, color=ft.Colors.TEAL_400, size=40),
        ft.Text(LANGUAGES[current_lang]["title"], size=28, weight=ft.FontWeight.BOLD, color=colors["text"]),
        ft.Row([
            ft.Dropdown(
                width=120,
                options=[ft.dropdown.Option(k, v["language"]) for k, v in LANGUAGES.items()],
                value=current_lang,
                on_change=lambda e: change_language(e),
                tooltip="Select Language",
                text_style=ft.TextStyle(color=colors["text"]),
                bgcolor=colors["container_bg"]
            ),
            ft.IconButton(ft.Icons.BRIGHTNESS_6, tooltip="Toggle Theme", on_click=lambda e: asyncio.run(toggle_theme(e))),
            ft.IconButton(ft.Icons.INFO, tooltip="About", on_click=lambda e: show_about_dialog(page))
        ])
    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    # Input creation with real-time validation
    def create_input(label, hint, units, tooltip, colors):
        def validate_input(e):
            value = e.control.value
            if value and (not value.replace('.', '').isdigit() or float(value) < 0):
                e.control.error_text = "Enter a positive number"
            else:
                e.control.error_text = None
            page.update()

        return ft.Column([
            ft.Text(label, color=colors["label"]),
            ft.TextField(
                width=250,
                hint_text=hint,
                keyboard_type=ft.KeyboardType.NUMBER,
                suffix_text=units,
                border_color=ft.Colors.TEAL_200,
                text_style=ft.TextStyle(color=colors["text"]),
                hint_style=ft.TextStyle(color=colors["hint"]),
                tooltip=tooltip,
                border_radius=8,
                on_change=validate_input
            )
        ], spacing=8)

    # Inputs
    inputs = {
        "electricity": create_input(LANGUAGES[current_lang]["electricity"], "Enter kWh", "kWh", "Avg US: 900 kWh/month", colors),
        "gas": create_input(LANGUAGES[current_lang]["gas"], "Enter therms", "therms", "Avg US: 50 therms/month", colors),
        "water": create_input(LANGUAGES[current_lang]["water"], "Enter liters", "liters", "Avg: 300 liters/day", colors),
        "kilometers": create_input(LANGUAGES[current_lang]["kilometers"], "Enter km", "km", "Avg US: 1,600 km/month", colors),
        "flights": create_input(LANGUAGES[current_lang]["flights"], "Enter flights", "flights", "Avg US: 2 flights/year", colors),
        "food": create_input(LANGUAGES[current_lang]["food"], "Enter kg", "kg", "Avg US: 7 kg/month", colors)
    }

    # UI elements
    unit_switch = ft.Switch(label="Use Imperial Units", value=False, on_change=lambda e: toggle_units(e))
    region_dropdown = ft.Dropdown(
        width=120,
        options=[ft.dropdown.Option(k, k) for k in REGIONAL_FACTORS.keys()],
        value=current_region,
        label=LANGUAGES[current_lang]["region"],
        on_change=lambda e: change_region(e),
        text_style=ft.TextStyle(color=colors["text"]),
        bgcolor=colors["container_bg"]
    )
    result_text = ft.Text("", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.TEAL_400)
    individual_results = ft.Column(spacing=10, visible=False)
    offset_suggestion = ft.Text("", size=16, color=ft.Colors.GREEN_400)
    progress_bar = ft.ProgressBar(width=600, value=0, color=ft.Colors.TEAL_600, bgcolor=colors["progress_bg"])
    chart_container = ft.Container(width=600, height=400, bgcolor=colors["container_bg"], border_radius=10)
    chart_type_dropdown = ft.Dropdown(
        width=200,
        options=[ft.dropdown.Option("Pie", "Pie Chart"), ft.dropdown.Option("Bar", "Bar Chart")],
        value="Pie",
        label="Chart Type",
        text_style=ft.TextStyle(color=colors["text"]),
        bgcolor=colors["container_bg"]
    )
    history_dropdown = ft.Dropdown(
        width=200,
        options=[],
        label="Select Historical Data",
        on_change=lambda e: load_historical_data(e),
        text_style=ft.TextStyle(color=colors["text"]),
        bgcolor=colors["container_bg"]
    )

    # Conversion factors
    conversion_factors = {
        "metric": REGIONAL_FACTORS[current_region],
        "imperial": {k: v * (2.20462 if k == "food" else 1) for k, v in REGIONAL_FACTORS[current_region].items()}
    }

    # Calculate footprint with offset suggestion
    def calculate_footprint(e):
        try:
            values = [float(inputs[key].controls[1].value or 0) for key in inputs]
            if any(val < 0 for val in values):
                show_snack_bar(page, "Please enter non-negative values", ft.Colors.RED_700)
                return

            unit_system = "imperial" if unit_switch.value else "metric"
            factors = conversion_factors[unit_system]
            categories = ["Electricity", "Gas", "Water", "Driving", "Flights", "Food"]
            footprints = [values[i] * factors[list(inputs.keys())[i]] for i in range(len(values))]
            total_footprint = sum(footprints)

            trees_needed = total_footprint * 12 / 25
            offset_suggestion.value = f"{LANGUAGES[current_lang]['offset']}: Plant {trees_needed:.1f} trees per year"

            unit_label = "lbs CO2/month" if unit_switch.value else "kg CO2/month"
            result_text.value = f"{LANGUAGES[current_lang]['total']}: {total_footprint:.2f} {unit_label}"
            individual_results.controls = [
                ft.Text(f"{cat}: {val:.2f} {unit_label}", color=colors["label"])
                for cat, val in zip(categories, footprints)
            ]
            individual_results.visible = True
            progress_bar.value = min(total_footprint / (11000 if unit_switch.value else 5000), 1.0)

            update_chart(footprints, categories)
            history.append({"timestamp": datetime.now().isoformat(), "total": total_footprint, "values": values})
            update_history_dropdown()

            page.update()
            logger.info("Calculation completed")
        except ValueError as e:
            logger.error(f"Invalid input: {str(e)}")
            show_snack_bar(page, "Please enter valid numbers", ft.Colors.RED_700)
        except Exception as e:
            logger.error(f"Calculation error: {str(e)}")
            show_snack_bar(page, f"Error: {str(e)}", ft.Colors.RED_700)

    def update_chart(footprints, categories):
        colors_list = [ft.Colors.TEAL_400, ft.Colors.RED_400, ft.Colors.BLUE_400, ft.Colors.YELLOW_400, ft.Colors.PURPLE_400, ft.Colors.ORANGE_400]
        if chart_type_dropdown.value == "Pie":
            chart_container.content = ft.PieChart(
                sections=[ft.PieChartSection(value=max(val, 0.001), title=f"{cat}\n{val:.1f}", color=color, radius=150)
                         for val, cat, color in zip(footprints, categories, colors_list)],
                sections_space=2,
                center_space_radius=40
            )
        else:
            chart_container.content = ft.BarChart(
                bar_groups=[ft.BarChartGroup(x=i, bar_rods=[ft.BarChartRod(from_y=0, to_y=val, width=40, color=color)])
                           for i, (val, color) in enumerate(zip(footprints, colors_list))],
                bottom_axis=ft.ChartAxis(labels=[ft.ChartAxisLabel(value=i, label=ft.Text(cat, color=colors["text"])) for i, cat in enumerate(categories)]),
                left_axis=ft.ChartAxis(labels_size=40),
                tooltip_bgcolor=colors["container_bg"]
            )

    def toggle_units(e):
        units = {
            "metric": {"electricity": "kWh", "gas": "therms", "water": "liters", "kilometers": "km", "flights": "flights", "food": "kg"},
            "imperial": {"electricity": "kWh", "gas": "therms", "water": "gallons", "kilometers": "miles", "flights": "flights", "food": "lbs"}
        }
        unit_system = "imperial" if e.control.value else "metric"
        for key, input_field in inputs.items():
            input_field.controls[1].suffix_text = units[unit_system][key]
        calculate_footprint(None)
        page.update()

    def change_language(e):
        nonlocal current_lang
        current_lang = e.control.value
        update_ui_language()
        page.update()

    def change_region(e):
        nonlocal current_region
        current_region = e.control.value
        conversion_factors["metric"] = REGIONAL_FACTORS[current_region]
        conversion_factors["imperial"] = {k: v * (2.20462 if k == "food" else 1) for k, v in REGIONAL_FACTORS[current_region].items()}
        calculate_footprint(None)
        page.update()

    async def toggle_theme(e):
        new_theme = ft.ThemeMode.LIGHT if page.theme_mode == ft.ThemeMode.DARK else ft.ThemeMode.DARK
        steps = 10  # Number of animation steps
        duration = 0.5  # Total duration in seconds
        step_time = duration / steps

        old_colors = colors.copy()
        new_colors = get_colors(new_theme)

        for step in range(steps + 1):
            progress = step / steps
            interpolated_colors = {
                key: interpolate_color(old_colors[key], new_colors[key], progress)
                for key in old_colors.keys()
            }
            page.bgcolor = interpolated_colors["background"]
            update_theme_colors(interpolated_colors)
            page.update()
            await asyncio.sleep(step_time)

        page.theme_mode = new_theme
        colors.update(new_colors)
        update_theme_colors(colors)
        page.update()

    def interpolate_color(start_color, end_color, progress):
        """Interpolate between two colors based on progress (0 to 1)."""
        start_rgb = ft.colors.to_rgb(start_color)
        end_rgb = ft.colors.to_rgb(end_color)
        r = int(start_rgb[0] + (end_rgb[0] - start_rgb[0]) * progress)
        g = int(start_rgb[1] + (end_rgb[1] - start_rgb[1]) * progress)
        b = int(start_rgb[2] + (end_rgb[2] - start_rgb[2]) * progress)
        return f"#{r:02x}{g:02x}{b:02x}"

    def update_theme_colors(temp_colors):
        colors.update(temp_colors)
        page.bgcolor = colors["background"]
        header.controls[1].color = colors["text"]
        for key, input_field in inputs.items():
            input_field.controls[0].color = colors["label"]
            input_field.controls[1].text_style = ft.TextStyle(color=colors["text"])
            input_field.controls[1].hint_style = ft.TextStyle(color=colors["hint"])
        region_dropdown.text_style = ft.TextStyle(color=colors["text"])
        region_dropdown.bgcolor = colors["container_bg"]
        chart_type_dropdown.text_style = ft.TextStyle(color=colors["text"])
        chart_type_dropdown.bgcolor = colors["container_bg"]
        history_dropdown.text_style = ft.TextStyle(color=colors["text"])
        history_dropdown.bgcolor = colors["container_bg"]
        progress_bar.bgcolor = colors["progress_bg"]
        chart_container.bgcolor = colors["container_bg"]
        individual_results.controls = [
            ft.Text(control.value, color=colors["label"]) for control in individual_results.controls
        ]
        for button in buttons.controls:
            button.color = colors["text"]
        page.theme.color_scheme.background = colors["background"]

    def save_data(e):
        try:
            data = {key: input_field.controls[1].value for key, input_field in inputs.items()}
            data["unit_system"] = "imperial" if unit_switch.value else "metric"
            data["timestamp"] = datetime.now().isoformat()
            data["region"] = current_region
            with open("footprint_data.json", "w") as f:
                json.dump(data, f, indent=2)
            show_snack_bar(page, "Data saved successfully!", ft.Colors.GREEN_700)
        except Exception as e:
            logger.error(f"Save error: {str(e)}")
            show_snack_bar(page, "Error saving data", ft.Colors.RED_700)

    def load_data(e):
        try:
            with open("footprint_data.json", "r") as f:
                data = json.load(f)
            for key, input_field in inputs.items():
                input_field.controls[1].value = data.get(key, "")
            unit_switch.value = data.get("unit_system", "metric") == "imperial"
            region_dropdown.value = data.get("region", "US")
            change_region(ft.ControlEvent(control=region_dropdown, data=region_dropdown.value))
            toggle_units(ft.ControlEvent(control=unit_switch, data=unit_switch.value))
            calculate_footprint(None)
            show_snack_bar(page, f"Data loaded from {data.get('timestamp', 'unknown time')}", ft.Colors.GREEN_700)
        except Exception as e:
            logger.error(f"Load error: {str(e)}")
            show_snack_bar(page, "No saved data found", ft.Colors.RED_700)

    def export_csv(e):
        try:
            values = [float(inputs[key].controls[1].value or 0) for key in inputs]
            unit_system = "imperial" if unit_switch.value else "metric"
            factors = conversion_factors[unit_system]
            categories = ["Electricity", "Gas", "Water", "Driving", "Flights", "Food"]
            footprints = [values[i] * factors[list(inputs.keys())[i]] for i in range(len(values))]
            total_footprint = sum(footprints)

            filename = f"carbon_footprint_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            with open(filename, "w", newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Category", f"CO2 ({'lbs' if unit_switch.value else 'kg'})"])
                for cat, val in zip(categories, footprints):
                    writer.writerow([cat, f"{val:.2f}"])
                writer.writerow(["Total", f"{total_footprint:.2f}"])
            show_snack_bar(page, f"Exported to {filename}", ft.Colors.GREEN_700)
        except Exception as e:
            logger.error(f"Export error: {str(e)}")
            show_snack_bar(page, "Error exporting data", ft.Colors.RED_700)

    def export_pdf(e):
        try:
            values = [float(inputs[key].controls[1].value or 0) for key in inputs]
            unit_system = "imperial" if unit_switch.value else "metric"
            factors = conversion_factors[unit_system]
            categories = ["Electricity", "Gas", "Water", "Driving", "Flights", "Food"]
            footprints = [values[i] * factors[list(inputs.keys())[i]] for i in range(len(values))]
            total_footprint = sum(footprints)

            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt=LANGUAGES[current_lang]["title"], ln=1, align="C")
            pdf.ln(10)
            for cat, val in zip(categories, footprints):
                pdf.cell(200, 10, txt=f"{cat}: {val:.2f} {'lbs' if unit_switch.value else 'kg'} CO2/month", ln=1)
            pdf.cell(200, 10, txt=f"{LANGUAGES[current_lang]['total']}: {total_footprint:.2f} {'lbs' if unit_switch.value else 'kg'} CO2/month", ln=1)
            filename = f"carbon_footprint_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            pdf.output(filename)
            show_snack_bar(page, f"Exported to {filename}", ft.Colors.GREEN_700)
        except Exception as e:
            logger.error(f"PDF export error: {str(e)}")
            show_snack_bar(page, "Error exporting PDF", ft.Colors.RED_700)

    def update_history_dropdown():
        history_dropdown.options = [ft.dropdown.Option(h["timestamp"], f"{h['timestamp']} - {h['total']:.2f}") for h in history]
        page.update()

    def load_historical_data(e):
        if e.control.value:
            selected = next(h for h in history if h["timestamp"] == e.control.value)
            for i, key in enumerate(inputs.keys()):
                inputs[key].controls[1].value = str(selected["values"][i])
            calculate_footprint(None)

    def reset_form(e):
        for input_field in inputs.values():
            input_field.controls[1].value = ""
        result_text.value = ""
        individual_results.controls = []
        individual_results.visible = False
        offset_suggestion.value = ""
        progress_bar.value = 0
        chart_container.content = None
        page.update()

    def show_snack_bar(page, message, color):
        page.snack_bar = ft.SnackBar(ft.Text(message), bgcolor=color)
        page.snack_bar.open = True
        page.update()

    def show_about_dialog(page):
        dlg = ft.AlertDialog(
            title=ft.Text(LANGUAGES[current_lang]["about"]),
            content=ft.Text("Advanced Carbon Footprint Calculator\nVersion 2.1\nCreated with Flet", color=colors["text"]),
            actions=[ft.TextButton("Close", on_click=lambda e: (setattr(page.dialog, 'open', False), page.update()))],
            bgcolor=colors["container_bg"]
        )
        page.dialog = dlg
        dlg.open = True
        page.update()

    def update_ui_language():
        page.title = LANGUAGES[current_lang]["title"]
        header.controls[1].value = LANGUAGES[current_lang]["title"]
        for key, input_field in inputs.items():
            input_field.controls[0].value = LANGUAGES[current_lang][key]
        region_dropdown.label = LANGUAGES[current_lang]["region"]
        buttons.controls[0].text = LANGUAGES[current_lang]["calculate"]
        buttons.controls[1].text = LANGUAGES[current_lang]["reset"]
        buttons.controls[2].text = LANGUAGES[current_lang]["save"]
        buttons.controls[3].text = LANGUAGES[current_lang]["load"]
        buttons.controls[4].text = LANGUAGES[current_lang]["export_csv"]
        buttons.controls[5].text = LANGUAGES[current_lang]["export_pdf"]

    # Buttons
    buttons = ft.Row([
        ft.ElevatedButton(LANGUAGES[current_lang]["calculate"], on_click=calculate_footprint, bgcolor=ft.Colors.TEAL_700, color=colors["text"]),
        ft.ElevatedButton(LANGUAGES[current_lang]["reset"], on_click=reset_form, bgcolor=ft.Colors.RED_700, color=colors["text"]),
        ft.ElevatedButton(LANGUAGES[current_lang]["save"], on_click=save_data, bgcolor=ft.Colors.GREEN_700, color=colors["text"]),
        ft.ElevatedButton(LANGUAGES[current_lang]["load"], on_click=load_data, bgcolor=ft.Colors.AMBER_700, color=colors["text"]),
        ft.ElevatedButton(LANGUAGES[current_lang]["export_csv"], on_click=export_csv, bgcolor=ft.Colors.BLUE_700, color=colors["text"]),
        ft.ElevatedButton(LANGUAGES[current_lang]["export_pdf"], on_click=export_pdf, bgcolor=ft.Colors.PURPLE_700, color=colors["text"])
    ], alignment=ft.MainAxisAlignment.CENTER, spacing=15)

    # Layout
    input_grid = ft.Column([
        ft.Row([inputs["electricity"], inputs["gas"]], spacing=20),
        ft.Row([inputs["water"], inputs["kilometers"]], spacing=20),
        ft.Row([inputs["flights"], inputs["food"]], spacing=20),
    ], spacing=20)

    settings_row = ft.Row([unit_switch, region_dropdown, chart_type_dropdown, history_dropdown], spacing=20)

    page.add(
        header,
        ft.Divider(color=colors["label"]),
        settings_row,
        ft.Container(input_grid, padding=20, bgcolor=colors["container_bg"], border_radius=10),
        buttons,
        ft.Container(result_text, padding=10, alignment=ft.alignment.center),
        ft.Container(offset_suggestion, padding=10, alignment=ft.alignment.center),
        ft.Container(individual_results, padding=10, bgcolor=colors["container_bg"], border_radius=10),
        ft.Container(progress_bar, padding=10),
        ft.Container(chart_container, alignment=ft.alignment.center, padding=10)
    )
    logger.info("Page setup complete")

if __name__ == "__main__":
    try:
        logger.info("Starting desktop application")
        ft.app(target=lambda page: asyncio.run(main(page)))
        logger.info("Application launched successfully")
    except Exception as e:
        logger.error(f"Failed to launch: {str(e)}")
        raise
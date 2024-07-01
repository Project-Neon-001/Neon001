from flask import Flask, render_template, request, jsonify, send_file
from io import BytesIO
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import model3

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/lofi')
def lofi():
    return render_template('lofi.html')

@app.route('/analyze', methods=['GET', 'POST'])
def analyze():
    if request.method == 'POST':
        # Get user input (load data) from the form
        load_data_file = request.files['load_data']
        load_data_df = pd.read_csv(load_data_file)

        # Create an instance of System_Builder with user input
        plant_name = request.form['plant_name']
        battery_hours = int(request.form['battery_hours'])
        distance = int(request.form['distance'])
        #plant = model3.System_Builder()
        plant = model3.System_Builder(load_data_df, plant_name, battery_hours, distance)

        # Call analysis methods
        #plant.plant_eval_data_cleanup()
        #plant.get_key_metrics()
        # ... other analysis methods (optional)
        plant.plant_eval_tester()

        # Prepare data for the response
        key_metrics = {
            # Extract key metrics from plant object
            'max_power': model3.Plant_Eval().get_max_power(),
            # ... other key metrics
        }

        return render_template('analysis_result.html', key_metrics=key_metrics)
    else:
        return render_template('analyze.html')

@app.route('/analysis_result')
def analysis_result():
    return render_template('analysis_result.html')

@app.route('/generate_quote', methods=['POST'])
def generate_quote():
    try:
        peak_load = float(request.form['peakLoad'])
    except ValueError:
        return jsonify(estimated_quote="Invalid input. Please enter numbers only."), 400

    # Calculate the required capacities
    duration_of_loadshedding = 2  # hours
    bess_capacity = peak_load * duration_of_loadshedding/0.8  # kWh
    pv_capacity = peak_load  # kW

    # Costs (for example)
    solar_cost_per_kw = 1000  # $1000 per kW
    bess_cost_per_kwh = 500   # $500 per kWh

    total_cost = (pv_capacity * solar_cost_per_kw) + (bess_capacity * bess_cost_per_kwh)

    # Generate PDF
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    pdf.drawString(100, 800, f"Solar PV and BESS Quote")
    pdf.drawString(100, 750, f"Peak Load: {peak_load} kW")
    pdf.drawString(100, 730, f"Required Solar PV Capacity: {pv_capacity} kW")
    pdf.drawString(100, 710, f"Required BESS Capacity: {bess_capacity} kWh")
    pdf.drawString(100, 690, f"Total Cost: ${total_cost:.2f}")
    pdf.save()
    buffer.seek(0)

    pdf_url = '/download_quote'

    response = jsonify({
        'estimated_quote': f"${total_cost:.2f}",
        'pv_size': f"{pv_capacity}",
        'bess_size': f"{bess_capacity}",
        'pdf_url': pdf_url
    })

    # Save PDF to file (so it can be downloaded)
    with open('static/quote.pdf', 'wb') as f:
        f.write(buffer.read())

    buffer.seek(0)

    return response

@app.route('/download_quote')
def download_quote():
    return send_file('static/quote.pdf', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)

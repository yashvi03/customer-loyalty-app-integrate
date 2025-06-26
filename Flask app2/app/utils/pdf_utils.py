from fpdf import FPDF

def generate_pdf(quotation_data, file_path):
    """
    Generates a PDF for the given quotation data.

    :param quotation_data: Dictionary containing customer details, items, and other metadata
    :param file_path: Path to save the generated PDF file
    :return: Path of the generated PDF file
    """
    pdf = FPDF()
    pdf.add_page()
    
    # Title
    pdf.set_font("Arial", size=16, style='B')
    pdf.cell(0, 10, txt="Quotation", ln=True, align='C')
    pdf.ln(10)  # Add a line break

    # Customer Details Section
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, txt="Customer Details", ln=True, align='L')
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 10, txt=f"Name: {quotation_data['customer']['name']}", ln=True, align='L')
    pdf.cell(0, 10, txt=f"Contact: {quotation_data['customer']['contact']}", ln=True, align='L')
    pdf.cell(0, 10, txt=f"Address: {quotation_data['customer']['address']}", ln=True, align='L')
    pdf.ln(10)

    # Items Section
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, txt="Items", ln=True, align='L')
    pdf.set_font("Arial", size=10)

    pdf.cell(50, 10, "Item Name", border=1, align='C')
    pdf.cell(30, 10, "Size", border=1, align='C')
    pdf.cell(30, 10, "Quantity", border=1, align='C')
    pdf.cell(30, 10, "Rate", border=1, align='C')
    pdf.cell(30, 10, "Total Price", border=1, align='C')
    pdf.ln()

    for item in quotation_data['items']:
        pdf.cell(50, 10, item['name'], border=1, align='L')
        pdf.cell(30, 10, item['size'], border=1, align='C')
        pdf.cell(30, 10, str(item['quantity']), border=1, align='C')
        pdf.cell(30, 10, f"{item['rate']:.2f}", border=1, align='C')
        pdf.cell(30, 10, f"{item['total_price']:.2f}", border=1, align='C')
        pdf.ln()

    pdf.ln(10)

    # Summary Section
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, txt="Summary", ln=True, align='L')
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 10, txt=f"Total Items: {len(quotation_data['items'])}", ln=True, align='L')
    pdf.cell(0, 10, txt=f"Grand Total: {quotation_data['grand_total']:.2f}", ln=True, align='L')

    # Save the PDF
    pdf.output(file_path)
    return file_path

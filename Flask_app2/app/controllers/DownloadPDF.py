from flask import Blueprint, send_file, request, jsonify
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import io
import requests
from PIL import Image as PILImage
import os
import tempfile
import logging
from datetime import date

download_quotation_bp = Blueprint("download_quotation", __name__)

@download_quotation_bp.route("/download_pdf/<quotation_id>", methods=["POST"])
def download_pdf(quotation_id):
    temp_files = []  # Track temp files for cleanup
    try:
        data = request.get_json()
        table_data = data.get("tableData", [])
        customer_data = data.get("customer", {})  # Expect customer data from frontend

        if not table_data:
            return jsonify({"error": "No table data provided"}), 400

        logging.debug(f"Received tableData: {table_data}")
        logging.debug(f"Received customerData: {customer_data}")

        pdf_buffer = io.BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, leftMargin=0.5*inch, rightMargin=0.5*inch, topMargin=0.5*inch, bottomMargin=0.5*inch)
        elements = []
        styles = getSampleStyleSheet()

        # Custom styles
        header_style = ParagraphStyle(
            name="Header",
            fontSize=12,
            fontName="Helvetica-Bold",
            alignment=0  # Left align
        )
        normal_style = ParagraphStyle(
            name="Normal",
            fontSize=10,
            fontName="Helvetica",
            leading=12
        )
        right_align_style = ParagraphStyle(
            name="RightAlign",
            alignment=2,  # Right align
            fontSize=10,
            fontName="Helvetica"
        )
        total_style = ParagraphStyle(
            name="Total",
            alignment=2,  # Right align
            fontSize=10,
            fontName="Helvetica-Bold"
        )

        # Header Section
        header_text = """
            PURANMAL SONS<br/>
            254, Jawahar Marg Rajmohalla<br/>
            Indore
        """
        elements.append(Paragraph(header_text, header_style))
        elements.append(Spacer(1, 0.1 * inch))

        # Quotation Title
        elements.append(Paragraph("Quotation", ParagraphStyle(name="TitleLeft", fontSize=14, fontName="Helvetica-Bold", alignment=0)))
        elements.append(Spacer(1, 0.1 * inch))

        # Quotation Number and Date
        quotation_info = Paragraph(
            f"<b>Quotation No:</b> {quotation_id}<br/><b>Date:</b> {date.today().strftime('%d/%m/%Y')}",
            right_align_style
        )
        elements.append(quotation_info)
        elements.append(Spacer(1, 0.2 * inch))

        # Customer Details
        customer_text = f"""
            <b>For:</b> {customer_data.get('project_name', 'Pharanal')}<br/>
            <b>Party Name:</b> {customer_data.get('name', 'Pharanal')}<br/>
            <b>Address:</b> {customer_data.get('billing_address', 'Pharanal Colony, Scheme No 54 Indore')}<br/>
            <b>City:</b> {customer_data.get('city', 'INDORE')}<br/>
            <b>State:</b> {customer_data.get('state', 'MADHYA PRADESH')}<br/>
            <b>Phone:</b> {customer_data.get('phone_number', '')}<br/>
            <b>Mobile:</b> {customer_data.get('whatsapp_number', '')}
        """
        elements.append(Paragraph(customer_text, normal_style))
        elements.append(Spacer(1, 0.2 * inch))

        # Table Header
        table_rows = [
            ["SNo.",'Make', 'Type','Size', "Item Image", "Item Description", "Qty", "Rate",'GST','Net Rate', "Amount"]
        ]
        sno = 1
        total_amount = 0
        

        for card in table_data:
            for item in card["items"]:
                image_obj = "No Image"  # Default fallback
                image_url = item.get("image_url")
                logging.debug(f"Processing item: {item.get('article', 'N/A')} with image_url: {image_url}")

                if image_url:
                    try:
                        logging.debug(f"Attempting to download image from: {image_url}")
                        response = requests.get(image_url, stream=True, timeout=10)
                        response.raise_for_status()
                        logging.debug(f"Image downloaded successfully, status: {response.status_code}")

                        img = PILImage.open(response.raw)
                        img.thumbnail((40, 40), PILImage.Resampling.LANCZOS)
                        logging.debug(f"Image resized to 40x40: {img.format}, {img.mode}")

                        content_type = response.headers.get("Content-Type", "").lower()
                        if "png" in content_type or image_url.endswith(".png"):
                            format = "PNG"
                            suffix = ".png"
                        elif "jpeg" in content_type or "jpg" in content_type or image_url.endswith((".jpg", ".jpeg")):
                            format = "JPEG"
                            suffix = ".jpg"
                        else:
                            format = "JPEG"
                            suffix = ".jpg"
                            if img.mode in ("RGBA", "LA"):
                                img = img.convert("RGB")
                                logging.debug("Converted RGBA to RGB for JPEG compatibility")

                        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
                            img.save(tmp_file.name, format)
                            logging.debug(f"Saved image as {format} to {tmp_file.name}")
                            image_obj = Image(tmp_file.name, width=40, height=40)
                            temp_files.append(tmp_file.name)

                    except requests.exceptions.RequestException as e:
                        logging.error(f"Failed to download image from {image_url}: {e}")
                    except Exception as e:
                        logging.error(f"Error processing image for {image_url}: {e}")

                # Item Description
                description = item.get("article", "N/A")
                if item.get("cat1"):
                    description += f" - {item.get('cat1')}"
                if item.get("cat2"):
                    description += f", {item.get('cat2')}"
                if item.get("cat3"):
                    description += f", {item.get('cat3')}"
                    
                final_price = float(item.get("final_price", 0))  # Price before GST
                gst_percent = float(item.get("gst", 0))
                gst_amount = final_price * (gst_percent / 100)
                net_rate = final_price + gst_amount
                total_price = net_rate * (float(item.get("quantity", 0)))

                table_rows.append([
                    str(sno),
                    item.get("make", "N/A"),
                    card.get("type", "N/A"),
                    card.get("size", "N/A"),
                    image_obj,
                    Paragraph(description, normal_style),
                    str(item.get("quantity", "N/A")),
                    f"Rs.{float(item.get('final_price', 0)):.2f}",
                    f"{gst_percent}%",
                    f"Rs.{float(net_rate):.2f}",
                    f"Rs.{float(total_price):.2f}"
                ])
                total_amount += total_price
                sno += 1

        # Column Widths
        col_widths = [25, 50,30,50,50, 150, 25, 50,35,50, 60]

        # Table Styling
        table = Table(table_rows, colWidths=col_widths)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("ALIGN", (1, 1), (1, -1), "LEFT"),
            ("ALIGN", (2, 1), (2, -1), "LEFT"),
            ("ALIGN", (3, 1), (3, -1), "RIGHT"),
            ("ALIGN", (5, 1), (5, -1), "LEFT"),
            ("ALIGN", (6, 1), (6, -1), "RIGHT"),
            ("ALIGN", (7, 1), (7, -1), "RIGHT"),
            ("ALIGN", (8, 1), (8, -1), "RIGHT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 0.2 * inch))

        # Total Amount
        # total_amount = sum(float(total_price) for card in table_data for item in card["items"])
        elements.append(Paragraph(f"<b>Total:</b> Rs.{total_amount:.2f}", total_style))
        elements.append(Spacer(1, 0.2 * inch))

        # Terms and Conditions (Added back)
        terms_text = """
            <b>Terms and Conditions:</b><br/>
            1. Prices are subject to change without notice.<br/>
            2. Payment terms: 50% advance, 50% on delivery.<br/>
            3. Delivery within 30 days from order confirmation.<br/>
            4. Goods once sold will not be taken back.
        """
        elements.append(Paragraph(terms_text, normal_style))
        elements.append(Spacer(1, 0.2 * inch))

        # Signature Line
        signature_text = "Authorized Signature: ___________________"
        elements.append(Paragraph(signature_text, normal_style))

        # Build the PDF
        doc.build(elements)

        pdf_buffer.seek(0)
        response = send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=f"quotation_{quotation_id}.pdf",
            mimetype="application/pdf",
        )

        # Cleanup temporary files
        for temp_file in temp_files:
            try:
                os.unlink(temp_file)
                logging.debug(f"Cleaned up temp file: {temp_file}")
            except OSError as e:
                logging.warning(f"Failed to delete temp file {temp_file}: {e}")

        return response

    except Exception as e:
        logging.error(f"Error generating PDF: {e}")
        for temp_file in temp_files:
            try:
                os.unlink(temp_file)
            except OSError:
                pass
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500
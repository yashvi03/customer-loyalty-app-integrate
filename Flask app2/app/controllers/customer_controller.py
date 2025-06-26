from flask import Blueprint, jsonify, request
from app.models import Customer, WIPQuotation
from app import db
from sqlalchemy.exc import SQLAlchemyError
import uuid

# Create a Blueprint for customer-related routes
customer_bp = Blueprint('customers', __name__, url_prefix='/customers')

@customer_bp.route('/add_customer/<string:quotation_id>', methods=['POST'])
def add_customer(quotation_id):
    try:
        data = request.get_json()
        
        quotation = WIPQuotation.query.filter_by(quotation_id=quotation_id).first()
        if not quotation:
            return jsonify({'error': 'Quotation not found'}), 404
        
        
        title = data.get("title")
        name = data.get("name")
        project_name = data.get("project_name")
        billing_address = data.get("billing_address")
        shipping_address = data.get("shipping_address")
        phone_number = data.get("phone_number")
        whatsapp_number = data.get("whatsapp_number")
            
     
        customer_id = str(uuid.uuid4())  
                
        new_customer = Customer(
                customer_id=customer_id,
                title=title,
                name=name,
                project_name=project_name,
                billing_address=billing_address,
                shipping_address=shipping_address,
                phone_number=phone_number,
                whatsapp_number=whatsapp_number
            )
                
        print(f"Adding new customer: {new_customer}")
                
        db.session.add(new_customer)
        db.session.commit()
                
          

        return jsonify({
            'message': 'Customer added/updated successfully',
            'customer': new_customer.to_dict()  # Return the list of added or updated margins
        }), 200
    
    except Exception as e:
        # Log the error and return a response
        return jsonify({'error': str(e)}), 500
    except SQLAlchemyError as e:
        print("SQLAlchemyError:", str(e))  # Debugging log
        db.session.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 400
        


@customer_bp.route('/get_customer', methods=['GET'])
def get_unique_customers():
    """Get unique customers based on name, shipping address, and phone number."""
    from sqlalchemy import distinct

    # Query for unique combinations of name, shipping address, and phone number
    unique_customers = (
        Customer.query.with_entities(
            Customer.customer_id,
            Customer.title,
            Customer.name,
            Customer.project_name,
            Customer.billing_address,
            Customer.shipping_address,
            Customer.phone_number,
            Customer.whatsapp_number,
        )
        .distinct(Customer.name, Customer.shipping_address, Customer.phone_number)
        .all()
    )

    result = [
        {
            "customer_id": customer.customer_id,
            "title": customer.title,
            "name": customer.name,
            "project_name": customer.project_name,
            "billing_address": customer.billing_address,
            "shipping_address": customer.shipping_address,
            "phone_number": customer.phone_number,
            "whatsapp_number": customer.whatsapp_number,
        }
        for customer in unique_customers
    ]

    return jsonify(result), 200



from app import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.mutable import MutableList
class ItemPricing(db.Model):
    __tablename__ = 'item_pricing'
    
    id = db.Column(db.Integer, primary_key=True)  # Primary key for the table
    itemname = db.Column(db.String(255), nullable=False)  # Name of the item
    discount = db.Column(db.Numeric(10, 2), nullable=True)  # Discount on the item
    netrate = db.Column(db.Numeric(10, 2), nullable=True)  # Net rate of the item
    margincategory = db.Column(db.String(50), nullable=True)  # Category for margin
    discountcategory = db.Column(db.String(50), nullable=True)  # Category for discount

    # Define a relationship with the Item model based on the discount category
    items = db.relationship('Item', backref='pricing', lazy=True, foreign_keys=[discountcategory], primaryjoin="Item.discount_category == ItemPricing.discountcategory")

    def __repr__(self):
        return f'<ItemPricing {self.itemname}>'

    def to_dict(self):
        return {
            'id': self.id,
            'itemname': self.itemname,
            'discount': str(self.discount) if self.discount else None,
            'netrate': str(self.netrate) if self.netrate else None,
            'margincategory': self.margincategory,
            'discountcategory': self.discountcategory
        }

# ------------------------
# Item Model
# ------------------------
class Item(db.Model):
    __tablename__ = 'items'

    item_id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(255))
    size = db.Column(db.String(50))
    mrp = db.Column(db.Numeric(10, 2))
    article = db.Column(db.String(255))
    cat1 = db.Column(db.String(50))
    cat2 = db.Column(db.String(50))
    cat3 = db.Column(db.String(50))
    margin_category = db.Column(db.String(50))
    discount_category = db.Column(db.String(50))
    mc_name = db.Column(db.String(255))
    image_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    type_image_url = db.Column(db.String(255))
    gst = db.Column(db.Numeric(5, 2))  # New GST column (e.g., 18.00)
    make = db.Column(db.String(255))   # New Make column (e.g., "BrandX")

    def __repr__(self):
        return f'<Item {self.item_id}>'

    def to_dict(self):
        return {
            'item_id': self.item_id,
            'type': self.type,
            'size': self.size,
            'mrp': str(self.mrp),
            'article': self.article,
            'cat1': self.cat1,
            'cat2': self.cat2,
            'cat3': self.cat3,
            'margin_category': self.margin_category,
            'discount_category': self.discount_category,
            'mc_name': self.mc_name,
            'image_url': self.image_url,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'type_image_url': self.type_image_url,
            'gst': str(self.gst) if self.gst is not None else None,  # New GST field
            'make': self.make                                # New Make field
        }
# ------------------------
# Customer Model
# ------------------------
class Customer(db.Model):
    __tablename__ = 'customer'

    customer_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = db.Column(db.String(10))
    name = db.Column(db.String(255), nullable=False)
    project_name = db.Column(db.String(30))
    billing_address = db.Column(db.Text)
    shipping_address = db.Column(db.Text)
    phone_number = db.Column(db.String(15))
    whatsapp_number = db.Column(db.String(15))

    def __repr__(self):
        return f'<Customer {self.customer_id}>'

    def to_dict(self):
        return {
            'customer_id': self.customer_id,
            'title': self.title,
            'name': self.name,
            'project_name': self.project_name,
            'billing_address': self.billing_address,
            'shipping_address': self.shipping_address,
            'phone_number': self.phone_number,
            'whatsapp_number': self.whatsapp_number
        }


# ------------------------
# QuotationItem Model
# ------------------------
# class QuotationItem(db.Model):
#     __tablename__ = 'quotation_items'

#     quotation_items_id = db.Column(db.Integer, primary_key=True)
#     quotation_id = db.Column(UUID(as_uuid=True), nullable=False)  
#     article = db.Column(db.String, nullable=False)  
#     category = db.Column(db.String, nullable=False)  
#     quantity = db.Column(db.Integer, nullable=False)
#     size = db.Column(db.String, nullable=False)  
#     type = db.Column(db.String, nullable=False)  
#     discount_rate = db.Column(db.Float, nullable=False)
#     net_rate = db.Column(db.Float, nullable=False)
#     margin = db.Column(db.Float, nullable=False)
#     final_rate = db.Column(db.Float, nullable=False)
#     mrp = db.Column(db.Float, nullable=False)  

#     def __init__(self, article, category, quantity, size, type, discount_rate, net_rate, margin, final_rate, mrp, quotation_id):
#         self.article = article
#         self.category = category
#         self.quantity = quantity
#         self.size = size
#         self.type = type
#         self.discount_rate = discount_rate
#         self.net_rate = net_rate
#         self.margin = margin
#         self.final_rate = final_rate
#         self.mrp = mrp 
#         self.quotation_id = quotation_id

#     def to_dict(self):
#         return {
#             'quotation_items_id': self.quotation_items_id,
#             'quotation_id': str(self.quotation_id),
            
#             'article': self.article,
#             'category': self.category,
#             'quantity': self.quantity,
#             'size': self.size,
#             'type': self.type,
#             'discount_rate': self.discount_rate,
#             'net_rate': self.net_rate,
#             'margin': self.margin,
#             'final_rate': self.final_rate,
#             'mrp': self.mrp, 
#         }


# ------------------------
# PickMargin Model
# ------------------------
class PickMargin(db.Model):
    __tablename__ = 'pickmargin'

    id = db.Column(db.Integer, primary_key=True)
    mc_name = db.Column(db.String(255), nullable=False)  # Margin category name
    margin = db.Column(db.Float, nullable=False)  # The margin value for the category
    quotation_id = db.Column(UUID(as_uuid=True), nullable=False)  # Just storing the quotation_id value

    def __init__(self, mc_name, margin, quotation_id):
        self.mc_name = mc_name
        self.margin = margin
        self.quotation_id = quotation_id

    def to_dict(self):
        return {
            'id': self.id,
            'mc_name': self.mc_name,
            'margin': self.margin,
            'quotation_id': str(self.quotation_id),
        }


class CardTable(db.Model):
    __tablename__ = 'cards'
    card_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = db.Column(db.String(50), nullable=False)
    size = db.Column(db.String(50), nullable=False)

    # Relationship with CardItem
    items = db.Column(db.JSON)

    def to_dict(self):
        return {
            'card_id': str(self.card_id),
            'type': self.type,
            'size': self.size,
            "items": self.items,
        }
        
class MarginTable(db.Model):
    __tablename__ = 'margin'
    margin_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mc_name = db.Column(db.String(50), nullable=False)
    margin = db.Column(db.Float, nullable=False)


    def to_dict(self):
        return {
            'margin_id': str(self.margin_id),
            'mc_name': self.mc_name,
            'margin': self.margin,
        }


class WIPQuotation(db.Model):
    __tablename__ = 'wip_quotation'

    quotation_id = db.Column(db.String(50), primary_key=True)
    customer_id = db.Column(UUID(as_uuid=True), default=uuid.uuid4)
    card_ids = db.Column(MutableList.as_mutable(db.ARRAY(UUID)))   # Storing UUIDs as strings in an array
    margin_ids = db.Column(MutableList.as_mutable(db.ARRAY(UUID)))  # Storing UUIDs as strings in an array
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_modified = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<WIPQuotation(quotation_id={self.quotation_id}, customer_id={self.customer_id}, card_ids={self.card_ids})>"

    def to_dict(self):
        return {
            "quotation_id": self.quotation_id,
            "customer_id": self.customer_id,
            "card_ids": self.card_ids,
            "margin_ids": self.margin_ids,
            "date_created": self.date_created,
            "date_modified": self.date_modified
        }
        

class FinalQuotation(db.Model):
    __tablename__ = 'final_quotation'

    quotation_id = db.Column(db.String(50), primary_key=True)
    customer_id = db.Column(UUID(as_uuid=True), default=uuid.uuid4)
    card_ids = db.Column(MutableList.as_mutable(db.ARRAY(UUID)))   # Storing UUIDs as strings in an array
    margin_ids = db.Column(MutableList.as_mutable(db.ARRAY(UUID)))  # Storing UUIDs as strings in an array
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_modified = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<WIPQuotation(quotation_id={self.quotation_id}, customer_id={self.customer_id}, card_ids={self.card_ids})>"

    def to_dict(self):
        return {
            "quotation_id": self.quotation_id,
            "customer_id": self.customer_id,
            "card_ids": self.card_ids,
            "margin_ids": self.margin_ids,
            "date_created": self.date_created,
            "date_modified": self.date_modified
        }
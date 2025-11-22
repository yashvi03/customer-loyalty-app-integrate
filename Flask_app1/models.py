from Flask_app1. app import db
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.sql import func

class Gifts(db.Model):
    __tablename__ = "gifts"
    __table_args__ = {'extend_existing': True} 

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Integer)
    points = db.Column(db.Integer)
    gift = db.Column(db.String())
    image = db.Column(db.String())

    def __init__(self, amount, points, gift, image):
        self.amount = amount
        self.points = points
        self.gift = gift
        self.image = image

    def __repr__(self):
        return "<id {}".format(self.id)


class Office(db.Model):
    __tablename__ = "office"
    __table_args__ = {'extend_existing': True} 

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    surname = db.Column(db.String())
    phone = db.Column(db.BigInteger)
    password = db.Column(db.String())
    profile_photo = db.Column(db.String())
    date = db.Column(db.DateTime(timezone=True), server_default=func.now())

    def __init__(self, name, surname, phone, password, profile_photo, date):
        self.name = name
        self.surname = surname
        self.phone = phone
        self.password = password
        self.profile_photo = profile_photo
        self.date = date

    def __repr__(self):
        return "<id {}".format(self.id)


class Admin(db.Model):
    __tablename__ = "admin"
    __table_args__ = {'extend_existing': True} 

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    surname = db.Column(db.String())
    phone = db.Column(db.BigInteger)
    password = db.Column(db.String())
    profile_photo = db.Column(db.String())
    date = db.Column(db.DateTime(timezone=True), server_default=func.now())

    def __init__(self, name, surname, phone, password, profile_photo, date):
        self.name = name
        self.surname = surname
        self.phone = phone
        self.password = password
        self.profile_photo = profile_photo
        self.date = date

    def __repr__(self):
        return "<id {}".format(self.id)


class Traders(db.Model):
    __tablename__ = "traders"
    __table_args__ = {'extend_existing': True} 

    id = db.Column(db.Integer, primary_key=True)
    is_subdealer = db.Column(db.Integer, default=0)
    name = db.Column(db.String())
    surname = db.Column(db.String())
    store_name = db.Column(db.String())
    phone = db.Column(db.BigInteger)
    address = db.Column(db.String())
    city = db.Column(db.String())
    username = db.Column(db.String())
    password = db.Column(db.String())
    profile_photo = db.Column(db.String())
    date = db.Column(db.DateTime(timezone=True), server_default=func.now())


    def __init__(self, is_subdealer, name, surname, store_name, phone, address, city, username, password, profile_photo, date):
        self.is_subdealer = is_subdealer
        self.name = name
        self.surname = surname
        self.store_name = store_name
        self.phone = phone
        self.address = address
        self.city = city
        self.username = username
        self.password = password
        self.profile_photo = profile_photo
        self.date = date

    def __repr__(self):
        return "<id {}".format(self.id)


class Traders_temp(db.Model):
    __tablename__ = "traders_temp"
    __table_args__ = {'extend_existing': True} 

    id = db.Column(db.Integer, primary_key=True)
    is_subdealer = db.Column(db.Integer, default=0)
    name = db.Column(db.String())
    surname = db.Column(db.String())
    store_name = db.Column(db.String())
    phone = db.Column(db.BigInteger)
    address = db.Column(db.String())
    city = db.Column(db.String())
    username = db.Column(db.String())
    password = db.Column(db.String())
    profile_photo = db.Column(db.String())
    date = db.Column(db.DateTime(timezone=True), server_default=func.now())


    def __init__(self, is_subdealer, name, surname, store_name, phone, address, city, username, password, profile_photo, date):
        self.is_subdealer = is_subdealer
        self.name = name
        self.surname = surname
        self.store_name = store_name
        self.phone = phone
        self.address = address
        self.city = city
        self.username = username
        self.password = password
        self.profile_photo = profile_photo
        self.date = date

    def __repr__(self):
        return "<id {}".format(self.id)


class Plumbers(db.Model):
    __tablename__ = "plumbers"
    __table_args__ = {'extend_existing': True} 

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    surname = db.Column(db.String())
    phone = db.Column(db.BigInteger)
    address = db.Column(db.String())
    city = db.Column(db.String())
    dob = db.Column(db.Date)
    doa = db.Column(db.Date)
    redeem_status = db.Column(db.String())
    username = db.Column(db.String())
    password = db.Column(db.String())
    profile_photo = db.Column(db.String())
    aadhar_photo = db.Column(db.String())
    date = db.Column(db.DateTime(timezone=True), server_default=func.now())


    def __init__(self, name, surname, phone, address, city, dob, doa, redeem_status, username, password, profile_photo, aadhar_photo, date):
        self.name = name
        self.surname = surname
        self.phone = phone
        self.address = address
        self.city = city
        self.dob = dob
        self.doa = doa
        self.redeem_status = redeem_status
        self.username = username
        self.password = password
        self.profile_photo = profile_photo
        self.aadhar_photo = aadhar_photo
        self.date = date

    def __repr__(self):
        return "<id {}".format(self.id)


class Plumbers_temp(db.Model):
    __tablename__ = "plumbers_temp"
    __table_args__ = {'extend_existing': True} 

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    surname = db.Column(db.String())
    phone = db.Column(db.BigInteger)
    address = db.Column(db.String())
    city = db.Column(db.String())
    dob = db.Column(db.Date)
    doa = db.Column(db.Date)
    redeem_status = db.Column(db.String())
    username = db.Column(db.String())
    password = db.Column(db.String())
    profile_photo = db.Column(db.String())
    aadhar_photo = db.Column(db.String())
    date = db.Column(db.DateTime(timezone=True), server_default=func.now())


    def __init__(self, name, surname, phone, address, city, dob, doa, redeem_status, username, password, profile_photo, aadhar_photo, date):
        self.name = name
        self.surname = surname
        self.phone = phone
        self.address = address
        self.city = city
        self.dob = dob
        self.doa = doa
        self.redeem_status = redeem_status
        self.username = username
        self.password = password
        self.profile_photo = profile_photo
        self.aadhar_photo = aadhar_photo
        self.date = date

    def __repr__(self):
        return "<id {}".format(self.id)


class TRPL(db.Model):
    __tablename__ = "trpl"
    __table_args__ = {'extend_existing': True} 

    id = db.Column(db.Integer, primary_key=True)
    tr_id = db.Column(db.Integer, db.ForeignKey('traders.id'))
    pl_id = db.Column(db.Integer, db.ForeignKey('plumbers.id'))
    sd_id = db.Column(db.Integer, db.ForeignKey('traders.id'))

    def __init__(self, tr_id, pl_id, sd_id):
        self.tr_id = tr_id
        self.pl_id = pl_id
        self.sd_id = sd_id

    def __repr__(self):
        return "<id {}".format(self.id)


class TRPL_temp(db.Model):
    __tablename__ = "trpl_temp"
    __table_args__ = {'extend_existing': True} 

    id = db.Column(db.Integer, primary_key=True)
    tr_id = db.Column(db.Integer, db.ForeignKey('traders.id'))
    pl_id = db.Column(db.Integer, db.ForeignKey('plumbers.id'))
    sd_id = db.Column(db.Integer, db.ForeignKey('traders.id'))

    def __init__(self, tr_id, pl_id, sd_id):
        self.tr_id = tr_id
        self.pl_id = pl_id
        self.sd_id = sd_id

    def __repr__(self):
        return "<id {}".format(self.id)


class Transactions(db.Model):
    __tablename__ = "transactions"
    __table_args__ = {'extend_existing': True} 

    id = db.Column(db.Integer, primary_key=True)
    tr_id = db.Column(db.Integer, db.ForeignKey('traders.id'))
    pl_id = db.Column(db.Integer, db.ForeignKey('plumbers.id'))
    sd_id = db.Column(db.Integer, db.ForeignKey('traders.id'))
    invoice = db.Column(db.String())
    amount = db.Column(db.Integer)
    points_allocated = db.Column(db.Integer)
    points_expired = db.Column(db.Integer)
    points_received = db.Column(db.Integer)    
    points_redeemable = db.Column(db.Integer)
    date = db.Column(db.DateTime(timezone=False), server_default=func.now())

    def __init__(self, tr_id, pl_id, sd_id, invoice, amount, points_allocated, points_redeemable, points_expired, points_received, date):
        self.tr_id = tr_id
        self.pl_id = pl_id
        self.sd_id = sd_id
        self.invoice = invoice
        self.amount = amount
        self.points_allocated = points_allocated
        self.points_redeemable = points_redeemable
        self.points_expired = points_expired
        self.points_received = points_received
        self.date = date

    def __repr__(self):
        return "<id {}".format(self.id)


class Transactions_temp(db.Model):
    __tablename__ = "transactions_temp"
    __table_args__ = {'extend_existing': True} 

    id = db.Column(db.Integer, primary_key=True)
    tr_id = db.Column(db.Integer)
    pl_id = db.Column(db.Integer)
    sd_id = db.Column(db.Integer, db.ForeignKey('traders.id'))
    invoice = db.Column(db.String())
    amount = db.Column(db.Integer)
    points_allocated = db.Column(db.Integer)
    points_expired = db.Column(db.Integer)
    points_received = db.Column(db.Integer)    
    points_redeemable = db.Column(db.Integer)
    date = db.Column(db.DateTime(timezone=False), server_default=func.now())

    def __init__(self, tr_id, pl_id, sd_id, invoice, amount, points_allocated, points_redeemable, points_expired, points_received, date):
        self.tr_id = tr_id
        self.pl_id = pl_id
        self.sd_id = sd_id
        self.invoice = invoice
        self.amount = amount
        self.points_allocated = points_allocated
        self.points_redeemable = points_redeemable
        self.points_expired = points_expired
        self.points_received = points_received
        self.date = date

    def __repr__(self):
        return "<id {}".format(self.id)


class Redemption(db.Model):
    __tablename__ = "redemption"
    __table_args__ = {'extend_existing': True} 

    id = db.Column(db.Integer, primary_key=True)
    pl_id = db.Column(db.Integer)
    points = db.Column(db.Integer)
    status = db.Column(db.String())
    gift = db.Column(db.String())
    recipient_image = db.Column(db.String())
    date = db.Column(db.DateTime(timezone=True), server_default=func.now())
    date_modified = db.Column(db.DateTime(timezone=True), server_default=func.now())

    def __init__(self, pl_id, points, status, gift, recipient_image, date, date_modified):
        self.pl_id = pl_id
        self.points = points
        self.status = status
        self.gift = gift
        self.recipient_image = recipient_image
        self.date = date
        self.date_modified = date_modified

    def __repr__(self):
        return "<id {}".format(self.id)


class Bulk_Plumber_Registration_History(db.Model):
    __tablename__ = "bulk_plumber_registration_history"
    __table_args__ = {'extend_existing': True} 

    id = db.Column(db.Integer, primary_key=True)
    sheet_url = db.Column(db.String())
    date = db.Column(db.DateTime(timezone=True), server_default=func.now())
    deleted_flag= db.Column(db.Integer, default=0)

    def __init__(self,sheet_url,date,deleted_flag=0):
        self.sheet_url=sheet_url
        self.date=date
        self.deleted_flag=deleted_flag

    def __repr__(self):
        return "<id {}".format(self.id)
    

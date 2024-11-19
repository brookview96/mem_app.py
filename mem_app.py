monumental_mason_system/
├── app.py                  # Main Streamlit application
├── models.py               # Data models for SQLite
├── database.py             # Database connection and utility functions
├── controllers/
│   ├── users.py            # User management logic
│   ├── orders.py           # Order management logic
│   ├── inventory.py        # Inventory management logic
├── requirements.txt        # Dependencies
└── assets/                 # Static assets (images, logos, etc.)
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

Base = declarative_base()

# User Model
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    role = Column(String, nullable=False)  # e.g., Admin, Sales, Designer

# Order Model
class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    customer_name = Column(String, nullable=False)
    monument_type = Column(String, nullable=False)
    material = Column(String, nullable=False)
    engraving_details = Column(String)
    status = Column(String, default='Inquiry')  # Status: Inquiry, Design, Production, Completed
    created_at = Column(DateTime, default=datetime.utcnow)

# Inventory Model
class Inventory(Base):
    __tablename__ = 'inventory'
    id = Column(Integer, primary_key=True)
    material_name = Column(String, nullable=False)
    quantity = Column(Float, nullable=False)
    reorder_level = Column(Float, default=0)

# Initialize the database
def init_db():
    engine = create_engine('sqlite:///monumental_mason.db')
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)

SessionLocal = init_db()
from models import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
import streamlit as st
from sqlalchemy.orm import Session
from database import get_db
from models import User, Order, Inventory

# Sidebar Navigation
st.sidebar.title("Monumental Mason Management System")
menu = st.sidebar.radio("Menu", ["Dashboard", "Orders", "Inventory", "Users"])

# Database session
db = next(get_db())

# Dashboard
if menu == "Dashboard":
    st.title("Dashboard")
    st.write("Overview of the business operations.")

    # Metrics Example
    total_orders = db.query(Order).count()
    pending_orders = db.query(Order).filter(Order.status != 'Completed').count()
    st.metric("Total Orders", total_orders)
    st.metric("Pending Orders", pending_orders)

# Orders
elif menu == "Orders":
    st.title("Orders")
    st.write("Manage customer orders.")

    # Add New Order
    with st.form("New Order"):
        customer_name = st.text_input("Customer Name")
        monument_type = st.selectbox("Monument Type", ["Headstone", "Plaque", "Other"])
        material = st.selectbox("Material", ["Granite", "Marble", "Limestone"])
        engraving_details = st.text_area("Engraving Details")
        if st.form_submit_button("Create Order"):
            new_order = Order(
                customer_name=customer_name,
                monument_type=monument_type,
                material=material,
                engraving_details=engraving_details,
            )
            db.add(new_order)
            db.commit()
            st.success("Order created successfully!")

    # List Orders
    st.subheader("Existing Orders")
    orders = db.query(Order).all()
    for order in orders:
        st.write(f"**Order #{order.id}** - {order.customer_name}")
        st.write(f"  - Monument: {order.monument_type}, Material: {order.material}")
        st.write(f"  - Status: {order.status}")

# Inventory
elif menu == "Inventory":
    st.title("Inventory")
    st.write("Manage inventory levels.")

    # Add New Material
    with st.form("New Material"):
        material_name = st.text_input("Material Name")
        quantity = st.number_input("Quantity", min_value=0.0)
        reorder_level = st.number_input("Reorder Level", min_value=0.0)
        if st.form_submit_button("Add Material"):
            new_inventory = Inventory(
                material_name=material_name,
                quantity=quantity,
                reorder_level=reorder_level,
            )
            db.add(new_inventory)
            db.commit()
            st.success("Material added successfully!")

    # List Inventory
    st.subheader("Current Inventory")
    inventory_items = db.query(Inventory).all()
    for item in inventory_items:
        st.write(f"**{item.material_name}** - {item.quantity} units (Reorder Level: {item.reorder_level})")

# Users
elif menu == "Users":
    st.title("Users")
    st.write("Manage system users.")

    # Add New User
    with st.form("New User"):
        name = st.text_input("Name")
        email = st.text_input("Email")
        role = st.selectbox("Role", ["Admin", "Sales", "Designer"])
        if st.form_submit_button("Create User"):
            new_user = User(name=name, email=email, role=role)
            db.add(new_user)
            db.commit()
            st.success("User created successfully!")

    # List Users
    st.subheader("System Users")
    users = db.query(User).all()
    for user in users:
        st.write(f"**{user.name}** ({user.role}) - {user.email}")

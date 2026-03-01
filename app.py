import streamlit as st
import sqlite3
from datetime import datetime

# ---------------- Session ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "role" not in st.session_state:
    st.session_state.role = None

# ---------------- Login Function ----------------
def login(username, password):
    if username == "admin" and password == "admin123":
        return "Admin"
    elif username == "user" and password == "user123":
        return "User"
    else:
        return None

# ---------------- Login Page ----------------
if not st.session_state.logged_in:
    st.set_page_config(page_title="Login - IT Service Desk")
    st.title("🔐 IT Service Desk Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        role = login(username, password)
        if role:
            st.session_state.logged_in = True
            st.session_state.role = role
            st.success("Login Successful!")
            st.rerun()
        else:
            st.error("Invalid Credentials")

# ---------------- Main App ----------------
else:

    # Database Connection
    conn = sqlite3.connect("it_service.db", check_same_thread=False)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        issue TEXT,
        description TEXT,
        priority TEXT,
        status TEXT,
        date TEXT
    )
    """)
    conn.commit()

    st.set_page_config(page_title="IT Service Desk", layout="wide")

    st.title("🖥 IT Service Desk Management System")
    st.sidebar.write(f"Logged in as: **{st.session_state.role}**")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.role = None
        st.rerun()

    menu = st.sidebar.selectbox("Menu", ["Raise Ticket", "View Tickets"])

    # ---------------- Raise Ticket ----------------
    if menu == "Raise Ticket":
        st.subheader("Raise New IT Ticket")

        name = st.text_input("Enter Your Name")
        issue = st.text_input("Issue Title")
        description = st.text_area("Issue Description")
        priority = st.selectbox("Priority", ["Low", "Medium", "High"])

        if st.button("Submit Ticket"):
            if name and issue and description:
                cursor.execute("""
                    INSERT INTO tickets (name, issue, description, priority, status, date)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (name, issue, description, priority, "Open",
                      datetime.now().strftime("%Y-%m-%d %H:%M")))
                conn.commit()
                st.success("✅ Ticket Submitted Successfully!")
            else:
                st.error("⚠ All fields are required!")

    # ---------------- View Tickets ----------------
    elif menu == "View Tickets":
        st.subheader("All Tickets")

        cursor.execute("SELECT * FROM tickets")
        rows = cursor.fetchall()

        if rows:
            for row in rows:
                st.write(f"### Ticket ID: {row[0]}")
                st.write(f"👤 Name: {row[1]}")
                st.write(f"📝 Issue: {row[2]}")
                st.write(f"📄 Description: {row[3]}")
                st.write(f"🔥 Priority: {row[4]}")
                st.write(f"📌 Status: {row[5]}")
                st.write(f"📅 Date: {row[6]}")

                # Only Admin can update status
                if st.session_state.role == "Admin":
                    new_status = st.selectbox(
                        f"Update Status for Ticket {row[0]}",
                        ["Open", "In Progress", "Closed"],
                        key=row[0]
                    )

                    if st.button(f"Update Ticket {row[0]}"):
                        cursor.execute("UPDATE tickets SET status=? WHERE id=?",
                                       (new_status, row[0]))
                        conn.commit()
                        st.success("Status Updated!")
                        st.rerun()

                st.markdown("---")
        else:
            st.info("No tickets available.")

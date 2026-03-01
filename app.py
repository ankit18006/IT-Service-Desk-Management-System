import streamlit as st
import sqlite3
from datetime import datetime

# ---------------- Session Setup ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
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
    st.title("🔐 IT Service Desk Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        role = login(username, password)
        if role:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = role
            st.success("Login Successful!")
            st.rerun()
        else:
            st.error("Invalid Credentials")

# ---------------- Main App ----------------
else:
    conn = sqlite3.connect("it_service.db", check_same_thread=False)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        issue TEXT,
        description TEXT,
        priority TEXT,
        status TEXT,
        date TEXT
    )
    """)
    conn.commit()

    st.title("🖥 IT Service Desk Management System")

    st.sidebar.write(f"👤 Logged in as: {st.session_state.username}")
    st.sidebar.write(f"🔑 Role: {st.session_state.role}")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.role = None
        st.rerun()

    # ---------------- USER PANEL ----------------
    if st.session_state.role == "User":

        menu = st.sidebar.selectbox("Menu", ["Raise Ticket", "My Tickets"])

        if menu == "Raise Ticket":
            st.subheader("Raise New Ticket")

            issue = st.text_input("Issue Title")
            description = st.text_area("Issue Description")
            priority = st.selectbox("Priority", ["Low", "Medium", "High"])

            if st.button("Submit Ticket"):
                if issue and description:
                    cursor.execute("""
                        INSERT INTO tickets (username, issue, description, priority, status, date)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        st.session_state.username,
                        issue,
                        description,
                        priority,
                        "Open",
                        datetime.now().strftime("%Y-%m-%d %H:%M")
                    ))
                    conn.commit()
                    st.success("✅ Ticket Raised Successfully!")
                else:
                    st.error("Please fill all fields")

        elif menu == "My Tickets":
            st.subheader("📋 My Tickets")

            cursor.execute("SELECT * FROM tickets WHERE username=?",
                           (st.session_state.username,))
            rows = cursor.fetchall()

            if rows:
                for row in rows:
                    st.write(f"### Ticket ID: {row[0]}")
                    st.write(f"Issue: {row[2]}")
                    st.write(f"Description: {row[3]}")
                    st.write(f"Priority: {row[4]}")
                    st.write(f"Status: {row[5]}")
                    st.write(f"Date: {row[6]}")

                    if row[5] == "Open":
                        st.warning("🟡 Status: In Process")
                    elif row[5] == "In Progress":
                        st.info("🔵 Status: In Progress")
                    else:
                        st.success("🟢 Status: Closed")

                    st.markdown("---")
            else:
                st.info("No tickets raised yet.")

    # ---------------- ADMIN PANEL ----------------
    elif st.session_state.role == "Admin":

        st.subheader("📋 All User Tickets")

        cursor.execute("SELECT * FROM tickets")
        rows = cursor.fetchall()

        if rows:
            for row in rows:
                st.write(f"### Ticket ID: {row[0]}")
                st.write(f"User: {row[1]}")
                st.write(f"Issue: {row[2]}")
                st.write(f"Description: {row[3]}")
                st.write(f"Priority: {row[4]}")
                st.write(f"Current Status: {row[5]}")
                st.write(f"Date: {row[6]}")

                new_status = st.selectbox(
                    f"Update Status for Ticket {row[0]}",
                    ["Open", "In Progress", "Closed"],
                    index=["Open", "In Progress", "Closed"].index(row[5]),
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

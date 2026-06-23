import streamlit as st
from db import db, Tags, connect_db

# =========================
# INIT DB
# =========================
connect_db()

st.set_page_config(page_title="Manage Tags")
st.title("🏷️ Manage Tags")


# =========================
# ADD TAG
# =========================
def add_tag(tag_name: str):
    tag_name = tag_name.strip().lower()

    if not tag_name:
        st.warning("Tag cannot be empty")
        return

    try:
        Tags.create(name=tag_name)
        st.success(f"Tag '{tag_name}' added successfully")
    except Exception as e:
        st.error(f"Error: {str(e)}")


# =========================
# DELETE TAG
# =========================
def delete_tag(tag_id: int):
    try:
        Tags.delete().where(Tags.id == tag_id).execute()
        st.success("Tag deleted successfully")
    except Exception as e:
        st.error(f"Error deleting tag: {str(e)}")


# =========================
# UI - ADD TAG
# =========================
tag_input = st.text_input("Enter new tag")

if st.button("Add Tag"):
    add_tag(tag_input)
    st.rerun()


# =========================
# SHOW TAGS
# =========================
st.subheader("Existing Tags")

tags = Tags.select().order_by(Tags.id.desc())

if tags:
    for tag in tags:
        col1, col2 = st.columns([4, 1])

        with col1:
            st.write(f"🏷️ {tag.name}")

        with col2:
            st.button(
                "🗑",
                key=f"delete_{tag.id}",
                on_click=delete_tag,
                args=(tag.id,)
            )
else:
    st.info("No tags found")
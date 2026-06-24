import streamlit as st
from db import Tags, connect_db

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="Manage Tags")

# =========================
# INIT DB
# =========================
@st.cache_resource
def init_db():
    connect_db()

init_db()

st.title("🏷️ Manage Tags")


# =========================
# ADD TAG
# =========================
def add_tag(tag_name: str):

    tag_name = tag_name.strip().lower()

    if not tag_name:
        st.warning("Tag cannot be empty")
        return

    existing = (
        Tags
        .select()
        .where(Tags.name == tag_name)
        .first()
    )

    if existing:
        st.warning("Tag already exists")
        return

    try:
        Tags.create(name=tag_name)
        st.success(f"Tag '{tag_name}' added successfully")

    except Exception as e:
        st.error(f"Error adding tag: {e}")


# =========================
# DELETE TAG
# =========================
def delete_tag(tag_id: int):

    try:
        Tags.delete().where(
            Tags.id == tag_id
        ).execute()

        st.success("Tag deleted successfully")
        st.rerun()

    except Exception as e:
        st.error(f"Error deleting tag: {e}")


# =========================
# ADD TAG UI
# =========================
st.subheader("Add New Tag")

tag_input = st.text_input(
    "Enter tag name"
)

if st.button("Add Tag"):

    add_tag(tag_input)
    st.rerun()


# =========================
# SHOW TAGS
# =========================
st.subheader("Existing Tags")

tags = (
    Tags
    .select()
    .order_by(Tags.id.desc())
)

if tags.exists():

    for tag in tags:

        col1, col2 = st.columns([5, 1])

        with col1:
            st.write(f"🏷️ {tag.name}")

        with col2:
            if st.button(
                "🗑️",
                key=f"delete_{tag.id}"
            ):
                delete_tag(tag.id)

else:
    st.info("No tags found")
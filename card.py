import easyocr
import pandas as pd
import io
from PIL import Image
import easyocr
import mysql.connector
import streamlit as st
import numpy as np
import base64

# Initialize EasyOCR reader
reader = easyocr.Reader(['en'])

# Connect to MySQL database
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="aavddgg",
    database="carddb"
)
c = conn.cursor()

# Create table if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS image_text
             (id INT AUTO_INCREMENT PRIMARY KEY,
             image LONGBLOB,
             text TEXT)''')
conn.commit()

# Streamlit app
def main():
    st.title("Extract Text from Image")
    uploaded_file = st.file_uploader("Upload an image", type=['jpg', 'jpeg', 'png'])

    if uploaded_file is not None:
        image = uploaded_file.read()
        st.image(uploaded_file, caption='Uploaded Image', use_column_width=True)

        # Extract text from image
        result = reader.readtext(image)
        extracted_text_list = [res[1] for res in result]
        extracted_text='\n'.join(extracted_text_list)      
        extract_text=' '.join(extracted_text_list)

        # Display extracted text
        st.header("Extracted Text:")
        st.text_area("Extracted Text", value=extracted_text, height=200)
        image_bytes = io.BytesIO()
        image_pil = Image.open(uploaded_file)
        image_pil.save(image_bytes, format='PNG')
        image_bytes = image_bytes.getvalue()
        def convert_to_python_type(value):
         if isinstance(value, np.int64):
          return int(value)
         return value

        if st.button('save to database'):
        # Store image and extracted text in MySQL database
         sql = "INSERT INTO image_text (image, text) VALUES (%s, %s)"
         val = tuple(convert_to_python_type(v) if isinstance(v, np.int64) else v for v in (image_bytes, extract_text))
         c.execute(sql, val)
         
         conn.commit()
         st.success("Text extracted and saved to database.")

    operation = st.selectbox("Select Operation", ["Read", "Update", "Delete"], index=0)

    if operation == "Read":
            st.subheader("Read Data")
            c.execute("SELECT image, text FROM image_text")
            data = c.fetchall()
            if data:
             df=pd.DataFrame(data, columns=['image', 'text'])
             st.dataframe(df)

    elif operation == "Update":
            st.subheader("Update Data")
            c.execute("SELECT id, image, text FROM image_text")
            data = c.fetchall()
            if data:
             df=pd.DataFrame(data, columns=['id', 'image', 'text'])
             df.set_index('id', inplace=True)
             st.dataframe(df.reset_index())
             selected_id = st.number_input("Enter the id of the entry to update", min_value=df.index.min(), max_value=df.index.max(), value=df.index.min(), step=1)
             new_text=st.text_input('Enter the new text')
             if st.button("Update"):
                
                sql = "UPDATE image_text SET text = %s WHERE id = %s"
                val = (new_text, selected_id)
                c.execute(sql, val)
                conn.commit()
                st.success("Data updated successfully.")
                
                df.loc[selected_id, 'text'] = new_text
                st.subheader("Updated Data")
                st.dataframe(df.reset_index(drop=True))

    elif operation == "Delete":
            st.subheader("Delete Data")
            c.execute("SELECT id, image, text FROM image_text")
            data = c.fetchall()
            if data:
             df = pd.DataFrame(data, columns=['id', 'image', 'text'])
             df.set_index('id', inplace=True)
             st.dataframe(df.reset_index())
             
             selected_id = st.number_input("Enter the index of the entry to delete", min_value=df.index.min(), max_value=df.index.max(), value=df.index.min(), step=1)
             if st.button("Delete"):
                sql = "DELETE FROM image_text WHERE id = %s"
                val = (selected_id,)
                c.execute(sql, val)
                conn.commit()
                st.success("Data deleted successfully.")
                df.drop(selected_id, inplace=True)
                
                
                st.subheader("Updated Data")
                st.dataframe(df.reset_index(drop=True))
        
    

main()

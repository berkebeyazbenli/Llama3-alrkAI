import streamlit as st
import pandas as pd
import os
import requests
from dotenv import load_dotenv
from apimyllama import ApiMyLlama

load_dotenv()


csv_dosya_yolu = "data/dataset1.csv"
excel_dosya_yolu = "data/Alarko_personel_list.xlsx"


df_csv = pd.read_csv(csv_dosya_yolu)
df = pd.read_excel(excel_dosya_yolu)

st.title("ALARKO YAPAY ZEKA")

st.write("CSV Dosyası İçeriği:")
st.write(df_csv.head(3))

st.write("Excel Dosyası İçeriği:")
st.write(df.head(3))

api_anahtarı = os.getenv("API_KEY")
sunucu_ip = "localhost"
api_sunucu_port = 8000  

api = ApiMyLlama(sunucu_ip, api_sunucu_port)

prompt = st.text_input("Lütfen bir girdi girin:")

def verileri_al(prompt, df):
    relevant_info = ""
    email_keywords = ["e-mail", "email", "mail", "mails", "emails"]
    if any(keyword in prompt.lower() for keyword in email_keywords):
        mail_columns = df.columns[df.columns.str.contains('e-mail', case=False, na=False)]
        if not mail_columns.empty:
            for column in mail_columns:
                relevant_info += df[column].dropna().to_string(index=False) + "\n"
    else:
        keyword = prompt.split()[-1] 
        relevant_rows = df[df.apply(lambda row: row.astype(str).str.contains(keyword, case=False).any(), axis=1)]
        if not relevant_rows.empty:
            relevant_info = relevant_rows.to_string()
    return relevant_info

if st.button("Üret"):
    if prompt:
        with st.spinner("Cevap üretiliyor..."):
            try:
                relevant_info_csv = verileri_al(prompt, df_csv)
                relevant_info_excel = verileri_al(prompt, df)
                
                full_prompt = prompt
                if relevant_info_csv:
                    full_prompt += f"\n\nCSV Verileri:\n{relevant_info_csv}"
                    st.write(f"CSV Verilerinden Bulunan Cevap:\n{relevant_info_csv}")
                if relevant_info_excel:
                    full_prompt += f"\n\nExcel Verileri:\n{relevant_info_excel}"
                    st.write(f"Excel Verilerinden Bulunan Cevap:\n{relevant_info_excel}")
                
                response = api.generate(api_anahtarı, full_prompt, "llama3", stream=False)
                st.write(response["response"]) 
                
            except requests.RequestException as e:
                st.error(f"Bir hata oluştu: {e}")
            except KeyError as e:
                st.error(f"Yanıt yapısında beklenmeyen anahtar: {e}")

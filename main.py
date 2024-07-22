import streamlit as st
import pandas as pd
import os
import requests
from dotenv import load_dotenv
from difflib import get_close_matches
from apimyllama import ApiMyLlama

load_dotenv()

csv_dosya_yolu = "data/newDataset2.csv"
excel_dosya_yolu = "data/Alarko_personel_list.xlsx"

df_csv = pd.read_csv(csv_dosya_yolu)
df = pd.read_excel(excel_dosya_yolu)

if 'kategori' not in df_csv.columns:
    df_csv['kategori'] = ''

if 'kategori' not in df.columns:
    df['kategori'] = ''

st.title("ALARKO YAPAY ZEKA")

api_anahtarı = os.getenv("API_KEY")
sunucu_ip = "localhost"
api_sunucu_port = 8000

api = ApiMyLlama(sunucu_ip, api_sunucu_port)

prompt = st.text_input("Lütfen bir girdi girin:")

# Hazır sorular ve cevaplar
questions_and_answers = {
    "Alarko Holding ne zaman kurulmuştur?": "Alarko Holding, 1954 yılında İshak Alaton ve Üzeyir Garih tarafından kurulmuştur.",
    "Alarko Holding hangi sektörlerde faaliyet göstermektedir?": "Alarko Holding, altyapı inşaatı, enerji, finans, gayrimenkul, hafif sanayi ve turizm sektörlerinde faaliyet göstermektedir.",
    "Alarko Holding’in kurucuları kimlerdir?": "Alarko Holding'in kurucuları İshak Alaton ve Üzeyir Garih'tir.",
    "Alarko Holding’in halka açıldığı yıl nedir?": "Alarko Holding, 1974 yılında halka açılmıştır.",
    "Alarko Holding’in tarihçesi nedir?": "Alarko Holding, 1954 yılında İshak Alaton ve Üzeyir Garih tarafından kurulmuş ve ilk yıllarında ısıtma, klima, soğutma işleri ile uğraşmıştır. 1973 yılında holding haline gelmiş ve 1974 yılında halka açılmıştır.",
    "Alarko'da kaç kişi çalışmaktadır?": "Bugün, 70 yıllık köklü geçmişi, 7 farklı faaliyet alanı, uluslararası yabancı ortaklıklar olmak üzere toplam 26 kuruluşu, 7.000 çalışanı ve 2022 sonu itibariyle yaklaşık 74 milyar TL kombine cirosu ile Türkiye'nin önde gelen sanayi kuruluşlarından biridir.",
    "Alarko Holding’in genel merkezi nerededir?": "İstanbul/Beşiktaş",
    "Alarko'nun alt şirketleri ya da yan şirketleri nelerdir?": """
        Alarko Carrier
        Alarko GYO
        Meram Elektrik
        Attaş Alarko Turistik Tesisler A.Ş.
        TÜM TESİSAT VE İNŞAAT A.Ş.
        SARET SANAYİ TAAHHÜTLERİ VE TİCARET A.Ş.
        MERAM ELEKTRİK DAĞITIM A.Ş.
        ALCEN ENERJİ DAĞITIM VE PERAKENDE SAT.HİZ.A.Ş.
        ALARKO FENNİ MALZEME SATIŞ VE İMALAT A.Ş.
        ALDEM ALARKO KONUT İNŞAAT VE TİC.A.Ş.
        ALARKO GAYRİMENKUL YATIRIM ORTAKLIĞI A.Ş.
        ALTEK ALARKO ELEKTRİK SAN.TES.İŞL.VE TİC.A.Ş.
        ALARKO CARRIER SANAYİ VE TİCARET A.Ş.
        MERAM ELEKTRİK ENERJİSİ TOPTAN SATIŞ A.Ş.
        MERAM ELEKTRİK PERAKENDE SATIŞ A.Ş.
        ALARKO KONUT PROJELERİ GELİŞTİRME A.Ş.
        ALEN ALARKO ENERJİ TİCARET A.Ş.
        ALSİM ALARKO SANAYİ TESİSLERİ VE TİCARET A.Ş.
    """
}

keyword_mapping = {
    "VPN Yapılandırması": ["vpn", "kurulum", "globalprotect", "bağlantı", "yapılandırma", "uzaktan bağlantı"],
    "Transfer Kılavuzu": ["transfer", "dosya paylaşımı", "atransfer", "şirket içi dosya paylaşımı"],
    "Ad Parola Değişikliği": ["parola", "şifre", "hesap", "değişikliği", "unuttum"],
    "Alarko Tarihçe": ["tarihçe", "kuruluş", "faaliyet"]
}

def verileri_al(prompt, df):
    relevant_info = ""
    email_keywords = ["e-mail", "email", "mail", "mails", "emails", "mailler", "mailleri", "E-mail"]
    if any(keyword in prompt.lower() for keyword in email_keywords):
        mail_columns = df.columns[df.columns.str.contains('E-mail', case=False, na=False)]
        if not mail_columns.empty:
            for column in mail_columns:
                relevant_info += df[column].dropna().to_string(index=False) + "\n"
    else:
        for category, keywords in keyword_mapping.items():
            if any(keyword in prompt.lower() for keyword in keywords):
                relevant_rows = df[df['kategori'] == category]
                if not relevant_rows.empty:
                    relevant_info = relevant_rows.to_string(index=False)
                    break
    return relevant_info

def find_best_match(question, prepared_answers):
    questions = list(prepared_answers.keys())
    best_match = get_close_matches(question, questions, n=1, cutoff=0.6)
    if best_match:
        return prepared_answers[best_match[0]]
    return None

if st.button("Üret"):
    if prompt:
        with st.spinner("Cevap aranıyor..."):
            best_match_answer = find_best_match(prompt, questions_and_answers)
            if best_match_answer:
                st.write("Bulunan Cevap:")
                st.write(best_match_answer)
            else:
                relevant_info_csv = verileri_al(prompt, df_csv)
                relevant_info_excel = verileri_al(prompt, df)

                if relevant_info_csv or relevant_info_excel:
                    if relevant_info_csv:
                        st.write("Bulunan Cevap:")
                        st.write(f"{relevant_info_csv}")
                    if relevant_info_excel:
                        st.write("Bulunan Cevap:")
                        st.write(f"{relevant_info_excel}")
                else:
                    with st.spinner("Cevap üretiliyor..."):
                        try:
                            full_prompt = prompt
                            response = api.generate(api_anahtarı, full_prompt, "llama3", stream=False)
                            st.write(response["response"])
                        except requests.RequestException as e:
                            st.error(f"Bir hata oluştu: {e}")
                        except KeyError as e:
                            st.error(f"Yanıt yapısında beklenmeyen anahtar: {e}")

#!/usr/bin/env python3

import os
import json
import streamlit as st
from groq import Groq
from dotenv import load_dotenv

# โหลด environment variables จากไฟล์ .env
load_dotenv(".env")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

def chatboot(question):
    system_prompt = """
Cancer Pain Management Chatbot
language: "Thai"

role: |
  คุณคือแชทบอทด้านการแพทย์ที่ออกแบบเพื่อช่วยผู้ป่วยและผู้ดูแลผู้ป่วยมะเร็ง
  ในการประเมินและจัดการอาการปวด โดยอ้างอิงจาก:
  - PainAD (5 มิติ: การหายใจ, การเปล่งเสียง, สีหน้า, ภาษากาย, การปลอบโยน)
  - Edmonton Classification System for Cancer Pain (ECS-CP: Mechanism, Incident, Psychological, Social)
  - WHO 3-step guideline ในการจัดการอาการปวด

instruction: |
  - จัดระดับความปวด: No pain / Mild / Moderate / Severe / Incident pain / Psychological factor / Social factor
  - แนะนำการจัดการตามแนวทาง WHO และบริบท
  - ต้องตอบด้วยภาษาไทย สุภาพ ตรงไปตรงมา
  - ทุกคำตอบต้องมี 3 ส่วน: 
    1) ระดับความปวด 
    2) แนวทางการจัดการ 
    3) เหตุผลสั้น ๆ
  - หากอยู่นอกเหนือขอบเขต ให้ตอบว่า:
    "ไม่สามารถให้คำตอบทางการแพทย์ได้ กรุณาติดต่อทีมแพทย์ผู้ดูแลของท่าน"
  - ห้ามสร้างข้อมูลที่ไม่มีหลักฐาน (no hallucination)
  - ห้ามวินิจฉัยโรคใหม่หรือนอกเหนือจาก guideline

output_format: |
  ระดับความปวด: [No pain / Mild / Moderate / Severe / Incident pain / Psychological factor / Social factor]
  แนวทางการจัดการ: [ข้อความสั้น ๆ ตาม WHO guideline]
  เหตุผล: [ข้อความสั้น ๆ อธิบายว่าใช้ criteria ไหน]

examples:

- Input: "ผู้ป่วยหายใจหอบ เสียงคราง สีหน้าบูดเบี้ยว ขยับตัวไม่อยู่นิ่ง ต้องปลอบบ่อย ๆ"
  Output:
    ระดับความปวด: Severe pain
    แนวทางการจัดการ: พิจารณา opioid ตาม WHO ขั้นที่ 3 และติดตามอาการใกล้ชิด
    เหตุผล: PainAD ผิดปกติหลายมิติรุนแรง

- Input: "ผู้ป่วยนั่งเงียบ หายใจปกติ ไม่มีสีหน้าปวด ขยับตัวสบาย ไม่ต้องปลอบ"
  Output:
    ระดับความปวด: No pain
    แนวทางการจัดการ: ไม่ต้องให้ยาเพิ่มเติม เพียงติดตามอาการ
    เหตุผล: ทุกมิติเป็นปกติ

- Input: "ผู้ป่วยถอนหายใจบ่อยๆ บ่นปวดเล็กน้อย สีหน้าเบี้ยวเล็กน้อย แต่ยังยิ้มตอบได้"
  Output:
    ระดับความปวด: Mild pain
    แนวทางการจัดการ: ใช้ยา non-opioid เช่น พาราเซตามอล และติดตามอาการ
    เหตุผล: มีอาการเล็กน้อยใน 2 มิติ

- Input: "ผู้ป่วยมีอาการปวดเฉียบพลันเวลาลุกจากเตียง"
  Output:
    ระดับความปวด: Incident pain
    แนวทางการจัดการ: ปรับยาก่อนการทำกิจกรรม
    เหตุผล: ปวดสัมพันธ์กับ movement

- Input: "ผู้ป่วยกังวลและร้องไห้บ่อย ถึงแม้ปวดไม่มาก"
  Output:
    ระดับความปวด: Psychological factor
    แนวทางการจัดการ: เสริมการให้คำปรึกษาหรือการสนับสนุนทางจิตใจ
    เหตุผล: ปัจจัยทางจิตใจเพิ่ม perception ของความปวด

- Input: "ครอบครัวผู้ป่วยไม่เข้าใจการใช้ยา ทำให้ผู้ป่วยไม่ได้รับยาอย่างต่อเนื่อง"
  Output:
    ระดับความปวด: Social factor
    แนวทางการจัดการ: จัดการด้านการสื่อสารและการให้ความรู้แก่ครอบครัว
    เหตุผล: ปัจจัยสังคมส่งผลต่อ pain control

- Input: "ผู้ป่วยหายใจแรงเป็นช่วงๆ แต่ไม่คราง สีหน้าเรียบเฉย"
  Output:
    ระดับความปวด: Mild pain
    แนวทางการจัดการ: ใช้ยา non-opioid และติดตาม
    เหตุผล: การหายใจผิดปกติเล็กน้อย

- Input: "ผู้ป่วยยกมือกุมท้องบ่อย สีหน้าบึ้งแต่ยังพูดคุยได้"
  Output:
    ระดับความปวด: Moderate pain
    แนวทางการจัดการ: เริ่ม opioid ขนาดต่ำตาม WHO ขั้นที่ 2
    เหตุผล: Body language + facial expression ผิดปกติชัดเจน

- Input: "ผู้ป่วยร้องเสียงดังและดิ้นไปมา ต้องมีคนจับไว้"
  Output:
    ระดับความปวด: Severe pain
    แนวทางการจัดการ: ให้ opioid ตาม WHO ขั้นที่ 3 และเฝ้าระวังอาการข้างเคียง
    เหตุผล: Vocalization + agitation สูง

- Input: "ผู้ป่วยยิ้ม หายใจปกติ ไม่มีการร้องหรือบ่น"
  Output:
    ระดับความปวด: No pain
    แนวทางการจัดการ: ไม่ต้องให้ยาเพิ่มเติม เพียงติดตาม
    เหตุผล: ไม่มีสัญญาณปวด

    Schema:
{
  "pain_level": "No pain | Mild pain | Moderate pain | Severe pain | Incident pain | Psychological factor | Social factor",
  "management": "ข้อความสั้น ๆ แนะนำการจัดการตาม WHO guideline",
  "reason": "ข้อความสั้น ๆ อธิบายสาเหตุการประเมินตาม PainAD/ECS-CP",
  "mechanism": "ถ้ามี ให้ระบุ เช่น Neuropathic, Nociceptive, Mixed",
  "incident_pain": "ถ้ามี อธิบายสั้น ๆ",
  "psychological": "ถ้ามี อธิบายสั้น ๆ",
  "social": "ถ้ามี อธิบายสั้น ๆ"
}

ห้ามตอบนอกเหนือ schema นี้
ถ้าอยู่นอกเหนือขอบเขต ให้ตอบ:
{
  "pain_level": "ไม่ระบุ",
  "management": "ไม่สามารถให้คำตอบทางการแพทย์ได้ กรุณาติดต่อทีมแพทย์ผู้ดูแลของท่าน",
  "reason": "Out of scope",
  "mechanism": "",
  "incident_pain": "",
  "psychological": "",
  "social": ""
}
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ],
        temperature=0.2,
        max_tokens=2048,
    )
    return response.choices[0].message.content.strip()


def main():
    # 🖼️ ตั้งค่าหน้าและธีมสี
    st.set_page_config(page_title="AI Cancer Pain Care Bot", page_icon="💊", layout="wide")
    st.markdown("""
        <style>
        body { background-color: #000000; }
        .stForm { background-color: #1a1a1a; padding: 2rem; border-radius: 12px; color: #ffffff; }
        </style>
    """, unsafe_allow_html=True)

    st.title("💊 แชตบอตดูแลอาการปวดมะเร็ง")
    st.subheader("ช่วยประเมินและจัดการอาการปวดตาม PainAD & ECS-CP")

    # 🧾 เก็บข้อความสนทนา
    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {"role": "assistant", "content": "สวัสดีค่ะ ฉันสามารถช่วยคุณประเมินอาการปวดมะเร็งได้จากการบรรยายอาการ 5 มิติค่ะ 💊"}
        ]

    with st.form("chat_form"):
        query = st.text_input("🗣️ คุณ:", placeholder="พิมพ์ลักษณะอาการปวด สีหน้า ท่าทาง หรือสิ่งที่ผู้ป่วยแสดงออก...").strip()
        submitted = st.form_submit_button("🚀 ส่งข้อความ")

        if submitted and query:
            answer = chatboot(query)
            st.session_state["messages"].append({"role": "user", "content": query})
            st.session_state["messages"].append({"role": "assistant", "content": answer})
        elif submitted and not query:
            st.warning("⚠️ กรุณาพิมพ์คำถามก่อนส่ง")

    # 🧠 แสดงผลแชตพร้อมจัดการ JSON
    for msg in st.session_state["messages"]:
        if msg["role"] == "user":
            st.markdown(f"**🧑‍⚕️ คุณ:** {msg['content']}")
        else:
            try:
                data = json.loads(msg["content"])
                with st.container():
                    st.markdown("#### 🤖 ผลการประเมินอาการปวด")
                    col1, col2 = st.columns(2)
                    col1.metric("ระดับความปวด", data.get("pain_level", "ไม่ระบุ"))
                    col1.metric("กลไกการปวด (Mechanism)", data.get("mechanism", "ไม่ระบุ"))
                    col2.metric("Incident Pain", data.get("incident_pain", "ไม่ระบุ"))
                    col2.metric("ปัจจัยจิตใจ (Psychological)", data.get("psychological", "ไม่ระบุ"))
                    st.metric("ปัจจัยสังคม (Social)", data.get("social", "ไม่ระบุ"))
                    st.info(data.get("reason", ""))
            except Exception:
                st.markdown(f"**🤖 บอท:** {msg['content']}")

if __name__ == "__main__":
    main()

import os, subprocess, textwrap, shutil, wave
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

OUT = "/home/claude/ScamShield_Demo_Pack"
for d in ["1_SMS_screenshots", "2_WhatsApp_screenshots", "3_QR_codes", "4_Audio_calls", "5_Paste_text"]:
    os.makedirs(f"{OUT}/{d}", exist_ok=True)

FD = "/usr/share/fonts/truetype/google-fonts/"
def F(name, size): return ImageFont.truetype(FD + f"Poppins-{name}.ttf", size)

# ---------------------------------------------------------------- screenshots
W, H = 720, 1440
def wrap(draw, text, font, maxw):
    lines = []
    for para in text.split("\n"):
        cur = ""
        for w in para.split(" "):
            t = (cur + " " + w).strip()
            if draw.textlength(t, font=font) <= maxw: cur = t
            else:
                lines.append(cur); cur = w
        lines.append(cur)
    return lines

def chat_screenshot(path, app, sender, sub, messages, time_label="10:42"):
    sms = app == "sms"
    bg = "#FFFFFF" if sms else "#ECE5DD"
    head = "#F2F2F7" if sms else "#075E54"
    fg = "#111111" if sms else "#FFFFFF"
    img = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 150], fill=head)
    d.text((34, 24), time_label, font=F("Medium", 26), fill=fg)
    d.text((W - 190, 24), "5G   82%", font=F("Regular", 22), fill=fg)
    d.ellipse([34, 70, 112, 148 - 0], fill="#9AA5B1" if sms else "#CFD8DC")
    d.text((58, 84), sender[0].upper() if sender[0].isalpha() else "#", font=F("Bold", 36), fill="#FFFFFF")
    d.text((132, 70), sender, font=F("Bold", 30), fill=fg)
    d.text((132, 110), sub, font=F("Regular", 21), fill="#6B7280" if sms else "#D1F2EB")
    y = 200
    d.rounded_rectangle([W//2 - 90, y, W//2 + 90, y + 40], 14, fill="#E5E7EB" if sms else "#FFF3C4")
    d.text((W//2 - 52, y + 6), "Today", font=F("Medium", 21), fill="#555")
    y += 80
    f = F("Regular", 27)
    for who, text, t in messages:
        incoming = who == "in"
        lines = wrap(d, text, f, 470)
        bh = len(lines) * 40 + 56
        bw = int(max(d.textlength(l, font=f) for l in lines)) + 60
        bw = max(bw, 150)
        x0 = 30 if incoming else W - 30 - bw
        col = ("#E9E9EB" if sms else "#FFFFFF") if incoming else ("#0B93F6" if sms else "#DCF8C6")
        d.rounded_rectangle([x0, y, x0 + bw, y + bh], 26, fill=col)
        tc = "#FFFFFF" if (sms and not incoming) else "#111111"
        for i, l in enumerate(lines):
            d.text((x0 + 30, y + 16 + i * 40), l, font=f, fill=tc)
        d.text((x0 + bw - 100, y + bh - 36), t, font=F("Regular", 17), fill="#8A8F98" if incoming else ("#CFE8FF" if sms else "#6B8F5E"))
        y += bh + 26
    # input bar
    d.rectangle([0, H - 130, W, H], fill="#F2F2F7" if sms else "#F0F0F0")
    d.rounded_rectangle([30, H - 100, W - 30, H - 36], 32, fill="#FFFFFF", outline="#D1D5DB")
    d.text((62, H - 86), "Text message" if sms else "Message", font=F("Regular", 24), fill="#9CA3AF")
    img.save(path)

SMS = "1_SMS_screenshots"; WA = "2_WhatsApp_screenshots"
S = [
 (SMS, "SCAM_01_kyc_expiry_sms", "sms", "VK-SBIKYC", "Unknown sender", [("in",
   "Dear customer, your SBI account will be BLOCKED today. KYC expired. Update immediately: http://sbi-kyc-update.example/login and enter your OTP to avoid suspension.", "10:41")]),
 (SMS, "SCAM_02_digital_arrest_sms", "sms", "+91 98765 4XXXX", "Unknown sender", [("in",
   "This is CBI Cyber Cell. A parcel in your name contains illegal items. You are under DIGITAL ARREST. Join video call now: http://cbi-verify.example/join. Do NOT tell anyone or you will be arrested.", "09:15")]),
 (SMS, "SCAM_03_electricity_cut_sms", "sms", "AX-POWERB", "Unknown sender", [("in",
   "Your electricity will be disconnected tonight 9:30 PM as last month bill is unpaid. Call officer now 98XXX XXXXX or click http://power-bill-pay.example to pay Rs 10 and update.", "17:02")]),
 (SMS, "REAL_01_bank_debit_alert_sms", "sms", "VM-HDFCBK", "Verified sender", [("in",
   "Rs 450.00 debited from A/c XX1234 on 18-11-26 to VPA sharmatea@okaxis (UPI Ref 6123456789). Not you? Call 1800 202 6161 or visit your branch. -HDFC Bank", "11:05")]),
 (SMS, "REAL_02_otp_with_warning_sms", "sms", "AD-AMAZON", "Verified sender", [("in",
   "123456 is your Amazon OTP. Do not share it with anyone, including Amazon staff. We will never ask for your OTP.", "14:20")]),
 (SMS, "REAL_03_train_ticket_sms", "sms", "IR-IRCTC", "Verified sender", [("in",
   "PNR 2412345678 CNF. Train 12609 Bengaluru-Chennai on 20-Nov-26. Coach S5 Seat 41. Happy journey. -IRCTC", "08:30")]),
 (WA, "SCAM_04_fake_job_whatsapp", "wa", "+91 91234 5XXXX", "last seen today at 12:10", [
   ("in", "Hi! Earn Rs 5,000 to Rs 15,000 daily just by liking YouTube videos from home. No experience needed. 100% guaranteed income!", "12:08"),
   ("out", "Is it real? Do I need to pay anything?", "12:09"),
   ("in", "Just a small registration fee of Rs 500 to activate your task account. Pay now to this UPI: jobs.activate@upi. You will get Rs 800 back today. Limited slots, hurry!", "12:10")]),
 (WA, "SCAM_05_upi_mistake_whatsapp", "wa", "+91 90123 4XXXX", "online", [
   ("in", "Sir sorry, I sent Rs 15,000 to your number by mistake. Please return it urgently, my mother is in hospital.", "15:44"),
   ("in", "I have sent you a payment request. Please approve it and enter your UPI PIN to send back my money.", "15:45")]),
 (WA, "SCAM_06_investment_group_whatsapp", "wa", "Stock Gold VIP 🚀", "+91 88XXX XXXXX added you", [
   ("in", "Welcome! Our expert gives GUARANTEED 300% returns in 7 days. Deposit Rs 10,000 today and get Rs 40,000. Hundreds already earned. Join now, offer ends tonight!", "19:30"),
   ("in", "Download our trading app from this link (APK) and transfer to the company account to start: http://gold-trade-vip.example/app.apk", "19:31")]),
 (WA, "REAL_04_delivery_update_whatsapp", "wa", "Rohan (Delivery)", "online", [
   ("in", "Hello, I am your delivery partner. I will reach your building gate in 5 minutes with your order. Please keep it ready to collect. Order is already paid online.", "13:10"),
   ("out", "Okay, thanks. Please call when you are at the gate.", "13:11")]),
 (WA, "REAL_05_family_message_whatsapp", "wa", "Amma ❤", "online", [
   ("in", "Reached home safely? Dinner is ready. Come soon, we are making your favourite sambar rice.", "20:15"),
   ("out", "On my way Amma. I will be there in 20 minutes.", "20:17")]),
 (WA, "REAL_06_college_notice_whatsapp", "wa", "Prof. Anitha (COA)", "last seen today at 10:00", [
   ("in", "Reminder: COA PBL demo is on Monday 10 AM in Lab 3. Bring your report draft. Please do not share any fees or personal details in this group.", "10:00")]),
]
for folder, name, app, sender, sub, msgs in S:
    chat_screenshot(f"{OUT}/{folder}/{name}.png", app, sender, sub, msgs)

# ---------------------------------------------------------------- QR codes
enc = cv2.QRCodeEncoder_create()
def make_qr(path, data, label, verdict):
    q = enc.encode(data)
    q = cv2.resize(q, None, fx=14, fy=14, interpolation=cv2.INTER_NEAREST)
    qi = Image.fromarray(q).convert("RGB")
    qi = Image.fromarray(np.array(qi))
    pad = 70
    canvas = Image.new("RGB", (qi.width + pad * 2, qi.height + pad * 2 + 130), "white")
    canvas.paste(qi, (pad, pad + 20))
    d = ImageDraw.Draw(canvas)
    d.text((pad, 24), label, font=F("Bold", 26), fill="#111")
    d.text((pad, qi.height + pad + 40), "(demo file - for ScamShield testing)", font=F("Regular", 20), fill="#777")
    canvas.save(path)

Q = "3_QR_codes"
make_qr(f"{OUT}/{Q}/SCAM_01_fake_kyc_phishing_link_qr.png", "http://sbi-kyc-update.example/login", "Update KYC - Scan Now", 0)
make_qr(f"{OUT}/{Q}/SCAM_02_upi_collect_refund_qr.png", "upi://pay?pa=refund.claim7788@upi&pn=Refund%20Desk&am=4999&cu=INR&tn=Claim%20Refund", "Scan to RECEIVE Rs 4,999 refund", 0)
make_qr(f"{OUT}/{Q}/SCAM_03_fake_parking_fine_qr.png", "http://traffic-fine-pay.example/challan?id=KA01", "Parking Fine - Pay Now", 0)
make_qr(f"{OUT}/{Q}/REAL_01_shop_upi_payment_qr.png", "upi://pay?pa=sharmatea@okaxis&pn=Sharma%20Tea%20Stall&cu=INR", "Sharma Tea Stall - Pay via UPI", 1)
make_qr(f"{OUT}/{Q}/REAL_02_sancharsaathi_official_qr.png", "https://sancharsaathi.gov.in/", "Sanchar Saathi (Govt. of India)", 1)
make_qr(f"{OUT}/{Q}/REAL_03_cybercrime_portal_qr.png", "https://cybercrime.gov.in/", "National Cyber Crime Portal", 1)

# ---------------------------------------------------------------- audio
def tts(text, voice, path, rate=None):
    safe = text.replace("'", "").replace(":", " ").replace(",", " ,")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i",
        f"flite=text='{safe}':voice={voice}", "-ar", "16000", "-ac", "1", path], check=True)

def silence(sec, path):
    subprocess.run(["ffmpeg","-y","-loglevel","error","-f","lavfi","-i",f"anullsrc=r=16000:cl=mono","-t",str(sec),path],check=True)

def make_call(name, lines):
    tmp = "/tmp/callparts"; shutil.rmtree(tmp, ignore_errors=True); os.makedirs(tmp)
    parts = []
    for i, (voice, text) in enumerate(lines):
        p = f"{tmp}/p{i}.wav"; tts(text, voice, p); parts.append(p)
        s = f"{tmp}/s{i}.wav"; silence(0.45, s); parts.append(s)
    lst = f"{tmp}/list.txt"
    open(lst, "w").write("".join(f"file '{p}'\n" for p in parts))
    raw = f"{tmp}/joined.wav"
    subprocess.run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",lst,"-c","copy",raw],check=True)
    # phone-line effect: band-limit + light line noise
    for ext, codec in (("wav", []), ("mp3", ["-codec:a", "libmp3lame", "-b:a", "96k"])):
        subprocess.run(["ffmpeg","-y","-loglevel","error","-i",raw,
            "-af","highpass=f=300,lowpass=f=3400,volume=1.8","-ar","16000"]+codec+[f"{OUT}/4_Audio_calls/{name}.{ext}"],check=True)

make_call("SCAM_01_digital_arrest_call", [
 ("awb", "Hello. This is Inspector Rajesh Verma from the C B I Cyber Crime Branch. A parcel booked in your name has been seized with illegal items and your Aadhaar is linked to money laundering."),
 ("slt", "What? I did not send any parcel."),
 ("awb", "You are now under digital arrest. Do not disconnect this video call and do not tell your family or anyone. If you tell anyone you will be arrested immediately."),
 ("awb", "To clear your name you must transfer fifty thousand rupees to the R B I safe account right now. Share the O T P that you receive on your phone. This is your last chance."),
])
make_call("SCAM_02_bank_kyc_otp_call", [
 ("rms", "Hello sir. I am calling from your bank head office. Your K Y C has expired and your account will be blocked in two hours."),
 ("slt", "Oh no. What should I do?"),
 ("rms", "Do not worry sir. I will update it right now. Please tell me the six digit O T P you just received, and your card number and C V V for verification. Quickly sir, it is urgent."),
])
make_call("SCAM_03_upi_refund_mistake_call", [
 ("rms", "Hello brother. I am very sorry. I sent you ten thousand rupees by mistake on U P I. Please return it, it is an emergency."),
 ("slt", "I have not checked. Let me see."),
 ("rms", "I have sent you a collect request. Just approve it and enter your U P I pin and the money will come back to me. Please do it fast sir."),
])
make_call("REAL_01_bank_info_call", [
 ("slt", "Good afternoon. This is an information call from your bank. Your credit card statement for this month is now available on the official mobile app."),
 ("slt", "Please note, we will never ask for your O T P, P I N, or C V V on a call. If you have any questions, visit your nearest branch or call the number printed on the back of your card. Thank you, and have a nice day."),
])
make_call("REAL_02_family_call", [
 ("kal", "Hi, it is me. I will reach home by seven today."),
 ("slt", "Okay. Do you need anything from the market?"),
 ("kal", "Yes, please get some vegetables and milk. See you soon, bye."),
])
make_call("REAL_03_delivery_call", [
 ("rms", "Hello, I am your delivery partner. I am outside your building gate with your order. Please come down to collect it."),
 ("slt", "Do I need to pay anything?"),
 ("rms", "No ma am, it is already paid online. Just show me the order number on the app. Thank you."),
])

# ---------------------------------------------------------------- paste-text files
P = "5_Paste_text"
paste = {
 "SCAM_paste_01_kyc.txt": "Dear customer, your SBI account will be BLOCKED today. KYC expired. Update immediately: http://sbi-kyc-update.example/login and enter your OTP to avoid suspension.",
 "SCAM_paste_02_digital_arrest.txt": "This is CBI Cyber Cell. A parcel in your name contains illegal items. You are under DIGITAL ARREST. Join video call now. Do NOT tell anyone or you will be arrested. Transfer Rs 50,000 to the safe account to clear your name.",
 "SCAM_paste_03_fake_job.txt": "Earn Rs 5,000 to Rs 15,000 daily by liking videos from home. 100% guaranteed income! Pay a small registration fee of Rs 500 to activate your account. Limited slots, hurry!",
 "SCAM_paste_04_upi_collect.txt": "Sorry sir, I sent Rs 15,000 to you by mistake. I have sent a payment request. Please approve it and enter your UPI PIN to return my money urgently.",
 "REAL_paste_01_bank_debit.txt": "Rs 450.00 debited from A/c XX1234 on 18-11-26 to VPA sharmatea@okaxis (UPI Ref 6123456789). Not you? Call 1800 202 6161 or visit your branch. -HDFC Bank",
 "REAL_paste_02_otp.txt": "123456 is your Amazon OTP. Do not share it with anyone, including Amazon staff.",
 "REAL_paste_03_family.txt": "Reached home safely? Dinner is ready. Come soon, we are making your favourite sambar rice.",
}
for k, v in paste.items(): open(f"{OUT}/{P}/{k}", "w").write(v + "\n")
print("done")

# ScamShield Family - Demo Test Pack

Every file starts with **SCAM_** or **REAL_**, so you always know what result your website should show.

| Folder | Upload to tab | Files | Expected result |
|---|---|---|---|
| 1_SMS_screenshots | SMS | SCAM_01-03, REAL_01-03 | SCAM = Scam / High risk, REAL = Safe |
| 2_WhatsApp_screenshots | WhatsApp | SCAM_04-06, REAL_04-06 | same |
| 3_QR_codes | any scanner / QR input | SCAM_01-03, REAL_01-03 | same |
| 4_Audio_calls (.mp3 and .wav) | Call | SCAM_01-03, REAL_01-03 | same |
| 5_Paste_text | paste into text box | SCAM_01-04, REAL_01-03 | same |

## Suggested live-demo order (about 2 minutes)
1. SMS: upload `SCAM_01_kyc_expiry_sms.png` (flagged), then `REAL_01_bank_debit_alert_sms.png` (safe)
2. WhatsApp: `SCAM_05_upi_mistake_whatsapp.png` (flagged), then `REAL_04_delivery_update_whatsapp.png` (safe)
3. Call: play `SCAM_01_digital_arrest_call.mp3` (flagged), then `REAL_02_family_call.mp3` (safe)
4. QR: `SCAM_02_upi_collect_refund_qr.png` (flagged), then `REAL_02_sancharsaathi_official_qr.png` (safe)

## Notes
- All names, numbers, UPI IDs and links are fictional. Scam links use the reserved `.example` domain, so they cannot lead to a real site. Phone numbers are masked with X.
- Audio uses a basic text-to-speech voice with a phone-line filter. It sounds robotic. For a more natural demo, record your own voice reading the same lines (they are in the Paste_text folder and in regenerate_pack.py).
- To change any text, QR link or audio line, edit `regenerate_pack.py` and run `python3 regenerate_pack.py`.
- Your site decides the actual verdict. If it gives a wrong result for a file, that is a useful bug to find before the demo.

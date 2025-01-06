import qrcode

# Replace with your server URL
url = "http://140.138.55.212:8000"

# Generate QR code
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)
qr.add_data(url)
qr.make(fit=True)

# Save QR code as an image
img = qr.make_image(fill_color="black", back_color="white")
img.save("server_qr_code.png")

print("QR code saved as 'server_qr_code.png'.")

from PIL import Image

def set_LSB(value, bit):
    if bit == '0':
        value = value & 254
    else:
        value = value | 1
    return value

message = "TARGET:192.168.1.50"

binary = ''.join([format(ord(c), '08b') for c in message])

img = Image.open("company_logo.png")
img = img.convert("RGBA")

pixels = list(img.getdata())

new_pixels = []

bit_index = 0

for i in range(len(pixels)):

    pixel = list(pixels[i])

    if bit_index < len(binary):

        for j in range(4):

            if bit_index < len(binary):
                pixel[j] = set_LSB(pixel[j], binary[bit_index])
                bit_index += 1
    
    new_pixels.append(tuple(pixel))


img.putdata(new_pixels)
img.save("company_logo_stego.png")

print("Message hidden successfully!")
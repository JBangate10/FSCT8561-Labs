from PIL import Image
import stepic

img = Image.open("profile_secret.png")

data = stepic.decode(img)

print("Recovered data:", data)
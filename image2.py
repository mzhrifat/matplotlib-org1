from PIL import Image, ImageOps, ImageDraw

# ছবির পাথ
img_path = "rsz_img_2881.jpg"

# ছবি ওপেন করে RGBA তে কনভার্ট করা
img = Image.open(img_path).convert("RGBA")

# মাস্ক বানানো (কালো ব্যাকগ্রাউন্ড)
mask = Image.new("L", img.size, 0)

# মাস্কে বৃত্ত আঁকা
draw = ImageDraw.Draw(mask)
size = min(img.size)
center = (img.size[0] // 2, img.size[1] // 2)
draw.ellipse(
    (center[0] - size//2, center[1] - size//2,
     center[0] + size//2, center[1] + size//2),
    fill=255
)

# ছবিতে মাস্ক লাগানো
rounded_img = ImageOps.fit(img, mask.size, centering=(0.5, 0.5))
rounded_img.putalpha(mask)

# সবুজ ব্যাকগ্রাউন্ড তৈরি
green_bg = Image.new("RGBA", img.size, (0, 255, 0, 255))  # সবুজ রঙ

# ব্যাকগ্রাউন্ডে ছবি পেস্ট করা
green_bg.paste(rounded_img, (0, 0), rounded_img)

# আউটপুট সেভ করা
green_bg.save("rounded_profile_green.png")

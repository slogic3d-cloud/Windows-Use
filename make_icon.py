"""Erstellt zero.ico — einmalig ausführen, dann braucht es nicht mehr gestartet werden."""
from PIL import Image, ImageDraw

def make():
    sizes = [16, 32, 48, 64, 128, 256]
    frames = []

    for s in sizes:
        img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)

        # Hintergrund (dunkler Kreis)
        d.ellipse([0, 0, s - 1, s - 1], fill=(5, 10, 14, 255))

        # Äußerer Teal-Ring
        rw = max(1, s // 14)
        d.ellipse([rw, rw, s - 1 - rw, s - 1 - rw],
                  outline=(0, 221, 180, 255), width=rw)

        # Innerer Glow-Ring
        rw2 = rw * 3
        d.ellipse([rw2, rw2, s - 1 - rw2, s - 1 - rw2],
                  outline=(0, 221, 180, 80), width=max(1, rw // 2))

        # Zentraler Leuchtpunkt
        c = s // 2
        dot = max(1, s // 10)
        d.ellipse([c - dot, c - dot, c + dot, c + dot],
                  fill=(0, 221, 180, 255))

        frames.append(img)

    frames[0].save(
        "zero.ico",
        format="ICO",
        sizes=[(s, s) for s in sizes],
        append_images=frames[1:],
    )
    print("zero.ico erstellt.")

if __name__ == "__main__":
    make()

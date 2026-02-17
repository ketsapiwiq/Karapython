#!/usr/bin/env python

import midifile, time, sys, subprocess, tempfile, os
import pygame

if len(sys.argv) < 2:
    print("Usage: python main.py <karaoke_file.kar>")
    sys.exit(1)

karaoke_file = sys.argv[1]

pygame.init()
screenx = 1200
screeny = 400
screen = pygame.display.set_mode((screenx, screeny))
pygame.display.set_caption(karaoke_file)

font = pygame.font.Font(None, 60)
purple = (100, 100, 250, 0)
white = (250, 250, 250, 0)

active_text_color = purple
base_text_color = white

m = midifile.midifile()
m.load_file(karaoke_file)

with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
    tmp_wav = tmp.name

try:
    print("Rendering MIDI to audio...")
    subprocess.run(
        ["timidity", "-Ow", "-o", tmp_wav, karaoke_file],
        capture_output=True,
        check=True,
    )

    pygame.mixer.init()
    pygame.mixer.music.load(tmp_wav)
    pygame.mixer.music.play()

    print("Playing...")

    done = False

    if not m.karfile:
        print("This is not a karaoke file. I'll just play it")
        while pygame.mixer.music.get_busy():
            time.sleep(1)
        sys.exit(0)

    while pygame.mixer.music.get_busy() and not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

        dt = pygame.mixer.music.get_pos() / 1000.0
        m.update_karaoke(dt)

        # Render the three karaoke lines
        for iline in range(3):
            l = font.size(m.karlinea[iline] + m.karlineb[iline])[0]
            x0a = screenx / 2 - l / 2.0
            line_a = font.render(m.karlinea[iline], 0, active_text_color)
            line_b = font.render(m.karlineb[iline], 0, base_text_color)
            rect_a = screen.blit(line_a, [x0a, 80 + iline * 60])
            x0b = x0a + rect_a.width
            rect_b = screen.blit(line_b, [x0b, 80 + iline * 60])

        pygame.display.flip()
        screen.fill(0)

        time.sleep(0.1)

finally:
    pygame.quit()
    # Cleanup temp WAV file
    if os.path.exists(tmp_wav):
        os.remove(tmp_wav)

import pygame as pg
import random as rand
import gameClass as gc
import sys


gs = 40
WIDTH, HEIGHT = 800, 600

 


pg.init()
pg.mixer.init()

window = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("Stars Example")
clock = pg.time.Clock()

# load music and play
pg.mixer.music.load("game_music.wav")
pg.mixer.music.set_volume(0.1)
pg.mixer.music.play(-1)

font = pg.font.Font(None, 80)

# create game objects
player = gc.Player(9, 13)
st = gc.Star(player.x, player.y)
scor = 0
time = 0
meto = gc.Meteor()

running = True
while running:
    dt = clock.tick(60) / 1000.0

    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
            sys.exit()
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_a and player.alive:
                player.shoot()

    # update
    player.move(6, dt)
    player.update_rect()
    st.update_of_star(dt)
    meto.update(dt)
    player.updateOf_l(dt)

    # collisions
    meto.collide_with_laser(player.laser)
    meto.collide_with_player(player)
    # If you want meteor-meteor collisions enabled:
    # meto.collide_with_self(dt)

    # draw
    window.fill((30, 30, 30))
    st.Draw(window)
    player.Draw(window)
    meto.Drew(window)
    time+=dt
    if time>=0.5:
        scor+=2
        time=0
    points = font.render(f"Points:{scor}",True,(255,30,12))
    points= pg.transform.scale(points,(70,50))
    dameg = font.render(f"Damage:{3-player.health}/3",True,(255,30,12))
    dameg= pg.transform.scale(dameg,(80,50))
    window.blit(points,(1*gs,1*gs))
    window.blit(dameg,(17*gs,1*gs))

    # game over handling
    if not player.alive:
        game_over_text = font.render("GAME OVER", True, (255, 0, 0))
        window.blit(game_over_text, (WIDTH // 2 - 120, HEIGHT // 2 - 50))
        pg.display.flip()
        pg.time.delay(2000)
        running = False
    # temp= clock.get_fps()
    # print(f"fps:{temp}")
    pg.display.flip()

pg.mixer.music.stop()
pg.quit()

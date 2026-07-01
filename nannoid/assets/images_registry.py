images = {}
images['paddles.l'] = ('paddles.png', (18, 0, 18, 6), (0, 0, 18, 6))
images['paddles.w'] = ('paddles.png', (36, 0, 18, 6), (0, 0, 18, 6))
images['paddles.3'] = ('paddles.png', (54, 0, 18, 6), (0, 0, 18, 6))
images['paddles.c'] = ('paddles.png', (72, 0, 18, 6), (0, 0, 18, 6))
images['paddles.e'] = ('paddles.png', (90, 0, 18, 6), (0, 0, 18, 6))
images['paddles.s'] = ('paddles.png', (108, 0, 18, 6), (0, 0, 18, 6))
images['paddles.x'] = ('paddles.png', (126, 0, 18, 6), (0, 0, 18, 6))
images['paddles.p'] = ('paddles.png', (144, 0, 18, 6), (0, 0, 18, 6))
images['ball'] = ('ball.png', (12, 0, 12, 12), (0, 0, 12, 12))
for i in range(1, 49):
    images[f'cubes.{i}'] = ('cubes.png', (i * 32, 0, 32, 32), (5, 5, 22, 22))
images['laser'] = ('laser.png', (6, 0, 6, 12), (0, 0, 6, 12))
for i in range(1, 17):
    images[f'pyramid.{i}'] = ('pyramid.png', (i * 32, 0, 32, 32), (5, 5, 22, 22))
images['pills.l'] = ('pills.png', (32, 0, 32, 16), (0, 0, 32, 16))
images['pills.w'] = ('pills.png', (64, 0, 32, 16), (0, 0, 32, 16))
images['pills.3'] = ('pills.png', (96, 0, 32, 16), (0, 0, 32, 16))
images['pills.c'] = ('pills.png', (128, 0, 32, 16), (0, 0, 32, 16))
images['pills.e'] = ('pills.png', (160, 0, 32, 16), (0, 0, 32, 16))
images['pills.s'] = ('pills.png', (192, 0, 32, 16), (0, 0, 32, 16))
images['pills.x'] = ('pills.png', (224, 0, 32, 16), (0, 0, 32, 16))
images['pills.p'] = ('pills.png', (256, 0, 32, 16), (0, 0, 32, 16))
for i in range(1, 25):
    images[f'sphere.{i}'] = ('sphere.png', (i * 32, 0, 32, 32), (5, 5, 22, 22))
for i in range(1, 9):
    images[f'boom.{i}'] = ('boom.png', (i * 32, 0, 32, 32), (5, 4, 27, 24))

int NUM = 2000;
Particle[] particles;

void setup() {
  size(800, 600);
  particles = new Particle[NUM];
  for (int i = 0; i < NUM; i++)
    particles[i] = new Particle();
}

void draw() {
  background(0, 8);
  for (Particle p : particles) {
    p.update();
    p.show();
  }
}

class Particle {
  PVector pos, vel;
  float size;

  Particle() {
    pos = new PVector(random(width), random(height));
    vel = PVector.random2D().mult(random(0.5, 2));
    size = random(1, 4);
  }

  void update() {
    vel.add(0, 0.05);
    pos.add(vel);
    if (pos.x < 0 || pos.x > width)  vel.x *= -0.8;
    if (pos.y < 0 || pos.y > height) vel.y *= -0.8;
    pos.x = constrain(pos.x, 0, width);
    pos.y = constrain(pos.y, 0, height);
    vel.mult(0.995);
  }

  void show() {
    float alpha = map(pos.y, height, 0, 50, 200);
    fill(255, alpha);
    noStroke();
    circle(pos.x, pos.y, size);
  }
}

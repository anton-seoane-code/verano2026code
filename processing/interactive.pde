ArrayList<Dot> dots = new ArrayList();
int NUM = 500;

void setup() {
  size(800, 600);
  for (int i = 0; i < NUM; i++)
    dots.add(new Dot());
}

void draw() {
  background(10, 12, 25);
  for (Dot d : dots) {
    d.update();
    d.show();
  }
}

class Dot {
  PVector pos, vel;

  Dot() {
    pos = new PVector(random(width), random(height));
    vel = new PVector();
  }

  void update() {
    PVector mouse = new PVector(mouseX, mouseY);
    PVector dir = PVector.sub(pos, mouse);
    float d = dir.mag();
    if (d > 0 && d < 150) {
      float force = map(d, 0, 150, 8, 0);
      dir.setMag(force);
      vel.add(dir);
    }
    if (mousePressed) {
      PVector toward = PVector.sub(mouse, pos);
      float d2 = toward.mag();
      if (d2 > 0 && d2 < 200) {
        toward.setMag(map(d2, 0, 200, 0, 2));
        vel.add(toward);
      }
    }
    vel.mult(0.95);
    pos.add(vel);
    pos.x = constrain(pos.x, 0, width);
    pos.y = constrain(pos.y, 0, height);
  }

  void show() {
    PVector mouse = new PVector(mouseX, mouseY);
    float d = pos.dist(mouse);
    float alpha = d < 150 ? map(d, 0, 150, 255, 50) : 50;
    float size = d < 150 ? map(d, 0, 150, 2, 6) : 6;
    float hue = map(d, 0, 300, 0, 200) + frameCount * 0.3;
    stroke(hue, 200, 255, alpha);
    strokeWeight(size);
    point(pos.x, pos.y);
  }
}

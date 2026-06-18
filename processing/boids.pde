int NUM = 150;
Boid[] boids;

void setup() {
  size(800, 600);
  boids = new Boid[NUM];
  for (int i = 0; i < NUM; i++)
    boids[i] = new Boid(random(width), random(height));
}

void draw() {
  background(10, 12, 25, 20);
  for (Boid b : boids) {
    b.flock(boids);
    b.update();
    b.wrap();
    b.show();
  }
}

class Boid {
  PVector pos, vel, acc;
  float maxSpeed = 3;
  float maxForce = 0.05;

  Boid(float x, float y) {
    pos = new PVector(x, y);
    vel = PVector.random2D().mult(maxSpeed);
    acc = new PVector();
  }

  void flock(Boid[] all) {
    acc.mult(0);
    acc.add(separate(all).mult(1.8));
    acc.add(align(all).mult(1.0));
    acc.add(cohere(all).mult(1.0));
  }

  PVector separate(Boid[] all) {
    PVector steer = new PVector();
    int count = 0;
    for (Boid b : all) {
      float d = pos.dist(b.pos);
      if (d > 0 && d < 25) {
        PVector diff = PVector.sub(pos, b.pos);
        diff.div(d);
        steer.add(diff);
        count++;
      }
    }
    if (count > 0) steer.div(count);
    if (steer.mag() > 0) {
      steer.setMag(maxSpeed);
      steer.sub(vel);
      steer.limit(maxForce);
    }
    return steer;
  }

  PVector align(Boid[] all) {
    PVector steer = new PVector();
    int count = 0;
    for (Boid b : all) {
      float d = pos.dist(b.pos);
      if (d > 0 && d < 60) {
        steer.add(b.vel);
        count++;
      }
    }
    if (count > 0) {
      steer.div(count);
      steer.setMag(maxSpeed);
      steer.sub(vel);
      steer.limit(maxForce);
    }
    return steer;
  }

  PVector cohere(Boid[] all) {
    PVector steer = new PVector();
    int count = 0;
    for (Boid b : all) {
      float d = pos.dist(b.pos);
      if (d > 0 && d < 60) {
        steer.add(b.pos);
        count++;
      }
    }
    if (count > 0) {
      steer.div(count);
      steer.sub(pos);
      steer.setMag(maxSpeed);
      steer.sub(vel);
      steer.limit(maxForce);
    }
    return steer;
  }

  void update() {
    vel.add(acc);
    vel.limit(maxSpeed);
    pos.add(vel);
  }

  void wrap() {
    if (pos.x < -10) pos.x = width + 10;
    if (pos.x > width + 10) pos.x = -10;
    if (pos.y < -10) pos.y = height + 10;
    if (pos.y > height + 10) pos.y = -10;
  }

  void show() {
    float angle = vel.heading();
    float hue = map(pos.x, 0, width, 180, 300) + frameCount * 0.5;
    stroke(hue, 200, 255, 180);
    strokeWeight(1.5);
    pushMatrix();
    translate(pos.x, pos.y);
    rotate(angle);
    line(6, 0, -6, -4);
    line(6, 0, -6, 4);
    popMatrix();
  }
}

float time = 0;

void setup() {
  size(800, 600);
}

void draw() {
  background(15, 18, 30);
  time += 0.02;
  translate(width / 2, height);
  branch(120, 0);
}

void branch(float len, int depth) {
  if (len < 4) {
    fill(255, 220, 100, 200);
    noStroke();
    circle(0, 0, 4);
    return;
  }
  float sway = noise(time + depth * 0.5) * 0.3 - 0.15;
  float angle = radians(25 + sway * 10);
  float thickness = map(len, 4, 120, 1, 6);
  float hue = map(depth, 0, 8, 220, 40);
  stroke(hue, 180, 255, 180);
  strokeWeight(thickness);
  line(0, 0, 0, -len);
  translate(0, -len);
  pushMatrix();
  rotate(angle);
  branch(len * 0.7, depth + 1);
  popMatrix();
  pushMatrix();
  rotate(-angle);
  branch(len * 0.7, depth + 1);
  popMatrix();
  if (depth % 2 == 0) {
    pushMatrix();
    rotate(0);
    branch(len * 0.5, depth + 2);
    popMatrix();
  }
}

float time = 0;

void setup() {
  size(800, 600);
}

void draw() {
  background(10, 12, 30);
  time += 0.005;

  strokeWeight(2);
  noFill();

  for (int row = 0; row < 6; row++) {
    float yOffset = row * 100 + 40;
    float amp = 40 + row * 8;
    float freq = 0.01 + row * 0.003;
    float speed = time + row * 0.5;

    float hue = (row * 40 + frameCount * 0.5) % 360;
    stroke(hue, 200, 255, 120);

    beginShape();
    for (int x = 0; x <= width; x += 3) {
      float y = yOffset + sin(x * freq + speed * 2) * amp * 0.5
                         + cos(x * freq * 0.7 + speed) * amp * 0.3
                         + noise(x * 0.005, row, time) * amp * 0.4;
      vertex(x, y);
    }
    endShape();
  }
}

int NUM = 12;
MorphShape[] shapes;

void setup() {
  size(800, 600);
  colorMode(HSB, 360, 100, 100);
  shapes = new MorphShape[NUM];
  for (int i = 0; i < NUM; i++)
    shapes[i] = new MorphShape(i);
}

void draw() {
  background(0, 0, 5);
  for (MorphShape m : shapes) {
    m.update();
    m.show();
  }
}

class MorphShape {
  float cx, cy, baseR;
  float phase, speed;
  int sides;
  float hue;

  MorphShape(int idx) {
    cx = random(width);
    cy = random(height);
    baseR = random(30, 80);
    phase = random(TWO_PI);
    speed = random(0.005, 0.02);
    sides = int(random(3, 9));
    hue = random(360);
  }

  void update() {
    phase += speed;
    cx += sin(phase * 0.3 + idx()) * 0.3;
    cy += cos(phase * 0.2 + idx()) * 0.3;
  }

  float idx() { return float(int(random(100))); }

  void show() {
    float r = baseR + sin(phase * 2) * 15;
    float morph = sin(phase * 0.7) * 0.5 + 0.5;
    int currentSides = int(lerp(sides, sides * 2, morph));
    float h = (hue + frameCount * 0.2) % 360;

    fill(h, 60, 90, 40);
    stroke(h, 80, 100, 180);
    strokeWeight(1.5);

    beginShape();
    for (int i = 0; i <= currentSides; i++) {
      float angle = map(i, 0, currentSides, 0, TWO_PI) - HALF_PI;
      float radiusVar = 1 + 0.3 * sin(angle * 3 + phase);
      float x = cx + cos(angle) * r * radiusVar;
      float y = cy + sin(angle) * r * radiusVar;
      curveVertex(x, y);
    }
    endShape(CLOSE);
  }
}

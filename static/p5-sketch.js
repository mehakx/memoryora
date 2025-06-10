// Visualization variables
let canvasWidth, canvasHeight;
let center;
let eyeSize = 200;
let pulseSize = 1;
let pulseDirection = 0.01;
let waveAmplitude = 10;
let waveFrequency = 0.02;
let wavePhase = 0;
let noiseOffset = 0;
let particleSystem = [];

// REMOVE these declarations since they're already in scripts.js
// let currentEmotion = "neutral";
// let emotionIntensity = 30;

// Colors for different emotions
const emotionColors = {
  sad: { primary: '#0066cc', secondary: '#001a33', accent: '#66a3ff' },
  fear: { primary: '#6600cc', secondary: '#1a0033', accent: '#cc99ff' },
  anger: { primary: '#cc0000', secondary: '#330000', accent: '#ff6666' },
  angry: { primary: '#cc0000', secondary: '#330000', accent: '#ff6666' }, // Alternative naming
  anxiety: { primary: '#cc6600', secondary: '#331a00', accent: '#ffcc66' },
  anxious: { primary: '#cc6600', secondary: '#331a00', accent: '#ffcc66' }, // Alternative naming
  neutral: { primary: '#666666', secondary: '#1a1a1a', accent: '#cccccc' },
  excitement: { primary: '#ffcc00', secondary: '#332b00', accent: '#ffee99' },
  excited: { primary: '#ffcc00', secondary: '#332b00', accent: '#ffee99' }, // Alternative naming
  joy: { primary: '#00cc00', secondary: '#003300', accent: '#99ff99' },
  happy: { primary: '#00cc00', secondary: '#003300', accent: '#99ff99' }, // Alternative naming
  confused: { primary: '#ff00ff', secondary: '#330033', accent: '#ff99ff' },
  tired: { primary: '#336699', secondary: '#0d1a26', accent: '#99c2ff' },
  hungry: { primary: '#ff9900', secondary: '#332600', accent: '#ffd699' },
  surprised: { primary: '#00ccff', secondary: '#003344', accent: '#99eeff' },
  fearful: { primary: '#6600cc', secondary: '#1a0033', accent: '#cc99ff' },
  disgusted: { primary: '#669900', secondary: '#1a2600', accent: '#bbff66' }
};

// Create a new p5 instance in instance mode
const sketch = (p) => {
  p.setup = function() {
    // Check if the container exists before trying to access it
    const container = document.getElementById('visualization-container');
    if (!container) {
      console.error('Visualization container not found');
      return;
    }
    
    canvasWidth = container.offsetWidth;
    canvasHeight = container.offsetHeight;
    
    let canvas = p.createCanvas(canvasWidth, canvasHeight);
    canvas.parent('p5-canvas');
    
    p.colorMode(p.HSB, 360, 100, 100, 1);
    
    // Set center point
    center = { x: canvasWidth/2, y: canvasHeight/2 };
    
    // Create initial particles
    createParticles(50);
    
    console.log('p5 visualization setup done');
  };

  p.draw = function() {
    // Check if center is defined
    if (!center) return;
    
    // Set background color based on current emotion
    const colors = emotionColors[window.currentEmotion] || emotionColors.neutral;
    p.background(colors.secondary);
    
    // Update wave phase
    wavePhase += 0.01;
    
    // Update pulse animation
    pulseSize += pulseDirection;
    if (pulseSize > 1.2 || pulseSize < 0.9) {
      pulseDirection *= -1;
    }
    
    // Update noise offset for particle movement
    noiseOffset += 0.01;
    
    // Draw outer waves
    drawWaves(colors.primary, colors.accent);
    
    // Draw the central eye
    drawAbstractEye(colors.primary, colors.accent);
    
    // Update and draw particles
    updateParticles(colors.primary);
    
    // Draw pupil
    drawPupil(colors.secondary);
  };

  p.windowResized = function() {
    const container = document.getElementById('visualization-container');
    if (!container) return;
    
    canvasWidth = container.offsetWidth;
    canvasHeight = container.offsetHeight;
    p.resizeCanvas(canvasWidth, canvasHeight);
    center = { x: canvasWidth/2, y: canvasHeight/2 };
  };

  function createParticles(count) {
    for (let i = 0; i < count; i++) {
      let angle = p.random(p.TWO_PI);
      let radius = p.random(eyeSize * 0.5, eyeSize * 2);
      particleSystem.push({
        pos: { x: center.x + p.cos(angle) * radius, y: center.y + p.sin(angle) * radius },
        vel: { x: p.random(-1, 1), y: p.random(-1, 1) },
        size: p.random(2, 8),
        color: p.color(p.random(360), 80, 90, p.random(0.5, 0.9)),
        angle: angle,
        radius: radius,
        speed: p.random(0.005, 0.02),
        noiseOffset: p.random(1000),
        lifespan: 255
      });
    }
  }

  function drawWaves(primaryColor, accentColor) {
    p.noFill();
    p.stroke(primaryColor);
    p.strokeWeight(2);
    
    // Draw concentric waves
    for (let i = 0; i < 5; i++) {
      let size = eyeSize * 1.5 + i * 50;
      p.beginShape();
      for (let a = 0; a < p.TWO_PI; a += 0.1) {
        let xoff = p.map(p.cos(a), -1, 1, 0, 2);
        let yoff = p.map(p.sin(a), -1, 1, 0, 2);
        let r = size + waveAmplitude * p.sin(waveFrequency * size + wavePhase);
        let x = center.x + r * p.cos(a);
        let y = center.y + r * p.sin(a);
        p.vertex(x, y);
      }
      p.endShape(p.CLOSE);
    }
    
    // Draw radiating lines
    p.stroke(accentColor);
    p.strokeWeight(1);
    let lineCount = 12;
    for (let i = 0; i < lineCount; i++) {
      let angle = i * p.TWO_PI / lineCount;
      let startX = center.x + eyeSize * 0.7 * p.cos(angle);
      let startY = center.y + eyeSize * 0.7 * p.sin(angle);
      let endX = center.x + (eyeSize * 2 + waveAmplitude * p.sin(wavePhase)) * p.cos(angle);
      let endY = center.y + (eyeSize * 2 + waveAmplitude * p.sin(wavePhase)) * p.sin(angle);
      p.line(startX, startY, endX, endY);
    }
  }

  function drawAbstractEye(primaryColor, accentColor) {
    // Draw iris
    p.noStroke();
    p.fill(primaryColor);
    p.ellipse(center.x, center.y, eyeSize * pulseSize, eyeSize * pulseSize);
    
    // Draw iris detail
    p.stroke(accentColor);
    p.strokeWeight(1);
    p.noFill();
    for (let i = 0; i < 3; i++) {
      p.ellipse(center.x, center.y, eyeSize * 0.8 * pulseSize - i * 15, eyeSize * 0.8 * pulseSize - i * 15);
    }
    
    // Draw light reflection
    p.noStroke();
    p.fill(255, 180);
    let reflectionX = center.x + eyeSize * 0.25;
    let reflectionY = center.y - eyeSize * 0.2;
    p.ellipse(reflectionX, reflectionY, eyeSize * 0.2, eyeSize * 0.15);
  }

  function drawPupil(secondaryColor) {
    p.fill(secondaryColor);
    p.noStroke();
    
    // Determine pupil size based on emotion intensity
    let pupilSize = p.map(window.emotionIntensity, 0, 100, eyeSize * 0.2, eyeSize * 0.5);
    p.ellipse(center.x, center.y, pupilSize, pupilSize);
    
    // Draw pupil detail
    p.fill(0);
    p.ellipse(center.x, center.y, pupilSize * 0.8, pupilSize * 0.8);
    
    // Small white reflection in pupil
    p.fill(255, 200);
    p.ellipse(center.x - pupilSize * 0.15, center.y - pupilSize * 0.15, pupilSize * 0.1, pupilSize * 0.1);
  }

  function updateParticles(primaryColor) {
    p.noStroke();
    for (let i = particleSystem.length - 1; i >= 0; i--) {
      let particle = particleSystem[i]; // Renamed to avoid confusion with p
      
      // Noise-based movement
      let noiseX = p.noise(particle.noiseOffset, 0, noiseOffset) * 2 - 1;
      let noiseY = p.noise(0, particle.noiseOffset, noiseOffset) * 2 - 1;
      
      // Angular movement
      particle.angle += particle.speed * (window.emotionIntensity / 50);
      particle.radius += p.sin(p.frameCount * 0.05) * 0.5;
      
      // Combine noise and circular movement
      particle.pos.x = center.x + p.cos(particle.angle) * particle.radius + noiseX * 10;
      particle.pos.y = center.y + p.sin(particle.angle) * particle.radius + noiseY * 10;
      
      // Decrease lifespan
      particle.lifespan -= 0.5;
      
      // Draw the particle
      let particleColor = p.color(p.hue(particle.color), p.saturation(particle.color), p.brightness(particle.color), particle.lifespan / 255);
      p.fill(particleColor);
      p.ellipse(particle.pos.x, particle.pos.y, particle.size, particle.size);
      
      // Remove dead particles
      if (particle.lifespan <= 0) {
        particleSystem.splice(i, 1);
      }
    }
    
    // Add new particles occasionally
    if (p.frameCount % 30 === 0) {
      createParticles(1);
    }
  }
};

// Create the p5 instance
let p5Instance;
window.addEventListener('DOMContentLoaded', () => {
  // Wait for DOM to be ready before creating p5 instance
  p5Instance = new p5(sketch);
});

// Function to update visualization based on emotion
window.updateVisualization = function(emotion, intensity) {
  // Update global variables that scripts.js can access
  window.currentEmotion = emotion.toLowerCase();
  window.emotionIntensity = Math.abs(intensity);
  
  // Visual response to emotion change
  waveAmplitude = p5Instance.map(window.emotionIntensity, 0, 100, 5, 30);
  waveFrequency = p5Instance.map(window.emotionIntensity, 0, 100, 0.01, 0.05);
  pulseSize = 1.5; // Expand the eye
  
  // Add new particles on emotion change
  if (typeof createParticles === 'function') {
    createParticles(30);
  }
  
  // Update the emotion panel appearance
  const colors = emotionColors[window.currentEmotion] || emotionColors.neutral;
  const emotionLabel = document.getElementById('emotion-label');
  if (emotionLabel) {
    emotionLabel.textContent = window.currentEmotion;
    emotionLabel.style.color = colors.primary;
  }
  
  // Update intensity bar
  const intensityFill = document.getElementById('intensity-fill');
  if (intensityFill) {
    intensityFill.style.width = `${window.emotionIntensity}%`;
    intensityFill.style.background = `repeating-linear-gradient(
      45deg,
      ${colors.primary}88,
      ${colors.primary}88 5px,
      ${colors.accent} 5px,
      ${colors.accent} 10px
    )`;
  }
  
  // Create a visual flash for emotion change
  const flashEl = document.createElement('div');
  flashEl.className = 'emotion-flash';
  flashEl.style.backgroundColor = colors.primary + '33';
  document.body.appendChild(flashEl);
  
  // Remove flash after animation
  setTimeout(() => {
    if (flashEl.parentNode) {
      flashEl.parentNode.removeChild(flashEl);
    }
  }, 500);
};









// // Visualization variables
// let canvasWidth, canvasHeight;
// let center;
// let eyeSize = 200;
// let pulseSize = 1;
// let pulseDirection = 0.01;
// let waveAmplitude = 10;
// let waveFrequency = 0.02;
// let wavePhase = 0;
// let noiseOffset = 0;
// let particleSystem = [];
// let currentEmotion = "neutral";
// let emotionIntensity = 30;

// // Colors for different emotions
// const emotionColors = {
//   sad: { primary: '#0066cc', secondary: '#001a33', accent: '#66a3ff' },
//   fear: { primary: '#6600cc', secondary: '#1a0033', accent: '#cc99ff' },
//   anger: { primary: '#cc0000', secondary: '#330000', accent: '#ff6666' },
//   angry: { primary: '#cc0000', secondary: '#330000', accent: '#ff6666' }, // Alternative naming
//   anxiety: { primary: '#cc6600', secondary: '#331a00', accent: '#ffcc66' },
//   anxious: { primary: '#cc6600', secondary: '#331a00', accent: '#ffcc66' }, // Alternative naming
//   neutral: { primary: '#666666', secondary: '#1a1a1a', accent: '#cccccc' },
//   excitement: { primary: '#ffcc00', secondary: '#332b00', accent: '#ffee99' },
//   excited: { primary: '#ffcc00', secondary: '#332b00', accent: '#ffee99' }, // Alternative naming
//   joy: { primary: '#00cc00', secondary: '#003300', accent: '#99ff99' },
//   happy: { primary: '#00cc00', secondary: '#003300', accent: '#99ff99' }, // Alternative naming
//   confused: { primary: '#ff00ff', secondary: '#330033', accent: '#ff99ff' },
//   tired: { primary: '#336699', secondary: '#0d1a26', accent: '#99c2ff' },
//   hungry: { primary: '#ff9900', secondary: '#332600', accent: '#ffd699' },
//   surprised: { primary: '#00ccff', secondary: '#003344', accent: '#99eeff' },
//   fearful: { primary: '#6600cc', secondary: '#1a0033', accent: '#cc99ff' },
//   disgusted: { primary: '#669900', secondary: '#1a2600', accent: '#bbff66' }
// };

// // Create a new p5 instance in instance mode
// const sketch = (p) => {
//   p.setup = function() {
//     canvasWidth = document.getElementById('visualization-container').offsetWidth;
//     canvasHeight = document.getElementById('visualization-container').offsetHeight;
//     let canvas = p.createCanvas(canvasWidth, canvasHeight);
//     canvas.parent('p5-canvas');
//     p.colorMode(p.HSB, 360, 100, 100, 1);
    
//     // Set center point
//     center = { x: canvasWidth/2, y: canvasHeight/2 };
    
//     // Create initial particles
//     createParticles(50);
    
//     console.log('p5 visualization setup done');
//   };
  
//   p.draw = function() {
//     // Set background color based on current emotion
//     const colors = emotionColors[currentEmotion] || emotionColors.neutral;
//     p.background(colors.secondary);
    
//     // Update wave phase
//     wavePhase += 0.01;
    
//     // Update pulse animation
//     pulseSize += pulseDirection;
//     if (pulseSize > 1.2 || pulseSize < 0.9) {
//       pulseDirection *= -1;
//     }
    
//     // Update noise offset for particle movement
//     noiseOffset += 0.01;
    
//     // Draw outer waves
//     drawWaves(colors.primary, colors.accent);
    
//     // Draw the central eye
//     drawAbstractEye(colors.primary, colors.accent);
    
//     // Update and draw particles
//     updateParticles(colors.primary);
    
//     // Draw pupil
//     drawPupil(colors.secondary);
//   };
  
//   p.windowResized = function() {
//     canvasWidth = document.getElementById('visualization-container').offsetWidth;
//     canvasHeight = document.getElementById('visualization-container').offsetHeight;
//     p.resizeCanvas(canvasWidth, canvasHeight);
//     center = { x: canvasWidth/2, y: canvasHeight/2 };
//   };
  
//   function createParticles(count) {
//     for (let i = 0; i < count; i++) {
//       let angle = p.random(p.TWO_PI);
//       let radius = p.random(eyeSize * 0.5, eyeSize * 2);
      
//       particleSystem.push({
//         pos: { 
//           x: center.x + p.cos(angle) * radius, 
//           y: center.y + p.sin(angle) * radius 
//         },
//         vel: { x: p.random(-1, 1), y: p.random(-1, 1) },
//         size: p.random(2, 8),
//         color: p.color(p.random(360), 80, 90, p.random(0.5, 0.9)),
//         angle: angle,
//         radius: radius,
//         speed: p.random(0.005, 0.02),
//         noiseOffset: p.random(1000),
//         lifespan: 255
//       });
//     }
//   }
  
//   function drawWaves(primaryColor, accentColor) {
//     p.noFill();
//     p.stroke(primaryColor);
//     p.strokeWeight(2);
    
//     // Draw concentric waves
//     for (let i = 0; i < 5; i++) {
//       let size = eyeSize * 1.5 + i * 50;
//       p.beginShape();
//       for (let a = 0; a < p.TWO_PI; a += 0.1) {
//         let xoff = p.map(p.cos(a), -1, 1, 0, 2);
//         let yoff = p.map(p.sin(a), -1, 1, 0, 2);
//         let r = size + waveAmplitude * p.sin(waveFrequency * size + wavePhase);
//         let x = center.x + r * p.cos(a);
//         let y = center.y + r * p.sin(a);
//         p.vertex(x, y);
//       }
//       p.endShape(p.CLOSE);
//     }
    
//     // Draw radiating lines
//     p.stroke(accentColor);
//     p.strokeWeight(1);
//     let lineCount = 12;
//     for (let i = 0; i < lineCount; i++) {
//       let angle = i * p.TWO_PI / lineCount;
//       let startX = center.x + eyeSize * 0.7 * p.cos(angle);
//       let startY = center.y + eyeSize * 0.7 * p.sin(angle);
//       let endX = center.x + (eyeSize * 2 + waveAmplitude * p.sin(wavePhase)) * p.cos(angle);
//       let endY = center.y + (eyeSize * 2 + waveAmplitude * p.sin(wavePhase)) * p.sin(angle);
      
//       p.line(startX, startY, endX, endY);
//     }
//   }
  
//   function drawAbstractEye(primaryColor, accentColor) {
//     // Draw iris
//     p.noStroke();
//     p.fill(primaryColor);
//     p.ellipse(center.x, center.y, eyeSize * pulseSize, eyeSize * pulseSize);
    
//     // Draw iris detail
//     p.stroke(accentColor);
//     p.strokeWeight(1);
//     p.noFill();
//     for (let i = 0; i < 3; i++) {
//       p.ellipse(center.x, center.y, 
//                 eyeSize * 0.8 * pulseSize - i * 15, 
//                 eyeSize * 0.8 * pulseSize - i * 15);
//     }
    
//     // Draw light reflection
//     p.noStroke();
//     p.fill(255, 180);
//     let reflectionX = center.x + eyeSize * 0.25;
//     let reflectionY = center.y - eyeSize * 0.2;
//     p.ellipse(reflectionX, reflectionY, eyeSize * 0.2, eyeSize * 0.15);
//   }
  
//   function drawPupil(secondaryColor) {
//     p.fill(secondaryColor);
//     p.noStroke();
    
//     // Determine pupil size based on emotion intensity
//     let pupilSize = p.map(emotionIntensity, 0, 100, eyeSize * 0.2, eyeSize * 0.5);
//     p.ellipse(center.x, center.y, pupilSize, pupilSize);
    
//     // Draw pupil detail
//     p.fill(0);
//     p.ellipse(center.x, center.y, pupilSize * 0.8, pupilSize * 0.8);
    
//     // Small white reflection in pupil
//     p.fill(255, 200);
//     p.ellipse(center.x - pupilSize * 0.15, center.y - pupilSize * 0.15, pupilSize * 0.1, pupilSize * 0.1);
//   }
  
//   function updateParticles(primaryColor) {
//     p.noStroke();
    
//     for (let i = particleSystem.length - 1; i >= 0; i--) {
//       let p5 = p; // Use p5 instance here to avoid confusion with particle p
//       let p = particleSystem[i];
      
//       // Noise-based movement
//       let noiseX = p5.noise(p.noiseOffset, 0, noiseOffset) * 2 - 1;
//       let noiseY = p5.noise(0, p.noiseOffset, noiseOffset) * 2 - 1;
      
//       // Angular movement
//       p.angle += p.speed * (emotionIntensity / 50);
//       p.radius += p5.sin(p5.frameCount * 0.05) * 0.5;
      
//       // Combine noise and circular movement
//       p.pos.x = center.x + p5.cos(p.angle) * p.radius + noiseX * 10;
//       p.pos.y = center.y + p5.sin(p.angle) * p.radius + noiseY * 10;
      
//       // Decrease lifespan
//       p.lifespan -= 0.5;
      
//       // Draw the particle
//       let particleColor = p5.color(p5.hue(p.color), p5.saturation(p.color), p5.brightness(p.color), p.lifespan / 255);
//       p5.fill(particleColor);
//       p5.ellipse(p.pos.x, p.pos.y, p.size, p.size);
      
//       // Remove dead particles
//       if (p.lifespan <= 0) {
//         particleSystem.splice(i, 1);
//       }
//     }
    
//     // Add new particles occasionally
//     if (p.frameCount % 30 === 0) {
//       createParticles(1);
//     }
//   }
// };

// // Create the p5 instance
// new p5(sketch);

// // Function to update visualization based on emotion
// function updateVisualization(emotion, intensity) {
//   currentEmotion = emotion.toLowerCase();
//   emotionIntensity = Math.abs(intensity);
  
//   // Visual response to emotion change
//   waveAmplitude = map(emotionIntensity, 0, 100, 5, 30);
//   waveFrequency = map(emotionIntensity, 0, 100, 0.01, 0.05);
//   pulseSize = 1.5;  // Expand the eye
  
//   // Add new particles on emotion change
//   createParticles(30);
  
//   // Update the emotion panel appearance
//   const colors = emotionColors[currentEmotion] || emotionColors.neutral;
//   document.getElementById('emotion-label').textContent = currentEmotion;
//   document.getElementById('emotion-label').style.color = colors.primary;
  
//   // Update intensity bar
//   document.getElementById('intensity-fill').style.width = `${emotionIntensity}%`;
//   document.getElementById('intensity-fill').style.background = `repeating-linear-gradient(
//     45deg,
//     ${colors.primary}88,
//     ${colors.primary}88 5px,
//     ${colors.accent} 5px,
//     ${colors.accent} 10px
//   )`;
  
//   // Create a visual flash for emotion change
//   const flashEl = document.createElement('div');
//   Object.assign(flashEl.style, {
//     position: 'absolute',
//     top: '0',
//     left: '0',
//     width: '100%',
//     height: '100%',
//     backgroundColor: colors.primary,
//     opacity: '0.2',
//     pointerEvents: 'none',
//     transition: 'opacity 0.5s',
//     zIndex: '10'
//   });
//   document.getElementById('visualization-container').appendChild(flashEl);
//   setTimeout(() => {
//     flashEl.style.opacity = '0';
//     setTimeout(() => flashEl.remove(), 500);
//   }, 100);
// }

// // Helper function for mapping values
// function map(value, start1, stop1, start2, stop2) {
//   return start2 + (stop2 - start2) * ((value - start1) / (stop1 - start1));
// }

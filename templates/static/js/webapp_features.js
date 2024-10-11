/* Group1: Select Filter & Recording Option */

let mediaType;
const iconBtn = document.getElementById('iconRecord');

// START: กำหนดโหมดการบันทึกเป็นรูปภาพ หรือ วิดีโอ (mediaType)
selectMode();
function selectMode() {
  const mediaType = document.querySelector('input[name="options-base"]:checked').value;
  if (mediaType === 'photo') {
    iconBtn.className = "bi bi-camera-fill bi-lg";
  } else if (mediaType === 'video') {
    iconBtn.className = "bi bi-camera-video-fill bi-lg";
  }
}

// ตรวจสอบการเลือกโหมด mediaType จากผู้ใช้
document.querySelectorAll('input[name="options-base"]').forEach(button => {
  button.addEventListener('change', selectMode);
});

// Nav-link เลือกออกแบบฟิลเตอร์ต่างๆ
const buttons = document.querySelectorAll('.nav-link');
buttons.forEach(button => {
  button.addEventListener('click', function() {
    if (this.classList.contains('activecolor')) {
      this.classList.remove('activecolor');
    } else {
      buttons.forEach(btn => btn.classList.remove('activecolor'));
      this.classList.add('activecolor');
    }
  });
});

/* Group4: Filters Setting */

// 4.1 manage collaspe components
const collapsibleElements = [
  document.getElementById('collapseText'),
  document.getElementById('collapseMask'),
  document.getElementById('collapseBg'),
  document.getElementById('collapseDb')
];

// click nav-link
document.querySelectorAll('.nav-link').forEach(link => {
  link.addEventListener('click', function() {
      const target = this.getAttribute('href');
      const targetElement = document.querySelector(target);
      closeOthers(targetElement);
  });
});

function closeOthers(except) {
  collapsibleElements.forEach(element => {
      if (element !== except) {
          const bsCollapse = bootstrap.Collapse.getInstance(element);
          if (bsCollapse) {
              bsCollapse.hide(); // ปิด collapse instance ที่ไม่ได้เลือก
          }
      }
  });
}

// 4.2 show demo image
function displayImage(card, imageSrc, container) {
  if (container === '.image-container') {
    sessionStorage.setItem("ObjectPath", 'templates/'+imageSrc);
  } else {
    sessionStorage.setItem("BgPath", 'templates/'+imageSrc);
  }
  const imageContainer = document.querySelector(container);
  if (imageSrc === 'icon') {
      imageContainer.innerHTML = '<p class="text-muted" id="selectedImageText">Select the image...</p>';
      if (container === '.image-container'){
        scale.hide();
        const existingOverlays = document.querySelectorAll('.overlay');
        existingOverlays.forEach(overlay => overlay.remove());
      }
  } else {
      imageContainer.innerHTML = `<img id="selectedImageText" src="${imageSrc}" class="img-fluid" style="max-height: 180px;"/>`;
      if (container === '.image-container'){
        selectImage();
      }
  }

  document.querySelectorAll('.card-img').forEach(el => {
    el.classList.remove('active');
  });
  card.classList.add('active');
}

// 4.3 upload image
const doesImageExist = (url) =>
  new Promise((resolve) => {
    const img = new Image();
    img.src = url;
    img.onload = () => resolve(true);
    img.onerror = () => resolve(false);
  });

function uploadImage(input, container) {
  const inputField = document.querySelector(`input[aria-describedby=${input}]`);
  const imageUrl = inputField.value;
  inputField.value = "";
  if (container === '.image-container') {
    sessionStorage.setItem("ObjectPath", imageUrl);
  } else {
    sessionStorage.setItem("BgPath", imageUrl);
  }

  if (imageUrl) {
    const imageExists = doesImageExist(imageUrl);

    if (imageExists) {
      const imageContainer = document.querySelector(container);
      imageContainer.innerHTML = `<img id="selectedImageText" src="${imageUrl}" class="img-fluid" style="max-height: 180px;"/>`;
      selectImage();

      document.querySelectorAll('.card-img').forEach(el => {
        el.classList.remove('active');
      });
    } else {
      alert("กรุณาตรวจสอบ Image Address ให้ถูกต้อง");
    }
  } else {
    alert("กรุณาตรวจสอบ Image Address ให้ถูกต้อง");
  }
}

// document.getElementById('bg-uploadBtn').addEventListener('click', uploadImage('bg-uploadBtn', 'bg-container'));
// document.getElementById('object-uploadBtn').addEventListener('click', uploadImage('object-uploadBtn', 'image-container'));
// document.getElementById('object-uploadBtn').addEventListener('click', async function () {
//   const inputField = document.querySelector('input[type="text"]');
//   const imageUrl = inputField.value;

//   if (imageUrl) {
//     const imageExists = await doesImageExist(imageUrl);

//     if (imageExists) {
//       document.cookie = `ObjectPath=${encodeURIComponent(imageUrl)}; path=/;`;
//       const imageContainer = document.querySelector('.image-container');
//       imageContainer.innerHTML = `<img id="selectedImageText" src="${imageUrl}" class="img-fluid" style="max-height: 180px;"/>`;
//       selectImage();

//       document.querySelectorAll('.card-img').forEach(el => {
//         el.classList.remove('active');
//       });
//     } else {
//       alert("กรุณาตรวจสอบ Image Address ให้ถูกต้อง");
//     }
//   } else {
//     alert("กรุณาตรวจสอบ Image Address ให้ถูกต้อง");
//   }
// });

// 4.4 scale setting
const collapseScale = document.getElementById('collapseScale');

let scale = new bootstrap.Collapse(collapseScale, {
  toggle: false
});

// ตรวจสอบการเลือก card-img
function selectImage() {
  console.log("test");

  document.getElementById('customRangeX').value = 0;
  document.getElementById('customRangeY').value = 0;
  document.getElementById('customRangeZ').value = 0;

  sessionStorage.setItem("left_eye", JSON.stringify([0, 0, 0]));
  sessionStorage.setItem("right_eye", JSON.stringify([0, 0, 0]));
  sessionStorage.setItem("lip", JSON.stringify([0, 0, 0]));

  scale.show();
  showOverlays();
}

// face demo
function showOverlays() {
  const existingOverlays = document.querySelectorAll('.overlay');
  existingOverlays.forEach(overlay => overlay.remove());

  // face1
  const face1 = document.createElement('img');
  face1.src = 'static/img/face1.png';
  face1.className = 'overlay left_eye';
  face1.style.left = '41%';
  face1.style.top = '30%';
  face1.dataset.sessionKey = 'left_eye';
  face1.addEventListener('click', () => handleFaceClick(face1));
  document.querySelector('.image-container').appendChild(face1);

  // face2
  const face2 = document.createElement('img');
  face2.src = 'static/img/face2.png';
  face2.className = 'overlay right_eye';
  face2.style.left = '51%';
  face2.style.top = '30%';
  face2.dataset.sessionKey = 'right_eye';
  face2.addEventListener('click', () => handleFaceClick(face2));
  document.querySelector('.image-container').appendChild(face2);

  // face3
  const face3 = document.createElement('img');
  face3.src = 'static/img/face3.png';
  face3.className = 'overlay lip';
  face3.style.left = '40%';
  face3.style.top = '55%';
  face3.dataset.sessionKey = 'lip';
  face3.addEventListener('click', () => handleFaceClick(face3));
  document.querySelector('.image-container').appendChild(face3);
}

let selectedFace;
function handleFaceClick(faceElement) {
  const faces = document.querySelectorAll('.overlay');
  faces.forEach(face => {
    face.style.border = 'none';
  });

  faceElement.style.border = '2px solid red';
  selectedFace = faceElement;

  const key = faceElement.dataset.sessionKey;
  const scale = JSON.parse(sessionStorage.getItem(key)) || [0, 0, 0];

  document.getElementById('customRangeX').value = scale[0];
  document.getElementById('customRangeY').value = scale[1];
  document.getElementById('customRangeZ').value = scale[2];
}

function moveSelectedFace() {
  if (selectedFace) {
    const customRangeX = parseInt(document.getElementById('customRangeX').value);
    const customRangeY = -parseInt(document.getElementById('customRangeY').value);
    const customRangeZ = parseInt(document.getElementById('customRangeZ').value);

    selectedFace.style.transform = `translate(${customRangeX}px, ${customRangeY}px) rotate(${customRangeZ}deg)`;

    const sessionKey = selectedFace.getAttribute('data-session-key');
    if (sessionKey) {
      const newScale = [customRangeX, -customRangeY, customRangeZ];
      sessionStorage.setItem(sessionKey, JSON.stringify(newScale));
    }
  }
}

document.getElementById('customRangeX').addEventListener('input', moveSelectedFace);
document.getElementById('customRangeY').addEventListener('input', moveSelectedFace);
document.getElementById('customRangeZ').addEventListener('input', moveSelectedFace);

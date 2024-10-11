// connect_api.js
const IMAGE_INTERVAL_MS = 28;

let image = document.getElementById("frame");
let ws;

image.onload = function(){
    //เมื่อภาพถูกโหลดจากเซิร์ฟเวอร์และแสดงใน <img> จะมีการเรียกใช้ฟังก์ชัน onload เพื่อปล่อย Blob URL ที่ไม่จำเป็นต้องใช้แล้ว เพื่อช่วยจัดการหน่วยความจำ
    URL.revokeObjectURL(this.src);
}

function access_signature_layer_custom_softpower() {

  ws = new WebSocket("ws://127.0.0.1:8000/ws");

  image.style.display = 'block';
  videoElement.style.display = 'none';

  ws.onmessage = function(event) {
    console.log(take_pictures);
    if (typeof event.data === 'string') {
      console.log('None Type');
    } else {
      image.src = URL.createObjectURL(event.data);

      if (take_pictures === true) {
        take_pictures=false;
        const newImgElement = document.createElement('img');
        newImgElement.src = URL.createObjectURL(event.data);

        // แทรกลงใน modal-body
        const modalBody = document.querySelector('#myModal .modal-body');
        modalBody.innerHTML = '';
        modalBody.appendChild(newImgElement);

        // Show modal with captured image
        const myModal = new bootstrap.Modal(document.getElementById('myModal'));
        myModal.show();
      }
    }
  }
}

document.getElementById("reset-link").addEventListener("click", function(event) {
  if (ws) {
    ws.close();
    image.style.display = 'none';
    videoElement.style.display = 'block';
  }

  // Send request to FastAPI to reset variables
  fetch('/reset-variables', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    }
  })
  .then(response => {
    if (response.ok) {
      console.log('Variables reset successfully');
    } else {
      console.error('Failed to reset variables');
    }
  })
  .catch(error => {
    console.error('Error:', error);
  });
});

document.getElementById("maskFilter").addEventListener("click", (event) => { //เปิดการเชื่อมต่อ ws

    // ตรวจสอบการอนุญาตเข้าถึงกล้อง
    if (!window.stream) {
        alert('อนุญาติการเข้าถึงกล้องและไมโครโฟนเพื่อเริ่มต้นใช้งาน');
        return; // จบการทำงาน
    }

    const ObjectImage = document.querySelector(".select_object");
    if (ObjectImage) {
        return; // จบการทำงาน
    }

    // session
    const left_eye = JSON.parse(sessionStorage.getItem("left_eye"));
    const right_eye = JSON.parse(sessionStorage.getItem("right_eye"));
    const lip = JSON.parse(sessionStorage.getItem("lip"));
    const Object = sessionStorage.getItem("ObjectPath");

    const configData = {
        LEFT_EYE: left_eye || [0, 0, 0],
        RIGHT_EYE: right_eye || [0, 0, 0],
        LIP: lip || [0, 0, 0],
        OBJECT: Object,
        width,
        height
    };

    try {
        // สร้างการเชื่อมต่อ WebSocket
        const socket = new WebSocket("ws://127.0.0.1:8000/mask_data");

        socket.onopen = () => {
            console.log("WebSocket Connected. Sending data...");
            socket.send(JSON.stringify(configData));  // ส่งข้อมูลไปยัง FastAPI
            access_signature_layer_custom_softpower();
        };
    } catch (error) {
        alert(`Error: ${error}`);
    }
});

document.getElementById("dbBtn").addEventListener("click", (event) => { //เปิดการเชื่อมต่อ ws

  try {
      // สร้างการเชื่อมต่อ WebSocket
      const socket = new WebSocket("ws://127.0.0.1:8000/database");
      socket.onmessage = (event) => {
        console.log("Data received from server:", event.data);
        const data = JSON.parse(event.data);
        console.log("Parsed data:", data);

        const dataDisplay = document.getElementById("dataDisplay");
        dataDisplay.innerHTML = "";

        // Loop through the data and create cards
        data.forEach(item => {
          const colDiv = document.createElement("div");
          colDiv.classList.add("col");

          const cardDiv = document.createElement("div");
          cardDiv.classList.add("card", "card-img", "filter");
          cardDiv.setAttribute("data-file-id", item.file_id);  // Store file_id in the element's dataset

          // Add an event listener to handle clicks on the card
          // cardDiv.addEventListener("click", () => {
          //     sendFileId(item.file_id, socket);  // Send file_id to the server
          // });

          const img = document.createElement("img");
          img.src = item.filter_path;  // Use the filter path for the image source
          img.classList.add("card-img-top");

          const cardBody = document.createElement("div");
          cardBody.classList.add("card-body", "pt-0");

          const cardTitle = document.createElement("p");
          cardTitle.classList.add("card-title", "text-center", "small");
          cardTitle.textContent = `filter ${item.file_id}`;  // Display file_id as title

          // Assemble the card
          cardDiv.appendChild(img);
          cardDiv.appendChild(cardBody);
          cardBody.appendChild(cardTitle);
          colDiv.appendChild(cardDiv);
          dataDisplay.appendChild(colDiv);
        });

        document.querySelectorAll(".card.card-img.filter").forEach(cardDiv => {
          cardDiv.addEventListener("click", async function () {
              console.log("click filter");
              const file_id = cardDiv.getAttribute("data-file-id");

              try {
                const socket = new WebSocket("ws://127.0.0.1:8000/database_filter");

                socket.onopen = () => {
                    console.log("WebSocket connected. Sending file_id...");
                    socket.send(JSON.stringify({ file_id: file_id }));  // Send file_id to the server
                };

                socket.onmessage = (event) => {
                    const result = JSON.parse(event.data);  // Parse the row data from server

                    // Handle the NULL (None) values
                    const configData = {
                        LEFT_EYE: [0, 0, 0],
                        RIGHT_EYE: [0, 0, 0],
                        LIP: [0, 0, 0],
                        TEXT: result.text,
                        OBJECT: result.object_path,
                        BG: result.bg_path,
                        width: width,
                        height: height
                    };

                    try {
                      // สร้างการเชื่อมต่อ WebSocket
                      const socket = new WebSocket("ws://127.0.0.1:8000/filter_data");

                      socket.onopen = () => {
                          console.log("WebSocket Connected. Sending data...");
                          socket.send(JSON.stringify(configData));
                          access_signature_layer_custom_softpower();
                      };
                  } catch (error) {
                      alert(`Error: ${error}`);
                  }

                };


            } catch (error) {
                console.error("Error retrieving data:", error);
                alert(`Error: ${error.message}`);
            }
          });
        });

    };

  } catch (error) {
      alert(`Error: ${error}`);
  }

  console.log(document.querySelectorAll(".card.card-img.filter").length); // Should log number of elements found
});

// function sendFileId(file_id, socket) {
//   const message = { "file_id": file_id };
//   socket.send(JSON.stringify(message));
// }

document.getElementById("bgFilter").addEventListener("click", (event) => { //เปิดการเชื่อมต่อ ws

  // ตรวจสอบการอนุญาตเข้าถึงกล้อง
  if (!window.stream) {
      alert('อนุญาติการเข้าถึงกล้องและไมโครโฟนเพื่อเริ่มต้นใช้งาน');
      return; // จบการทำงาน
  }

  const BG = sessionStorage.getItem("BgPath");

  const configData = {
      BG: BG,
      width,
      height
  };

  try {
      // สร้างการเชื่อมต่อ WebSocket
      const socket = new WebSocket("ws://127.0.0.1:8000/bg_data");

      socket.onopen = () => {
          console.log("WebSocket connected. Sending data...");
          socket.send(JSON.stringify(configData));  // ส่งข้อมูลไปยัง FastAPI

          access_signature_layer_custom_softpower();
      };
  } catch (error) {
      alert(`Error: ${error}`);
  }
});

document.getElementById("textFilter").addEventListener("click", (event) => { //เปิดการเชื่อมต่อ ws

  // ตรวจสอบการอนุญาตเข้าถึงกล้อง
  if (!window.stream) {
      alert('อนุญาติการเข้าถึงกล้องและไมโครโฟนเพื่อเริ่มต้นใช้งาน');
      return; // จบการทำงาน
  }

  const Object = document.querySelector(".form-control.text");
  if (Object.value === "") {
      alert('กรอกข้อความเพื่อสร้างฟิลเตอร์');
      return; // จบการทำงาน
  }

  const configData = {
      TEXT: Object.value,
      width,
      height
  };

  try {
      // สร้างการเชื่อมต่อ WebSocket
      const socket = new WebSocket("ws://127.0.0.1:8000/text_data");

      socket.onopen = () => {
          console.log("WebSocket connected. Sending data...");
          socket.send(JSON.stringify(configData));  // ส่งข้อมูลไปยัง FastAPI

          access_signature_layer_custom_softpower();
      };
  } catch (error) {
      alert(`Error: ${error}`);
  }
});

// Handle form submission
const form = document.getElementById('uploadMask');
form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const formData = new FormData(form);

    const response = await fetch('/', {
        method: 'POST',
        body: formData
    });

    if (response.ok) {
        // Parse JSON response from the backend
        const result = await response.json();
        console.log(result); // Log result to the console
        const imageUrl = `static/img/${result.filename}`;
        sessionStorage.setItem("ObjectPath", 'templates/'+imageUrl);

        const imageContainer = document.querySelector('.image-container');
        imageContainer.innerHTML = `<img id="selectedImageText" src="${imageUrl}" class="img-fluid" style="max-height: 180px;"/>`;
        selectImage();

        document.querySelectorAll('.card-img').forEach(el => {
          el.classList.remove('active');
        });

    } else {
        alert('Error uploading image!');
    }
});

const fileInput = document.getElementById('imagefile');
const submitBtn = document.getElementById('submitBtn');

// Add event listener to file input
fileInput.addEventListener('change', function() {
    // Trigger the submit button click when a file is selected
    if (fileInput.files.length > 0) {
        submitBtn.click();
    }
});

/* MediaRecorder */

// start: โหลดภาพสตรีม
window.onload = init;
function init() {
  const isPortrait = window.matchMedia("(orientation: portrait)").matches; //กำหนดขนาดวิดีโอตามมุมมองอุปกรณ์
  setVideoProperties(isPortrait);

  navigator.mediaDevices.getUserMedia({ video: { width: width, height: height } }) // การขอเข้าถึงกล้องและไมโครโฟนของผู้ใช้
    .then((stream) => {
      window.stream = stream;
      videoElement.srcObject = stream; // แสดงภาพสตรีมบนหน้าเว็บ
    })
    .catch((e) => {
      alert(`อนุญาติการเข้าถึงกล้องและไมโครโฟนเพื่อเริ่มต้นใช้งาน navigator.getUserMedia error: ${e.toString()}`);
    });
}

let width, height;
function setVideoProperties(portrait) {
  if (portrait) {
    width = 1080;
    height = 1920;
    videoElement.style.width = '300px';
    videoElement.style.aspectRatio = '9 / 16';
  } else {
    width = 1920;
    height = 1080;
    videoElement.style.width = '700px';
    videoElement.style.aspectRatio = '16 / 9';
  }
}

// ตรวจสอบการหมุนหน้าจอของอุปกรณ์
const canvas = document.getElementById("Display");
const videoElement = document.querySelector('video#videoDisplay');
window.matchMedia("(orientation: portrait)").addEventListener("change", () => {
  init();
});

// VIDEO
const mediaSource = new MediaSource(); //object จัดการข้อมูลสื่อ
mediaSource.addEventListener('sourceopen', handleSourceOpen, false);
let mediaRecorder;
let recordedBlobs;
let sourceBuffer;

// เพิ่ม source buffer เก็บข้อมูลสำหรับนำไปเล่น เมื่อ mediaSource เปิดใช้งาน
function handleSourceOpen(event) {
  console.log('MediaSource opened');
  sourceBuffer = mediaSource.addSourceBuffer('video/webm; codecs="vp8"'); // define type recode (on process)
  console.log('Source buffer: ', sourceBuffer);
}

// click บันทึก
let take_pictures=false;
const recordButton = document.querySelector('button#record');
recordButton.addEventListener('click', () => {
    if (iconBtn.classList.contains('bi-camera-fill')) { //
      if (image.style.display === 'none') {
        imageCapture();
      } else {
        take_pictures=true;
      }
    } else if (iconRecord.classList.contains('bi-camera-video-fill')) {
      console.log('click');
      startRecording();
    } else {
      stopRecording();
      iconBtn.className = "bi bi-camera-video-fill bi-lg";
    }
});

function startRecording() {
  recordedBlobs = [];
  let options = { mimeType: 'video/webm;codecs=vp9' };
  if (!MediaRecorder.isTypeSupported(options.mimeType)) {
      console.error(`${options.mimeType} is not Supported`);
      options = { mimeType: 'video/webm;codecs=vp8' };
      if (!MediaRecorder.isTypeSupported(options.mimeType)) {
          console.error(`${options.mimeType} is not Supported`);
          options = { mimeType: 'video/webm' };
          if (!MediaRecorder.isTypeSupported(options.mimeType)) {
              console.error(`${options.mimeType} is not Supported`);
              options = { mimeType: '' };
          }
      }
  }

  try {
      mediaRecorder = new MediaRecorder(window.stream, options);
  } catch (e) {
      console.error('Exception while creating MediaRecorder:', e);
      alert('Exception while creating MediaRecorder:', e);
      return;
  }

  console.log('Created MediaRecorder', mediaRecorder, 'with options', options);
  iconBtn.className = "bi bi-stop-fill bi-lg";

  mediaRecorder.onstop = (event) => {
      console.log('Recorder stopped: ', event);
      console.log('Recorded Blobs: ', recordedBlobs);
  };
  mediaRecorder.ondataavailable = handleDataAvailable;
  mediaRecorder.start(10); // collect 10ms of data
  console.log('MediaRecorder started', mediaRecorder);
}

function stopRecording() {
  mediaRecorder.stop();

  // สร้าง element <video>
  const recordedVideo = document.createElement('video');
  recordedVideo.id = 'recorded';
  recordedVideo.playsInline = true;
  recordedVideo.loop = true;
  // recordedVideo.controls = true;
  recordedVideo.style.width = videoElement.style.width;
  recordedVideo.style.aspectRatio = videoElement.style.aspectRatio;

  const modalBody = document.querySelector('#myModal .modal-body');
  modalBody.innerHTML = ''; // ล้างเนื้อหาเก่า
  modalBody.appendChild(recordedVideo);

  // Show modal after stopping the recording
  const myModal = new bootstrap.Modal(document.getElementById('myModal'));
  myModal.show();
  playRecorded();
}

function handleDataAvailable(event) {
  console.log('handleDataAvailable', event);
  if (event.data && event.data.size > 0) {
      recordedBlobs.push(event.data); //เก็บข้อมูลที่บันทึก
  }
}

function playRecorded() {
    const recordedVideo = document.querySelector('video#recorded');
    const superBuffer = new Blob(recordedBlobs, { type: 'video/webm' });
    recordedVideo.src = null;
    recordedVideo.srcObject = null;
    recordedVideo.src = window.URL.createObjectURL(superBuffer);
    recordedVideo.controls = true;
    recordedVideo.play();
}

// click ดาวน์โหลด
const downloadButton = document.querySelector('button#download');
downloadButton.addEventListener('click', () => {
  const imgElement = document.querySelector('#myModal .modal-body img');

  if (imgElement) {
    const url = imgElement.src;
    const a = document.createElement('a');
    a.style.display = 'none';
    a.href = url;
    a.download = 'filterlab.png';
    document.body.appendChild(a);
    a.click();
    setTimeout(() => {
      document.body.removeChild(a);
    }, 100);
  } else {
    // ถ้าไม่มีรูปภาพใน modal ให้ทำการดาวน์โหลดวิดีโอแทน
    const blob = new Blob(recordedBlobs, { type: 'video/webm' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.style.display = 'none';
    a.href = url;
    a.download = 'filterlab.webm';
    document.body.appendChild(a);
    a.click();
    setTimeout(() => {
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    }, 100);
  }
});

// PICTURE
function imageCapture() {
  const track = window.stream.getVideoTracks()[0];
  const imageCapture = new ImageCapture(track); // สร้าง ImageCapture instance

  imageCapture.takePhoto()
    .then((blob) => {
      const imgURL = URL.createObjectURL(blob);

    // สร้างภาพจาก blob
    const imgElement = new Image();
    imgElement.src = imgURL;

    imgElement.onload = () => {
      // สร้าง canvas เพื่อปรับขนาดภาพ
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      const scaleFactor = 0.5; // ลดขนาดภาพลงครึ่งหนึ่ง
      canvas.width = imgElement.naturalWidth * scaleFactor;
      canvas.height = imgElement.naturalHeight * scaleFactor;
      ctx.drawImage(imgElement, 0, 0, canvas.width, canvas.height);

      // แปลง canvas กลับเป็นภาพใหม่
      const newImgElement = document.createElement('img');
      newImgElement.src = canvas.toDataURL();

      // แทรกลงใน modal-body
      const modalBody = document.querySelector('#myModal .modal-body');
      modalBody.innerHTML = '';
      modalBody.appendChild(newImgElement);

      // Show modal with captured image
      const myModal = new bootstrap.Modal(document.getElementById('myModal'));
      myModal.show();
    };
  })
  .catch((error) => {
    alert('Error capturing image: ' + error.toString());
  });

}



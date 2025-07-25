const width = 640; // We will scale the photo width to this
let height = 0; // This will be computed based on the input stream

let streaming = false;
let photo_captured = false;

function clearPhoto() {
  const canvas = document.getElementById("canvas");
  const context = canvas.getContext("2d");
  context.fillStyle = "#AAA";
  context.fillRect(0, 0, canvas.width, canvas.height);

  const data = canvas.toDataURL("image/png");
  photo.setAttribute("src", data);
  photo_captured = false;
  $('[name="barcode_btn"]').prop('disabled', true);
}

function takePicture() {
  const canvas = document.getElementById("canvas");
  const video = document.getElementById("video");
  const photo = document.getElementById("photo")
  const context = canvas.getContext("2d");
  if (width && height) {
//    canvas.width = width;
    photo.width = width;
    photo.height = height;
//    canvas.height = height;
    console.log(video.width)

    context.drawImage(video, 0, 0, width, height);

    const data = canvas.toDataURL("image/jpg");
    photo.setAttribute("src", data);
    $("#photo").show()
    $(".output").show()
    $("#video").hide()
    $(".camera").hide()
    photo_captured = true;
    $("#id_image").val(canvas.toDataURL("image/jpg"));
    $('[name="barcode_btn"]').prop('disabled', false);
  } else {
    clearPhoto();
    $('[name="barcode_btn"]').prop('disabled', true);
  }
}

$(document).ready(() => {
    const video = document.getElementById("video");
    const canvas = document.getElementById("canvas");
    const photo = document.getElementById("photo");

    $("#photo").hide()
    $(".output").hide()

    const constraints = {
      video: {
        width: {
          min: 1280,
          ideal: 1920,
          max: 2560,

        },
        height: {
          min: 720,
          ideal: 1080,
          max: 1440,
        },
        facingMode: "environment",
      },
    }
    navigator.mediaDevices.getUserMedia(constraints)
        .then((stream) => {
            video.srcObject = stream;
            video.play();
            const track = stream.getVideoTracks()[0];

//            //Create image capture object and get camera capabilities
//            const imageCapture = new ImageCapture(track)
//            const photoCapabilities = imageCapture.getPhotoCapabilities().then(() => {
//
//            //todo: check if camera has a torch
//
//            //let there be light!
//            const btn = document.querySelector('.switch');
//            btn.addEventListener('click', function(){
//              track.applyConstraints({
//                advanced: [{torch: true}]
//              });
//            });
//            $(".message").html("hasTorch " + hasTorch);
        })
        .catch((error) => {
            console.error("Error accessing the camera: ", error);
            alert("Could not access the camera. Please allow permissions and try again.");
        });
    video.addEventListener(
      "canplay",
      (ev) => {

        if (!streaming) {
          height = video.videoHeight / (video.videoWidth / width);

          if (video.videoHeight > video.videoWidth) {
            $(".ratio").css("--bs-aspect-ratio", "177%") // 9:16 aspect ratio for vertical camera
          } else {
            $(".ratio").css("--bs-aspect-ratio", "56%") // 16:9 aspect ratio for horizontal camera
          }
          video.setAttribute("width", width);
          video.setAttribute("height", height);
          canvas.setAttribute("width", width);
          canvas.setAttribute("height", height);
          streaming = true;
        }
      },
      false,
    );

    $("#video").click(function(ev) {
        takePicture();
        ev.preventDefault();
    });

    clearPhoto();
    $("#barcode-form").submit(function(e){
        if ($("#id_bow_id").val() == '' && !photo_captured && $("#id_image_field").val()) {
            e.preventDefault();
        }
    });
    $('[name="barcode_btn"]').prop('disabled', true);

    $("#id_bow_id").change(function(e){
        if ($("#id_bow_id").val() == '' && !photo_captured) {
            $('[name="barcode_btn"]').prop('disabled', true);
        } else {
            $('[name="barcode_btn"]').prop('disabled', false);
        }
    });
    $("#id_image_field").change(function(e) {
        if ($("#id_image_field").val() == '' && $("#id_bow_id").val() == '' && !photo_captured){
            $('[name="barcode_btn"]').prop('disabled', true);
        } else {
            $('[name="barcode_btn"]').prop('disabled', false);
        }
    });
    $("#photo").click(function(ev) {
        $("#photo").hide()
        $(".output").hide()
        $("#video").show()
        $(".camera").show()
        clearPhoto()
    });
});
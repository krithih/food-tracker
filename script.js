function uploadFile(event) {
    event.preventDefault();  // this doesn't let the page reload when form is submitted

    let file = document.getElementById("fileUpload").files[0];  //id matches input id in html

    if (!file) {  //in case no file is uploaded
        document.getElementById("uploadMessage").innerText = "Please select a file.";  
        return;
    } 

    let formData = new FormData();   //create a form container
    formData.append("file", file);    //adds the file to the container, the key "file" matches the key in the backend flask app.py


    fetch("http://127.0.0.1:5000/upload", {   // sends request to /upload Flask route (5000 instead of live server 5500 route)
        method: "POST",   //sending data, as opposed to "GET" which requests data
        body: formData    //send file
    })
    .then(response => response.text())  //Flask responds w Promise, .text() converts it to string
    .then(data => {
        document.getElementById("uploadMessage").innerText = data;  //updates the "uploadMessage" id paragraph with the text response from Flask
    })
    .catch(error => {
        document.getElementById("uploadMessage").innerText = "Upload failed: " + error.message; //if anything goes wrong in fetch(), error message displayed
    });
}


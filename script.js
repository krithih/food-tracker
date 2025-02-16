function uploadFile(event) {
    event.preventDefault();  // this doesn't let the page reload when form is submitted

    let file = document.getElementById("fileUpload").files[0];  //id matches input id in html

    if (!file) {  //in case no file is uploaded
        document.getElementById("uploadMessage").innerText = "Please select a file.";  
        return;
    } 

    let formData = new FormData();   //create a form container
    formData.append("file", file);    //adds the file to the container, the key "file" matches the key in the backend flask app.py


    fetch("http://127.0.0.1:5000/upload", {
        method: "POST",
        body: formData
    })
    .then(response => {
        console.log("Response status:", response.status);
        return response.json();
    })
    .then(data => {
        console.log("Server Response:", data);
        console.log("Message:", data.message);
        console.log("Extracted Text:", data.extracted_text);
    
        document.getElementById("uploadMessage").innerText = data.message || "Upload completed";
        document.getElementById("extractedText").innerText = data.extracted_text ? "Extracted Text: " + data.extracted_text : "No text extracted.";
        })
    .catch(error => {
        console.error("Fetch error:", error);
        document.getElementById("uploadMessage").innerText = "Upload failed: " + error.message;
    });
}

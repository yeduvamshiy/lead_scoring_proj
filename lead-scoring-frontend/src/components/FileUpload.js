import React, { useState } from 'react';
import axios from 'axios';
import 'bootstrap/dist/css/bootstrap.min.css';
import '../App.css';

const FileUpload = () => {
    const [file, setFile] = useState(null);

    const handleFileChange = (event) => {
        setFile(event.target.files[0]);
    };

    const handleFileUpload = () => {
        if (!file) {
            alert("Please select a file first!");
            return;
        }
        const formData = new FormData();
        formData.append('file', file);

        axios.post('http://localhost:5000/score', formData)
            .then(response => {
                const url = window.URL.createObjectURL(new Blob([response.data]));
                const link = document.createElement('a');
                link.href = url;
                link.setAttribute('download', 'scoring_results.csv');
                document.body.appendChild(link);
                link.click();
            })
            .catch(error => {
                alert('Error uploading file');
                console.error(error);
            });
    };

    return (
        <div className="container mt-5">
            <h3 className="mb-4">Upload CSV for Scoring</h3>
            <div className="mb-3">
                <input type="file" className="form-control" onChange={handleFileChange} />
            </div>
            <button className="btn btn-primary mt-2" onClick={handleFileUpload}>Process File</button>
        </div>
    );
};

export default FileUpload;

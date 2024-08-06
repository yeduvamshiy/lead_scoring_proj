import React from 'react';
import UpdateWeights from './components/UpdateWeights';
import FileUpload from './components/FileUpload';
import './App.css';

const App = () => {
  return (
    <div className="container">
      <UpdateWeights />
      <FileUpload />
    </div>
  );
};

export default App;

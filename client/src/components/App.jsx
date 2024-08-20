import React from 'react';
import 'antd/dist/reset.css';
import '../scss/App.scss';
import ImageUploader from './ImageUploader';

function App() {
  return (
    <div className="App">
      <h1>Image Similarity Finder</h1>
      <ImageUploader />
    </div>
  );
}

export default App;
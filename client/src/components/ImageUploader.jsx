import React, { useState } from 'react';
import { Upload, Button, Image, Row, Col, Spin, message } from 'antd';
import { UploadOutlined } from '@ant-design/icons';

const ImageUploader = () => {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState([]);

  const handleUpload = ({ file }) => {
    setFile(file);
  };

  const handleSubmit = async () => {
    if (!file) {
      message.error('Please upload an image first');
      return;
    }

    setLoading(true);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:5000/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to upload image');
      }

      const data = await response.json();
      setResults(data);
      message.success('Image uploaded and processed successfully');
    } catch (error) {
      console.error('Error uploading the image:', error);
      message.error('There was an error processing your request');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '50px' }}>
      <Row gutter={[16, 16]}>
        <Col span={24}>
          <Upload beforeUpload={() => false} onChange={handleUpload}>
            <Button icon={<UploadOutlined />}>Click to Upload</Button>
          </Upload>
        </Col>
        <Col span={24}>
          <Button type="primary" onClick={handleSubmit} disabled={!file || loading}>
            {loading ? <Spin /> : 'Submit'}
          </Button>
        </Col>
      </Row>

      {results.length > 0 && (
        <div style={{ marginTop: '30px' }}>
          <h3>Similar Images:</h3>
          <Row gutter={[16, 16]}>
            {results.map((result, index) => (
              <Col key={index} span={6}>
                <Image
                  width={200}
                  src={`http://localhost:5000/${result.image_path}`}
                  alt={`Similar Image ${index + 1}`}
                />
                <p>Similarity Score: {result.score.toFixed(2)}</p>
              </Col>
            ))}
          </Row>
        </div>
      )}
    </div>
  );
};

export default ImageUploader;
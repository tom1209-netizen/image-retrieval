import React, { useState, useEffect } from 'react';
import { Upload, Button, Image, Row, Col, Spin, message } from 'antd';
import { UploadOutlined } from '@ant-design/icons';

const ImageUploader = () => {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState([]);
  const [fetchedImages, setFetchedImages] = useState([]);

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
      const response = await fetch(`${import.meta.env.VITE_BACKEND_DOMAIN}/upload`, {
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

  useEffect(() => {
    if (results.length > 0) {
      // Fetch images for each result
      const fetchImages = async () => {
        const images = await Promise.all(
          results.map(async (result) => {
            const response = await fetch(`${import.meta.env.VITE_BACKEND_DOMAIN}/images/${result.image_path}`);
            if (response.ok) {
              const blob = await response.blob();
              return URL.createObjectURL(blob);
            } else {
              return null;
            }
          })
        );
        setFetchedImages(images);
      };
      fetchImages();
    }
  }, [results]);

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

      {fetchedImages.length > 0 && (
        <div style={{ marginTop: '30px' }}>
          <h3>Top 10 Similar Images:</h3>
          <Row gutter={[16, 16]}>
            {fetchedImages.map((imageSrc, index) => (
              <Col key={index} span={6}>
                {imageSrc ? (
                  <Image
                    width={200}
                    src={imageSrc}
                    alt={`Similar Image ${index + 1}`}
                  />
                ) : (
                  <p>Image could not be loaded</p>
                )}
                <p>Similarity Score: {results[index].score.toFixed(2)}</p>
              </Col>
            ))}
          </Row>
        </div>
      )}
    </div>
  );
};

export default ImageUploader;